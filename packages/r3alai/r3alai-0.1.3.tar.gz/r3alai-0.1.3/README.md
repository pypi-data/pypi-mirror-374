# R3ALAI

Python SDK for Random Set Neural Networks (RSNN): uncertainty estimation, conformal prediction, and active learning. Built to add RSNN benefits (sample efficiency, robustness, reliability) to ML workflows.

## Install
- Base: `pip install r3alai`
- With vision backbones: `pip install 'r3alai[vision]'`
- With YOLO: `pip install 'r3alai[yolo]'`

Requires Python 3.8+ and PyTorch.

## What it provides
- `r3alai.models`: `RSNNClassifier` — RSNN head on a backbone (torchvision or custom `nn.Module`).
- `r3alai.conformal`: `ConformalPredictor` — confidence sets with distribution-free coverage after calibration.
- `r3alai.active_learning`: `ActiveLearner` — entropy/credal querying and simple disagreement mode.
- `r3alai.utils`: `RSNNYOLOWrapper`, `YOLOFeatureExtractor` — plug RSNN uncertainty into YOLOv8.

## How to use (high-level)
1) Create an RSNN model
- Pick a backbone: `"resnet50"`, `"mobilenet_v2"`, `"efficientnet_b0"`, or use a custom backbone.
- Set `n_classes` (one-hot labels expected). Optional `alpha`/`beta` regularization.

2) Train
- Call `fit(X, y, ...)` with tensors/ndarrays; early stopping and LR scheduling are included.

3) Predict with uncertainty
- Call `predict(..., return_uncertainty=True)` to get predictions, pignistic entropy, and credal width.

## Conformal prediction
1) Wrap a trained RSNN with `ConformalPredictor(confidence_level=0.9/0.95)`.
2) Calibrate on a held-out split (features and one-hot labels).
3) Use `predict` for confidence sets; `get_coverage` to measure empirical coverage.

## Active learning
1) Construct `ActiveLearner(model, uncertainty_measure="entropy"|"credal")`.
2) Provide an unlabeled pool to `query` to select samples and indices for annotation.

## YOLO integration (optional)
1) Install extras: `r3alai[yolo]`.
2) Initialize `RSNNYOLOWrapper(yolo_model_path, n_classes)`.
3) Train with your DataLoaders; optionally calibrate conformal and then predict with uncertainty or confidence sets.

## Custom backbones and frameworks
- Custom `nn.Module`: set `base_model="custom"`, assign your module to `rsnn_model.base_model`, then call `set_belief_layer(feature_dim)`.
- Hugging Face models: adapt outputs to a 512-dim feature vector and connect as a custom backbone.

## Tips
- Keep a small calibration split to enable conformal coverage.
- Start active learning with entropy querying; try disagreement for harder pools.
- For detection, first freeze the YOLO backbone and train only the RSNN head.

## Support
- See docstrings on `RSNNClassifier`, `ConformalPredictor`, `ActiveLearner`, and `RSNNYOLOWrapper`.
- Report issues and requests on GitHub Issues.

## License
MIT