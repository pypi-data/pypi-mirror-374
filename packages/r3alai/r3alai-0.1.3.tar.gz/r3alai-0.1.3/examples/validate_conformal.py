import torch
import numpy as np
from r3alai.models import RSNNClassifier
from r3alai.conformal import ConformalPredictor


def main():
    model = RSNNClassifier(base_model="custom", n_classes=5)

    class DummyBackbone(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = torch.nn.Linear(16, 512)
        def forward(self, x):
            return self.fc(x)

    model.base_model = DummyBackbone()
    model.set_belief_layer(512)

    X_train = torch.randn(128, 16)
    y_train = torch.nn.functional.one_hot(torch.randint(0, 5, (128,)), num_classes=5).float()
    model.fit(X_train, y_train, epochs=1, batch_size=16, validation_split=0.2)

    X_cal = torch.randn(64, 16)
    y_cal = torch.nn.functional.one_hot(torch.randint(0, 5, (64,)), num_classes=5).float()

    conformal = ConformalPredictor(model=model, confidence_level=0.9)
    conformal.calibrate(X_cal, y_cal)

    X_test = torch.randn(20, 16)
    y_test = torch.nn.functional.one_hot(torch.randint(0, 5, (20,)), num_classes=5).float()

    preds, sets_ = conformal.predict(X_test)
    coverage = conformal.get_coverage(X_test, y_test)
    print("Average set size:", np.mean([len(s) for s in sets_]))
    print("Coverage:", coverage)


if __name__ == "__main__":
    main()


