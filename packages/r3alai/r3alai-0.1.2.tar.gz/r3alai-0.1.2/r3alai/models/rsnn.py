"""Implementation of Random Set Neural Network (RSNN) Classifier."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Union, List
import numpy as np
from sklearn.mixture import GaussianMixture
from torch.utils.data import DataLoader, TensorDataset

class RSNNClassifier(nn.Module):
    def __init__(
        self,
        base_model: str = "resnet50",
        n_classes: int = 10,
        alpha: float = 0.1,
        beta: float = 0.1,
        n_components: int = 3,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Random Set Neural Network (RSNN) Classifier with uncertainty estimation.
        
        Args:
            base_model (str or nn.Module): Base model architecture to use or a custom nn.Module
            n_classes (int): Number of output classes
            alpha (float): Regularization parameter for mass regularization
            beta (float): Regularization parameter for subset regularization
            n_components (int): Number of components for GMM
            device (str): Device to run the model on
        """
        super().__init__()
        self.n_classes = n_classes
        self.alpha = alpha
        self.beta = beta
        self.n_components = n_components
        self.device = device
        
        # Initialize base model
        if isinstance(base_model, str):
            self.base_model = self._get_base_model(base_model)
            # Belief function layer for standard models
            if hasattr(self.base_model, 'fc'):
                self.belief_layer = nn.Linear(self.base_model.fc.out_features, n_classes)
        elif isinstance(base_model, nn.Module):
            # Use provided custom model
            self.base_model = base_model
            # We'll set up the belief layer externally for custom models
        else:
            raise ValueError("base_model must be either a string or nn.Module")
        
        # Initialize GMM for budgeting
        self.gmm = GaussianMixture(n_components=n_components)
        
    def _get_base_model(self, model_name: str) -> nn.Module:
        """Initialize the base model architecture."""
        if model_name in {"resnet50", "mobilenet_v2", "efficientnet_b0"}:
            try:
                import torchvision.models as tvm
            except Exception as exc:
                raise ImportError(
                    "torchvision and Pillow are required for built-in backbones. "
                    "Install with: pip install 'r3alai[vision]'\n"
                    f"Original error: {exc}"
                )
            if model_name == "resnet50":
                # Support both legacy pretrained=True and new weights API
                try:
                    model = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V1)  # type: ignore[attr-defined]
                except Exception:
                    model = tvm.resnet50(pretrained=True)
                num_ftrs = model.fc.in_features
                model.fc = nn.Linear(num_ftrs, 512)
                return model
            if model_name == "mobilenet_v2":
                try:
                    model = tvm.mobilenet_v2(weights=tvm.MobileNet_V2_Weights.IMAGENET1K_V1)  # type: ignore[attr-defined]
                except Exception:
                    model = tvm.mobilenet_v2(pretrained=True)
                num_ftrs = model.classifier[1].in_features
                model.classifier = nn.Linear(num_ftrs, 512)
                return model
            if model_name == "efficientnet_b0":
                try:
                    model = tvm.efficientnet_b0(weights=tvm.EfficientNet_B0_Weights.IMAGENET1K_V1)  # type: ignore[attr-defined]
                except Exception:
                    model = tvm.efficientnet_b0(pretrained=True)
                num_ftrs = model.classifier[1].in_features
                model.classifier = nn.Linear(num_ftrs, 512)
                return model
        elif model_name == "custom":
            # Placeholder for custom model, will be set externally
            return nn.Identity()
        else:
            raise ValueError(f"Unsupported base model: {model_name}")
    
    def set_belief_layer(self, in_features: int):
        """Set up the belief layer for a custom base model."""
        self.belief_layer = nn.Linear(in_features, self.n_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
        features = self.base_model(x)
        # Make sure belief_layer is defined
        if not hasattr(self, 'belief_layer'):
            raise RuntimeError("Belief layer not defined. For custom models, call set_belief_layer() first.")
        belief_scores = self.belief_layer(features)
        return belief_scores
    
    def _compute_mass_regularization(self, belief_scores: torch.Tensor) -> torch.Tensor:
        """Compute mass regularization term."""
        return torch.mean(torch.sum(belief_scores**2, dim=1))
    
    def _compute_subset_regularization(self, belief_scores: torch.Tensor) -> torch.Tensor:
        """Compute subset regularization term."""
        # Operate on probabilities to ensure numerical stability
        probs = torch.sigmoid(belief_scores)
        return torch.mean(torch.sum(probs * torch.log(probs + 1e-10), dim=1))
    
    def _compute_loss(
        self,
        belief_scores: torch.Tensor,
        targets: torch.Tensor,
        alpha: float,
        beta: float
    ) -> torch.Tensor:
        """Compute the RSNN loss function."""
        bce_loss = F.binary_cross_entropy_with_logits(belief_scores, targets)
        mass_reg = self._compute_mass_regularization(belief_scores)
        subset_reg = self._compute_subset_regularization(belief_scores)
        
        return bce_loss + alpha * mass_reg + beta * subset_reg
    
    def fit(
        self,
        X: Union[np.ndarray, torch.Tensor],
        y: Union[np.ndarray, torch.Tensor],
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        validation_split: float = 0.1,
        early_stopping_patience: int = 10
    ) -> dict:
        """
        Train the RSNN model with improved training loop.
        
        Args:
            X: Input features
            y: Target labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
            validation_split: Fraction of data to use for validation
            early_stopping_patience: Number of epochs to wait for improvement
            
        Returns:
            Dictionary containing training history
        """
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X)
        if isinstance(y, np.ndarray):
            y = torch.FloatTensor(y)
            
        X = X.to(self.device)
        y = y.to(self.device)
        
        # Split into training and validation sets
        if validation_split > 0:
            val_size = int(len(X) * validation_split)
            train_size = len(X) - val_size
            
            # Random split
            train_dataset, val_dataset = torch.utils.data.random_split(
                TensorDataset(X, y), [train_size, val_size]
            )
            
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        else:
            train_loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True)
            val_loader = None
        
        # Initialize optimizer with weight decay
        optimizer = torch.optim.AdamW(self.parameters(), lr=learning_rate, weight_decay=1e-4)
        
        # Learning rate scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Initialize early stopping
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        # Initialize history
        history = {
            'train_loss': [],
            'val_loss': []
        }
        
        self.train()
        for epoch in range(epochs):
            # Training phase
            epoch_loss = 0
            self.train()
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                
                belief_scores = self(batch_X)
                loss = self._compute_loss(belief_scores, batch_y, self.alpha, self.beta)
                
                loss.backward()
                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
                optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_train_loss = epoch_loss / len(train_loader)
            history['train_loss'].append(avg_train_loss)
            
            # Validation phase
            if val_loader is not None:
                val_loss = 0
                self.eval()
                with torch.no_grad():
                    for batch_X, batch_y in val_loader:
                        belief_scores = self(batch_X)
                        loss = self._compute_loss(belief_scores, batch_y, self.alpha, self.beta)
                        val_loss += loss.item()
                
                avg_val_loss = val_loss / len(val_loader)
                history['val_loss'].append(avg_val_loss)
                
                # Update learning rate
                scheduler.step(avg_val_loss)
                
                # Early stopping check
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                    # Save best model
                    best_model_state = {k: v.cpu().detach() for k, v in self.state_dict().items()}
                else:
                    patience_counter += 1
                
                print(f"Epoch {epoch + 1}/{epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
                
                # Check if early stopping criteria is met
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping triggered after {epoch + 1} epochs")
                    # Load best model
                    if best_model_state is not None:
                        self.load_state_dict({k: v.to(self.device) for k, v in best_model_state.items()})
                    break
            else:
                print(f"Epoch {epoch + 1}/{epochs}, Train Loss: {avg_train_loss:.4f}")
        
        # If early stopping didn't trigger, load the best model
        if val_loader is not None and best_model_state is not None and epoch == epochs - 1:
            self.load_state_dict({k: v.to(self.device) for k, v in best_model_state.items()})
            
        return history
    
    def predict(
        self,
        X: Union[np.ndarray, torch.Tensor],
        return_uncertainty: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Make predictions with optional uncertainty estimates.

        Args:
            X: Input features
            return_uncertainty: Whether to return uncertainty measures

        Returns:
            If return_uncertainty is False:
                Predictions
            If return_uncertainty is True:
                Tuple of (predictions, pignistic entropy, credal set width)
        """
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X)
        X = X.to(self.device)

        was_training = self.training  # remember if model was in training mode
        self.train(False)  # temporarily set to eval mode

        with torch.no_grad():
            belief_scores = self(X)
            predictions = torch.sigmoid(belief_scores)

            if not return_uncertainty:
                self.train(was_training)  # restore original mode
                return predictions

            # Compute pignistic entropy
            pignistic_probs = predictions / predictions.sum(dim=1, keepdim=True)
            pignistic_entropy = -torch.sum(pignistic_probs * torch.log(pignistic_probs + 1e-10), dim=1)

            # Compute credal set width
            credal_width = torch.sum(predictions, dim=1)

        self.train(was_training)  # restore original mode
        return predictions, pignistic_entropy, credal_width

    def save(self, path: str):
        """Save the model to a file."""
        torch.save({
            'model_state_dict': self.state_dict(),
            'n_classes': self.n_classes,
            'alpha': self.alpha,
            'beta': self.beta,
            'n_components': self.n_components
        }, path)
        
    @classmethod
    def load(cls, path: str, device: str = None):
        """Load the model from a file."""
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
        checkpoint = torch.load(path, map_location=device)
        
        model = cls(
            base_model="custom",  # We'll load the actual model from the state dict
            n_classes=checkpoint['n_classes'],
            alpha=checkpoint['alpha'],
            beta=checkpoint['beta'],
            n_components=checkpoint['n_components'],
            device=device
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        return model