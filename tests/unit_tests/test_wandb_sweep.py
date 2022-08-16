"""Sweep tests."""
from typing import Any, Dict, List

import pytest
import wandb

# Sweep configs used for testing
SWEEP_CONFIG_GRID: Dict[str, Any] = {
    "name": "mock-sweep-grid",
    "method": "grid",
    "parameters": {"param1": {"values": [1, 2, 3]}},
}
SWEEP_CONFIG_GRID_HYPERBAND: Dict[str, Any] = {
    "name": "mock-sweep-grid-hyperband",
    "method": "grid",
    "early_terminate": {
        "type": "hyperband",
        "max_iter": 27,
        "s": 2,
        "eta": 3,
    },
    "metric": {"name": "metric1", "goal": "maximize"},
    "parameters": {"param1": {"values": [1, 2, 3]}},
}
SWEEP_CONFIG_GRID_NESTED: Dict[str, Any] = {
    "name": "mock-sweep-grid",
    "method": "grid",
    "parameters": {"param1": {"parameters": {"param2": {"values": [1, 2, 3]}}}},
}
SWEEP_CONFIG_BAYES: Dict[str, Any] = {
    "name": "mock-sweep-bayes",
    "method": "bayes",
    "metric": {"name": "metric1", "goal": "maximize"},
    "parameters": {"param1": {"values": [1, 2, 3]}},
}
SWEEP_CONFIG_RANDOM: Dict[str, Any] = {
    "name": "mock-sweep-random",
    "method": "random",
    "parameters": {"param1": {"values": [1, 2, 3]}},
}

# List of all valid base configurations
VALID_SWEEP_CONFIGS: List[Dict[str, Any]] = [
    SWEEP_CONFIG_GRID,
    SWEEP_CONFIG_GRID_HYPERBAND,
    SWEEP_CONFIG_GRID_NESTED,
    SWEEP_CONFIG_BAYES,
    SWEEP_CONFIG_RANDOM,
]


@pytest.mark.parametrize("sweep_config", VALID_SWEEP_CONFIGS)
def test_sweep_create(user, relay_server, sweep_config):
    with relay_server() as relay:
        sweep_id = wandb.sweep(sweep_config, entity=user)
    assert sweep_id in relay.context.entries


@pytest.mark.parametrize("sweep_config", VALID_SWEEP_CONFIGS)
def test_sweep_entity_project_callable(user, relay_server, sweep_config):
    def sweep_callable():
        return sweep_config

    with relay_server() as relay:
        sweep_id = wandb.sweep(sweep_callable, project="test", entity=user)
    sweep_response = relay.context.entries[sweep_id]
    assert sweep_response["project"]["entity"]["name"] == user
    assert sweep_response["project"]["name"] == "test"
    assert sweep_response["name"] == sweep_id


def test_minmax_validation():
    api = wandb.apis.InternalApi()
    sweep_config = {
        "name": "My Sweep",
        "method": "random",
        "parameters": {"parameter1": {"min": 0, "max": 1}},
    }

    filled = api.api._validate_config_and_fill_distribution(sweep_config)
    assert "distribution" in filled["parameters"]["parameter1"]
    assert "int_uniform" == filled["parameters"]["parameter1"]["distribution"]

    sweep_config = {
        "name": "My Sweep",
        "method": "random",
        "parameters": {"parameter1": {"min": 0.0, "max": 1.0}},
    }

    filled = api.api._validate_config_and_fill_distribution(sweep_config)
    assert "distribution" in filled["parameters"]["parameter1"]
    assert "uniform" == filled["parameters"]["parameter1"]["distribution"]

    sweep_config = {
        "name": "My Sweep",
        "method": "random",
        "parameters": {"parameter1": {"min": 0.0, "max": 1}},
    }

    with pytest.raises(ValueError):
        api.api._validate_config_and_fill_distribution(sweep_config)