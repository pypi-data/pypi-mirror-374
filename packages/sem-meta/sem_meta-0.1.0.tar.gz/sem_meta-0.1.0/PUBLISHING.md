# Publishing sem-meta to PyPI

This guide will help you publish the sem-meta package to PyPI.

## Prerequisites

1. **Install required tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI account:**
   - Go to https://pypi.org and create an account
   - Verify your email address

3. **Create API Token (recommended):**
   - Go to https://pypi.org/manage/account/
   - Create an API token for the project
   - Save the token securely

## Building the Package

1. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

   This will create:
   - `dist/sem_meta-X.X.X.tar.gz` (source distribution)
   - `dist/sem_meta-X.X.X-py3-none-any.whl` (wheel distribution)

## Testing the Build

1. **Check the package:**
   ```bash
   twine check dist/*
   ```

2. **Test install locally:**
   ```bash
   pip install dist/sem_meta-*.whl
   ```

3. **Test the package:**
   ```python
   import sem_meta
   from sem_meta import SEMMeta, OCRPS, ConvertScale, FullSEMKeys
   print("Package imported successfully!")
   ```

## Publishing to Test PyPI (Recommended First Step)

1. **Upload to Test PyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Install from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ sem-meta
   ```

3. **Test the installation:**
   ```python
   import sem_meta
   print("Test installation successful!")
   ```

## Publishing to PyPI

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

2. **Verify on PyPI:**
   - Go to https://pypi.org/project/sem-meta/
   - Check that your package appears correctly

3. **Install from PyPI:**
   ```bash
   pip install sem-meta
   ```

## Using API Token for Authentication

Instead of username/password, you can use an API token:

1. **Create .pypirc file** in your home directory:
   ```ini
   [distutils]
   index-servers = pypi testpypi

   [pypi]
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   username = __token__
   password = pypi-your-test-api-token-here
   ```

2. **Set secure permissions:**
   ```bash
   chmod 600 ~/.pypirc
   ```

## Version Management

The package uses setuptools_scm for automatic versioning based on git tags:

1. **Create a release tag:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **The version will be automatically determined** from the git tag when building.

## Updating the Package

1. **Make your changes**
2. **Update CHANGELOG.md**
3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Update for version X.X.X"
   ```

4. **Create new tag:**
   ```bash
   git tag vX.X.X
   git push origin vX.X.X
   ```

5. **Build and upload:**
   ```bash
   rm -rf dist/ build/
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Common Issues:

1. **Import errors during build:**
   - Make sure all imports in `__init__.py` use relative imports (`.module`)
   - Ensure all dependencies are listed in `pyproject.toml`

2. **Version conflicts:**
   - Check if the version already exists on PyPI
   - Create a new git tag with incremented version

3. **Authentication errors:**
   - Verify your PyPI credentials
   - Check API token permissions
   - Ensure `.pypirc` file has correct format and permissions

4. **Build errors:**
   - Make sure you're in the project root directory
   - Check that `pyproject.toml` is properly formatted
   - Verify all source files are included in `MANIFEST.in`

### Getting Help:

- PyPI documentation: https://packaging.python.org/
- Setuptools documentation: https://setuptools.pypa.io/
- Twine documentation: https://twine.readthedocs.io/
