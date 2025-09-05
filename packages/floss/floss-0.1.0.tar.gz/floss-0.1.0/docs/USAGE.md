# floss Usage Guide

This guide provides comprehensive examples and best practices for using floss in various scenarios.

## Table of Contents

- [Installation Guide](#installation-guide)
- [Quick Start Examples](#quick-start-examples)
- [CLI Usage Patterns](#cli-usage-patterns)
- [Configuration Examples](#configuration-examples)
- [Dashboard Usage](#dashboard-usage)
- [Integration Scenarios](#integration-scenarios)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Installation Guide

### Basic Installation

For basic fault localization functionality:

```bash
pip install floss
```

### With Dashboard Support

For full functionality including the web dashboard:

```bash
pip install "floss[ui]"
```

### Development Installation

For contributing to floss:

```bash
git clone https://github.com/example/floss.git
cd floss
pip install -e ".[dev,ui]"
```

### Verify Installation

```bash
floss --help
```

## Learning with Examples

floss includes curated examples that demonstrate fault localization on real-world projects. These examples are the best way to learn floss's capabilities.

### Example Categories

#### Educational Examples
Perfect for learning floss basics:
```bash
# Simple synthetic bug - great for beginners
cd examples/dummy-example
floss run --source-dir src --test-dir tests
floss ui --report report.json
```

#### Real Framework Bugs
Actual bugs from popular Python frameworks:
```bash
# FastAPI dependency injection bug
cd examples/fastapi
./setup.sh 6  # Setup bug 6 specifically
cd fastapi
floss run
floss ui --report report.json

# FastAPI with multiple bug examples (1-16 available)
./setup.sh 11  # Response model validation issue
./setup.sh 8   # Authentication middleware issue

# Cookiecutter template engine bugs
cd examples/cookiecutter
./setup.sh 1   # File encoding issue
cd cookiecutter
floss run
```

#### 📊 Data Science Examples
Fault localization on scientific computing code:
```bash
# PyGraphistry visualization library
cd examples/pygraphistry
./setup.sh  # Downloads PyGraphistry
cd pygraphistry
floss test --source-dir graphistry --test-dir tests
```

### Example Learning Path

1. **Start Here**: `examples/dummy-example` - Learn basic concepts
2. **Web Frameworks**: `examples/fastapi/` - 16 different FastAPI bugs covering various scenarios
3. **Template Engines**: `examples/cookiecutter/` - Template generation and file handling bugs
4. **Data Processing**: `examples/pygraphistry` - Scientific computing bugs

#### FastAPI Bug Categories
- **Input/Output Validation**: bugs 3, 4, 9, 11 (request/response validation issues)
- **Middleware & Dependencies**: bugs 6, 8, 13 (dependency injection, authentication, middleware)
- **Schema & Documentation**: bugs 2, 7 (OpenAPI schema, response serialization)
- **Advanced Features**: bugs 10, 12, 15, 16 (file upload, WebSocket, static files, background tasks)
- **Error Handling**: bug 14 (exception handling problems)
- **Multi-bug Scenarios**: `multi-bugs/` (complex scenarios with multiple issues)

Each example includes:
- ✅ Detailed README with bug description
- ✅ Automated setup scripts
- ✅ **Bug patch files** showing the exact fix
- ✅ Pre-generated floss reports for comparison
- ✅ Pre-configured floss settings
- ✅ Expected results and analysis guides

For complete example documentation, see [`examples/README.md`](../examples/README.md).

## Quick Start Examples

### Example 1: Basic Project Analysis

Let's start with a simple Python project:

```
my_project/
├── src/
│   ├── calculator.py
│   └── utils.py
├── tests/
│   ├── test_calculator.py
│   └── test_utils.py
└── floss.conf
```

**Step 1**: Create configuration file (`floss.conf`):

```ini
[test]
source_dir = src
test_dir = tests

[fl]
formulas = ochiai, tarantula, dstar2
```

**Step 2**: Run complete analysis:

```bash
cd my_project
floss run
```

**Step 3**: View results:

```bash
floss ui
```

### Example 2: Large Project with Custom Settings

For larger projects with specific requirements:

```bash
# Run with specific test filters and exclusions
floss run \
  --source-dir src \
  --test-dir tests \
  --test-filter "not slow and not integration" \
  --ignore "*/migrations/*" \
  --ignore "*/third_party/*" \
  --omit "*/test_*" \
  --formulas ochiai tarantula jaccard dstar2 \
  --output detailed_report.json

# Launch dashboard on custom port
floss ui --report detailed_report.json --port 8080
```

### Example 3: CI/CD Integration

```bash
#!/bin/bash
# ci_fault_localization.sh

set -e

echo "Running floss analysis..."

# Run fault localization
floss run \
  --source-dir src \
  --test-dir tests \
  --output fl_report.json \
  --config .floss.conf

# Check if report was generated
if [ -f "fl_report.json" ]; then
    echo "✓ Fault localization completed successfully"

    # Optional: Extract summary statistics
    python -c "
import json
with open('fl_report.json') as f:
    data = json.load(f)
    totals = data.get('totals', {})
    print(f'Tests: {totals.get(\"total_tests\", 0)}')
    print(f'Failed: {totals.get(\"failed_tests\", 0)}')
    print(f'Lines analyzed: {totals.get(\"lines_analyzed\", 0)}')
"
else
    echo "✗ Fault localization failed"
    exit 1
fi
```

## CLI Usage Patterns

### Test Command Patterns

#### Basic Test Execution

```bash
# Minimal setup - auto-detect test directory
floss test --source-dir src

# Explicit test directory
floss test --source-dir src --test-dir tests

# Custom output file
floss test --source-dir src --output my_coverage.json
```

#### Test Filtering

```bash
# Run only fast tests
floss test --test-filter "not slow"

# Run specific test categories
floss test --test-filter "unit or integration"

# Run tests matching pattern
floss test --test-filter "test_calculate*"

# Exclude specific tests
floss test --test-filter "not test_expensive_operation"
```

#### File Pattern Management

```bash
# Ignore specific directories from test discovery
floss test --ignore "*/migrations/*" --ignore "*/vendor/*"

# Omit files from coverage collection
floss test --omit "*/test_*" --omit "*/__init__.py"

# Combine multiple patterns
floss test \
  --ignore "*/migrations/*" \
  --ignore "*/third_party/*" \
  --omit "*/__init__.py" \
  --omit "*/conftest.py"
```

### Fault Localization Command Patterns

#### Formula Selection

```bash
# Use single formula
floss fl --formulas ochiai

# Use multiple formulas
floss fl --formulas ochiai tarantula jaccard

# Use all available formulas
floss fl --formulas ochiai tarantula jaccard dstar2 dstar3 kulczynski2 naish1 russellrao sorensendice sbi
```

#### File Handling

```bash
# Custom input/output files
floss fl --input my_coverage.json --output detailed_report.json

# Process multiple coverage files (requires scripting)
for coverage_file in coverage_*.json; do
    output_file="report_${coverage_file#coverage_}"
    floss fl --input "$coverage_file" --output "$output_file"
done
```

### Pipeline Command Patterns

#### Complete Workflow

```bash
# Basic pipeline
floss run

# Customized pipeline
floss run \
  --source-dir src \
  --test-dir tests \
  --output final_report.json \
  --formulas ochiai tarantula dstar2

# Pipeline with filtering
floss run \
  --test-filter "not slow" \
  --ignore "*/migrations/*" \
  --formulas ochiai dstar2
```

### Dashboard Command Patterns

#### Basic Dashboard Launch

```bash
# Default settings
floss ui

# Custom report file
floss ui --report my_report.json

# Custom port
floss ui --port 8080

# Don't auto-open browser
floss ui --no-open
```

#### Dashboard for Remote Access

```bash
# For remote server access
floss ui --port 8501 --no-open
# Then access via http://server-ip:8501
```

## Configuration Examples

### Basic Configuration

```ini
# floss.conf
[test]
source_dir = src
test_dir = tests
output_file = coverage.json

[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula
```

### Advanced Configuration

```ini
# floss.conf
[test]
source_dir = src
test_dir = tests
output_file = coverage.json
# Ignore patterns for test discovery
ignore = */migrations/*, */vendor/*, */third_party/*
# Omit patterns from coverage
omit = */__init__.py, */conftest.py, */test_*.py

[fl]
input_file = coverage.json
output_file = report.json
# Multiple formulas for comparison
formulas = ochiai, tarantula, jaccard, dstar2, dstar3, kulczynski2
```

### Project-Specific Configurations

#### Django Project

```ini
# floss.conf
[test]
source_dir = .
test_dir = tests
ignore = */migrations/*, */venv/*, */static/*, manage.py
omit = */migrations/*, */venv/*, */settings/*, manage.py

[fl]
formulas = ochiai, tarantula, dstar2
```

#### Flask Project

```ini
# floss.conf
[test]
source_dir = app
test_dir = tests
ignore = */instance/*, */migrations/*
omit = */instance/*, config.py

[fl]
formulas = ochiai, jaccard, dstar2
```

#### Scientific Computing Project

```ini
# floss.conf
[test]
source_dir = src
test_dir = tests
# Ignore notebook checkpoints and data files
ignore = */.ipynb_checkpoints/*, */data/*, */models/*
omit = */notebooks/*, */data/*, */experiments/*

[fl]
# Use formulas effective for numerical code
formulas = ochiai, dstar2, kulczynski2
```

### Environment-Specific Configurations

#### Development Environment

```ini
# floss.dev.conf
[test]
source_dir = src
test_dir = tests
ignore = */migrations/*
omit = */__init__.py

[fl]
# Use fewer formulas for faster iteration
formulas = ochiai, tarantula
```

#### CI/CD Environment

```ini
# floss.ci.conf
[test]
source_dir = src
test_dir = tests
ignore = */migrations/*, */scripts/*
omit = */__init__.py, */conftest.py

[fl]
# Comprehensive analysis for CI
formulas = ochiai, tarantula, jaccard, dstar2, dstar3
```

## Dashboard Usage

### Navigation and Basic Usage

1. **Launch Dashboard**:
   ```bash
   floss ui --report report.json
   ```

2. **File Selection**:
   - Use the file browser in the sidebar
   - Or drag-and-drop JSON files
   - Select different report files for comparison

3. **Visualization Selection**:
   - **Treemap**: Hierarchical view of project structure
   - **Sunburst**: Circular hierarchical visualization
   - **Coverage Matrix**: Test-to-code coverage mapping
   - **Source Code**: Line-by-line code analysis

### Treemap Visualization

The treemap provides a hierarchical view of your project with suspiciousness-based coloring:

- **Size**: Represents file size or number of lines
- **Color**: Represents suspiciousness level (red = high, green = low)
- **Interaction**: Click to drill down into directories

Demo:

![Treemap demo](gifs/treemap_demo.gif)

Static example:

![Treemap static](imgs/treemap.png)

**Best Uses**:
- Quick overview of project health
- Identifying problematic modules
- Understanding project structure

### Sunburst Chart

The sunburst chart offers a circular view of project hierarchy:

- **Inner rings**: Directory levels
- **Outer rings**: Individual files
- **Color coding**: Suspiciousness levels
- **Interaction**: Click to zoom and filter

**Best Uses**:
- Alternative hierarchical view
- Complex project navigation
- Pattern identification

Demo:

![Sunburst demo](gifs/sunburst_demo.gif)

Static example:

![Sunburst static](imgs/sunburst.png)

### Coverage Matrix

The coverage matrix shows which tests cover which lines of code:

- **Rows**: Test cases
- **Columns**: Source code lines
- **Colors**: Green (passed & covered), Red (failed & covered), Gray (not covered)

**Best Uses**:
- Understanding test coverage patterns
- Identifying under-tested code
- Analyzing test-fault relationships

### Source Code Viewer

The source code viewer displays actual code with suspiciousness overlays:

- **Syntax highlighting**: Language-specific coloring
- **Suspiciousness scores**: Displayed next to each line
- **Multiple formulas**: Compare different formula results
- **Interactive**: Click lines for detailed information

**Best Uses**:
- Detailed code analysis
- Understanding specific fault locations
- Formula comparison

Screenshot:

![Source code viewer screenshot](imgs/source_code_example.png)

### Advanced Dashboard Features

#### Filtering and Thresholds

1. **Suspiciousness Threshold**:
   - Adjust slider to filter by suspiciousness level
   - Hide low-suspicion code
   - Focus on most problematic areas

2. **Formula Selection**:
   - Choose which formulas to display
   - Compare formula effectiveness
   - Switch between formula results

3. **File Pattern Filtering**:
   - Filter by file extensions
   - Include/exclude specific directories
   - Focus on specific modules

#### Export and Sharing

1. **Export Visualizations**:
   - Download charts as PNG/SVG
   - Save filtered datasets as CSV
   - Export configuration settings

2. **Share Reports**:
   - Copy dashboard URLs
   - Export static HTML reports
   - Generate summary statistics

## Integration Scenarios

### Continuous Integration

#### GitHub Actions Example

```yaml
# .github/workflows/fault-localization.yml
name: Fault Localization

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  fault-localization:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -e .
        pip install floss

    - name: Run fault localization
      run: |
        floss run --source-dir src --test-dir tests --output fl_report.json

    - name: Upload fault localization report
      uses: actions/upload-artifact@v3
      with:
        name: fault-localization-report
        path: fl_report.json

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      run: |
        python scripts/comment_pr.py fl_report.json
```

#### Jenkins Pipeline Example

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -e .'
                sh 'pip install floss'
            }
        }

        stage('Fault Localization') {
            steps {
                sh 'floss run --config .floss.ci.conf --output fl_report.json'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'fl_report.json', fingerprint: true
                }
            }
        }

        stage('Analysis') {
            steps {
                script {
                    def report = readJSON file: 'fl_report.json'
                    def failedTests = report.totals.failed_tests
                    if (failedTests > 0) {
                        echo "Found ${failedTests} failed tests - fault localization completed"
                    } else {
                        echo "All tests passed - no fault localization needed"
                    }
                }
            }
        }
    }
}
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: floss-analysis
        name: floss Analysis
        entry: bash -c 'floss test --source-dir src --test-dir tests'
        language: system
        pass_filenames: false
        stages: [pre-push]
```

### IDE Integration

#### VS Code Task Example

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "floss: Run Analysis",
            "type": "shell",
            "command": "floss",
            "args": ["run", "--source-dir", "src", "--test-dir", "tests"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "floss: Launch Dashboard",
            "type": "shell",
            "command": "floss",
            "args": ["ui", "--report", "report.json"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```

## Best Practices

### Configuration Management

1. **Use Configuration Files**:
   - Create project-specific `floss.conf`
   - Version control configuration files
   - Document configuration choices

2. **Pattern Management**:
   - Be specific with ignore/omit patterns
   - Document why files are excluded
   - Regularly review exclusion patterns

### Test Organization

1. **Test Structure**:
   - Organize tests logically
   - Use descriptive test names
   - Group related tests

2. **Coverage Optimization**:
   - Ensure good test coverage
   - Test both success and failure paths
   - Include edge cases

3. **Test Performance**:
   - Keep tests fast for frequent analysis
   - Use test filters for large test suites
   - Parallel test execution when possible

### Formula Selection

1. **Start Simple**:
   - Begin with Ochiai (most effective general-purpose)
   - Add Tarantula for comparison
   - Experiment with other formulas

2. **Formula Comparison**:
   - Use multiple formulas to cross-validate results
   - Compare effectiveness on your specific codebase
   - Document which formulas work best for your project

3. **Context-Specific Choices**:
   - Different formulas may work better for different types of code
   - Consider project characteristics (size, test coverage, code complexity)

### Workflow Integration

1. **Regular Analysis**:
   - Run fault localization on failing builds
   - Include in code review process
   - Use for debugging sessions

2. **Team Adoption**:
   - Train team on dashboard usage
   - Establish analysis procedures
   - Share effective configurations

3. **Continuous Improvement**:
   - Monitor formula effectiveness
   - Refine configuration over time
   - Collect feedback from team

## Troubleshooting

### Common Issues

#### 1. No Coverage Data Generated

**Symptoms**: Empty or minimal coverage.json file

**Solutions**:
```bash
# Check if tests are being discovered
floss test

# Verify source and test directories
floss test --source-dir src --test-dir tests

# Check ignore patterns
floss test --ignore "*/__init__.py"
```

#### 2. Tests Not Found

**Symptoms**: "No tests found" or empty test results

**Solutions**:
```bash
# Let pytest auto-discover tests
floss test --source-dir src

# Specify test directory explicitly
floss test --source-dir src --test-dir tests

# Check test naming conventions (test_*.py or *_test.py)
ls tests/test_*.py
```

#### 3. Import Errors in Tests

**Symptoms**: Tests fail due to import errors

**Solutions**:
```bash
# Ensure source directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
floss test --source-dir src --test-dir tests

# Use relative imports in tests
# Or install package in development mode
pip install -e .
```

#### 4. Dashboard Not Loading

**Symptoms**: Dashboard fails to start or load data

**Solutions**:
```bash
# Check if UI dependencies are installed
pip install "floss[ui]"

# Verify report file exists and is valid JSON
python -m json.tool report.json

# Try different port
floss ui --port 8080
```

#### 5. Performance Issues

**Symptoms**: Slow execution or high memory usage

**Solutions**:
```bash
# Reduce scope with ignore patterns
floss test --ignore "*/migrations/*" --ignore "*/vendor/*"

# Use test filters to run subset
floss test --test-filter "not slow"

# Reduce number of formulas
floss fl --formulas ochiai tarantula

# Process smaller chunks of tests
floss test --test-filter "unit"
floss test --test-filter "integration"
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
floss --verbose run --source-dir src --test-dir tests
```

### Getting Help

1. **Check Documentation**: Review this guide and the main README
2. **Verbose Mode**: Use `--verbose` flag for detailed output
3. **Issue Tracker**: Report bugs and issues on GitHub
4. **Community**: Ask questions in project discussions

### Log Analysis

floss provides structured logging. Key log messages to look for:

- **Configuration Loading**: Verify correct settings are loaded
- **Test Discovery**: Check how many tests are found
- **Coverage Collection**: Monitor coverage data generation
- **Formula Calculation**: Verify suspiciousness calculations
- **Report Generation**: Confirm successful report creation

This usage guide should help you effectively integrate floss into your Python development workflow. Start with the basic examples and gradually adopt more advanced features as your needs grow.
