"""Promote model to production in MLflow Model Registry."""

import argparse
import logging

from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def promote_model(model_name: str, stage: str = "Production"):
    """
    Promote latest staging model to production.
    
    Args:
        model_name: Name of registered model
        stage: Target stage
    """
    client = MlflowClient()
    
    # Get latest version in Staging
    staging_versions = client.get_latest_versions(model_name, stages=["Staging"])
    
    if not staging_versions:
        logger.error(f"No models in Staging for {model_name}")
        return
    
    latest_staging = staging_versions[0]
    version = latest_staging.version
    
    logger.info(f"Promoting model {model_name} version {version} to {stage}")
    
    # Archive current production models
    production_versions = client.get_latest_versions(model_name, stages=["Production"])
    for prod_version in production_versions:
        client.transition_model_version_stage(
            name=model_name,
            version=prod_version.version,
            stage="Archived"
        )
        logger.info(f"Archived previous production version {prod_version.version}")
    
    # Promote staging to production
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage
    )
    
    logger.info(f"Successfully promoted version {version} to {stage}")


def main():
    parser = argparse.ArgumentParser(description='Promote model to production')
    parser.add_argument('--model-name', type=str, required=True)
    parser.add_argument('--stage', type=str, default='Production')
    
    args = parser.parse_args()
    promote_model(args.model_name, args.stage)


if __name__ == '__main__':
    main()
