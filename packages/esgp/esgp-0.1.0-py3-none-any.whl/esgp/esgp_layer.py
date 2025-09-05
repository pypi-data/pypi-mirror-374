import torch
import torch.nn as nn
from .esgp_cell import ESGPCell

class ESGP(nn.Module):
    """
    ESGP layer that can process sequences, similar to LSTM/GRU.
    
    Args:
        input_size: The number of expected features in the input x
        hidden_size: The number of features in the hidden state h
        num_layers: Number of recurrent layers
        sparsity: Sparsity of the recurrent weight matrix (default: 0.1)
        spectral_radius: Desired spectral radius (default: 0.9)
        batch_first: If True, then input and output tensors are provided as
            (batch, seq, feature) instead of (seq, batch, feature) (default: True)
    """
    def __init__(self, input_size, hidden_size, num_layers=1, 
                 sparsity=0.1, spectral_radius=0.9, batch_first=True):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.sparsity = sparsity
        self.spectral_radius = spectral_radius
        self.batch_first = batch_first
        
        # Create ESGP cells for each layer
        self.cells = nn.ModuleList()
        
        # First layer
        self.cells.append(ESGPCell(input_size, hidden_size, sparsity, spectral_radius))
        
        # Additional layers
        for _ in range(1, num_layers):
            self.cells.append(ESGPCell(hidden_size, hidden_size, sparsity, spectral_radius))
    
    def forward(self, x, h_0=None):
        """
        Forward pass for the ESGP layer.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_size) if batch_first=True,
                or (seq_len, batch_size, input_size) if batch_first=False
            h_0: Initial hidden state for each element in the batch. 
                Defaults to zeros if not provided.
                
        Returns:
            output: Tensor containing the output features (h_t) from the last layer 
                for each timestep
            h_n: Tensor containing the hidden state for t = seq_len
        """
        if self.batch_first:
            # (batch, seq, features) -> (seq, batch, features)
            x = x.transpose(0, 1)
        
        seq_len, batch_size, _ = x.size()
        
        # Initialize hidden state if not provided
        if h_0 is None:
            h_0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, 
                             device=x.device, dtype=x.dtype)
        
        # Process each timestep
        h_n = []  # Final hidden states for each layer
        outputs = []
        h_prev = [h_0[layer] for layer in range(self.num_layers)]
        
        for t in range(seq_len):
            x_t = x[t]
            
            # Process through each layer
            for layer_idx, cell in enumerate(self.cells):
                h_prev[layer_idx] = cell(x_t, h_prev[layer_idx])
                x_t = h_prev[layer_idx]  # Output of current layer is input to next
            
            outputs.append(x_t)  # Store output of last layer
        
        # Stack outputs and convert back to batch_first if needed
        output = torch.stack(outputs, dim=0)
        if self.batch_first:
            output = output.transpose(0, 1)  # (seq, batch, features) -> (batch, seq, features)
        
        # Stack final hidden states
        h_n = torch.stack(h_prev, dim=0)
        
        return output, h_n
    
    def extra_repr(self):
        return f"input_size={self.input_size}, hidden_size={self.hidden_size}, " \
               f"num_layers={self.num_layers}, sparsity={self.sparsity}, " \
               f"spectral_radius={self.spectral_radius}, batch_first={self.batch_first}"