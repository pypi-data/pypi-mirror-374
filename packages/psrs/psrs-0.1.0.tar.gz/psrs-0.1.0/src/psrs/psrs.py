import logging
from typing import List, Optional, Union

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from . import utils
from scipy.spatial import procrustes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)


class DeepShallow(nn.Module):
    """
    DeepShallow model for combining linear and non-linear features.
    """

    def __init__(
        self, input_dim, hidden_dims_list, output_dim, activation_function="ReLU"
    ):
        """
        Initialize the DeepShallow model.

        Args:
        :param input_dim: int, the dimension of the input
        :param hidden_dims_list: list of int, the dimensions of the hidden layers, excluding the input
            and output layer dimensions
        :param output_dim: int, the dimension of the output
        :param activation_function: str, the activation function to use in the hidden layers.
            Options: 'ReLU' or 'GELU'

        """
        super(DeepShallow, self).__init__()
        # Initialize the shallow model component as a linear layer
        self.shallow = nn.Linear(input_dim, output_dim)

        # Initialize the activation function for the deep part
        if activation_function == "ReLU":
            self.activation_function = nn.ReLU()
        elif activation_function == "GELU":
            self.activation_function = nn.GELU()

        # Initialize the deep model component as a sequence of layers
        deep_layers = []
        if len(hidden_dims_list) == 0:
            # If there are no hidden layers, the deep part is just a linear layer
            logger.info("No hidden layers specified. The deep layer is also shallow.")
            self.deep = nn.Linear(input_dim, output_dim)
            return

        for hidden_dim in hidden_dims_list:
            # Add a linear layer
            deep_layers.append(nn.Linear(input_dim, hidden_dim))
            # Add a ReLU activation function
            deep_layers.append(self.activation_function)
            # Update input_dims for the next layer
            input_dim = hidden_dim
        # The final layer of the deep part outputs to the same dimension as the shallow part
        deep_layers.append(nn.Linear(hidden_dims_list[-1], output_dim))

        self.deep = nn.Sequential(*deep_layers)
        # Initialize a layer for Rotation, translation, and scaling
        self.rts = nn.Linear(output_dim, output_dim, bias=True)

    def forward(self, x):
        """
        Forward pass of the DeepShallow model.

        Args:
        :param x: torch.Tensor, the input tensor with shape (batch_size, input_dim)
        """
        shallow_output = self.shallow(x)
        deep_output = self.deep(x)
        # Combine the outputs from the shallow and deep components.
        # This could also be an element-wise multiplication or a linear_layer(concatenation)
        combined_output = shallow_output + deep_output

        return combined_output


class PSRS:
    """
    Procrustes Similarity with Reconstructed Space (PSRS) model.

    This class helps in reconstructing one space (space B) from another space (space A) using a neural network-based approach.
    """

    def __init__(
        self,
        space_a: Union[np.ndarray, torch.Tensor],
        space_b: Union[np.ndarray, torch.Tensor],
        random_state: Optional[int] = None,
        verbose: bool = False
    ):
        """
        Initialize the PSRS model with two spaces.

        Args:
            space_a (Union[np.ndarray, torch.Tensor]): Source space A.
            space_b (Union[np.ndarray, torch.Tensor]): Target space B.
            random_state (Optional[int]): Random seed for reproducibility.
            verbose (bool): If True, enables detailed logging.
        """
        self.verbose = verbose
        # Convert input spaces to torch.Tensor if they are not torch tensors
        self.space_a = self._ensure_tensor(space_a)
        self.space_b = self._ensure_tensor(space_b)

        # Ensure space_a and space_b have the same number of data points
        self._validate_input_spaces()

        self.model = None
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()

        # Initialize attributes
        self._initialize_attributes()

        # Set the random seed
        if random_state:
            torch.manual_seed(random_state)

    def _ensure_tensor(self, data: Union[np.ndarray, torch.Tensor]) -> torch.Tensor:
        """
        Convert input to PyTorch tensor if it's not already a tensor.
        """
        return torch.from_numpy(data) if not isinstance(data, torch.Tensor) else data

    def _initialize_attributes(self):
        """
        Initialize various attributes of the class.
        """
        # Separate initialization for each attribute
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_train_pred = None
        self.y_test_pred = None
        self.train_loss_history = []
        self.test_loss_history = []
        self.test_procrustes_similarity_history = []
        self.train_procrustes_similarity_history = []

    def _validate_input_spaces(self):
        """
        Validate that input spaces have the same number of data points.
        """
        if self.space_a.shape[0] != self.space_b.shape[0]:
            raise ValueError(
                "space_a and space_b must have the same number of data points"
            )
        logger.info(f"Shape of space A: {self.space_a.shape}")
        logger.info(f"Shape of space B: {self.space_b.shape}")

    def _initialize_model(self, hidden_dims_list: List[int], activation_function: str):
        """
        Initialize the neural network model with the specified architecture.
        """
        self.model = DeepShallow(
            input_dim=self.space_a.shape[1],
            hidden_dims_list=hidden_dims_list,
            output_dim=self.space_b.shape[1],
            activation_function=activation_function,
        )

    def _prepare_data(self, random_state: Optional[int], test_size: float):
        """
        Prepare the training and testing datasets by splitting and scaling.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            self.space_a, self.space_b, test_size=test_size, random_state=random_state
        )

        # Scale the data
        self.X_train = torch.Tensor(self.scaler_X.fit_transform(X_train))
        self.y_train = torch.Tensor(self.scaler_y.fit_transform(y_train))
        self.X_test = torch.Tensor(self.scaler_X.transform(X_test))
        self.y_test = torch.Tensor(self.scaler_y.transform(y_test))

    def reconstruct(
        self,
        epochs: int = 100,
        learning_rate: float = 0.005,
        hidden_dims_list: Optional[List[int]] = None,
        random_state: Optional[int] = None,
        test_size: float = 0.3,
        loss_fn: str = "procrustes",
        checkpoint_interval: int = 50,
        loss_reduction_method: str = "mean",
        activation_function: str = "ReLU",
        batch_size: int = 128,
        optimizer: Optional[torch.optim.Optimizer] = None,
    ):
        """
        Fit the model to reconstruct space B using space A.

        Args:
            epochs (int): Number of training epochs.
            learning_rate (float): Learning rate for training.
            hidden_dims_list (Optional[List[int]]): List of hidden layer dimensions.
            random_state (Optional[int]): Random seed for reproducibility.
            test_size (float): Fraction of data to be used for testing.
            loss_fn (str): Loss function to use ('mse' or 'procrustes').
            checkpoint_interval (int): Interval to print the loss during training.
            loss_reduction_method (str): Reduction method for loss ('mean' or 'sum').
            activation_function (str): Activation function to use.
            batch_size (int): Batch size for training.
            optimizer (Optional[torch.optim.Optimizer]): Custom optimizer for training.
        """
        if hidden_dims_list is None:
            hidden_dims_list = [
                self.space_a.shape[1] * 2,
                np.max(self.space_a.shape[1] + self.space_b.shape[1]),
                self.space_b.shape[1],
            ]

        # Initialize the model
        self._initialize_model(hidden_dims_list, activation_function)

        # Prepare data
        self._prepare_data(random_state, test_size)

        # Initialize the optimizer
        if optimizer is None:
            optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        # Batch size check
        if batch_size > len(self.X_train):
            logger.info(f"Batch size {batch_size} is larger than the number of training data {len(self.X_train)}")
            batch_size = len(self.X_train)
            logger.info(f"Batch size has been adjusted to: {batch_size}")

        # Run training loop
        self._run_dl_model(
            epochs,
            optimizer,
            loss_fn,
            checkpoint_interval,
            batch_size,
            loss_reduction_method,
        )

    def calculate_procrustes_similarity(self):
        """
        Calculate the procrustes similarity between the original and reconstructed spaces.
        """
        self.model.eval()  # Set model to evaluation mode
        with torch.no_grad():
            self.y_train_pred = self.model(self.X_train)
            self.y_test_pred = self.model(self.X_test)

        # Calculate the procrustes similarity
        mtx1, mtx2, train_reconstructed_disparity = procrustes(
            self.y_train_pred, self.y_train
        )
        mtx1, mtx2, test_reconstructed_disparity = procrustes(
            self.y_test_pred, self.y_test
        )

        # similarity = 1 - disparity
        self.train_procrustes_similarity_history.append(
            1 - train_reconstructed_disparity
        )
        self.test_procrustes_similarity_history.append(1 - test_reconstructed_disparity)

        return 1 - test_reconstructed_disparity

    def _run_dl_model(
        self,
        epochs: int,
        optimizer: torch.optim.Optimizer,
        loss_fn: str,
        checkpoint_interval: int,
        batch_size: int,
        loss_reduction_method: str = "mean",
    ):
        """
        Train the deep learning model.
        """
        # Input checks
        if not isinstance(checkpoint_interval, int) or checkpoint_interval <= 0:
            raise ValueError("checkpoint_interval should be a positive integer")

        # Set the loss function
        if loss_fn.lower() == "mse":
            loss_fn = nn.MSELoss(reduction=loss_reduction_method)
        elif loss_fn.lower() == "procrustes":
            logger.warning(
                "Please note that while procrustes loss is much faster, it might lead to back propagation instability and training failure in some special cases. Change to 'mse' if that happens."
            )
            loss_fn = utils.ProcrustesLoss(reduction=loss_reduction_method)
        else:
            raise ValueError(
                f"Unknown loss function: {loss_fn}, please choose from 'mse' or 'procrustes'"
            )

        logger.info(f"Loss function: {loss_fn}")

        # Create data loader for training
        train_loader = DataLoader(
            TensorDataset(self.X_train, self.y_train),
            batch_size=batch_size,
            shuffle=True,
            num_workers=4  # Use multiple workers for faster data loading
        )

        # Training loop
        for epoch in range(epochs):
            self.model.train()  # Set model to training mode
            for X_batch, y_batch in train_loader:
                y_pred_batch = self.model(X_batch)
                loss = loss_fn(y_pred_batch, y_batch)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Calculate and store loss values and procrustes similarity
            self.calculate_procrustes_similarity()
            train_loss = loss_fn(self.y_train_pred, self.y_train)
            test_loss = loss_fn(self.y_test_pred, self.y_test)

            self.train_loss_history.append(train_loss.item())
            self.test_loss_history.append(test_loss.item())

            # Log training progress
            if self.verbose and (epoch + 1) % checkpoint_interval == 0:
                logger.info(f"====== Epoch [{epoch+1}/{epochs}] ======")
                logger.info(f"Train Loss: {self.train_loss_history[-1]:.4f}")
                logger.info(f"Test Loss: {self.test_loss_history[-1]:.4f}")
                logger.info(
                    f"Train PSRS score: {self.train_procrustes_similarity_history[-1]:.4f}"
                )
                logger.info(
                    f"Test PSRS score: {self.test_procrustes_similarity_history[-1]:.4f}"
                )
                logger.info(f"========================================")

