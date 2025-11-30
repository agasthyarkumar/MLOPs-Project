"""Register model in MLflow Model Registry."""

import argparse
import logging

import mlflow
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_model(model_name: str, stage: str = "Staging"):
    """
    Register latest model in MLflow Model Registry.
    
    Args:
        model_name: Name for the registered model
        stage: Initial stage (Staging, Production, Archived)
    """
    client = MlflowClient()
    
    # Get latest run
    experiment = client.get_experiment_by_name("automated-retraining")
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        logger.error("No runs found to register")
        return
    
    latest_run = runs[0]
    run_id = latest_run.info.run_id
    
    # Register model
    model_uri = f"runs:/{run_id}/model"
    
    logger.info(f"Registering model from run {run_id}")
    result = mlflow.register_model(model_uri, model_name)
    
    version = result.version
    logger.info(f"Registered model version: {version}")
    
    # Transition to stage
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage
    )
    
    logger.info(f"Transitioned model to {stage} stage")


def main():
    parser = argparse.ArgumentParser(description='Register model in MLflow')
    parser.add_argument('--model-name', type=str, required=True)
    parser.add_argument('--stage', type=str, default='Staging')
    
    args = parser.parse_args()
    register_model(args.model_name, args.stage)


if __name__ == '__main__':
    main()
