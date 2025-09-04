import torch
import torch.nn as nn
from .base import BasePanelModel

class BiLSTM(BasePanelModel):
    """Bidirectional LSTM with entity embeddings for panel data forecasting"""
    
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
        Initialize BiLSTM model
        
        Args:
            input_size: Number of input features
            hidden_size: Hidden layer size
            output_size: Number of output features (default: 1)
            num_entities: Number of unique entities
            embedding_dim: Entity embedding dimension
            num_layers: Number of LSTM layers
            dropout: Dropout probability
            batch_first: If True, input shape is (batch, seq, feature)
        """
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = True
        self.batch_first = batch_first

        # Entity embeddings
        self.entity_embedding = nn.Embedding(num_entities, embedding_dim)
        self.embedding_dropout = nn.Dropout(dropout * 0.5)

        # LSTM input includes entity embeddings
        lstm_input_size = input_size + embedding_dim

        self.lstm = nn.LSTM(
            input_size=lstm_input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
            batch_first=batch_first
        )

        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.batch_norm = nn.BatchNorm1d(hidden_size * 2)
        self.linear = nn.Linear(hidden_size * 2, output_size)

        # Initialize weights
        self._init_weights()

        # Store model info
        self.model_info = {
            'model_type': 'BiLSTM',
            'input_size': input_size,
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'embedding_dim': embedding_dim,
            'bidirectional': True,
            'dropout': dropout,
            'total_parameters': self.count_parameters()
        }

    def _init_weights(self):
        """Initialize model weights using Xavier/Orthogonal initialization"""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                # Set forget gate bias to 1
                n = param.size(0)
                param.data[(n//4):(n//2)].fill_(1)

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

        # Entity embeddings
        entity_emb = self.entity_embedding(entity_seq)  # [batch, seq_len, emb_dim]
        entity_emb = self.embedding_dropout(entity_emb)

        # Combine input and entity embeddings
        combined_input = torch.cat([input_seq, entity_emb], dim=-1)  # [batch, seq_len, input + emb]

        # BiLSTM pass
        lstm_out, _ = self.lstm(combined_input)  # [batch, seq_len, hidden*2]

        # Use last timestep
        last_output = lstm_out[:, -1, :]  # [batch_size, hidden_size*2]

        # Output projection
        output = self.dropout(last_output)
        output = self.batch_norm(output)
        predictions = self.linear(output)

        return predictions

    def init_hidden(self, batch_size: int, device: torch.device) -> tuple:
        """Initialize hidden and cell states for bidirectional LSTM"""
        num_directions = 2
        hidden = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size, device=device)
        cell = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size, device=device)
        return hidden, cell
