import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    r2_score,
    mean_absolute_percentage_error,
    mean_squared_error
)
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler


def plot_residuals(actuals, predictions):
    """
    Plot residuals (errors) against predictions to assess patterns in prediction errors.

    Args:
        actuals (array-like): Ground truth target values.
        predictions (array-like): Model predicted values.
    """
    residuals = actuals - predictions
    plt.figure(figsize=(10, 6))
    plt.scatter(predictions, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predictions')
    plt.ylabel('Residuals')
    plt.title('Residuals vs. Predictions')
    plt.show()


def plot_actual_vs_predicted(actuals, predictions):
    """
    Plot actual values against predicted values.

    Args:
        actuals (array-like): Ground truth target values.
        predictions (array-like): Model predicted values.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(actuals, predictions, alpha=0.5)
    plt.plot([min(actuals), max(actuals)], [min(actuals), max(actuals)], 'r--')
    plt.xlabel('Actuals')
    plt.ylabel('Predictions')
    plt.title('Actual vs. Predicted')
    plt.show()


def plot_error_distribution(errors):
    """
    Plot histogram of prediction errors.

    Args:
        errors (array-like): Differences between actuals and predictions.
    """
    plt.figure(figsize=(10, 6))
    plt.hist(errors, bins=50, edgecolor='k')
    plt.xlabel('Error')
    plt.ylabel('Frequency')
    plt.title('Error Distribution')
    plt.show()


def calculate_metrics(dataloader, model):
    """
    Calculate and print detailed regression metrics and plots for model evaluation.

    Args:
        dataloader (DataLoader): DataLoader containing input and ground truth.
        model (nn.Module): Trained forecasting model.

    Returns:
        Tuple containing:
            - R2 score
            - MAPE (%)
            - MSE
            - RMSE
            - MAE
            - Standard deviation of errors
            - Pearson correlation
            - Spearman correlation
    """
    prediction = model.predict(dataloader)
    actuals = torch.cat([y[0] for x, y in iter(dataloader)])

    actuals_np = actuals.cpu().numpy().flatten()
    predictions_np = prediction.cpu().numpy().flatten()

    errors = actuals_np - predictions_np

    print("Error Analysis\n")
    plot_residuals(actuals_np, predictions_np)
    plot_actual_vs_predicted(actuals_np, predictions_np)
    plot_error_distribution(errors)
    print('\n***************\n')

    r2 = r2_score(actuals_np, predictions_np)
    mape = mean_absolute_percentage_error(actuals_np, predictions_np) * 100
    mse = mean_squared_error(actuals_np, predictions_np)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(errors))
    error_std = np.std(errors)

    pearson_corr, _ = pearsonr(actuals_np, predictions_np)
    spearman_corr, _ = spearmanr(actuals_np, predictions_np)

    print(f"R2: {r2}")
    print(f"MAPE: {mape}%")
    print(f"MSE: {mse}")
    print(f"RMSE: {rmse}")
    print(f"MAE: {mae}")
    print(f"Error Std Dev: {error_std}")
    print(f"Pearson Correlation: {pearson_corr}")
    print(f"Spearman Correlation: {spearman_corr}\n")

    scaler = StandardScaler()
    actuals_scaled = scaler.fit_transform(actuals_np.reshape(-1, 1)).flatten()
    predictions_scaled = scaler.transform(predictions_np.reshape(-1, 1)).flatten()

    mae_std = np.mean(np.abs(actuals_scaled - predictions_scaled))
    mse_std = np.mean((actuals_scaled - predictions_scaled) ** 2)
    rmse_std = np.sqrt(mse_std)

    print(f"Standardized MAE: {mae_std}")
    print(f"Standardized MSE: {mse_std}")
    print(f"Standardized RMSE: {rmse_std}")

    return r2, mape, mse, rmse, mae, error_std, pearson_corr, spearman_corr