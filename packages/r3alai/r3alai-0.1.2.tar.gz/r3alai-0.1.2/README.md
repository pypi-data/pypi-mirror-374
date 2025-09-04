# R3ALAI

A Python library for Random Set Neural Networks with uncertainty estimation, active learning capabilities, and conformal prediction methods.

## Installation

```bash
pip install r3alai
```

Alternatively, from source:

```bash
pip install build
python -m build
pip install dist/*.whl
```

For examples that use torchvision backbones (e.g., quickstart), install the optional vision extras:

```bash
pip install 'r3alai[vision]'
```

## Module Overview

R3ALAI consists of several key modules that can be used together to build robust models with uncertainty quantification:

### Models (`r3alai.models`)
- **RSNNClassifier**: The core Random Set Neural Network implementation that extends traditional neural networks with belief function theory to provide uncertainty estimation.
- Features include:
  - Support for various pre-trained backbone architectures (ResNet50, MobileNetV2, EfficientNet)
  - Custom model integration
  - Built-in mass and subset regularization
  - Uncertainty estimation via belief functions

### Conformal Prediction (`r3alai.conformal`)
- **ConformalPredictor**: Provides distribution-free uncertainty quantification with statistical guarantees.
- Features include:
  - Calibration on validation data
  - Confidence set generation with guaranteed coverage
  - Empirical coverage evaluation

### Active Learning (`r3alai.active_learning`)
- **ActiveLearner**: Implements uncertainty-based sampling strategies for active learning.
- Features include:
  - Entropy-based sample selection
  - Credal width-based selection
  - Model disagreement query mechanisms

### Utils (`r3alai.utils`)
- **Integration**: Tools to integrate R3ALAI with other models and workflows.
- **RSNNYOLOWrapper**: Integration with YOLOv8 for object detection with uncertainty.
- **YOLOFeatureExtractor**: Feature extraction from YOLO models for use with RSNN.

## Architecture Usage Examples

### Basic Classification with Uncertainty

```python
import torch
from r3alai.models import RSNNClassifier

# Initialize the classifier
model = RSNNClassifier(
    base_model="resnet50",  # Options: "resnet50", "mobilenet_v2", "efficientnet_b0", or custom nn.Module
    n_classes=10,
    alpha=0.1,  # Mass regularization parameter
    beta=0.1    # Subset regularization parameter
)

# Train the model
X_train = torch.randn(100, 3, 224, 224)  # Example input
y_train = torch.eye(10)[torch.randint(0, 10, (100,))]  # One-hot encoded labels
history = model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=16,
    validation_split=0.2,
    early_stopping_patience=5  # Early stopping to prevent overfitting
)

# Make predictions with uncertainty
X_test = torch.randn(10, 3, 224, 224)
predictions, entropy, credal_width = model.predict(X_test, return_uncertainty=True)
# - predictions: class probabilities
# - entropy: Shannon entropy of the predictions (higher = more uncertain)
# - credal_width: width of the credal set (higher = more uncertain)
```

### Using Conformal Prediction for Confidence Sets

```python
from r3alai.models import RSNNClassifier
from r3alai.conformal import ConformalPredictor
import torch

# Initialize and train your RSNN model
model = RSNNClassifier(base_model="resnet50", n_classes=10)
# ... train the model ...

# Create a conformal predictor
conformal = ConformalPredictor(
    model=model,
    confidence_level=0.95  # 95% confidence level
)

# Calibrate the predictor on calibration data
X_cal = torch.randn(50, 3, 224, 224)  
y_cal = torch.eye(10)[torch.randint(0, 10, (50,))]
conformal.calibrate(X_cal, y_cal)

# Get predictions with conformal confidence sets
X_test = torch.randn(10, 3, 224, 224)
predictions, confidence_sets = conformal.predict(X_test)
# confidence_sets contains classes that are in the 95% confidence set for each sample

# Evaluate empirical coverage
coverage = conformal.get_coverage(X_test, y_test)
print(f"Empirical coverage: {coverage:.2f}")
```

### Active Learning for Efficient Data Collection

```python
from r3alai.models import RSNNClassifier
from r3alai.active_learning import ActiveLearner
import torch
import numpy as np

# Initialize and train your RSNN model
model = RSNNClassifier(base_model="resnet50", n_classes=10)
# ... train the model ...

# Create an active learner
active_learner = ActiveLearner(
    model=model,
    uncertainty_measure="entropy",  # Options: "entropy" or "credal"
    batch_size=5  # Number of samples to select in each iteration
)

# Create a pool of unlabeled data
X_pool = torch.randn(1000, 3, 224, 224)

# Select the most informative samples
selected_samples, selected_indices = active_learner.query(X_pool)

# Alternatively, use disagreement-based selection
selected_samples, selected_indices = active_learner.disagreement_query(
    X_pool, 
    n_instances=10, 
    n_models=5  # Number of models to use for disagreement
)
```

### Integrating with YOLO for Object Detection with Uncertainty

```python
from r3alai.utils.integration import RSNNYOLOWrapper
import torch

# Initialize the wrapper with a YOLOv8 model
wrapper = RSNNYOLOWrapper(
    yolo_model_path="yolov8n.pt",
    n_classes=10,
    confidence_level=0.95
)

# Train the model
train_loader = torch.utils.data.DataLoader(...)  # Your training data
val_loader = torch.utils.data.DataLoader(...)    # Your validation data

history = wrapper.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=50,
    learning_rate=0.001,
    freeze_backbone=True  # Freeze YOLO backbone weights
)

# Calibrate conformal predictor (optional but recommended)
wrapper.calibrate_conformal(X_cal, y_cal)

# Make predictions with uncertainty
images = torch.randn(10, 3, 640, 640)
predictions, entropy, credal_width = wrapper.predict(images, return_uncertainty=True)

# Or with conformal confidence sets
preds, confidence_sets = wrapper.predict_with_conformal(images)
```

## Architecture Improvements

R3ALAI can be extended in several ways to improve performance:

1. **Ensemble Methods**: Combine multiple RSNN models for improved robustness
   ```python
   # Create an ensemble of RSNN models
   models = [RSNNClassifier(base_model="resnet50", n_classes=10) for _ in range(5)]
   # ... train each model ...
   
   # Average predictions
   def ensemble_predict(X):
       preds = [model.predict(X)[0] for model in models]
       return torch.mean(torch.stack(preds), dim=0)
   ```

2. **Custom Backbones**: Use domain-specific architectures as the backbone
   ```python
   # Create a custom backbone
   custom_backbone = MyCustomModel()
   
   # Initialize RSNN with custom backbone
   model = RSNNClassifier(base_model=custom_backbone, n_classes=10)
   model.set_belief_layer(custom_backbone.output_dim)
   ```

3. **Hybrid Methods**: Combine RSNN with other uncertainty quantification methods
   ```python
   # Create a hybrid model with both RSNN and Dropout-based uncertainty
   class HybridModel(nn.Module):
       def __init__(self):
           super().__init__()
           self.rsnn = RSNNClassifier(base_model="resnet50", n_classes=10)
           self.dropout = nn.Dropout(0.5)
           
       def predict_with_uncertainty(self, X):
           # Get RSNN uncertainty
           rsnn_preds, entropy, credal_width = self.rsnn.predict(X, return_uncertainty=True)
           
           # Calculate dropout uncertainty (monte carlo dropout)
           self.train()  # Enable dropout during inference
           mc_samples = []
           for _ in range(10):
               mc_samples.append(self.dropout(rsnn_preds))
           mc_samples = torch.stack(mc_samples)
           dropout_uncertainty = torch.var(mc_samples, dim=0)
           
           return rsnn_preds, entropy, credal_width, dropout_uncertainty
   ```

## Publishing to PyPI

This package uses GitHub Actions with Trusted Publishing to automatically publish to PyPI when a new version tag is pushed.

### Setting up Trusted Publishing

To set up trusted publishing between GitHub and PyPI:

1. Log in to PyPI (https://pypi.org/)
2. Navigate to your project's settings
3. Go to the "Publishing" tab
4. Click "Add" under Trusted Publishers
5. Enter your repository details:
   - **Owner**: "R3AL-AI" (your GitHub organization name)
   - **Repository name**: "package" (your GitHub repository name)
   - **Workflow name**: "publish.yml"
   - **Environment**: Leave blank

### Publishing a new version

To publish a new version:

1. Update the version number in `setup.py`
2. Commit and push your changes
3. Create and push a tag:
   ```bash
   git tag v0.1.2
   git push origin v0.1.2
   ```

The GitHub Actions workflow will automatically build and publish your package to PyPI.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License 