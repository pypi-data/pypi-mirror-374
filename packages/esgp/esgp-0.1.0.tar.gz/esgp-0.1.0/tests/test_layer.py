import torch
from esgp import ESGP, ESGPCell

def test_esgp_layer():
    """Test the ESGP layer forward pass"""
    batch_size, seq_len, input_size, hidden_size = 5, 8, 10, 20
    layer = ESGP(input_size, hidden_size, num_layers=2, batch_first=True)
    
    x = torch.randn(batch_size, seq_len, input_size)
    output, h_n = layer(x)
    
    assert output.shape == (batch_size, seq_len, hidden_size)
    assert h_n.shape == (2, batch_size, hidden_size)
    print("ESGP Layer test passed!")

if __name__ == "__main__":
    test_esgp_layer()