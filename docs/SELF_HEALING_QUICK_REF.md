# 🔄 Self-Healing Quick Reference

## At-a-Glance: Self-Healing vs Traditional Pipeline

| Scenario | Traditional Pipeline | Self-Healing Pipeline |
|----------|---------------------|----------------------|
| **Data has missing values** | ❌ Tests fail, pipeline stops | ✅ Auto-fixes, continues |
| **Model accuracy drops to 65%** | ⚠️ Deploys anyway | ✅ Auto-rolls back |
| **Data drift detected** | 📧 Email alert sent | ✅ Auto-retrains model |
| **API service crashes** | 🛑 Downtime, manual restart | ✅ Auto-recovers in seconds |
| **Outliers in data** | ⚠️ Degrades model quality | ✅ Auto-caps outliers |

---

## 🚀 Quick Start Commands

### Test Self-Healing Locally

```bash
# 1. Test data quality auto-fix
python scripts/auto_fix_data_issues.py --data-path data/raw/housing.csv

# 2. Test model rollback
python scripts/rollback_model.py --current-metric 0.65 --threshold 0.70

# 3. Test auto-retraining
python scripts/auto_retrain_on_drift.py --drift-detected --drift-score 0.85

# 4. Test service recovery
python scripts/auto_recover_service.py --method process --service-url http://localhost:8000
```

---

## 📊 Self-Healing Scripts Overview

| Script | Purpose | When It Runs | Key Parameters |
|--------|---------|--------------|----------------|
| `auto_fix_data_issues.py` | Fixes data quality issues | Before tests, on validation failure | `--data-path` |
| `rollback_model.py` | Reverts to previous model | When accuracy < threshold | `--threshold`, `--current-metric` |
| `auto_retrain_on_drift.py` | Retrains on drift | When drift detected | `--drift-score`, `--drift-detected` |
| `auto_recover_service.py` | Recovers failed services | When health check fails | `--method`, `--service-url` |

---

## 🔧 Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `config/self_healing_config.json` | Main self-healing config | All thresholds, enable/disable flags |
| `config/monitoring_config.json` | Monitoring settings | Drift thresholds, cooldown periods |
| `.github/triggers/retraining_log.json` | Retraining history | Last retrain time, cooldown check |

---

## 📝 Log Files (Audit Trail)

| Log File | Contains | Use For |
|----------|----------|---------|
| `monitoring/recovery_log.json` | Service recovery events | Track downtime incidents |
| `models/rollback_log.json` | Model rollback history | Version control, debugging |
| `.github/triggers/retraining_log.json` | Auto-retrain events | Drift response tracking |

---

## ⚙️ Workflow Integration Points

### In `.github/workflows/main.yml`:

```yaml
# Stage 1: CI with auto-fix
Run tests → Fail → Auto-fix data → Retry tests

# Stage 3: Model validation with rollback
Validate model → Performance < 70% → Auto-rollback

# Stage 5: Monitoring with auto-retrain
Check drift → Drift detected → Auto-retrain

# Stage 6: API test with recovery
Health check → Fails → Auto-recover → Retry
```

---

## 🎯 Key Thresholds (Configurable)

| Metric | Default | Configurable In |
|--------|---------|-----------------|
| Min Model Accuracy | 70% | `self_healing_config.json` → `model_validation.min_accuracy_threshold` |
| Drift Threshold | 0.5 | `self_healing_config.json` → `drift_detection.drift_threshold` |
| Retraining Cooldown | 24 hours | `self_healing_config.json` → `drift_detection.retraining_cooldown_hours` |
| Max Recovery Attempts | 3 | `self_healing_config.json` → `service_recovery.max_recovery_attempts` |
| Outlier IQR Multiplier | 3.0 | `self_healing_config.json` → `data_quality.outlier_threshold_iqr` |

---

## 🔍 Monitoring Self-Healing Actions

### View Recent Auto-Fixes
```bash
cat monitoring/recovery_log.json | jq '.[-5:]'
```

### View Rollback History
```bash
cat models/rollback_log.json | jq '.'
```

### View Retraining Log
```bash
cat .github/triggers/retraining_log.json | jq '.'
```

### Check Last Retraining Time
```bash
cat .github/triggers/retraining_log.json | jq '.last_retrain_time'
```

---

## 🛡️ Safety Features

| Feature | Purpose | Prevents |
|---------|---------|----------|
| **Cooldown Periods** | 24h between retrains | Excessive resource usage |
| **Max Retries** | 3 attempts max | Infinite loops |
| **Auto Backup** | Before any changes | Data loss |
| **Rollback Capability** | Can undo changes | Permanent mistakes |
| **Audit Logging** | Track all actions | Unknown state |

---

## 📊 Success Metrics

Track these to measure self-healing effectiveness:

1. **Auto-fix Success Rate**: `(fixes_successful / total_issues) * 100`
2. **Mean Time to Recovery (MTTR)**: Time from failure to fix
3. **Rollback Frequency**: Number per week/month
4. **Drift Response Time**: Detection to retraining completion
5. **Service Uptime**: % time service is healthy

---

## 🚨 When to Intervene Manually

Self-healing handles most issues, but investigate if:

- ❌ Same issue occurs > 3 times in 24 hours
- ❌ Rollback happens repeatedly (indicates systemic issue)
- ❌ Drift detected constantly (data pipeline issue)
- ❌ Service recovery fails all attempts
- ❌ Auto-fix doesn't resolve data quality issues

---

## 📚 Learn More

- **Full Documentation**: [docs/SELF_HEALING.md](SELF_HEALING.md)
- **MLflow Tracking**: http://localhost:5000
- **API Health Check**: http://localhost:8000/health
- **GitHub Actions**: `.github/workflows/main.yml`

---

## 💡 Pro Tips

1. **Test locally first**: Run self-healing scripts manually before relying on automation
2. **Monitor logs**: Check audit logs weekly for patterns
3. **Adjust thresholds**: Fine-tune based on your model's characteristics
4. **Use cooldown wisely**: Balance responsiveness vs. resource usage
5. **Keep backups**: Self-healing creates them, but verify they exist

---

**Status**: ✅ All self-healing features active and tested
