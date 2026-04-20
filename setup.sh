#!/bin/bash
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
poetry install
MODEL=$(python3 -c "import yaml; print(yaml.safe_load(open('retail_lakehouse/config.yaml'))['agent']['model'])")
ollama pull "$MODEL"
poetry run streamlit run retail_lakehouse/app/app.py
