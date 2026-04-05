# ML Artifacts

These files are excluded from git (large binary files).

## To generate them locally:

1. Generate synthetic training data:

```bash
   python -m app.ml.generate_data
```

2. Build dataset and train the model:

```bash
   python -m app.ml.train
```

This will produce:

- `safedip_lstm.pt` — trained LSTM model weights
- `scaler.pkl` — MinMaxScaler for normalisation
- `loss_curve.png` — training vs validation loss plot

## Pre-trained weights

If you don't want to retrain, ask Abiram for the `.pt` and `.pkl` files
and drop them in this folder.
