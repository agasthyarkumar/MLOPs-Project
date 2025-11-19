"""
Complete Improved Training Pipeline
Runs all improvements in sequence and compares results
"""

import logging
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('.')

from src.data.ingestion import DataIngestion
from src.data.preprocessing_improved import EnhancedDataPreprocessor
from src.models.ensemble import EnsembleModel
from src.models.train import ModelTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def compare_results(baseline_metrics, improved_metrics):
    """Compare and display improvement"""
    print_section("📊 PERFORMANCE COMPARISON")
    
    metrics_to_compare = ['rmse', 'mae', 'r2', 'mape']
    
    comparison_df = pd.DataFrame({
        'Metric': metrics_to_compare,
        'Baseline': [baseline_metrics.get(m, 0) for m in metrics_to_compare],
        'Improved': [improved_metrics.get(m, 0) for m in metrics_to_compare]
    })
    
    # Calculate improvements
    comparison_df['Change'] = comparison_df['Improved'] - comparison_df['Baseline']
    comparison_df['% Change'] = (
        (comparison_df['Change'] / comparison_df['Baseline']) * 100
    ).round(2)
    
    print(comparison_df.to_string(index=False))
    
    # Highlight key improvements
    print("\n🎯 KEY IMPROVEMENTS:")
    rmse_improvement = ((baseline_metrics['rmse'] - improved_metrics['rmse']) / 
                       baseline_metrics['rmse'] * 100)
    r2_improvement = improved_metrics['r2'] - baseline_metrics['r2']
    
    print(f"   • RMSE improved by ${baseline_metrics['rmse'] - improved_metrics['rmse']:,.2f}")
    print(f"   • RMSE reduction: {rmse_improvement:.2f}%")
    print(f"   • R² improved from {baseline_metrics['r2']:.4f} to {improved_metrics['r2']:.4f}")
    print(f"   • R² increase: {r2_improvement:.4f}")
    print(f"   • MAPE improved from {baseline_metrics['mape']:.2f}% to {improved_metrics['mape']:.2f}%")


def main():
    """Run complete improved pipeline"""
    
    print("\n" + "🚀 "*25)
    print("        RUNNING IMPROVED ML PIPELINE")
    print("🚀 "*25)
    
    # Record baseline metrics (from your training output)
    baseline_metrics = {
        'rmse': 50403.94,
        'mae': 33862.94,
        'r2': 0.8061,
        'mape': 19.31
    }
    
    try:
        # =====================================
        # PHASE 1: DATA LOADING & PREPROCESSING
        # =====================================
        print_section("📥 PHASE 1: DATA INGESTION")
        ingestion = DataIngestion()
        df = ingestion.ingest()
        logger.info(f"✓ Loaded {len(df):,} samples with {len(df.columns)} features")
        
        print_section("🔧 PHASE 2: ENHANCED PREPROCESSING")
        logger.info("Using enhanced preprocessing with advanced feature engineering...")
        
        preprocessor = EnhancedDataPreprocessor()
        X_train, X_test, y_train, y_test = preprocessor.preprocess(df)
        preprocessor.save_preprocessor("models/preprocessor_enhanced.pkl")
        
        logger.info(f"✓ Created {X_train.shape[1]} features (including engineered)")
        logger.info(f"✓ Train set: {X_train.shape[0]:,} samples")
        logger.info(f"✓ Test set: {X_test.shape[0]:,} samples")
        
        # =====================================
        # PHASE 2: MODEL TRAINING
        # =====================================
        
        # Option A: Single Improved Model
        print_section("🤖 PHASE 3A: TRAINING IMPROVED SINGLE MODEL")
        logger.info("Training with regularized hyperparameters...")
        
        trainer = ModelTrainer(
            config_path="config/config.yaml",
            model_config_path="config/model_config_improved.yaml"
        )
        single_model = trainer.train(X_train, X_test, y_train, y_test)
        
        # Get predictions for single model
        y_test_pred_single = single_model.predict(X_test)
        single_metrics = {
            'rmse': np.sqrt(np.mean((y_test - y_test_pred_single)**2)),
            'mae': np.mean(np.abs(y_test - y_test_pred_single)),
            'r2': 1 - (np.sum((y_test - y_test_pred_single)**2) / 
                      np.sum((y_test - np.mean(y_test))**2)),
            'mape': np.mean(np.abs((y_test - y_test_pred_single) / y_test)) * 100
        }
        
        logger.info(f"✓ Single Model Test RMSE: ${single_metrics['rmse']:,.2f}")
        logger.info(f"✓ Single Model Test R²: {single_metrics['r2']:.4f}")
        
        # Option B: Ensemble Models
        print_section("🤖 PHASE 3B: TRAINING ENSEMBLE MODELS")
        
        ensemble = EnsembleModel(
            config_path="config/config.yaml",
            model_config_path="config/model_config_improved.yaml"
        )
        
        # Train Voting Ensemble
        logger.info("\n🗳️  Training Voting Ensemble...")
        voting_model = ensemble.train(
            X_train, X_test, y_train, y_test, 
            ensemble_type='voting'
        )
        
        # Get predictions for voting ensemble
        y_test_pred_voting = voting_model.predict(X_test)
        voting_metrics = {
            'rmse': np.sqrt(np.mean((y_test - y_test_pred_voting)**2)),
            'mae': np.mean(np.abs(y_test - y_test_pred_voting)),
            'r2': 1 - (np.sum((y_test - y_test_pred_voting)**2) / 
                      np.sum((y_test - np.mean(y_test))**2)),
            'mape': np.mean(np.abs((y_test - y_test_pred_voting) / y_test)) * 100
        }
        
        # Train Stacking Ensemble
        logger.info("\n📚 Training Stacking Ensemble...")
        stacking_model = ensemble.train(
            X_train, X_test, y_train, y_test, 
            ensemble_type='stacking'
        )
        
        # Get predictions for stacking ensemble
        y_test_pred_stacking = stacking_model.predict(X_test)
        stacking_metrics = {
            'rmse': np.sqrt(np.mean((y_test - y_test_pred_stacking)**2)),
            'mae': np.mean(np.abs(y_test - y_test_pred_stacking)),
            'r2': 1 - (np.sum((y_test - y_test_pred_stacking)**2) / 
                      np.sum((y_test - np.mean(y_test))**2)),
            'mape': np.mean(np.abs((y_test - y_test_pred_stacking) / y_test)) * 100
        }
        
        # =====================================
        # PHASE 4: RESULTS COMPARISON
        # =====================================
        print_section("📊 PHASE 4: COMPARING ALL MODELS")
        
        results_df = pd.DataFrame({
            'Model': ['Baseline (Original)', 'Improved Single', 'Voting Ensemble', 'Stacking Ensemble'],
            'RMSE': [
                baseline_metrics['rmse'],
                single_metrics['rmse'],
                voting_metrics['rmse'],
                stacking_metrics['rmse']
            ],
            'MAE': [
                baseline_metrics['mae'],
                single_metrics['mae'],
                voting_metrics['mae'],
                stacking_metrics['mae']
            ],
            'R²': [
                baseline_metrics['r2'],
                single_metrics['r2'],
                voting_metrics['r2'],
                stacking_metrics['r2']
            ],
            'MAPE (%)': [
                baseline_metrics['mape'],
                single_metrics['mape'],
                voting_metrics['mape'],
                stacking_metrics['mape']
            ]
        })
        
        print("\n" + results_df.to_string(index=False))
        
        # Find best model
        best_idx = results_df['RMSE'].idxmin()
        best_model_name = results_df.loc[best_idx, 'Model']
        best_rmse = results_df.loc[best_idx, 'RMSE']
        best_r2 = results_df.loc[best_idx, 'R²']
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   • Test RMSE: ${best_rmse:,.2f}")
        print(f"   • Test R²: {best_r2:.4f}")
        print(f"   • Improvement: ${baseline_metrics['rmse'] - best_rmse:,.2f} ({((baseline_metrics['rmse'] - best_rmse) / baseline_metrics['rmse'] * 100):.2f}%)")
        
        # =====================================
        # PHASE 5: SAVE BEST MODEL
        # =====================================
        print_section("💾 PHASE 5: SAVING BEST MODEL")
        
        if best_model_name == 'Voting Ensemble':
            best_model = voting_model
        elif best_model_name == 'Stacking Ensemble':
            best_model = stacking_model
        else:
            best_model = single_model
        
        import joblib
        import os
        
        os.makedirs('models', exist_ok=True)
        
        # Save as production model
        joblib.dump(best_model, 'models/production_model.pkl')
        logger.info("✓ Best model saved as 'models/production_model.pkl'")
        
        # Save model metadata
        metadata = {
            'model_name': best_model_name,
            'test_rmse': float(best_rmse),
            'test_r2': float(best_r2),
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'features': X_train.columns.tolist(),
            'n_features': X_train.shape[1]
        }
        
        with open('models/production_model_metadata.yaml', 'w') as f:
            yaml.dump(metadata, f)
        
        logger.info("✓ Model metadata saved")
        
        # =====================================
        # FINAL SUMMARY
        # =====================================
        print_section("✅ PIPELINE COMPLETE")
        
        print("📦 Generated Artifacts:")
        print("   • models/production_model.pkl (Best model)")
        print("   • models/preprocessor_enhanced.pkl (Preprocessor)")
        print("   • models/production_model_metadata.yaml (Metadata)")
        print("   • models/ensemble_voting_model.pkl")
        print("   • models/ensemble_stacking_model.pkl")
        print(f"   • models/{trainer.model_type}_model.pkl")
        
        print("\n📈 Next Steps:")
        print("   1. Run 'make mlflow-ui' to view all experiments")
        print("   2. Update API to use production_model.pkl")
        print("   3. Run 'make serve' to start the API")
        print("   4. Test predictions with improved model")
        print("   5. (Optional) Run hyperparameter tuning for even better results")
        
        print("\n" + "🎉 "*25)
        print("        IMPROVEMENT PIPELINE SUCCESS!")
        print("🎉 "*25 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
