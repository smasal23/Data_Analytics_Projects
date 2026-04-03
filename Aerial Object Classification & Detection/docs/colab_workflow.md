# Colab Workflow

1. Open notebook in Google Colab
2. Mount Google Drive
3. Define `PROJECT_ROOT` inside Drive
4. Create persistent project directories
5. Load YAML configs
6. Run dataset audit
7. Save figures and report inside Drive-backed folders

Important rule:
All critical outputs must be saved inside Google Drive, not only in temporary Colab storage.