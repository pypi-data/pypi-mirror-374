import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score
from typing import Tuple

class PanelEvaluator:
    """Panel-specific evaluation metrics"""
    
    @staticmethod
    def calculate_metrics(actuals: np.ndarray, predictions: np.ndarray) -> Tuple[float, float, float, float, float]:
        """Calculate standard regression metrics"""
        mae = mean_absolute_error(actuals, predictions)
        mse = mean_squared_error(actuals, predictions)
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(actuals, predictions) * 100
        r2 = r2_score(actuals, predictions)
        return mae, mse, rmse, mape, r2
    
    @staticmethod
    def entity_wise_metrics(actuals: np.ndarray, predictions: np.ndarray, 
                          entity_ids: np.ndarray) -> dict:
        """Calculate metrics for each entity separately"""
        metrics_by_entity = {}
        
        for entity in np.unique(entity_ids):
            mask = entity_ids == entity
            entity_actuals = actuals[mask]
            entity_predictions = predictions[mask]
            
            metrics_by_entity[entity] = PanelEvaluator.calculate_metrics(
                entity_actuals, entity_predictions
            )
        
        return metrics_by_entity