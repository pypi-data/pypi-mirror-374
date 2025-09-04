import torch
import torch.nn as nn
from .base import BasePanelModel

class GRU(BasePanelModel):
    """GRU model with entity embeddings for panel data forecasting"""
    
    def __init__(self, 
                 input_size: int,
                 hidden_size: int,
                 output_size: int = 1,
                 num_entities: int = 1,
                 embedding_dim: int = 10,
                 num_layers: int = 1,
                 dropout: float = 0.1,
                 batch_first: bool = True):
        """
        Initialize GRU model
        
        Args:
            input_size: Number of input features
            hidden_size: Hidden layer size
            output_size: Number of output features
            num_entities: Number of unique entities
            embedding_dim: Entity embedding dimension
            num_layers: Number of GRU layers
            dropout: Dropout probability
            batch_first: If True, input shape is (batch, seq, feature)
        """
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        
        # Entity embeddings
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
        
        # Output layers with residual connection
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_size)
        
        # Multi-layer output head
        self.output_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(hidden_size // 2, output_size)
        )
        
        # Initialize weights
        self._init_weights()
        
        # Store model info
        self.model_info = {
            'model_type': 'GRU',
            'input_size': input_size,
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'embedding_dim': embedding_dim,
            'dropout': dropout,
            'total_parameters': self.count_parameters()
        }
    
    def _init_weights(self):
        """Initialize model weights"""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
            elif 'weight' in name and len(param.shape) >= 2:
                nn.init.xavier_uniform_(param.data)
    
    def forward(self, input_seq: torch.Tensor, entity_seq: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            input_seq: Input sequences [batch_size, seq_len, input_size]
            entity_seq: Entity IDs [batch_size, seq_len]
            
        Returns:
            Predictions [batch_size, output_size]
        """
        batch_size, seq_len, _ = input_seq.shape
        
        # Get entity embeddings
        entity_emb = self.entity_embedding(entity_seq)
        entity_emb = self.embedding_dropout(entity_emb)
        
        # Combine input with entity embeddings
        combined_input = torch.cat([input_seq, entity_emb], dim=-1)
        
        # GRU forward pass
        gru_out, hidden = self.gru(combined_input)
        
        # Use last timestep output with layer normalization
        last_output = gru_out[:, -1, :]
        last_output = self.layer_norm(last_output)
        
        # Apply dropout
        output = self.dropout(last_output)
        
        # Final prediction through output head
        predictions = self.output_head(output)
        
        return predictions
    
    def init_hidden(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Initialize hidden state"""
        return torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)