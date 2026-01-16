# Installation Troubleshooting Guide

## Python 3.13 Issues

### Problem: `ModuleNotFoundError: No module named 'distutils'`

**Solution**: Python 3.13 removed `distutils`. Install setuptools first:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Problem: PyTorch not available for Python 3.13

**Issue**: `sentence-transformers` requires PyTorch, but PyTorch doesn't have Python 3.13 wheels yet.

**Solution**: Use Python 3.11 or 3.12 instead:
```bash
# Using pyenv (recommended)
pyenv install 3.12.0
pyenv local 3.12.0

# Or using conda
conda create -n policy-intel python=3.12
conda activate policy-intel
```

## Common Installation Issues

### Issue: ChromaDB build errors

**Solution**: Ensure you have build tools installed:
```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential

# Then retry installation
pip install -r requirements.txt
```

### Issue: NumPy compatibility errors

**Solution**: NumPy 1.26+ is required for Python 3.13. For Python 3.11/3.12, use:
```bash
pip install "numpy>=1.24.0,<2.0.0"
```

### Issue: Memory errors during model download

**Solution**: The embedding model (`all-MiniLM-L6-v2`) will be downloaded on first use (~80MB). Ensure you have:
- At least 200MB free disk space
- Stable internet connection
- Sufficient RAM (2GB+ recommended)

## Recommended Setup (Python 3.12)

```bash
# 1. Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# 2. Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import fastapi, sentence_transformers, chromadb; print('✓ All dependencies installed')"
```

## Alternative: Using Conda

```bash
# Create environment with Python 3.12
conda create -n policy-intel python=3.12
conda activate policy-intel

# Install dependencies
pip install -r requirements.txt
```

## Verifying Installation

After installation, verify everything works:

```bash
# Check Python version (should be 3.11 or 3.12)
python --version

# Test imports
python -c "
import fastapi
import sentence_transformers
import chromadb
import pydantic
print('✓ All core dependencies imported successfully')
"

# Run health check (after starting server)
curl http://localhost:8000/health
```
