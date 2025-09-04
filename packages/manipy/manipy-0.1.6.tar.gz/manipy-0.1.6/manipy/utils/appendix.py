import torch
import numpy as np
import matplotlib.pyplot as plt

# Training utilities
def evaluate_r2(model, data_loader, device):
    model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for xb, yb in data_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            pred = model(xb)
            y_true.append(yb.cpu().numpy())
            y_pred.append(pred.cpu().numpy())
    y_true = np.concatenate(y_true, axis=0)
    y_pred = np.concatenate(y_pred, axis=0)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - ss_res / (ss_tot + 1e-12)
    return r2



@torch.no_grad()
def density_special_gaussian(x: torch.Tensor,
                             a: float = 2.0,
                             b: float = 1.0,
                             y_std: float = 2.0,
                             return_log: bool = False) -> torch.Tensor:
    """
    Unnormalized density p(x) corresponding to the (y, s) construction.
    Matches your NumPy expression up to a constant factor.
      p_y(y) = N(0, y_std^2)
      p(s|y) = N(0, σ²(y)), σ²(y)=exp(-y^2/4)
      y = f_lin(x) = a x1 + b x2
      s = projection of x onto tangent direction
    We return p_x ∝ p_y(y) * p(s|y) * ||∇f||  (your code’s convention).
    """
    device, dtype = x.device, x.dtype
    n_hat, t_hat, gnorm = ortho_frame(a, b, device, dtype)

    y = f_linear(x, a, b)  # (N,)
    alpha = y / (gnorm + 1e-12)   # along n_hat
    # Decompose x in (n_hat, t_hat) basis to get s
    s = (x * t_hat).sum(dim=1)    # (N,)

    # p_y
    log_p_y = -0.5 * (y * y) / (y_std * y_std) - torch.log(torch.tensor(y_std * np.sqrt(2 * np.pi), dtype=dtype, device=device))
    # sigma^2(y)
    sigma2 = sigma2_of_y(y)
    # p(s|y)
    log_p_s = -0.5 * (s * s) / (sigma2 + 1e-12) - 0.5 * torch.log(2 * torch.pi * sigma2 + 1e-12)

    # your convention multiplies by ||∇f|| (a constant factor)
    log_p = log_p_y + log_p_s + torch.log(torch.tensor(gnorm, dtype=dtype, device=device) + 1e-12)

    return log_p if return_log else torch.exp(log_p)
def make_impression_function(
    # --- main peak (a smooth hill) ---
    peak_mu=(0.2, -0.1),
    peak_cov=((0.35, 0.12), (0.12, 0.6)),
    peak_amp=1.0,
    # --- low-valued attractors (valleys/minima) ---
    attractors=(
        {"mu": (-1.0,  0.8), "cov": ((0.25, 0.00), (0.00, 0.06)), "depth": 0.9},
        {"mu": ( 0.9, -0.9), "cov": ((0.18, 0.07), (0.07, 0.12)), "depth": 0.7},
        {"mu": ( 0.3,  0.9), "cov": ((0.10, 0.00), (0.00, 0.30)), "depth": 0.6},
    ),
    # --- optional oriented lanes (anisotropic tubes, +ridge / -valley) ---
    lanes=(
        {"dir": (1.0, 0.0), "center": (0.0, 0.0), "width_perp": 0.15, "length_along": 1.6, "gain": 0.35, "sign": +1.0},
        {"dir": (0.0, 1.0), "center": (-0.6, 0.3), "width_perp": 0.10, "length_along": 1.0, "gain": 0.25, "sign": -1.0},
    ),
    # --- NEW: linear component along z = x + y ---
    lin_z_gain: float = 0.0,       # set >0 to enable (adds a plane along the 45° diagonal)
    lin_z_center: float = 0.0,     # shift: uses (z - lin_z_center)
    lin_z_tanh_alpha: float = 0.0, # if >0, saturate with tanh(alpha * (z - center))
    # --- sigmoid envelope so the landscape "ends" smoothly ---
    envelope_center=(0.0, 0.0),
    envelope_r0=2.2,
    envelope_beta=2.0,
    # --- global squashing of the final value (keeps outputs in [-scale, scale]) ---
    squash_alpha=0.9,
    squash_scale=1.0,
    # --- tiny roughness (set to 0.0 to remove) ---
    roughness_amp=0.05,
    roughness_scale=1.5,
    density = density_special_gaussian,
):
    """
    Returns: impression_function(x: (N,2)->(N,)) closure.

    Components:
      + Main anisotropic peak (μ, Σ)
      - Attractor wells (anisotropic minima)
      ± Oriented lanes (ridges/valleys)
      + Linear diagonal term: z = x1 + x2  (tilts landscape along 45°)
      × Radial sigmoid envelope (ends the landscape)
      → Optional global tanh squash
    """
    # tensors for closure
    peak_mu_t = torch.tensor(peak_mu, dtype=torch.float32)
    peak_cov_t = torch.tensor(peak_cov, dtype=torch.float32)
    env_c_t = torch.tensor(envelope_center, dtype=torch.float32)

    attract_list = []
    for it in attractors:
        mu_t = torch.tensor(it["mu"], dtype=torch.float32)
        cov_t = torch.tensor(it["cov"], dtype=torch.float32)
        depth = float(it["depth"])
        attract_list.append((mu_t, cov_t, depth))

    lane_list = []
    for it in lanes:
        d = torch.tensor(it["dir"], dtype=torch.float32)
        d = d / (torch.norm(d) + 1e-12)
        c = torch.tensor(it["center"], dtype=torch.float32)
        wp = float(it["width_perp"])
        la = float(it["length_along"])
        gain = float(it["gain"])
        sign = float(it.get("sign", +1.0))
        d_perp = torch.tensor([-d[1], d[0]], dtype=torch.float32)
        R = torch.stack([d, d_perp], dim=1)  # 2x2
        S = torch.tensor([[la**2, 0.0], [0.0, wp**2]], dtype=torch.float32)
        cov_lane = R @ S @ R.T
        lane_list.append((c, cov_lane, gain, sign))

    eye2 = torch.eye(2)

    def _precision(cov: torch.Tensor, device, dtype):
        cov = cov.to(device=device, dtype=dtype)
        return torch.inverse(cov + 1e-6 * eye2.to(device=device, dtype=dtype))

    def _gauss_aniso(x, mu, cov_prec):
        d = x - mu
        q = torch.einsum('ni,ij,nj->n', d, cov_prec, d)
        return torch.exp(-0.5 * q)

    def impression_function(x: torch.Tensor) -> torch.Tensor:
        device, dtype = x.device, x.dtype

        # Base: main peak
        P_peak = _precision(peak_cov_t, device, dtype)
        mu = peak_mu_t.to(device=device, dtype=dtype)
        val = _gauss_aniso(x, mu, P_peak) * float(peak_amp)

        # Subtract attractors (valleys)
        for (mu_i, cov_i, depth_i) in attract_list:
            P = _precision(cov_i, device, dtype)
            mui = mu_i.to(device=device, dtype=dtype)
            val = val - float(depth_i) * _gauss_aniso(x, mui, P)

        # Add oriented lanes
        for (c_i, cov_lane, gain_i, sign_i) in lane_list:
            P = _precision(cov_lane, device, dtype)
            ci = c_i.to(device=device, dtype=dtype)
            val = val + float(sign_i) * float(gain_i) * _gauss_aniso(x, ci, P)

        # --- NEW: linear component z = x1 + x2 ---
        if lin_z_gain != 0.0:
            z = x[:, 0] + x[:, 1]
            z_shift = z - float(lin_z_center)
            if lin_z_tanh_alpha and lin_z_tanh_alpha > 0.0:
                z_term = float(lin_z_gain) * torch.tanh(float(lin_z_tanh_alpha) * z_shift)
            else:
                z_term = float(lin_z_gain) * z_shift *z_shift*(z_shift)
            val = val + z_term

        # Optional tiny smooth roughness
        if roughness_amp != 0.0:
            s = float(roughness_scale)
            val = val + float(roughness_amp) * torch.exp(
                -0.5 * ((x[:, 0] / s) ** 2 + (x[:, 1] / s) ** 2)
            ) * (0.25 * x[:, 0] + 0.35 * x[:, 1])

        # Radial sigmoid envelope
        r = torch.norm(x - env_c_t.to(device=device, dtype=dtype), dim=1)
        gate = torch.sigmoid(float(envelope_beta) * (float(envelope_r0) - r))
        val = gate * val*(torch.sigmoid((val+.7)**3)*density(x, 2,1)+torch.sigmoid((val+.7)**3)/7)
        val = val+ float(lin_z_gain) * z_shift*3

        # Final squash
        out = float(squash_scale) * torch.tanh(float(squash_alpha) * val)
        return out

    return impression_function
import torch
import numpy as np
import time


# --- NEW: Data distribution visualization ---
def plot_data_distribution(distribution_sampler,
                           n_samples: int = 30000,
                           show_support: bool = True,
                           support_method: str = "constraints",
                           p_min: float | None = None,
                           p_min_rel: float = 0.05,
                           bandwidth: float = 0.15,
                           title: str = "Data distribution",
                           fig = None, ax = None):
    """
    Visualize sampled data with a density-like background and (optional) support boundary.
    """
    import matplotlib.pyplot as plt

    x = distribution_sampler(n_samples).cpu()
    X = x.numpy()
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.0))
    else:
        title = None
    hb = ax.hexbin(X[:, 0], X[:, 1], gridsize=65, bins='log', alpha=0.8)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('log counts')

    if show_support:
        draw_support_boundary(ax,density_fn=density_special_gaussian,density_kwargs=dict(a=2.0, b=1.0, y_std=2.0),
            xlim=(-3, 3), ylim=(-3, 3), resolution=300, p_min=None, p_rel=0.25, linewidth=2.0, linestyle="-.", color="white")
    if title is not None:
        ax.set_title(title)
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")
    plt.tight_layout()
    if title is not None:
        plt.show()
    else:
        return ax



def plot_trajectories_with_impression_and_support(trajectories, impression_fn,
                                                  title="",
                                                  show_support: bool = True,
                                                  support_method: str = "constraints",
                                                  p_min: float | None = None,
                                                  p_min_rel: float = 0.05,
                                                  bandwidth: float = 0.15,
                                                  xlim=(-3., 3.), ylim=(-2, 2)):
    """
    Same as your plot_trajectories_with_impression, but adds a probability-support boundary.
    - support_method="constraints" draws the analytic boundary of the sampler's base region.
    - support_method="kde" draws {x : p_hat(x) > threshold}, where threshold is p_min (or p_min_rel * max p).
    """
    x_range = np.linspace(xlim[0], xlim[1], 160)
    y_range = np.linspace(ylim[0], ylim[1], 160)
    X, Y = np.meshgrid(x_range, y_range)

    grid_points = torch.tensor(np.stack([X.ravel(), Y.ravel()], axis=1), dtype=torch.float32)
    Z = impression_fn(grid_points).detach().numpy().reshape(X.shape)

    fig, ax = plt.subplots(1, 1, figsize=((xlim[1]-xlim[0])*2, (ylim[1]-ylim[0])*2))
    contour = ax.contourf(X, Y, Z, levels=24, cmap='viridis', alpha=0.6)
    plt.colorbar(contour, ax=ax, label='Impression Value')

    # Plot trajectories (expects shape (T, N, 2))
    T, N, _ = trajectories.shape
    n_plot = min(N, 100)
    for traj in trajectories.transpose(1, 0, 2)[:n_plot]:
        ax.plot(traj[:, 0], traj[:, 1], 'r-', alpha=0.3, linewidth=0.7)
        ax.scatter(traj[0, 0], traj[0, 1], c='blue', s=8, alpha=0.7)
        ax.scatter(traj[-1, 0], traj[-1, 1], c='red', s=8, alpha=0.7)

    # NEW: support boundary
    if show_support:
        draw_support_boundary(ax,density_fn=density_special_gaussian,density_kwargs=dict(a=2.0, b=1.0, y_std=2.0),
            xlim=(-3, 3), ylim=(-3, 3), resolution=300, p_min=None, p_rel=0.25, linewidth=2.0, linestyle="-.", color="white")


    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_xlabel('x₁'); ax.set_ylabel('x₂'); ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def plot_streamlines_with_impression_and_support(vector_field_fn, impression_fn,
                                                 title="",
                                                 show_support: bool = True,
                                                 support_method: str = "constraints",
                                                 p_min: float | None = None,
                                                 p_min_rel: float = 0.05,
                                                 bandwidth: float = 0.15,
                                                 xlim=(-3., 3.), ylim=(-2, 2),
                                                 density=1.2):
    """
    Visualize the impression function as a background and overlay streamlines of the vector field.
    vector_field_fn: function mapping (N,2) torch tensor to (N,2) torch tensor (the vector field)
    impression_fn: function mapping (N,2) torch tensor to (N,) torch tensor (the impression)
    """
    x_range = np.linspace(xlim[0], xlim[1], 160)
    y_range = np.linspace(ylim[0], ylim[1], 160)
    X, Y = np.meshgrid(x_range, y_range)
    grid_points = torch.tensor(np.stack([X.ravel(), Y.ravel()], axis=1), dtype=torch.float32)

    # Impression background
    Z = impression_fn(grid_points).detach().numpy().reshape(X.shape)

    # Vector field
    V = vector_field_fn(grid_points).detach().numpy()
    Ux = V[:, 0].reshape(X.shape)
    Uy = V[:, 1].reshape(X.shape)

    fig, ax = plt.subplots(1, 1, figsize=((xlim[1]-xlim[0])*2, (ylim[1]-ylim[0])*2))
    contour = ax.contourf(X, Y, Z, levels=24, cmap='viridis', alpha=0.6)
    plt.colorbar(contour, ax=ax, label='Impression Value')

    # Streamlines
    strm = ax.streamplot(X, Y, Ux, Uy, color='w', density=density, linewidth=1.2, arrowsize=1.5, broken_streamlines=False)

    # Support boundary
    if show_support:
        draw_support_boundary(ax, density_fn=density_special_gaussian, density_kwargs=dict(a=2.0, b=1.0, y_std=2.0),
            xlim=(-3, 3), ylim=(-3, 3), resolution=300, p_min=None, p_rel=0.25, linewidth=2.0, linestyle="-.", color="white")

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel('x₁')
    ax.set_ylabel('x₂')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# --- Live dashboard (requires the StreamlineMetricsDashboard + MetricSpec definitions from the previous cell) ---

# Shape-safe wrappers (expect (N,2) -> (N,2) for vf, (N,2) -> (N,) for scalar fields)
def vf_wrapper(pts: torch.Tensor) -> torch.Tensor:
    # model returns (N,2)
    return model(pts)

def impression_wrapper(pts: torch.Tensor) -> torch.Tensor:
    out = ensemble(pts)                   # could be (N,) or (N,1)
    return out.view(-1) if out.ndim > 1 else out

def density_wrapper(pts: torch.Tensor) -> torch.Tensor:
    # match the kwargs you used for support drawing elsewhere
    return density_special_gaussian(pts, a=2.0, b=1.0, y_std=2.0)

# dash = StreamlineMetricsDashboard(
#     vector_field_fn=vf_wrapper,
#     impression_fn=impression_wrapper,
#     density_fn=density_wrapper,          # or None to hide the dashed support curve
#     device=device,
#     xlim=(-3., 3.), ylim=(-2., 2.),
#     resolution=100,                      # higher = smoother background/streamlines
#     seed_grid=(24, 18),                  # more seeds = denser streamlines
#     max_steps=700,
#     support_cutoff=0.02,
#     metrics=[
#         MetricSpec("loss", "MSE Loss"),
#         MetricSpec("lr",   "Learning Rate", dash="dot", formatter=lambda v: f"{v:.1e}"),
#     ],
#     title="PGFM Training (Streamlines + Metrics)",
# )