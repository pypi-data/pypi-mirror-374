# Publishing to PyPI

This document describes how to publish the `bricks-and-graphs` package to PyPI using GitHub Actions.

## Overview

We use GitHub Actions for automated publishing to PyPI with the following features:

- **API Token Authentication**: Uses PyPI API tokens stored as GitHub secrets
- **Automatic Release Publishing**: Triggered when you create a GitHub release
- **Manual Publishing**: Can be triggered manually for testing

## Prerequisites

### 1. PyPI Account Setup

1. Create an account on [PyPI](https://pypi.org/account/register/)
2. Verify your email address

### 2. PyPI API Token Setup

**Get PyPI API Token**:
- Go to https://pypi.org/manage/account/token/
- Click "Add API token"
- Name: `bricks-and-graphs-github-actions`
- Scope: "Entire account" (or specific to your project once it exists)
- Copy the token (starts with `pypi-`)

### 3. GitHub Secrets Setup

Add the API token as a GitHub repository secret:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add this secret:
   - **Name**: `PYPI_API_TOKEN`, **Value**: Your PyPI API token

## Publishing Process

### 1. Automatic Publishing (Recommended)

The easiest way to publish is through GitHub releases:

1. **Update Version**: Update the version in `pyproject.toml`
   ```toml
   [project]
   version = "0.2.0"  # Update this
   ```

2. **Commit and Push**:
   ```bash
   git add pyproject.toml
   git commit -m "🔖 Bump version to 0.2.0"
   git push
   ```

3. **Create GitHub Release**:
   - Go to your repository → Releases → Create a new release
   - Tag: `v0.2.0` (must match the version in pyproject.toml)
   - Title: `Release v0.2.0`
   - Description: Add release notes describing changes
   - Click "Publish release"

4. **Automatic Workflow**: The publish workflow will automatically:
   - Run all tests
   - Run linting
   - Build the package
   - Publish to PyPI
   - Attach build artifacts to the release

### 2. Manual Publishing

For testing or emergency releases:

- Go to Actions → Publish to PyPI → Run workflow
- Click "Run workflow"

### 3. Testing Package Installation

After publishing, test the installation:

```bash
# Install from PyPI
pip install bricks-and-graphs

# Test basic functionality
python -c "import bag; print('✅ Package installed successfully')"
```

## Version Management

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Versions

For testing, you can use pre-release versions:

- **Alpha**: `1.0.0a1`, `1.0.0a2`, etc.
- **Beta**: `1.0.0b1`, `1.0.0b2`, etc.
- **Release Candidate**: `1.0.0rc1`, `1.0.0rc2`, etc.

Example workflow for pre-release:
1. Update version to `0.2.0a1` in `pyproject.toml`
2. Create release with tag `v0.2.0a1`
3. Test installation and functionality
4. Update to `0.2.0` when ready for production

## Troubleshooting

### Common Issues

1. **"File already exists" error**:
   - You're trying to upload a version that already exists
   - Update the version number in `pyproject.toml`

2. **Authentication failed**:
   - Check that your API token is correctly set in GitHub secrets
   - Verify the secret name matches exactly (`PYPI_API_TOKEN`)
   - Make sure the API token hasn't expired

3. **Build failures**:
   - Check that all tests pass locally
   - Ensure pre-commit hooks pass
   - Verify the package builds locally: `uv build`

4. **Import errors after installation**:
   - Check that all dependencies are properly declared
   - Test the package in a clean environment

### Local Testing

Before publishing, always test locally:

```bash
# Build the package
uv build

# Check the package
uv run twine check dist/*

# Test in a clean environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/*.whl
python -c "import bag; print('Success!')"
```

## Security Notes

- **Never commit API keys** to the repository
- **Store API token as GitHub secrets** only
- **Use scoped API token** when possible (project-specific rather than account-wide)
- **Only publish from the main branch** for production releases
- **Review all changes** before creating releases
- **Rotate API token** periodically for security

## Package Information

- **Package Name**: `bricks-and-graphs`
- **PyPI URL**: https://pypi.org/project/bricks-and-graphs/
- **Test PyPI URL**: https://test.pypi.org/project/bricks-and-graphs/
- **Documentation**: https://github.com/wheredatalives/bricks-and-graphs
- **Source Code**: https://github.com/wheredatalives/bricks-and-graphs

## Support

If you encounter issues with publishing:

1. Check the GitHub Actions logs for detailed error messages
2. Review this documentation for common solutions
3. Create an issue in the repository for help
4. Contact the maintainers if needed
