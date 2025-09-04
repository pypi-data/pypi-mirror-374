import torch
import torch.nn as nn
from .base import BasePanelModel


class GRU(BasePanelModel):
    """
    GRU model with entity embeddings for panel data forecasting.
    """
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int = 1,
        num_entities: int = 1,
        embedding_dim: int = 10,
        num_layers: int = 1,
        dropout: float = 0.1,
        batch_first: bool = True
    ):
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        
        # Entity embedding
        self.entity_embedding = nn.Embedding(num_entities, embedding_dim)
        self.embedding_dropout = nn.Dropout(dropout * 0.5)
        
        # GRU layer
        gru_input_size = input_size + embedding_dim
        self.gru = nn.GRU(
            input_size=gru_input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=batch_first
        )
        
        # Output head
        self.dropout = nn.Dropout(dropout)
        self.batch_norm = nn.BatchNorm1d(hidden_size)
        self.linear = nn.Linear(hidden_size, output_size)
        
        # Weight initialization
        self._init_weights()
        
        # Metadata
        self.model_info.update({
            'model_type': 'GRU',
            'input_size': input_size,
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'embedding_dim': embedding_dim,
            'dropout': dropout,
            'total_parameters': self.count_parameters()
        })
    
    def _init_weights(self):
        """Initialize GRU weights"""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                # Slight bias to reset gate
                n = param.size(0)
                param.data[n//4:n//2].fill_(1.0)  # Reset and update gates
    
    def forward(self, input_seq: torch.Tensor, entity_seq: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = input_seq.shape
        
        # Embed entities
        emb = self.entity_embedding(entity_seq.long())
        emb = self.embedding_dropout(emb)
        
        # Combine
        x = torch.cat([input_seq, emb], dim=-1)
        
        # GRU forward
        gru_out, hidden = self.gru(x)  # gru_out: (B, T, H)
        
        # Last timestep
        last_out = gru_out[:, -1, :]  # (B, H)
        
        # Output head
        out = self.dropout(last_out)
        out = self.batch_norm(out)
        pred = self.linear(out)
        
        return pred

    def init_hidden(self, batch_size: int, device: torch.device):
        hidden = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)
        return hidden