
def sample_gaussian_around_x(n: int,
                             x_points: torch.Tensor,
                             kernel_std: float = 0.1,
                             device=None,
                             dtype=torch.float32) -> torch.Tensor:
    """
    Sample n points from a Gaussian kernel centered at a randomly selected x from x_points.

    Args:
        n: Number of samples to generate.
        x_points: Tensor of shape (M, D) containing candidate x points.
        kernel_std: Standard deviation of the Gaussian kernel.
        device: Torch device.
        dtype: Torch dtype.

    Returns:
        samples: Tensor of shape (n, D) of samples.
    """
    if device is None:
        device = x_points.device
    x_points = x_points.to(device=device, dtype=dtype)
    M, D = x_points.shape
    idx = torch.randint(0, M, (1,))
    x_center = x_points[idx].squeeze(0)  # shape (D,)
    samples = x_center + torch.randn(n, D, device=device, dtype=dtype) * kernel_std
    return samples

