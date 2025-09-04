# CI/CD Integration Examples for UV-Based Testing

This document provides examples of how to integrate UV-based testing into various CI/CD platforms.

## GitHub Actions

### Basic Workflow

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Install UV
      uses: astral-sh/setup-uv@v4
      with:
        version: "latest"

    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}

    - name: Install dependencies
      run: uv sync --group test

    - name: Run tests
      run: uv run pytest --cov=agent_framework --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
```

### Advanced Multi-Job Workflow

```yaml
name: Comprehensive Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv python install 3.11
    - run: uv sync --group test
    - run: uv run black --check agent_framework tests
    - run: uv run flake8 agent_framework tests
    - run: uv run mypy agent_framework

  unit-tests:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv python install ${{ matrix.python-version }}
    - run: uv sync --group test
    - run: uv run pytest -m unit --maxfail=5

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv python install 3.11
    - run: uv sync --group test
    - run: uv run pytest -m integration

  performance-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv python install 3.11
    - run: uv sync --group test
    - run: uv run pytest -m performance --benchmark-only
```

## GitLab CI

### Basic Configuration (.gitlab-ci.yml)

```yaml
stages:
  - test
  - coverage

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - .venv/

before_script:
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - source $HOME/.cargo/env
  - uv python install 3.11
  - uv sync --group test

test:unit:
  stage: test
  script:
    - uv run pytest -m unit --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml

test:integration:
  stage: test
  script:
    - uv run pytest -m integration

test:coverage:
  stage: coverage
  script:
    - uv run pytest --cov=agent_framework --cov-report=xml --cov-report=html
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
  coverage: '/TOTAL.+?(\d+\%)$/'
```

## Azure DevOps

### Pipeline Configuration (azure-pipelines.yml)

```yaml
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

strategy:
  matrix:
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'
    Python312:
      python.version: '3.12'

steps:
- script: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    uv python install $(python.version)
  displayName: 'Install UV and Python'

- script: |
    source $HOME/.cargo/env
    uv sync --group test
  displayName: 'Install dependencies'

- script: |
    source $HOME/.cargo/env
    uv run pytest -m unit --junitxml=junit/test-results.xml --cov=agent_framework --cov-report=xml
  displayName: 'Run tests'

- task: PublishTestResults@2
  condition: succeededOrFailed()
  inputs:
    testResultsFiles: '**/test-*.xml'
    testRunTitle: 'Publish test results for Python $(python.version)'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: Cobertura
    summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'
```

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        UV_CACHE_DIR = "${WORKSPACE}/.uv-cache"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    source $HOME/.cargo/env
                    uv python install 3.11
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    source $HOME/.cargo/env
                    uv sync --group test
                '''
            }
        }
        
        stage('Lint') {
            steps {
                sh '''
                    source $HOME/.cargo/env
                    uv run black --check agent_framework tests
                    uv run flake8 agent_framework tests
                    uv run mypy agent_framework
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                    source $HOME/.cargo/env
                    uv run pytest -m unit --junitxml=junit.xml
                '''
            }
            post {
                always {
                    junit 'junit.xml'
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    source $HOME/.cargo/env
                    uv run pytest -m integration
                '''
            }
        }
        
        stage('Coverage') {
            steps {
                sh '''
                    source $HOME/.cargo/env
                    uv run pytest --cov=agent_framework --cov-report=xml --cov-report=html
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

## CircleCI

### Configuration (.circleci/config.yml)

```yaml
version: 2.1

orbs:
  python: circleci/python@2.0.3

jobs:
  test:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install UV
          command: |
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source $HOME/.cargo/env
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> $BASH_ENV
      - run:
          name: Install dependencies
          command: |
            uv python install 3.11
            uv sync --group test
      - run:
          name: Run tests
          command: |
            uv run pytest --junitxml=test-results/junit.xml --cov=agent_framework --cov-report=xml
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: htmlcov

workflows:
  test-workflow:
    jobs:
      - test
```

## Docker-based CI

### Dockerfile for Testing

```dockerfile
FROM python:3.11-slim

# Install UV
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --group test

# Run tests by default
CMD ["uv", "run", "pytest"]
```

### Docker Compose for Testing

```yaml
version: '3.8'

services:
  test:
    build: .
    command: uv run pytest --cov=agent_framework --cov-report=html
    volumes:
      - ./htmlcov:/app/htmlcov
    environment:
      - PYTHONPATH=/app

  test-unit:
    build: .
    command: uv run pytest -m unit

  test-integration:
    build: .
    command: uv run pytest -m integration
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

## Pre-commit Hooks

### .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: uv-test-fast
        name: UV Fast Tests
        entry: uv run pytest -m "not slow" --maxfail=3
        language: system
        pass_filenames: false
        always_run: true

      - id: uv-lint
        name: UV Lint Check
        entry: uv run black --check agent_framework tests
        language: system
        pass_filenames: false
        always_run: true

      - id: uv-type-check
        name: UV Type Check
        entry: uv run mypy agent_framework
        language: system
        pass_filenames: false
        always_run: true
```

## Makefile Integration

### Cross-platform Makefile

```makefile
# Detect OS
ifeq ($(OS),Windows_NT)
    UV_INSTALL = powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    UV_PATH = $(USERPROFILE)\.cargo\bin\uv.exe
else
    UV_INSTALL = curl -LsSf https://astral.sh/uv/install.sh | sh
    UV_PATH = uv
endif

.PHONY: install-uv setup test test-ci

install-uv:
	@command -v $(UV_PATH) >/dev/null 2>&1 || { echo "Installing UV..."; $(UV_INSTALL); }

setup: install-uv
	$(UV_PATH) sync --group test

test: setup
	$(UV_PATH) run pytest

test-ci: setup
	$(UV_PATH) run pytest --cov=agent_framework --cov-report=xml --junitxml=junit.xml

lint: setup
	$(UV_PATH) run black --check agent_framework tests
	$(UV_PATH) run flake8 agent_framework tests
	$(UV_PATH) run mypy agent_framework
```

## Environment-specific Configurations

### Development Environment

```bash
# .env.development
AGENT_LOG_LEVEL=DEBUG
MONGODB_URL=mongodb://localhost:27017/agent_framework_dev
REDIS_URL=redis://localhost:6379/0
```

### Testing Environment

```bash
# .env.testing
AGENT_LOG_LEVEL=INFO
MONGODB_URL=mongodb://localhost:27017/agent_framework_test
REDIS_URL=redis://localhost:6379/1
PYTEST_CURRENT_TEST=true
```

### CI Environment

```bash
# .env.ci
AGENT_LOG_LEVEL=WARNING
MONGODB_URL=mongodb://mongo:27017/agent_framework_ci
REDIS_URL=redis://redis:6379/2
CI=true
```

## Performance Monitoring

### Benchmark Tracking

```yaml
# .github/workflows/benchmark.yml
name: Benchmark

on:
  push:
    branches: [ main ]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv python install 3.11
    - run: uv sync --group test
    - run: uv run pytest -m performance --benchmark-json=benchmark.json
    - uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark.json
        github-token: ${{ secrets.GITHUB_TOKEN }}
        auto-push: true
```

These examples demonstrate how to integrate UV-based testing into various CI/CD platforms, providing fast, reliable, and consistent test execution across different environments.