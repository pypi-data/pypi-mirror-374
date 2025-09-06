import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional, Dict, Any
from torch.utils.data import DataLoader

class PanelTrainer:
    """Advanced trainer for panel forecasting models"""
    
    def __init__(self, model: nn.Module, 
                 optimizer: Optional[torch.optim.Optimizer] = None,
                 criterion: Optional[nn.Module] = None,
                 device: str = 'auto'):
        
        self.model = model
        self.device = torch.device('cuda' if torch.cuda.is_available() and device == 'auto' else 'cpu')
        self.model.to(self.device)
        
        # Default optimizer and loss
        self.optimizer = optimizer or optim.Adam(model.parameters(), lr=0.001)
        self.criterion = criterion or nn.MSELoss()
        
        # Training history
        self.history = {'train_loss': [], 'val_loss': []}
        
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, (X, y, e) in enumerate(train_loader):
            X, y, e = X.to(self.device), y.to(self.device), e.to(self.device)
            
            self.optimizer.zero_grad()
            predictions = self.model(X, e)
            loss = self.criterion(predictions, y)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate_epoch(self, val_loader: DataLoader) -> float:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for X, y, e in val_loader:
                X, y, e = X.to(self.device), y.to(self.device), e.to(self.device)
                predictions = self.model(X, e)
                loss = self.criterion(predictions, y)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def fit(self, train_loader: DataLoader, 
            val_loader: Optional[DataLoader] = None,
            epochs: int = 100, patience: int = 10,
            verbose: bool = True) -> Dict[str, Any]:
        """Train the model with early stopping"""
        
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        for epoch in range(epochs):
            # Training
            train_loss = self.train_epoch(train_loader)
            self.history['train_loss'].append(train_loss)
            
            # Validation
            if val_loader:
                val_loss = self.validate_epoch(val_loader)
                self.history['val_loss'].append(val_loss)
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    best_model_state = self.model.state_dict().copy()
                else:
                    patience_counter += 1
                
                if verbose:
                    print(f'Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
                
                if patience_counter >= patience:
                    if verbose:
                        print(f'Early stopping at epoch {epoch+1}')
                    break
            else:
                if verbose:
                    print(f'Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}')
        
        # Load best model if validation was used
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
        
        return {
            'final_train_loss': self.history['train_loss'][-1],
            'final_val_loss': self.history['val_loss'][-1] if val_loader else None,
            'best_val_loss': best_val_loss if val_loader else None,
            'epochs_trained': len(self.history['train_loss'])
        }
