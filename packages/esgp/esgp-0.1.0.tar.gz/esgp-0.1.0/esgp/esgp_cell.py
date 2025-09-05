import torch
import torch.nn as nn
import torch.nn.functional as F

# === Utility: Spectral Radius Normalization ===
def normalize_spectral_radius(W, desired_radius=0.9):
    """
    Normalizes the spectral radius of a given weight matrix W.
    Ensures that the largest absolute eigenvalue is equal to desired_radius.
    """
    # Ensure W is a square matrix
    if W.dim() == 2 and W.size(0) == W.size(1):
        # Compute eigenvalues and their absolute values
        eigvals = torch.linalg.eigvals(W).abs()
        # Find the maximum absolute eigenvalue (spectral radius)
        max_eig = eigvals.max()
        # Normalize if max_eig is not negligible
        if max_eig > 1e-6:  # Avoid division by zero for very small eigenvalues
            return W * (desired_radius / max_eig)
    return W  # Return original if not a square matrix or max_eig is too small

# === ESGP++ Cell ===
class ESGPCell(nn.Module):
    """
    Echo State Gated Population Cell (ESGP++) as described in research papers.
    It combines a fixed, spectrally normalized recurrent matrix with a learned gate.
    """
    def __init__(self, input_size, hidden_size, sparsity=0.1, spectral_radius=0.9):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.sparsity = sparsity
        self.spectral_radius = spectral_radius
        
        # Initialize recurrent weight matrix W with random values
        W = torch.randn(hidden_size, hidden_size)
        # Normalize its spectral radius
        W = normalize_spectral_radius(W, desired_radius=spectral_radius)
        # Register W as a buffer; it's part of the model state but not a trainable parameter
        self.register_buffer("W", W)
        
        # Create a sparse mask for W
        self.register_buffer("mask", (torch.rand_like(W) < sparsity).float())
        
        # Input weight matrix Win (trainable)
        self.Win = nn.Linear(input_size, hidden_size, bias=False)
        
        # Gating mechanism weights (trainable)
        self.gate = nn.Linear(hidden_size, hidden_size)

    def forward(self, x, h_prev):
        """
        Forward pass for one timestep of the ESGP++ cell.
        
        Args:
            x (torch.Tensor): Current input, shape (batch_size, input_size)
            h_prev (torch.Tensor): Previous hidden state, shape (batch_size, hidden_size)
            
        Returns:
            torch.Tensor: Current hidden state, shape (batch_size, hidden_size)
        """
        # Calculate the "reservoir" part of the hidden state
        h_res = torch.tanh(self.Win(x) + F.linear(h_prev, self.W * self.mask))
        
        # Calculate the gate activation
        g = torch.sigmoid(self.gate(h_res))
        
        # Combine the new reservoir state and the previous hidden state using the gate
        h = g * h_res + (1 - g) * h_prev
        return h

    def extra_repr(self):
        return f"input_size={self.input_size}, hidden_size={self.hidden_size}, " \
               f"sparsity={self.sparsity}, spectral_radius={self.spectral_radius}"