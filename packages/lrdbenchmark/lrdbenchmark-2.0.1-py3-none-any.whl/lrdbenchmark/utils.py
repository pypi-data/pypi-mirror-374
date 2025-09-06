"""
Utility functions for LRDBenchmark package.
"""

import os
import pkg_resources
from pathlib import Path
from typing import Optional


def get_package_data_path(relative_path: str) -> str:
    """
    Get the absolute path to a data file within the package.
    
    This function works both in development and when the package is installed from PyPI.
    
    Parameters
    ----------
    relative_path : str
        Relative path to the data file within the package
        
    Returns
    -------
    str
        Absolute path to the data file
        
    Examples
    --------
    >>> model_path = get_package_data_path("models/svr_estimator.joblib")
    >>> config_path = get_package_data_path("models/neural_network_config.json")
    """
    try:
        # Try to get the path from the installed package
        return pkg_resources.resource_filename('lrdbenchmark', relative_path)
    except (pkg_resources.DistributionNotFound, pkg_resources.ExtractionError):
        # Fallback to relative path (for development)
        package_dir = Path(__file__).parent.parent
        return str(package_dir / relative_path)


def get_pretrained_model_path(model_name: str, model_type: str = "joblib") -> Optional[str]:
    """
    Get the path to a pretrained model file.
    
    Parameters
    ----------
    model_name : str
        Name of the model (e.g., 'svr_estimator', 'random_forest_estimator')
    model_type : str
        Type of model file ('joblib' for ML models, 'pth' for neural networks)
        
    Returns
    -------
    str or None
        Path to the model file if it exists, None otherwise
    """
    if model_type == "joblib":
        # Try models/ directory first, then final_results/saved_models/
        for base_path in ["models", "final_results/saved_models"]:
            model_path = get_package_data_path(f"{base_path}/{model_name}.joblib")
            if os.path.exists(model_path):
                return model_path
    elif model_type == "pth":
        model_path = get_package_data_path(f"models/{model_name}.pth")
        if os.path.exists(model_path):
            return model_path
    
    return None


def get_neural_network_model_path(model_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Get the paths to a neural network model and its config file.
    
    Parameters
    ----------
    model_name : str
        Name of the neural network model
        
    Returns
    -------
    tuple
        (model_path, config_path) if both exist, (None, None) otherwise
    """
    model_path = get_package_data_path(f"models/{model_name}_neural_network.pth")
    config_path = get_package_data_path(f"models/{model_name}_neural_network_config.json")
    
    if os.path.exists(model_path) and os.path.exists(config_path):
        return model_path, config_path
    
    return None, None
