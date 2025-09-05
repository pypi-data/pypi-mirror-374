import torch
from esgp import ESGP, ESGPCell

def test_esgp_cell():
    """Test the ESGP cell forward pass"""
    batch_size, input_size, hidden_size = 5, 10, 20
    cell = ESGPCell(input_size, hidden_size)
    
    x = torch.randn(batch_size, input_size)
    h_prev = torch.zeros(batch_size, hidden_size)
    
    h_next = cell(x, h_prev)
    assert h_next.shape == (batch_size, hidden_size)
    print("ESGP Cell test passed!")

if __name__ == "__main__":
    test_esgp_cell()