#!/bin/bash
# Dev container setup script
# Runs after container is created to install project dependencies

set -e

# Run the comprehensive setup script in devcontainer mode
bash scripts/setup-environment.sh --devcontainer
