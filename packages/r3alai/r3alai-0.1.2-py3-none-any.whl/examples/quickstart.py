import torch
from r3alai.models import RSNNClassifier


def main():
    model = RSNNClassifier(base_model="resnet50", n_classes=10)

    X = torch.randn(32, 3, 224, 224)
    y = torch.nn.functional.one_hot(torch.randint(0, 10, (32,)), num_classes=10).float()

    history = model.fit(X, y, epochs=1, batch_size=8, validation_split=0.25)
    print("History keys:", list(history.keys()))

    preds, ent, cred = model.predict(torch.randn(4, 3, 224, 224), return_uncertainty=True)
    print("Preds shape:", preds.shape)
    print("Entropy shape:", ent.shape)
    print("Credal width shape:", cred.shape)


if __name__ == "__main__":
    main()


