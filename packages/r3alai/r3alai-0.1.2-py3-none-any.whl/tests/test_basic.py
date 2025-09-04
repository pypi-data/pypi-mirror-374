import torch
from r3alai.models import RSNNClassifier


def test_rsnn_forward_and_predict():
    model = RSNNClassifier(base_model="custom", n_classes=3)
    # simple identity backbone to produce 512-dim features
    class DummyBackbone(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = torch.nn.Linear(8, 512)
        def forward(self, x):
            return self.fc(x)
    model.base_model = DummyBackbone()
    model.set_belief_layer(512)

    X = torch.randn(4, 8)
    y = torch.nn.functional.one_hot(torch.randint(0, 3, (4,)), num_classes=3).float()

    out = model(X)
    assert out.shape == (4, 3)

    preds, ent, cred = model.predict(X, return_uncertainty=True)
    assert preds.shape == (4, 3)
    assert ent.shape[0] == 4
    assert cred.shape[0] == 4


