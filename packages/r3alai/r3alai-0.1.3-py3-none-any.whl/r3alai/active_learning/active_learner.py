"""Implementation of Active Learning for RSNN models."""

import numpy as np
import torch
from typing import List, Tuple, Union, Callable, Optional
from sklearn.base import BaseEstimator
from r3alai.models.rsnn import RSNNClassifier

class ActiveLearner:
    def __init__(
        self,
        model: Union[RSNNClassifier, BaseEstimator],
        uncertainty_measure: str = "entropy",
        batch_size: int = 1
    ):
        """
        Active learning wrapper for RSNN models.
        
        Args:
            model: The RSNN model to use for active learning
            uncertainty_measure: Type of uncertainty measure to use ("entropy" or "credal")
            batch_size: Number of samples to select in each iteration
        """
        self.model = model
        self.uncertainty_measure = uncertainty_measure
        self.batch_size = batch_size
        
    def _compute_uncertainty(
        self,
        X_pool: Union[np.ndarray, torch.Tensor]
    ) -> np.ndarray:
        """Compute uncertainty scores for unlabeled data."""
        if isinstance(self.model, RSNNClassifier):
            _, entropy, credal_width = self.model.predict(X_pool, return_uncertainty=True)
            if self.uncertainty_measure == "entropy":
                return entropy.cpu().numpy()
            else:
                return credal_width.cpu().numpy()
        else:
            raise ValueError("Model must be an RSNNClassifier")
    
    def query(
        self,
        X_pool: Union[np.ndarray, torch.Tensor],
        n_instances: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Query the most informative instances from the pool.
        
        Args:
            X_pool: Pool of unlabeled instances
            n_instances: Number of instances to query (defaults to batch_size)
            
        Returns:
            Tuple of (selected instances, their indices)
        """
        if n_instances is None:
            n_instances = self.batch_size
            
        uncertainty_scores = self._compute_uncertainty(X_pool)
        query_idx = np.argsort(uncertainty_scores)[-n_instances:]
        
        if isinstance(X_pool, torch.Tensor):
            X_pool = X_pool.cpu().numpy()
            
        return X_pool[query_idx], query_idx
    
    def disagreement_query(
        self,
        X_pool: Union[np.ndarray, torch.Tensor],
        n_instances: Optional[int] = None,
        n_models: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Query instances based on model disagreement.
        
        Args:
            X_pool: Pool of unlabeled instances
            n_instances: Number of instances to query
            n_models: Number of models to use for disagreement
            
        Returns:
            Tuple of (selected instances, their indices)
        """
        if n_instances is None:
            n_instances = self.batch_size
            
        # Create ensemble of models
        predictions = []
        for _ in range(n_models):
            # Create a copy of the model with different initialization
            model_copy = type(self.model)(
                base_model=self.model.base_model,
                n_classes=self.model.n_classes,
                alpha=self.model.alpha,
                beta=self.model.beta
            )
            model_copy.load_state_dict(self.model.state_dict())
            
            # Add some noise to the weights
            for param in model_copy.parameters():
                param.data += torch.randn_like(param.data) * 0.01
                
            # Get predictions
            with torch.no_grad():
                preds = model_copy.predict(X_pool)
                if isinstance(preds, tuple):
                    preds = preds[0]  # Get only predictions if uncertainty is returned
                predictions.append(preds.cpu().numpy())
            
        # Compute disagreement as variance of predictions
        predictions = np.stack(predictions)
        disagreement = np.var(predictions, axis=0).mean(axis=1)
        
        # Select instances with highest disagreement
        query_idx = np.argsort(disagreement)[-n_instances:]
        
        if isinstance(X_pool, torch.Tensor):
            X_pool = X_pool.cpu().numpy()
            
        return X_pool[query_idx], query_idx