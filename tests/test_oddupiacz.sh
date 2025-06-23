#!/bin/bash
# tests/test_oddupiacz.sh

set -e

# Setup
setup() {
  TEST_DIR=$(mktemp -d)
  TEST_REPO="$TEST_DIR/test-repo"
  TEST_HOOKS_DIR="$TEST_DIR/.githooks"  # Changed from githooks to .githooks to match justfile

  # Override hooks path for testing
  export HOME="$TEST_DIR"
  mkdir -p "$TEST_HOOKS_DIR"

  # Copy oddupiacz.sh to the test directory
  cp "oddupiacz.sh" "$TEST_DIR/"
  cp "justfile" "$TEST_DIR/"

  # Create test repo
  mkdir -p "$TEST_REPO"
  cd "$TEST_REPO"
  git init
  git config --local core.hooksPath "$TEST_HOOKS_DIR"
}

# Teardown
teardown() {
  cd "$OLDPWD"
  rm -rf "$TEST_DIR"
}

# Test installation
test_install() {
  just install

  if [ ! -x "$TEST_HOOKS_DIR/pre-commit" ]; then
    echo "❌ Installation test failed: pre-commit hook not found or not executable"
    return 1
  fi
  echo "✅ Installation test passed"
}

# Test with forbidden words
test_forbidden_words() {
  # Set up config with forbidden words
  echo "badword anotherword" > "$TEST_HOOKS_DIR/oddupiacz.conf"

  # Create a test file with forbidden word
  echo "This contains badword in it" > test_file.txt
  git add test_file.txt

  # Attempt commit - should fail
  if git commit -m "Test commit" 2>/dev/null; then
    echo "❌ Forbidden word test failed: commit succeeded when it should fail"
    return 1
  fi
  echo "✅ Forbidden word test passed"
}

# Run tests
run_tests() {
  setup
  test_install
  test_forbidden_words
  teardown
}

run_tests
