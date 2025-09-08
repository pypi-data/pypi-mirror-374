# PyPI Deployment Guide for forgeNN

This guide walks you through deploying the forgeNN package to PyPI.

## Prerequisites

### 1. PyPI Account Setup
1. Create accounts on both:
   - **TestPyPI**: https://test.pypi.org/account/register/
   - **PyPI**: https://pypi.org/account/register/

2. Enable 2FA (Two-Factor Authentication) on both accounts

3. Create API tokens:
   - Go to Account Settings → API tokens
   - Create a token for "Entire account" 
   - Save the token securely (starts with `pypi-`)

### 2. Configure Authentication

#### Option A: Using .pypirc file (Recommended)
Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

#### Option B: Environment Variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

## Quick Deployment

### Automated Deployment (Recommended)
```bash
# 1. Build the package
python build_package.py

# 2. Upload to PyPI
python upload_package.py
```

### Manual Deployment
```bash
# 1. Install build tools
pip install build twine

# 2. Clean and build
rm -rf dist/ build/ *.egg-info/
python -m build

# 3. Check package
python -m twine check dist/*

# 4. Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# 5. Test installation
pip install --index-url https://test.pypi.org/simple/ forgeNN

# 6. Upload to PyPI
python -m twine upload dist/*
```

## Step-by-Step Process

### 1. Pre-deployment Checklist

- [ ] All tests pass
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] LICENSE file exists
- [ ] All required files in MANIFEST.in

### 2. Build Package
```bash
python build_package.py
```

This script will:
- ✅ Check dependencies
- ✅ Validate package configuration  
- ✅ Clean build artifacts
- ✅ Build wheel and source distribution
- ✅ Validate built packages

### 3. Test Upload
```bash
# Upload to TestPyPI
python upload_package.py
# Choose option 1 (TestPyPI)
```

### 4. Test Installation
```bash
# Create fresh environment
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ forgeNN

# Test import
python -c "import forgeNN; print(f'forgeNN v{forgeNN.__version__} works!')"

# Run example
python -c "
from forgeNN.tensor import Tensor
from forgeNN.vectorized import VectorizedMLP
model = VectorizedMLP(10, [32, 16], 2)
print('✅ forgeNN working correctly!')
"
```

### 5. Production Upload
```bash
python upload_package.py
# Choose option 2 (PyPI) or option 3 (Both)
```

## Version Management

### Semantic Versioning
forgeNN follows [SemVer](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Updating Version
Update version in `pyproject.toml`:
```toml
[project]
version = "1.0.1"  # Update this
```

## Troubleshooting

### Common Issues

#### 1. "File already exists" error
```bash
# Solution: Update version number in pyproject.toml
# PyPI doesn't allow re-uploading same version
```

#### 2. Authentication errors
```bash
# Check your API token
# Ensure .pypirc format is correct
# Try with environment variables
```

#### 3. Package validation fails
```bash
# Run: python -m twine check dist/*
# Fix issues reported by twine
# Common: Missing README, invalid metadata
```

#### 4. Import errors after installation
```bash
# Check MANIFEST.in includes all necessary files
# Verify package structure with: tar -tf dist/*.tar.gz
```

### Getting Help

1. **Package Issues**: Check `python -m twine check dist/*`
2. **Upload Issues**: Check PyPI status page
3. **Installation Issues**: Try in fresh virtual environment
4. **API Issues**: Verify API token permissions

## Post-Deployment

### 1. Verify Upload
- Check package page: https://pypi.org/project/forgeNN/
- Test installation: `pip install forgeNN`
- Verify import works correctly

### 2. Update Documentation
- Update README with installation instructions
- Tag release in git: `git tag v1.0.0`
- Create GitHub release with changelog

### 3. Announce Release
- Update project documentation
- Notify users/community
- Share on relevant platforms

## Security Best Practices

1. **API Tokens**: Never commit tokens to git
2. **2FA**: Always enable on PyPI accounts  
3. **Scoped Tokens**: Use project-specific tokens when possible
4. **Regular Rotation**: Rotate API tokens periodically

## Automation Options

### GitHub Actions
Consider setting up automated publishing with GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish package
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## Quick Reference

```bash
# Complete deployment workflow
python build_package.py           # Build package
python upload_package.py          # Upload (TestPyPI → PyPI)
pip install forgeNN              # Test installation
python -c "import forgeNN"       # Verify import
```

🎉 **Your forgeNN package is now ready for the world!**
