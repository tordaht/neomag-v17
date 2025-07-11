import pytest

def test_import_simulation_components():
    """
    A simple smoke test to ensure all major simulation components can be imported
    without raising exceptions (e.g., due to circular dependencies).
    """
    try:
        from server.simulation.agent import Agent, AgentBrain
        from server.simulation.evolution import evolve_population
        from server.simulation.world_v12 import ProductionWorld as World, Food
    except ImportError as e:
        pytest.fail(f"Failed to import simulation components: {e}")

def test_import_analysis_components():
    """
    Smoke test for the analysis components.
    """
    try:
        from server.analysis.data_exporter import ScientificDataExporter
        from server.analysis.dataset_loader import load_historical_population_data
        from server.analysis.statistical_analyzer import run_full_analysis
    except ImportError as e:
        pytest.fail(f"Failed to import analysis components: {e}")

def test_import_api_and_main_components():
    """
    Smoke test for API and main application components.
    """
    try:
        from server.main import app
        from server.celery_app import celery_app
    except ImportError as e:
        pytest.fail(f"Failed to import API/main components: {e}") 