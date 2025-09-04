# Panelformer

[![Project](https://img.shields.io/badge/Project-Panelformer-blue)]()
[![Research](https://img.shields.io/badge/Type-Research-green)]()
[![Lead](https://img.shields.io/badge/Lead-Dr.%20T.%20Uthayasanker-purple)]()
[![Contributor](https://img.shields.io/badge/Contributor-Shabthana%20Johnson-teal)]()
[![Contributor](https://img.shields.io/badge/Contributor-Kajaani%20Balabavan-orange)]()
[![Contributor](https://img.shields.io/badge/Contributor-Sathurgini%20Uthayakumar-yellow)]()

<!-- **Project Lead(s) / Mentor(s)**
Dr. T. Uthayasanker

**Contributor(s)**
Kajaani Balabavan
Shabthana Johnson
Sathurgini Uthayakumar -->

**Panelformer** is a transformer-based deep learning model designed for accurate and scalable **panel time series forecasting**. Built on top of the Temporal Fusion Transformer (TFT), Panelformer introduces several innovations to address the limitations of existing models when applied to heterogeneous panel datasets.

### 🔑 Keywords

**Panel time series**, **Temporal Fusion Transformer**, **Transformer architecture**, **Forecasting**, **Panelformer**

## 🔍 Overview

Panel time series involve multiple entities (e.g., countries, products) observed over time — requiring models to handle both temporal and cross-sectional complexity. Panelformer enhances forecasting accuracy across diverse panel structures by integrating the following features:

- **Segment-wise Attention**: Reduces complexity and captures local patterns in long sequences.
- **Multi-Scale Series Decomposition**: Separates trend and seasonal components using learnable moving averages.
- **Cross-Entity Attention**: Models dependencies between different panel entities.
- **Parallel Trend-Seasonal Paths**: Dedicated processing for distinct temporal dynamics.
- **Adaptive Component Weighting**: Learns to prioritize seasonal vs. trend features dynamically.

## 🚀 Key Results

Evaluated on 11 real-world datasets spanning economics, energy, climate, and health domains, Panelformer achieved:

- **7.99% average MAPE improvement** over baseline TFT
- Robust performance on balanced/unbalanced, short/long, micro/macro panels
- Significant accuracy gains on high-frequency datasets like foreign exchange, surface temperature, and electricity

## 📦 Installation

```bash
pip install panelformer
```

## 🛠️ How to Use

Using Panelformer involves four main steps:

### 🧬 Step 1: Data Preparation

Prepare your panel dataset with columns for entity IDs, timestamps, and target values. Convert your date column to datetime format and create a sequential time index for modeling.

### 🧩 Step 2: Dataset Creation

Use the `pytorch_forecasting` library’s `TimeSeriesDataSet` class to define training, validation, and test datasets. This includes specifying encoder and decoder lengths, grouping by entity, and applying normalization.

### 🏋️ Step 3: Train the Model

Instantiate the `Panelformer` model using the prepared dataset, configure hyperparameters (like learning rate, hidden sizes, attention heads), and train with a PyTorch Lightning `Trainer` for efficient training management.

```python

from Panelformer import Panelformer

import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, LearningRateMonitor
from lightning.pytorch.loggers import TensorBoardLogger
from pytorch_forecasting.metrics import QuantileLoss

early_stop_callback = EarlyStopping(monitor="val_loss", min_delta=1e-10, patience=5, verbose=False, mode="min")
lr_logger = LearningRateMonitor()
logger = TensorBoardLogger("lightning_logs")

trainer = pl.Trainer(
    max_epochs = 50,
    enable_model_summary=True,
    gradient_clip_val=0.1,
    callbacks=[lr_logger, early_stop_callback],
    logger=logger,
)

model = Panelformer.from_dataset(
    training,
    learning_rate=0.001,
    hidden_size=16,
    attention_head_size=2,
    dropout=0.1,
    segment_size=4,
    decomposition_kernel_sizes=[3, 7, 15, 31],
    trend_processing_layers=2,
    use_cross_series_attention=True,
    adaptive_trend_weight=True,
    hidden_continuous_size=8,
    loss=QuantileLoss()
)

trainer.fit(model, train_dataloaders=train_dataloader, val_dataloaders=val_dataloader)
```

### 📈 Step 4: Make Predictions

Use the trained model to predict on new data by passing a test dataloader, retrieving forecasts for evaluation or downstream use.

```python
predictions = model.predict(test_dataloader, mode="raw", return_x=True)
```

### 🧪 Step 5: Evaluation Utilities

Panelformer comes with a built-in utility module to simplify model evaluation and visualization. This includes standard regression metrics and diagnostic plots to help assess performance.

#### ✅ Features:

- Residual analysis (`Residuals vs Predictions`)
- Actual vs Predicted scatter plot
- Error distribution histogram
- Standard metrics: R², MAPE, MSE, RMSE, MAE
- Correlation metrics: Pearson, Spearman
- Standardized error metrics (optional)

#### 🔧 Example Usage:

```python
from Panelformer import utils

# Evaluate on validation set
print("Validation Metrics:")
val_r2, val_mape, val_mse, val_rmse, val_mae, val_error_std, val_pearson_corr, val_spearman_corr = utils.calculate_metrics(val_dataloader, model)

# Evaluate on test set
print("\nTest Metrics:")
test_r2, test_mape, test_mse, test_rmse, test_mae, test_error_std, test_pearson_corr, test_spearman_corr = utils.calculate_metrics(test_dataloader, model)
```

#### 🎯 Output:

- Metrics printed to console
- Diagnostic plots shown:

  - Residuals vs Predictions
  - Actual vs Predicted
  - Error Distribution

This helps **visually diagnose model behavior**, including overfitting, heteroscedasticity, or bias in predictions.

<!-- ## 📄 Citation

==============

```
......

``` -->

## 🛠 License

Released under the MIT License. Built on top of [PyTorch Forecasting](https://github.com/jdb78/pytorch-forecasting).
