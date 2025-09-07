# File: src/samudra_ai/__init__.py
from .core import SamudraAI
from .data_loader import load_and_mask_dataset
from .trainer import prepare_training_data, plot_training_history
from .evaluator import evaluate_model
from .preprocess_dcpp import preprocess_dcpp

__version__ = "1.1.9"
__all__ = [
    'SamudraAI',
    'load_and_mask_dataset',
    'prepare_training_data',
    'plot_training_history',
    'evaluate_model',
    "preprocess_dcpp",
]