# Testing Scripts

This directory contains automated testing scripts for Epic LLM.

## Quick Test (Recommended)

```bash
./scripts/quick-test.sh
# or
make test-quick
```

**Fast end-to-end validation** that tests:
- ✅ CLI help and commands work
- ✅ Provider listing functions
- ✅ Dependency checking works
- ✅ Status commands respond
- ✅ Invalid input handling
- ✅ Package builds successfully
- ✅ Core unit tests pass

**Duration**: ~1-2 seconds  
**Purpose**: Quick validation before commits/releases

## Comprehensive E2E Test

```bash
python scripts/test-e2e.py
# or  
make test-e2e
```

**Comprehensive end-to-end testing** with:
- 🔍 Isolated test environment
- 📊 Detailed test results and timing
- 🧪 Unit test integration
- 🏗️ Package build verification
- 📈 Progress reporting

**Duration**: ~30-60 seconds  
**Purpose**: Thorough validation for releases

## When to Use

- **Quick Test**: Before commits, during development
- **Comprehensive Test**: Before releases, CI/CD pipelines
- **Both**: To ensure Epic LLM works correctly

## Output

Both scripts provide colored output:
- 🟢 **Green**: Tests passed
- 🔴 **Red**: Tests failed  
- 🟡 **Yellow**: Partial success (expected)

## Integration

These scripts are integrated into:
- `Makefile` targets (`test-quick`, `test-e2e`)
- `make release` pipeline
- Development workflow documentation