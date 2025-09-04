from typing import Dict, Any, Optional, List, Union
from .data.loader import PanelDataLoader
from .data.preprocessing import PanelPreprocessor
from .utils.sequence import SequenceGenerator
from .training.trainer import PanelTrainer
from .evaluation.metrics import PanelEvaluator

class PanelForecaster:
    """High-level interface for panel data forecasting"""
    
    def __init__(self):
        self.loader = PanelDataLoader()
        self.preprocessor = PanelPreprocessor()
        self.sequence_generator = SequenceGenerator()
        self.model = None
        self.trainer = None
        self.is_fitted = False
        
    def load_data(self, file_path: str, **kwargs) -> 'PanelForecaster':
        """Load data from file"""
        self.data = self.loader.load_csv(file_path, **kwargs)
        self.data_info = self.loader.validate_panel_structure(
            self.data, kwargs.get('entity_col', 'Entity'), 
            kwargs.get('time_col', 'Date')
        )
        return self
    
    def prepare_data(self, entity_col: str = 'Entity', 
                    time_col: str = 'Date', target_col: str = 'Value',
                    feature_cols: Optional[List[str]] = None,
                    train_ratio: float = 0.7, val_ratio: float = 0.15,
                    seq_length: int = 10, batch_size: int = 32) -> 'PanelForecaster':
        """Prepare data for training"""
        
        # Preprocess
        processed_data = self.preprocessor.fit_transform(
            self.data, entity_col, time_col, target_col, feature_cols
        )
        
        # Split
        train_data, val_data, test_data = self.preprocessor.split_panel_data(
            processed_data, entity_col, train_ratio, val_ratio, time_col
        )
        
        # Create sequences
        X_train, y_train, e_train = self.sequence_generator.create_sequences(
            train_data, entity_col, target_col, feature_cols, seq_length
        )
        X_val, y_val, e_val = self.sequence_generator.create_sequences(
            val_data, entity_col, target_col, feature_cols, seq_length
        )
        X_test, y_test, e_test = self.sequence_generator.create_sequences(
            test_data, entity_col, target_col, feature_cols, seq_length
        )
        
        # Create data loaders
        self.train_loader = self.sequence_generator.create_data_loaders(
            X_train, y_train, e_train, batch_size, shuffle=True
        )
        self.val_loader = self.sequence_generator.create_data_loaders(
            X_val, y_val, e_val, batch_size, shuffle=False
        )
        self.test_loader = self.sequence_generator.create_data_loaders(
            X_test, y_test, e_test, batch_size, shuffle=False
        )
        
        return self
    
    def fit(self, model, epochs: int = 100, **trainer_kwargs) -> 'PanelForecaster':
        """Fit the model"""
        self.model = model
        self.trainer = PanelTrainer(model)
        
        self.training_results = self.trainer.fit(
            self.train_loader, self.val_loader, epochs, **trainer_kwargs
        )
        
        self.is_fitted = True
        return self
    
    def evaluate(self) -> Dict[str, Any]:
        """Evaluate model performance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")
        
        evaluator = PanelEvaluator(self.model, self.preprocessor)
        return evaluator.evaluate_all_splits(
            self.train_loader, self.val_loader, self.test_loader
        )