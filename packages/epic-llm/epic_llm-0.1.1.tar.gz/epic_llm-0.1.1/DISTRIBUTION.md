# Epic LLM Distribution Guide

## uvx Distribution (Recommended)

Epic LLM is designed for distribution via `uvx`, which provides the best user experience.

### Benefits of uvx Distribution

✅ **No Installation Required**: Users run Epic LLM without installing it  
✅ **Automatic Dependency Management**: uvx handles virtual environments automatically  
✅ **Always Latest Version**: Users can easily get the latest version  
✅ **No System Pollution**: Doesn't clutter user's Python environment  
✅ **Cross-Platform**: Works identically on Linux, macOS, and Windows  

### User Experience

Users can run Epic LLM immediately:

```bash
# Run Epic LLM without any installation
uvx epic-llm --help
uvx epic-llm check
uvx epic-llm start

# Always get the latest version
uvx epic-llm@latest check --install
```

## Release Process

### 1. Pre-Release Testing

```bash
# Run full test suite
make check-all

# Test uvx distribution
make test-uvx
```

### 2. Version Management

Update version in `pyproject.toml`:
```toml
version = "0.2.0"
```

### 3. Build and Test

```bash
# Build package
uv build

# Test local uvx distribution
uvx --from ./dist/epic_llm-*.whl epic-llm --help
```

### 4. GitHub Release

```bash
# Create and push tag
git tag v0.2.0
git push origin v0.2.0
```

This triggers GitHub Actions which:
- Runs tests
- Builds the package
- Creates a GitHub release with artifacts
- Optionally publishes to PyPI

### 5. Verify Release

After GitHub Actions completes:

```bash
# Test from GitHub release
uvx epic-llm --help

# Test specific version
uvx epic-llm@0.2.0 --help
```

## Distribution Options

### Option 1: Direct uvx (Simplest for users)
```bash
uvx epic-llm --help
```
Users get the latest version from PyPI automatically.

### Option 2: Local wheel file
```bash
# Download .whl from GitHub releases
uvx --from ./epic_llm-0.2.0-py3-none-any.whl epic-llm --help
```

### Option 3: Git repository
```bash
uvx --from git+https://github.com/user/epic-llm.git epic-llm --help
```

### Option 4: Traditional installation
```bash
# Install with uv
uv tool install epic-llm

# Install with pip  
pip install epic-llm
```

## Publishing to PyPI

To enable `uvx epic-llm` (without specifying source), publish to PyPI:

### Manual Publishing
```bash
# Build package
uv build

# Publish to PyPI (requires account and API token)
uv publish
```

### Automated Publishing
Uncomment the `publish-pypi` job in `.github/workflows/release.yml` and add `PYPI_API_TOKEN` secret.

## User Installation Instructions

### For End Users (Recommended)

**Instant usage (no installation):**
```bash
uvx epic-llm --help
uvx epic-llm check
uvx epic-llm start
```

**Install for regular use:**
```bash
uv tool install epic-llm
epic-llm --help
```

### For Developers

**Development setup:**
```bash
git clone https://github.com/user/epic-llm.git
cd epic-llm
uv sync --dev
uv run epic-llm --help
```

## Troubleshooting

### uvx not found
Users need to install uv first:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then use uvx
uvx epic-llm --help
```

### Package not found
If `uvx epic-llm` fails, the package isn't on PyPI. Users can use:
```bash
# From GitHub releases
uvx --from https://github.com/user/epic-llm/releases/download/v0.2.0/epic_llm-0.2.0-py3-none-any.whl epic-llm --help
```

### Version conflicts
uvx creates isolated environments, so this shouldn't happen. If it does:
```bash
# Clear uvx cache
uvx --help  # Check uvx documentation for cache clearing
```

## Marketing Benefits

### For Users
- **Zero friction**: Run without installation
- **Always up-to-date**: Latest version automatically
- **Safe**: No system pollution or conflicts
- **Professional**: Real package management, not scripts

### For Epic LLM
- **Lower support burden**: No installation issues
- **Higher adoption**: Easier to try
- **Better updates**: Users get fixes automatically
- **Cross-platform**: Same experience everywhere

## Comparison with Binary Distribution

| Aspect | uvx | Binary |
|--------|-----|--------|
| **User experience** | Excellent | Good |
| **File size** | ~50KB package | ~50-100MB binary |
| **Updates** | Automatic | Manual download |
| **Dependencies** | Auto-managed | Self-contained |
| **Build complexity** | Simple | Complex |
| **Cross-platform** | Perfect | Platform-specific builds |
| **Legal isolation** | Perfect | Good |

## Conclusion

uvx distribution provides the best experience for Epic LLM:
- Users get instant access without installation friction
- Automatic dependency and environment management
- Simple release process for maintainers
- Perfect legal isolation (no bundled third-party tools)
- Professional package management ecosystem