#!/usr/bin/env python
# coding: utf-8
"""
Bias–Variance Decomposition Toolkit
===================================

This module provides utilities to estimate the bias and variance components of
machine learning models using two loss functions:

1. Mean Squared Error (MSE) – for regression tasks
2. 0–1 Loss – for classification tasks

The toolkit works with both scikit-learn models and PyTorch models.
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from inspect import isclass
from scipy.stats import mode
import uuid


def train_model(
    train_data_list,
    loss_fn,
    lr,
    model_class,
    model_kwargs,
    num_models,
    X_test,
    max_epochs,
    batch_size,
    patience=10,
    device="cpu",
    task="regression",
):
    """
    Train an ensemble of models using bootstrapped training sets.

    Parameters
    ----------
    train_data_list : list of tuples
        Each element is (X_train_resampled, y_train_resampled).

    Returns
    -------
    all_preds : list of np.ndarray
        Predictions from each trained model.
    train_loss : list of float
        Final training loss per model.
    """
    all_preds = []
    train_loss = []
    unique_id = str(uuid.uuid4())

    for i, train_data in enumerate(train_data_list):
        print(f"\n--- Training Model {i+1}/{num_models} ---")

        X_train_resampled, y_train_resampled = train_data

        # Train-validation split
        X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
            X_train_resampled, y_train_resampled, test_size=0.2, random_state=42
        )

        # Tensors
        X_train_tensor = torch.tensor(X_train_split, dtype=torch.float32).to(device)
        X_val_tensor = torch.tensor(X_val_split, dtype=torch.float32).to(device)
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)

        if isinstance(loss_fn, nn.CrossEntropyLoss):
            y_train_tensor = torch.tensor(y_train_split, dtype=torch.long).to(device)
            y_val_tensor = torch.tensor(y_val_split, dtype=torch.long).to(device)
        else:  # regression
            y_train_tensor = torch.tensor(y_train_split, dtype=torch.float32).to(device)
            y_val_tensor = torch.tensor(y_val_split, dtype=torch.float32).to(device)

        # DataLoader
        effective_batch = min(batch_size, max(1, len(X_train_tensor)))
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=effective_batch, shuffle=True)

        # Model + optimizer
        model = model_class(**model_kwargs).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        # Early stopping
        best_val_loss = float("inf")
        patience_counter = 0

        for epoch in range(max_epochs):
            model.train()
            epoch_loss = 0.0
            for x, y in train_loader:
                optimizer.zero_grad()
                output = model(x)
                loss = loss_fn(output, y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * x.size(0)

            # Validation
            model.eval()
            with torch.no_grad():
                val_output = model(X_val_tensor)
                val_loss = loss_fn(val_output, y_val_tensor)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_state_dict = model.state_dict()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping after {epoch+1} epochs.")
                    break

        # Restore best model
        model.load_state_dict(best_state_dict)
        model.eval()

        # Final training loss
        with torch.no_grad():
            train_output = model(X_train_tensor)
            final_train_loss = loss_fn(train_output, y_train_tensor).item()
        train_loss.append(final_train_loss)

        # Predictions
        with torch.no_grad():
            if task == "classification":
                preds = torch.argmax(model(X_test_tensor), dim=1).cpu().numpy()
            else:
                preds = model(X_test_tensor).cpu().numpy()
            all_preds.append(preds)

    return all_preds, train_loss


def get_bvd_mse(all_preds_np: np.ndarray, y_test: np.ndarray):
    if all_preds_np.ndim == 3 and all_preds_np.shape[-1] == 1:
        all_preds_np = all_preds_np.squeeze(-1)

    y_test = y_test.squeeze()
    mean_preds = np.mean(all_preds_np, axis=0)
    bias = np.mean((mean_preds - y_test) ** 2)
    variance = np.mean(np.var(all_preds_np, axis=0, ddof=0))
    return bias, variance


def estimate_bias_variance_mse(
    model_class,
    X_train,
    y_train,
    X_test,
    y_test,
    loss_fn,
    model_kwargs={},
    num_models=20,
    max_epochs=100,
    patience=10,
    batch_size=64,
    lr=0.001,
    device="cpu",
):
    """
    Compute bias and variance decomposition for regression (MSE).
    Parameters
    ----------
    loss_fn : torch.nn loss function
        Loss function (e.g. nn.MSELoss, nn.CrossEntropyLoss).
    lr : float
        Learning rate.
    model_class : nn.Module
        PyTorch model class.
    model_kwargs : dict
        Keyword arguments for model initialization.
    num_models : int
        Number of bootstrapped models to train.
    X_test : np.ndarray
        Test feature matrix.
    y_test: Test depended matrix
    max_epochs : int
        Maximum training epochs.
    batch_size : int
        Mini-batch size.
    patience : int, optional
        Early stopping patience (default=10).
    device : str, optional
        Device to train on ("cpu" or "cuda").
    task : str, optional
        Task type: "regression" or "classification".

    Returns
    -------
    bias_sq, variance, total_error, bias_plus_variance, avg_train_loss, test_loss
    """
    train_data_list = [resample(X_train, y_train, replace=True) for _ in range(num_models)]
    all_preds, train_loss = train_model(
        train_data_list,
        loss_fn,
        lr,
        model_class,
        model_kwargs,
        num_models,
        X_test,
        max_epochs,
        batch_size,
        patience,
        device,
        task="regression",
    )
    all_preds_np = np.stack(all_preds, axis=0).squeeze()
    y_test = y_test.squeeze()

    bias_sq, variance = get_bvd_mse(all_preds_np, y_test)
    total_error = np.mean((all_preds_np - y_test) ** 2)
    bias_plus_variance = bias_sq + variance
    avg_train_loss = np.mean(train_loss)
    test_loss = np.mean((np.mean(all_preds_np, axis=0) - y_test) ** 2)

    print("\n--- MSE Decomposition Results ---")
    print(f"Bias²              : {bias_sq:.4f}")
    print(f"Variance           : {variance:.4f}")
    print(f"Total error (MSE)  : {total_error:.4f}")
    print(f"Bias² + Variance   : {bias_plus_variance:.4f}")

    return bias_sq, variance, total_error, bias_plus_variance, avg_train_loss, test_loss


def estimate_bias_variance_0_1(
    model_class,
    loss_fn,
    X_train,
    y_train,
    X_test,
    y_test,
    model_kwargs={},
    num_models=20,
    max_epochs=100,
    patience=10,
    batch_size=64,
    lr=0.001,
    device="cpu",
):
    """
    Estimate bias–variance decomposition using 0–1 loss (classification).
    Parameters
    ----------
    loss_fn : torch.nn loss function
        Loss function (e.g. nn.MSELoss, nn.CrossEntropyLoss).
    lr : float
        Learning rate.
    model_class : nn.Module
        PyTorch model class.
    model_kwargs : dict
        Keyword arguments for model initialization.
    num_models : int
        Number of bootstrapped models to train.
    X_test : np.ndarray
        Test feature matrix.
    max_epochs : int
        Maximum training epochs.
    batch_size : int
        Mini-batch size.
    patience : int, optional
        Early stopping patience (default=10).
    device : str, optional
        Device to train on ("cpu" or "cuda").
    task : str, optional
        Task type: "regression" or "classification".

    Returns
    -------
    avg_bias, avg_variance, expected_loss, empirical_loss, avg_train_loss, test_loss
    """
    train_data_list = [resample(X_train, y_train, replace=True) for _ in range(num_models)]
    all_preds, train_loss = train_model(
        train_data_list,
        loss_fn,
        lr,
        model_class,
        model_kwargs,
        num_models,
        X_test,
        max_epochs,
        batch_size,
        patience,
        device,
        task="classification",
    )

    all_preds = np.stack(all_preds, axis=0)
    y_test = y_test.flatten()

    # Majority vote
    mode_preds, _ = mode(all_preds, axis=0, keepdims=False)
    mode_preds = np.array(mode_preds).flatten()

    bias_arr = (mode_preds != y_test).astype(float)
    var_arr = (all_preds != mode_preds).mean(axis=0)

    expected_loss_arr = np.where(bias_arr == 0, var_arr, 1 - var_arr)
    avg_bias = bias_arr.mean()
    avg_var = var_arr.mean()
    expected_loss = expected_loss_arr.mean()
    empirical_loss = (all_preds != y_test).mean()
    avg_train_loss = np.mean(train_loss)
    test_loss = np.mean((np.mean(all_preds, axis=0) - y_test) ** 2)

    print("\n--- 0–1 Loss Decomposition Results ---")
    print(f"Average Bias       : {avg_bias:.4f}")
    print(f"Average Variance   : {avg_var:.4f}")
    print(f"Expected 0–1 Loss  : {expected_loss:.4f}")
    print(f"Empirical 0–1 Loss : {empirical_loss:.4f}")

    return avg_bias, avg_var, expected_loss, empirical_loss, avg_train_loss, test_loss
