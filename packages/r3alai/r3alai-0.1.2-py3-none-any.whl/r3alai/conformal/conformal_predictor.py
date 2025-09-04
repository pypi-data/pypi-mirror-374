"""Implementation of Conformal Prediction for RSNN models."""

import numpy as np
import torch
from typing import Tuple, Union, List
from r3alai.models.rsnn import RSNNClassifier

class ConformalPredictor:
    def __init__(
        self,
        model: RSNNClassifier,
        confidence_level: float = 0.95
    ):
        """
        Conformal prediction wrapper for RSNN models.
        
        Args:
            model: The RSNN model to use for conformal prediction
            confidence_level: Desired confidence level (between 0 and 1)
        """
        self.model = model
        self.confidence_level = confidence_level
        self.calibration_scores = None
        
    def calibrate(
        self,
        X_cal: Union[np.ndarray, torch.Tensor],
        y_cal: Union[np.ndarray, torch.Tensor]
    ):
        """
        Calibrate the conformal predictor using calibration data.
        
        Args:
            X_cal: Calibration features
            y_cal: Calibration labels
        """
        if isinstance(X_cal, np.ndarray):
            X_cal = torch.FloatTensor(X_cal)
        if isinstance(y_cal, np.ndarray):
            y_cal = torch.FloatTensor(y_cal)
            
        # Get predictions and uncertainty scores
        preds, entropy, _ = self.model.predict(X_cal, return_uncertainty=True)
        
        # Compute non-conformity scores
        # For classification, we use the negative predicted probability of the true class
        n_samples = len(y_cal)
        scores = []
        for i in range(n_samples):
            true_class = y_cal[i].argmax().item() if len(y_cal[i].shape) > 0 else int(y_cal[i].item())
            score = -preds[i, true_class].item()
            scores.append(score)
            
        self.calibration_scores = np.array(scores)
        
    def predict(
        self,
        X: Union[np.ndarray, torch.Tensor]
    ) -> Tuple[np.ndarray, List[List[int]]]:
        """
        Make predictions with conformal confidence sets.
        
        Args:
            X: Input features
            
        Returns:
            Tuple of (predictions, confidence sets)
        """
        if self.calibration_scores is None:
            raise ValueError("Must calibrate the predictor first")
            
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X)
            
        # Get predictions and uncertainty scores
        preds, entropy, _ = self.model.predict(X, return_uncertainty=True)
        preds = preds.cpu().numpy()
        
        # Compute quantile of calibration scores
        quantile = np.quantile(
            self.calibration_scores,
            1 - self.confidence_level
        )
        
        # Create confidence sets
        confidence_sets = []
        for i in range(len(X)):
            # Include all classes with predicted probability above threshold
            threshold = -quantile
            included_classes = np.where(preds[i] > threshold)[0].tolist()
            confidence_sets.append(included_classes)
            
        return preds, confidence_sets
    
    def get_coverage(
        self,
        X_test: Union[np.ndarray, torch.Tensor],
        y_test: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Compute the empirical coverage of the confidence sets.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Empirical coverage rate
        """
        if isinstance(y_test, np.ndarray):
            y_test = torch.FloatTensor(y_test)
            
        preds, confidence_sets = self.predict(X_test)
        
        # Compute coverage
        n_correct = 0
        for i in range(len(y_test)):
            true_class = y_test[i].argmax().item() if len(y_test[i].shape) > 0 else int(y_test[i].item())
            if true_class in confidence_sets[i]:
                n_correct += 1
                
        return n_correct / len(y_test)