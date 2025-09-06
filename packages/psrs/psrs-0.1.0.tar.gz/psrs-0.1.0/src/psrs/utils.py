import logging
from typing import Tuple

import torch
import torch.nn.modules.loss as loss

# instantiate logger
logger = logging.getLogger(__name__)
logger.propagate = True


class ProcrustesLoss(loss._Loss):
    """
    Implements Procrustes analysis as a PyTorch loss function.

    Calculates the disparity (sum of squared differences) between two centered
    and normalized point clouds (input and target) after applying the optimal
    orthogonal transformation (rotation/reflection and scaling) to align the
    input to the target.
    """
    __constants__ = ["reduction"]

    def __init__(self, size_average=None, reduce=None, reduction: str = "mean") -> None:
        """
        Initializes the ProcrustesLoss module.

        Args:
            size_average (Optional[bool]): Deprecated (see `reduction`).
            reduce (Optional[bool]): Deprecated (see `reduction`).
            reduction (str): Specifies the reduction to apply to the output:
                             'none' | 'mean' | 'sum'. 'mean': the sum of the output will
                             be divided by the number of elements in the output.
                             'sum': the output will be summed. Default: 'mean'
        """
        super().__init__(size_average, reduce, reduction)

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Computes the Procrustes loss between input and target tensors.

        Args:
            input (torch.Tensor): The input tensor (point cloud) to align.
                                  Shape: (n_points, n_dimensions).
            target (torch.Tensor): The target tensor (point cloud).
                                   Shape: (n_points, n_dimensions).

        Returns:
            torch.Tensor: The calculated Procrustes disparity (loss value).
                          Scalar if reduction is 'mean' or 'sum'.
        """
        # Ensure data is float
        input = input.float()
        target = target.float()

        # Center the data by subtracting the mean
        input = input - torch.mean(input, 0)
        target = target - torch.mean(target, 0)

        # Normalize the data to unit norm
        norm_input = torch.norm(input)
        norm_target = torch.norm(target)
        input = input / norm_input
        target = target / norm_target

        # Apply the optimal orthogonal transformation
        R, scale = self.orthogonal_procrustes(input, target)
        transformed_input = torch.mm(input, R.t()) * scale

        # Compute the disparity (sum of squared differences)
        disparity = torch.sum((target - transformed_input) ** 2)

        return disparity

    @staticmethod
    def orthogonal_procrustes(A: torch.Tensor, B: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Computes the optimal orthogonal transformation (rotation/reflection matrix R
        and scaling factor scale) that minimizes ||B - A @ R.T * scale||^2 using SVD.

        Aligns matrix A to matrix B.

        Args:
            A (torch.Tensor): Input matrix (point cloud) to be transformed.
                              Shape (n_points, n_dimensions). Should be centered and normalized.
            B (torch.Tensor): Target matrix (point cloud).
                              Shape (n_points, n_dimensions). Should be centered and normalized.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]:
                - R (torch.Tensor): The optimal rotation/reflection matrix. Shape (n_dimensions, n_dimensions).
                - scale (torch.Tensor): The optimal scaling factor (scalar tensor).
        """
        # Compute the matrix product of B.T and A
        product = B.T @ A

        # Singular Value Decomposition
        U, S, V = approximate_svd(product)  # Use custom SVD for stability potentially

        # Compute the rotation/reflection matrix R
        R = U @ V.T

        # Compute the scale factor as the sum of singular values
        scale = S.sum()
        return R, scale


def approximate_svd(A: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Approximate Singular Value Decomposition (SVD) of a matrix A.

    This custom SVD is used to handle specific numerical stability issues that
    may arise in the context of Procrustes analysis, where the input matrix
    product A @ A.T is symmetric. The custom approach ensures that the singular
    values are computed accurately even when the matrix is nearly singular or
    has very small eigenvalues.

    Args:
        A (torch.Tensor): The input matrix of shape (m, n).

    Returns:
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            - U (torch.Tensor): Left singular vectors. Shape (m, m).
            - S (torch.Tensor): Singular values (diagonal of Σ). Shape (k,) where k=min(m,n).
            - V (torch.Tensor): Right singular vectors. Shape (n, n). Note: torch.linalg.svd returns V.T (Vh).
    """
    # Compute eigenvalues and eigenvectors for A @ A^T
    try:
        eigenvalues, U = torch.linalg.eigh(A @ A.T)
    except torch._C._LinAlgError as e:
        logger.error(f"Eigendecomposition failed in approximate_svd: {e}")
        raise e

    # Sort singular values and corresponding vectors in descending order
    sorted_indices = torch.argsort(eigenvalues.real, descending=True)
    eigenvalues = eigenvalues[sorted_indices]
    U = U[:, sorted_indices]

    # Ensure eigenvalues are non-negative before sqrt
    eigenvalues_clamped = torch.clamp(eigenvalues.real, min=0)

    # Calculate singular values
    S = torch.sqrt(eigenvalues_clamped)

    # Handle potential numerical issues in U (NaN/Inf)
    if torch.isnan(U).any() or torch.isinf(U).any():
        logger.warning("NaN or Inf detected in U during approximate_svd. Results might be unreliable.")

    # Compute V using the formula V = A.T @ U @ diag(1/S)
    s_inv = torch.zeros_like(S)
    non_zero_mask = S > 1e-9
    s_inv[non_zero_mask] = 1.0 / S[non_zero_mask]
    S_inv_diag = torch.diag(s_inv)

    if A.shape[0] == A.shape[1]:
        V = (A.T @ U) @ S_inv_diag
    else:
        logger.error("approximate_svd currently assumes square matrix based on usage context.")
        U_svd, S_svd, Vh_svd = torch.linalg.svd(A, full_matrices=False)
        return U_svd, S_svd, Vh_svd.T

    # Check V for NaN/Inf
    if torch.isnan(V).any() or torch.isinf(V).any():
        logger.warning("NaN or Inf detected in V during approximate_svd. Results might be unreliable.")

    return U, S, V

