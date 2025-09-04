import torch
from transformers import AutoModel, AutoFeatureExtractor
from r3alai.models import RSNNClassifier


def main():
    model_name = "google/vit-base-patch16-224"
    extractor = AutoFeatureExtractor.from_pretrained(model_name)
    backbone = AutoModel.from_pretrained(model_name)

    class HFBackbone(torch.nn.Module):
        def __init__(self, backbone_model):
            super().__init__()
            self.backbone = backbone_model
            self.pool = torch.nn.AdaptiveAvgPool1d(1)
            self.fc = torch.nn.Linear(self.backbone.config.hidden_size, 512)
        def forward(self, x):
            # x: (B, C, H, W) -> convert to features using HF extractor outside
            outputs = self.backbone(pixel_values=x)
            feats = outputs.last_hidden_state.transpose(1, 2)  # (B, D, T)
            pooled = self.pool(feats).squeeze(-1)  # (B, D)
            return self.fc(pooled)

    rsnn = RSNNClassifier(base_model="custom", n_classes=10)
    rsnn.base_model = HFBackbone(backbone)
    rsnn.set_belief_layer(512)

    X = torch.randn(8, 3, 224, 224)
    y = torch.nn.functional.one_hot(torch.randint(0, 10, (8,)), num_classes=10).float()
    rsnn.fit(X, y, epochs=1, batch_size=4, validation_split=0.25)

    preds, ent, cred = rsnn.predict(torch.randn(2, 3, 224, 224), return_uncertainty=True)
    print(preds.shape, ent.shape, cred.shape)


if __name__ == "__main__":
    main()


