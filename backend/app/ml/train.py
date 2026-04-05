import torch
import torch.nn as nn
import os
import time
import matplotlib.pyplot as plt

from .model import SafeDipLSTM
from .dataset import load_and_prepare

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH    = os.path.join(ARTIFACTS_DIR, "safedip_lstm.pt")


def train(
    epochs: int     = 50,
    learning_rate: float = 1e-3,
    batch_size: int = 64,
):
    # --- Device ---
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    # --- Data ---
    train_loader, val_loader, _ = load_and_prepare(batch_size=batch_size)

    # --- Model ---
    model     = SafeDipLSTM().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    # Learning rate scheduler — halves LR if val loss plateaus for 5 epochs
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    best_val_loss  = float("inf")
    train_losses   = []
    val_losses     = []

    print(f"\nStarting training — {epochs} epochs\n")
    print(f"{'Epoch':>6} | {'Train Loss':>12} | {'Val Loss':>12} | {'Time':>8}")
    print("-" * 48)

    for epoch in range(1, epochs + 1):
        start = time.time()

        # --- Training pass ---
        model.train()
        train_loss = 0.0

        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)

            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()

            # Gradient clipping — prevents exploding gradients in LSTM
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()
            train_loss += loss.item()

        train_loss /= len(train_loader)

        # --- Validation pass ---
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                pred    = model(xb)
                loss    = criterion(pred, yb)
                val_loss += loss.item()

        val_loss /= len(val_loader)

        # Step scheduler
        scheduler.step(val_loss)

        train_losses.append(train_loss)
        val_losses.append(val_loss)

        elapsed = time.time() - start
        print(f"{epoch:>6} | {train_loss:>12.6f} | {val_loss:>12.6f} | {elapsed:>7.1f}s")

        # --- Save best model ---
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            os.makedirs(ARTIFACTS_DIR, exist_ok=True)
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"         ✓ Best model saved (val loss: {best_val_loss:.6f})")

    print(f"\nTraining complete. Best val loss: {best_val_loss:.6f}")
    print(f"Model saved to: {MODEL_PATH}")

    # --- Plot loss curves ---
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label="Train Loss", linewidth=2)
    plt.plot(val_losses,   label="Val Loss",   linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("SafeDip LSTM — Training vs Validation Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plot_path = os.path.join(ARTIFACTS_DIR, "loss_curve.png")
    plt.savefig(plot_path)
    print(f"Loss curve saved to: {plot_path}")
    plt.show()


if __name__ == "__main__":
    train()