"""Integration utilities for connecting RSNN with other models."""

import torch
import numpy as np
from typing import Optional, Dict, Any, Union, List, Tuple
import torch.nn as nn
from r3alai.models.rsnn import RSNNClassifier
from r3alai.conformal.conformal_predictor import ConformalPredictor

class YOLOFeatureExtractor(nn.Module):
    """
    Custom feature extractor that uses YOLOv8's backbone.
    """
    
    def __init__(
        self,
        yolo_nn_module: nn.Module,
        feature_dim: int,
        output_dim: int = 512
    ):
        """
        Initialize the feature extractor.
        
        Args:
            yolo_nn_module: The YOLOv8's core nn.Module (e.g., YOLO('path.pt').model)
            feature_dim: Dimension of features extracted by YOLO
            output_dim: Dimension of output features
        """
        super().__init__()
        
        # Ensure all submodules of the yolo_nn_module are in evaluation mode
        # using the original torch.nn.Module.train method to avoid side effects.
        for sub_module in yolo_nn_module.modules():
            torch.nn.Module.train(sub_module, False)
            sub_module.requires_grad_(False) # Also freeze weights as we are only extracting features

        # self.yolo_model = yolo_model # Removed, as we only need the nn.Module part
        
        # Get YOLO model's backbone from the nn.Module part
        # yolo_nn_module is typically DetectionModel, its layers are in yolo_nn_module.model
        self.backbone = yolo_nn_module.model[0:9]
        
        # Add adaptive pooling to handle variable input sizes
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Add fully connected layer to match the expected input of RSNNClassifier
        self.fc = nn.Linear(feature_dim, output_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the feature extractor."""
        # Extract features using YOLO backbone
        features = self.backbone(x)
        
        # Pool features
        pooled = self.adaptive_pool(features)
        
        # Flatten
        flattened = pooled.view(pooled.size(0), -1)
        
        # Pass through FC layer
        output = self.fc(flattened)
        
        return output


class RSNNYOLOWrapper:
    """
    A wrapper class to integrate RSNNClassifier with YOLOv8 models for
    improved performance and uncertainty estimation.
    """
    
    def __init__(
        self,
        yolo_model_path: str,
        n_classes: int,
        confidence_level: float = 0.95,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize the RSNN-YOLO integration.
        
        Args:
            yolo_model_path: Path to the YOLOv8 model
            n_classes: Number of classes in the dataset
            confidence_level: Confidence level for conformal prediction
            device: Device to run the model on
        """
        self.device = device
        
        # Dynamically import YOLO to avoid requiring it for the entire package
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError("To use RSNNYOLOWrapper, please install ultralytics: pip install ultralytics")
        
        # Initialize YOLO model
        self.yolo_model = YOLO(yolo_model_path)
        yolo_nn_module = self.yolo_model.model # Get the nn.Module part
        
        # Get feature extractor dimension
        # YOLOv8 backbone (model[0:9] for yolov8n) outputs features of shape (batch_size, 256, H, W)
        # The previous value 1024 might be for a different layer or larger model.
        feature_dim = 256 # Changed from 1024
        
        # Initialize RSNN with a custom feature extractor
        self.rsnn_model = RSNNClassifier(
            base_model="custom",  # We'll handle the base model manually
            n_classes=n_classes,
            device=device
        )
        
        # Replace the base model with a custom adapter
        self.rsnn_model.base_model = YOLOFeatureExtractor(yolo_nn_module, feature_dim)
        
        # Set up the belief layer for our custom model
        self.rsnn_model.set_belief_layer(512)  # Output dim of the feature extractor
        
        # Initialize conformal predictor
        self.conformal_predictor = ConformalPredictor(
            model=self.rsnn_model,
            confidence_level=confidence_level
        )
        
        # Move model to device
        self.rsnn_model.to(device)
    
    def extract_features(self, images: Union[torch.Tensor, np.ndarray]) -> torch.Tensor:
        """
        Extract features from images using YOLOv8's backbone.
        
        Args:
            images: Input images
            
        Returns:
            Features extracted by YOLOv8 backbone
        """
        if isinstance(images, np.ndarray):
            images = torch.from_numpy(images).float().to(self.device)
        
        return self.rsnn_model.base_model(images)
    
    def train(
        self,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None,
        epochs: int = 50,
        learning_rate: float = 0.001,
        freeze_backbone: bool = True
    ) -> Dict[str, List[float]]:
        """
        Train the RSNN model using YOLOv8 features.
        
        Args:
            train_loader: DataLoader for training data
            val_loader: DataLoader for validation data
            epochs: Number of training epochs
            learning_rate: Learning rate for optimizer
            freeze_backbone: Whether to freeze the YOLOv8 backbone
            
        Returns:
            Dictionary containing training history
        """
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.rsnn_model.base_model.backbone.parameters():
                param.requires_grad = False
        
        # Initialize optimizer
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, self.rsnn_model.parameters()),
            lr=learning_rate
        )
        
        # Initialize history
        history = {
            "train_loss": [],
            "val_loss": []
        }
        
        # Training loop
        for epoch in range(epochs):
            # Training
            self.rsnn_model.train()
            train_loss = 0.0
            for images, targets in train_loader:
                images = images.to(self.device)
                targets = targets.to(self.device).float()
                optimizer.zero_grad()
                belief_scores = self.rsnn_model(images)
                loss = self.rsnn_model._compute_loss(
                    belief_scores=belief_scores,
                    targets=targets,
                    alpha=self.rsnn_model.alpha,
                    beta=self.rsnn_model.beta
                )
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.rsnn_model.parameters(), max_norm=1.0)
                optimizer.step()
                train_loss += loss.item()
            avg_train = train_loss / max(1, len(train_loader))
            history["train_loss"].append(avg_train)

            # Validation
            if val_loader is not None:
                self.rsnn_model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for images, targets in val_loader:
                        images = images.to(self.device)
                        targets = targets.to(self.device).float()
                        belief_scores = self.rsnn_model(images)
                        loss = self.rsnn_model._compute_loss(
                            belief_scores=belief_scores,
                            targets=targets,
                            alpha=self.rsnn_model.alpha,
                            beta=self.rsnn_model.beta
                        )
                        val_loss += loss.item()
                avg_val = val_loss / max(1, len(val_loader))
                history["val_loss"].append(avg_val)
                print(f"Epoch {epoch + 1}/{epochs} - train_loss: {avg_train:.4f} - val_loss: {avg_val:.4f}")
            else:
                print(f"Epoch {epoch + 1}/{epochs} - train_loss: {avg_train:.4f}")

        return history

    def predict(self, images: Union[torch.Tensor, np.ndarray], return_uncertainty: bool = False):
        """
        Predict with the wrapped RSNN model using YOLO features.
        """
        if isinstance(images, np.ndarray):
            images = torch.from_numpy(images).float()
        images = images.to(self.device)
        return self.rsnn_model.predict(images, return_uncertainty=return_uncertainty)

    def calibrate_conformal(self, X_cal: Union[torch.Tensor, np.ndarray], y_cal: Union[torch.Tensor, np.ndarray]):
        """Calibrate the internal conformal predictor."""
        self.conformal_predictor.calibrate(X_cal, y_cal)

    def predict_with_conformal(self, images: Union[torch.Tensor, np.ndarray]):
        """Predict with conformal confidence sets."""
        return self.conformal_predictor.predict(images)