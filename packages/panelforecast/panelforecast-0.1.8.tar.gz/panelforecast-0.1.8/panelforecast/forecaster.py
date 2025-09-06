from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np

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
        
        self.data = None
        self.data_info = None
        
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        self.model = None
        self.trainer = None
        self.is_fitted = False
        
    def load_data(self, source: Union[str, pd.DataFrame], **kwargs) -> 'PanelForecaster':
        """
        Load data from file path or pandas DataFrame.
        
        Args:
            source: Path to CSV file OR a pandas DataFrame
            **kwargs: Passed to PanelDataLoader.load_csv (e.g., entity_col, time_col)
            
        Returns:
            Self (for method chaining)
        """
        # Extract and remove from kwargs to avoid duplication
        entity_col = kwargs.pop('entity_col', 'Entity')
        time_col = kwargs.pop('time_col', 'Date')
        target_col = kwargs.pop('target_col', 'Value')
        
        self.data = self.loader.load_csv(
            source,
            entity_col=entity_col,
            time_col=time_col,
            target_col=target_col,
            **kwargs
        )
        
        # Validate structure
        self.data_info = self.loader.validate_panel_structure(self.data, entity_col, time_col)
        
        print(f"✅ Loaded panel data: {self.data_info['n_entities']} entities, "
              f"{self.data_info['n_time_periods']} time points")
        return self
    
    def prepare_data(self,
                     entity_col: str = 'Entity',
                     time_col: str = 'Date',
                     target_col: str = 'Value',
                     feature_cols: Optional[List[str]] = None,
                     train_ratio: float = 0.7,
                     val_ratio: float = 0.15,
                     seq_length: int = 10,
                     batch_size: int = 32) -> 'PanelForecaster':
        """
        Prepare data: preprocess, split, create sequences and PyTorch DataLoaders.
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Preprocess: fit-transform on training part after split
        processed_data = self.preprocessor.fit_transform(
            self.data, entity_col, time_col, target_col, feature_cols
        )
        
        # Split panel data (temporal split within each entity)
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
        
        # Create PyTorch DataLoaders
        self.train_loader = self.sequence_generator.create_data_loaders(
            X_train, y_train, e_train, batch_size=batch_size, shuffle=True
        )
        self.val_loader = self.sequence_generator.create_data_loaders(
            X_val, y_val, e_val, batch_size=batch_size, shuffle=False
        )
        self.test_loader = self.sequence_generator.create_data_loaders(
            X_test, y_test, e_test, batch_size=batch_size, shuffle=False
        )
        
        print(f"✅ Data prepared: Train={len(X_train)} seqs, Val={len(X_val)}, Test={len(X_test)}")
        return self
    
    def fit(self, model, epochs: int = 100, **trainer_kwargs) -> 'PanelForecaster':
        """
        Fit the forecasting model.
        """
        if self.train_loader is None:
            raise ValueError("Data not prepared. Call prepare_data() first.")
        
        self.model = model
        self.trainer = PanelTrainer(model)
        
        self.training_results = self.trainer.fit(
            self.train_loader,
            self.val_loader,
            epochs=epochs,
            **trainer_kwargs
        )
        
        self.is_fitted = True
        print(f"✅ Training completed. Best val loss: {self.training_results['best_val_loss']:.4f}")
        return self
    
    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate model on train, val, and test sets using real-world scale metrics.
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")
        
        evaluator = PanelEvaluator()  # No args needed
        results = {}
        
        for name, loader in [("train", self.train_loader), 
                           ("val", self.val_loader), 
                           ("test", self.test_loader)]:
            if loader is None:
                continue
            
            # Extract true values and entity IDs
            all_true, all_pred, all_entity_ids = [], [], []
            
            self.model.eval()
            with torch.no_grad():
                for X, y, e in loader:
                    pred = self.model(X, e).cpu().numpy().flatten()
                    all_pred.extend(pred)
                    all_true.extend(y.cpu().numpy().flatten())
                    all_entity_ids.extend(e[:, 0].cpu().numpy())  # one ID per sequence
            
            # Inverse transform to original scale
            true_original = self.preprocessor.inverse_transform_target(
                np.array(all_true), np.array(all_entity_ids)
            )
            pred_original = self.preprocessor.inverse_transform_target(
                np.array(all_pred), np.array(all_entity_ids)
            )
            
            # Calculate metrics
            mae, mse, rmse, mape, r2 = evaluator.calculate_metrics(true_original, pred_original)
            results[f"{name}_mae"] = mae
            results[f"{name}_rmse"] = rmse
            results[f"{name}_mape"] = mape
            results[f"{name}_r2"] = r2
        
        print("✅ Evaluation complete.")
        return results