# Release Process

This document outlines the automated release process for the LogFlux Python SDK.

## Overview

The LogFlux Python SDK uses **GitHub Releases** to trigger automated publishing to PyPI. When you create a new release on GitHub, the system automatically:

1. Yes Builds the Python package
2. Yes Validates the package integrity
3. Yes Tests installation from Test PyPI
4. Yes Publishes to Production PyPI
5. Yes Attaches build artifacts to the GitHub release

## Prerequisites

### 1. PyPI Account Setup

**Required for first-time setup only:**

```bash
# Create accounts at:
# - https://pypi.org (production)
# - https://test.pypi.org (testing)

# Enable 2FA on both accounts for security
# Generate API tokens for automation
```

### 2. GitHub Secrets Configuration

Add these secrets to your GitHub repository settings (`Settings > Secrets and variables > Actions`):

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `PYPI_API_TOKEN` | Your PyPI API token | Publishing to production PyPI |
| `TEST_PYPI_API_TOKEN` | Your Test PyPI API token | Testing publication process |

**To generate API tokens:**
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click "Add API token"
3. Set scope to "Entire account" (or specific project once published)
4. Copy the token (starts with `pypi-`)
5. Add to GitHub repository secrets

## Release Steps

### 1. Prepare the Release

**Update Version Number:**
```bash
# Update version in logflux/__init__.py
__version__ = "0.2.0"  # Example version
```

**Update CHANGELOG.md:**
```markdown
## [0.2.0] - 2024-01-15
### Added
- New feature X
- Improved performance for Y

### Fixed  
- Bug fix for Z
```

**Test Everything:**
```bash
# Run full test suite
make test

# Run integration tests
python tests/integration/run_integration_tests.py --mode=mock

# Test package build
python -m build
twine check dist/*
```

### 2. Create GitHub Release

**Via GitHub Web Interface:**

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. **Tag version**: Enter version (e.g., `v0.2.0`)
   - WARNING: **Important**: Tag must match package version (with or without 'v' prefix)
4. **Release title**: Descriptive title (e.g., "LogFlux Python SDK v0.2.0")
5. **Description**: Copy from CHANGELOG.md or write release notes
6. Check "Set as a pre-release" if this is a beta version
7. Click "Publish release"

**Via GitHub CLI:**
```bash
# Create and publish release
gh release create v0.2.0 \
  --title "LogFlux Python SDK v0.2.0" \
  --notes-file CHANGELOG.md \
  --prerelease  # Remove if stable release
```

### 3. Automated Process

Once you publish the release, GitHub Actions automatically:

#### **Phase 1: Validation**
- Yes Checks out the code
- Yes Sets up Python environment
- Yes Verifies version matches release tag
- Yes Builds the package (wheel and source distribution)
- Yes Validates package with `twine check`

#### **Phase 2: Test Publication**
- Yes Publishes to Test PyPI
- Yes Waits for package availability
- Yes Tests installation from Test PyPI
- Yes Validates import and basic functionality

#### **Phase 3: Production Publication**
- Yes Publishes to Production PyPI
- Yes Uploads build artifacts to GitHub release
- Yes Tests final installation from production PyPI

### 4. Verification

**Check Publication Success:**
```bash
# Verify package is available on PyPI
curl https://pypi.org/project/logflux/

# Test installation in fresh environment  
python -m venv test_env
source test_env/bin/activate
pip install logflux
python -c "import logflux; print(logflux.__version__)"
deactivate
```

**Monitor Release:**
- Check [GitHub Actions](../../actions) for workflow status
- Verify [PyPI project page](https://pypi.org/project/logflux/)
- Review download statistics after 24-48 hours

## Version Management

### Version Format
- **Stable releases**: `1.0.0`, `1.1.0`, `1.1.1`
- **Beta releases**: `1.0.0-beta`, `1.0.0-beta.2`
- **Alpha releases**: `1.0.0-alpha`, `1.0.0-alpha.3`

### Version Matching Requirements
The GitHub Actions workflow **requires** that:
```
Package version (logflux/__init__.py) == Git tag (without 'v' prefix)
```

**Examples of valid combinations:**
- Package: `0.2.0` → Git tag: `v0.2.0` Yes
- Package: `0.2.0` → Git tag: `0.2.0` Yes
- Package: `1.0.0-beta` → Git tag: `v1.0.0-beta` Yes

**Invalid combinations:**
- Package: `0.2.0` → Git tag: `v0.1.9` No
- Package: `0.2.0-beta` → Git tag: `v0.2.0` No

## Troubleshooting

### Release Workflow Failed

**Check the logs:**
```bash
# View GitHub Actions logs
gh run list --workflow=release.yml
gh run view [RUN_ID] --log
```

**Common issues:**

#### Version Mismatch
```
Error: Package version (0.2.0) doesn't match release tag (0.1.9)
```
**Solution**: Update package version in `logflux/__init__.py` to match git tag.

#### PyPI Authentication Failed
```
Error: 403 Forbidden from https://upload.pypi.org/
```
**Solution**: Check PyPI API tokens in GitHub secrets.

#### Package Already Exists
```
Error: File already exists
```
**Solution**: PyPI doesn't allow re-uploading same version. Increment version number.

#### Test PyPI Installation Failed
```
Error: No matching distribution found for logflux
```  
**Solution**: Wait longer for Test PyPI propagation, or check if dependencies are available.

### Manual Recovery

If automated release fails, you can publish manually:

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*

# Upload artifacts to GitHub release
gh release upload v0.2.0 dist/*
```

### Rolling Back

**If you need to yank a release:**
```bash
# Yank from PyPI (makes it unavailable for new installs)
twine yank logflux==0.2.0

# Delete GitHub release (optional)
gh release delete v0.2.0
```

## Security Considerations

### API Token Management
- Yes **Use scoped tokens**: Limit to specific project when possible
- Yes **Rotate regularly**: Update tokens every 6-12 months
- Yes **Monitor usage**: Check PyPI project history for unauthorized uploads
- Yes **Enable 2FA**: Required for PyPI publishing

### Release Validation
- Yes **Code review**: All changes should be reviewed before release
- Yes **Automated testing**: CI/CD must pass before release
- Yes **Security scanning**: Dependency vulnerabilities checked
- Yes **Package validation**: `twine check` runs automatically

## Post-Release Tasks

### Update Documentation
- Update any version-specific documentation
- Update compatibility matrices if needed
- Announce release in relevant channels

### Monitor Release
- Check download statistics after 24-48 hours
- Monitor for user feedback/issues
- Update any dependent projects

### Prepare Next Release
- Create milestone for next version
- Update project board/planning
- Begin work on next features

## Emergency Procedures

### Critical Security Issue
1. **Immediately yank** affected versions from PyPI
2. **Create hotfix** release with security patch
3. **Notify users** via GitHub Security Advisories
4. **Update documentation** with security recommendations

### Broken Release
1. **Yank broken version** from PyPI
2. **Investigate** root cause
3. **Create patch release** with fix
4. **Update CI/CD** to prevent similar issues

## Release Checklist

Use this checklist for each release:

### Pre-Release
- [ ] Version updated in `logflux/__init__.py`
- [ ] `CHANGELOG.md` updated with changes
- [ ] All tests passing (unit + integration)
- [ ] Package builds successfully (`python -m build`)
- [ ] Package validates (`twine check dist/*`)
- [ ] Security scan passed
- [ ] Code reviewed and approved

### Release
- [ ] GitHub release created with correct tag
- [ ] Release notes written
- [ ] Automated workflow completed successfully
- [ ] Package available on PyPI
- [ ] Installation tested from PyPI

### Post-Release
- [ ] Documentation updated (if needed)
- [ ] Announcement made (if significant release)
- [ ] Download statistics monitored
- [ ] Next milestone created

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Authority Guidelines](https://www.pypa.io/)