from squid import Server
from squid import SklearnLogger, PytorchLogger, TensorflowLogger
from .utils import *
import pytest
import numpy as np
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow import MlflowClient
from sklearn.linear_model import LinearRegression
import tensorflow as tf

# Fixtures for infrastructure setup and logging
@pytest.fixture(scope="module", autouse=True)
def infra_setup_and_teardown():
    server = Server(
        "test_project", 
        ui_port=5001, 
        artifact_store_port=5002, 
        console_port=5003
    )

    server.start()
    yield
    server.down(delete_all_data=True)


@pytest.fixture
def sklearn_logger():
    """Fixture for SklearnLogger."""
    return SklearnLogger(logging_kwargs={"log_models": True})


@pytest.fixture
def pytorch_logger():
    """Fixture for PytorchLogger with graph saving disabled."""
    return PytorchLogger(save_graph=False, logging_kwargs={"log_models": True})


@pytest.fixture
def pytorch_logger_save_graph():
    """Fixture for PytorchLogger with graph saving enabled."""
    return PytorchLogger(save_graph=True, logging_kwargs={"log_models": True})


@pytest.fixture
def tensorflow_logger():
    return TensorflowLogger(logging_kwargs={"log_models": True})


# Dummy Training Functions for Testing
def dummy_train_function_sklearn(model, x, y, *args, **kwargs):
    """A dummy training function for sklearn models."""
    model.fit(x, y)
    return model, {'accuracy': 0.95}  # Return model and dummy metrics


def dummy_train_function_pytorch(model, datamodule, *args, **kwargs):
    """A dummy training function for PyTorch models."""
    trainer = create_trainer(3)
    trainer.fit(model=model, datamodule=datamodule)
    return trainer.model, {"accuracy": 0.95}  # Return trainer's model and metrics


def dummy_train_function_tensorflow(model, x, y, *args, **kwargs):
    model.fit(x, y, epochs=3, batch_size=5)
    return model, {"accuracy": 0.95}


def create_simple_tf_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


# Sklearn Logger Tests
def test_sklearn_logger_log_invalid(sklearn_logger):
    """Test to ensure ValueError is raised when 'experiment_name' is missing."""
    model = LinearRegression()
    x = np.random.rand(10, 10)
    y = np.random.rand(10, 1)

    logged_func = sklearn_logger.log(dummy_train_function_sklearn)
    with pytest.raises(ValueError, match=f"experiment_name must be specified as a kwarg when calling dummy_train_function_sklearn."):
        logged_func(model, x, y)


def test_sklearn_logger_log(sklearn_logger):
    """Test logging with SklearnLogger."""
    model = LinearRegression()
    x = np.random.rand(10, 10)
    y = np.random.rand(10, 1)

    logged_func = sklearn_logger.log(dummy_train_function_sklearn)
    model, metrics = logged_func(model, x, y, experiment_name='test_sklearn')
    
    # Ensure the correct metrics were returned
    assert metrics['accuracy'] == 0.95


def test_mlflow_run_sklearn_logger():
    """Test to verify the model was logged correctly with MLflow."""
    client = MlflowClient(mlflow.get_tracking_uri())
    latest_run = client.search_runs(experiment_ids=[1])[0].to_dictionary()

    artifact_uri = latest_run["info"]["artifact_uri"]
    model = mlflow.sklearn.load_model(artifact_uri + "/model")

    assert latest_run["info"]["status"] == "FINISHED"
    assert isinstance(model, LinearRegression)  # Ensure model type is correct


# PyTorch Logger Tests
def test_pytorch_logger_save_graph_log_invalid(pytorch_logger_save_graph):
    """Test to ensure appropriate errors are raised for missing experiment_name and input_shape."""
    model = NeuralNetwork()
    datamodule = TensorDataModule(
        X=torch.rand((20, 10)), 
        y=torch.randint(0, 2, (20, ))
    )

    logged_func = pytorch_logger_save_graph.log(dummy_train_function_pytorch)

    with pytest.raises(ValueError, match=f"experiment_name must be specified as a kwarg when calling dummy_train_function_pytorch."):
        logged_func(model, datamodule)

    with pytest.raises(ValueError, match=f"input_shape must be specified as a kwarg when calling dummy_train_function_pytorch if save_graph=True."):
        logged_func(model, datamodule, experiment_name="test_pytorch")


def test_pytorch_logger_log(pytorch_logger):
    """Test logging with PytorchLogger."""
    model = NeuralNetwork()
    datamodule = TensorDataModule(
        X=torch.rand((20, 10)), 
        y=torch.randint(0, 2, (20, ))
    )

    logged_func = pytorch_logger.log(dummy_train_function_pytorch)
    model, metrics = logged_func(model, datamodule, experiment_name="test_pytorch")     

    assert metrics["accuracy"] == 0.95


def test_mlflow_run_pytorch_logger():
    """Test to verify the PyTorch model was logged correctly with Mlflow."""
    client = MlflowClient(mlflow.get_tracking_uri())
    latest_run = client.search_runs(experiment_ids=[2])[0].to_dictionary()

    artifact_uri = latest_run["info"]["artifact_uri"]
    model = mlflow.pytorch.load_model(artifact_uri + "/model")

    assert latest_run["info"]["status"] == "FINISHED"
    assert isinstance(model, NeuralNetwork)  # Ensure model type is correct


# TensorFlow Logger Tests
def test_tensorflow_logger_log(tensorflow_logger):
    """Test logging with TensorflowLogger."""
    model = create_simple_tf_model()
    x = np.random.rand(10, 10)
    y = np.random.randint(0, 2, (10, 1))

    logged_func = tensorflow_logger.log(dummy_train_function_tensorflow)
    model, metrics = logged_func(model, x, y, experiment_name='test_tensorflow')
    
    # Ensure the correct metrics were returned
    assert metrics['accuracy'] == 0.95


def test_mlflow_run_tensorflow_logger():
    """Test to verify the TensorFlow model was logged correctly with MLflow."""
    client = MlflowClient(mlflow.get_tracking_uri())
    latest_run = client.search_runs(experiment_ids=[3])[0].to_dictionary()

    artifact_uri = latest_run["info"]["artifact_uri"]
    model = mlflow.tensorflow.load_model(artifact_uri + "/model")

    assert latest_run["info"]["status"] == "FINISHED"
    assert isinstance(model, tf.keras.Model)  # Ensure model type is correct