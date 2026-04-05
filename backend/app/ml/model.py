import torch
import torch.nn as nn


class SafeDipLSTM(nn.Module):
    """
    Multivariate LSTM forecaster.
    Input:  (batch, 30, 5)  — 30 timesteps, 5 sensor parameters
    Output: (batch, 10, 5)  — 10 future timesteps, 5 sensor parameters
    """

    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 128,
        num_layers: int = 2,
        forecast_horizon: int = 10,
        dropout: float = 0.2,
    ):
        super(SafeDipLSTM, self).__init__()

        self.hidden_size      = hidden_size
        self.num_layers       = num_layers
        self.forecast_horizon = forecast_horizon
        self.input_size       = input_size

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,       # input shape: (batch, seq, features)
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Fully connected output layer
        # Maps last hidden state → 10 future steps × 5 parameters
        self.fc = nn.Linear(hidden_size, forecast_horizon * input_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, 30, 5)

        # LSTM pass — we only need the final hidden state
        lstm_out, _ = self.lstm(x)          # (batch, 30, hidden_size)
        last_hidden  = lstm_out[:, -1, :]   # (batch, hidden_size)

        # Project to forecast
        out = self.fc(last_hidden)          # (batch, 10 * 5)

        # Reshape to (batch, 10, 5)
        out = out.view(-1, self.forecast_horizon, self.input_size)

        # Clamp output to [0, 1] since inputs are normalized
        out = torch.sigmoid(out)

        return out


if __name__ == "__main__":
    # Quick sanity check
    model = SafeDipLSTM()
    print(model)

    dummy_input = torch.randn(64, 30, 5)    # fake batch
    output      = model(dummy_input)

    print(f"\nInput shape:  {dummy_input.shape}")
    print(f"Output shape: {output.shape}")   # should be (64, 10, 5)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters: {total_params:,}")