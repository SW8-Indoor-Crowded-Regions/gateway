#!/usr/bin/env bash

# Stop any running E2E test containers
docker-compose -f docker-compose.yml -f docker-compose.e2e.yml down

# Run E2E tests with all dependencies
docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up --exit-code-from test-runner

# Capture the exit code of the test-runner service
EXIT_CODE=$?

# Cleanup after tests (optional)
docker-compose -f docker-compose.yml -f docker-compose.e2e.yml down

# Exit with the test-runner's exit code (important for CI/CD)
exit $EXIT_CODE
