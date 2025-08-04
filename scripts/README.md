# Scripts Directory

This directory contains utility scripts for development, testing, and deployment.

## Python Scripts

- `debug_openai.py` - Debug OpenAI/OpenRouter client initialization and configuration
- `preview_output.py` - Preview what would be posted to Slack without actually posting (dry run)

## Shell Scripts

### Deployment Scripts
- `deploy_auto.sh` - Automated deployment script
- `deploy_production.sh` - Deploy to production environment
- `redeploy.sh` - Quick redeployment script

### Utility Scripts
- `enable_apis.sh` - Enable required Google Cloud APIs
- `trigger_test.sh` - Trigger test runs
- `update_schedule.sh` - Update Cloud Scheduler configuration

## Usage

All Python scripts should be run from the project root directory:

```bash
python scripts/debug_openai.py
python scripts/preview_output.py
```

Shell scripts can be run directly:

```bash
./scripts/deploy_production.sh
```