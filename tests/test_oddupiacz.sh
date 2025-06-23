#!/bin/bash

set -e

setup() {
  TEST_DIR=$(mktemp -d)
  TEST_REPO="$TEST_DIR/test-repo"
  TEST_HOOKS_DIR="$TEST_DIR/.githooks"

  export HOME="$TEST_DIR"
  mkdir -p "$TEST_HOOKS_DIR"

  cp "oddupiacz.sh" "$TEST_DIR/"
  cp "justfile" "$TEST_DIR/"

  mkdir -p "$TEST_REPO"
  cd "$TEST_REPO"
  git init
  git config --local core.hooksPath "$TEST_HOOKS_DIR"
  git config --local user.email "test@example.com"
  git config --local user.name "Test User"
}

teardown() {
  cd "$OLDPWD"
  rm -rf "$TEST_DIR"
}

test_install() {
  setup

  just install

  if [ ! -x "$TEST_HOOKS_DIR/pre-commit" ]; then
    echo "❌ Installation test failed: pre-commit hook not found or not executable"
    teardown
    return 1
  fi
  echo "✅ Installation test passed"

  teardown
}

test_edit_config() {
  setup

  echo "word" | just edit_config

  if [ ! -f "$TEST_HOOKS_DIR/oddupiacz.conf" ]; then
    echo "❌ Config file not created"
    teardown
    return 1
  fi

  CONFIG_CONTENT=$(cat "$TEST_HOOKS_DIR/oddupiacz.conf")
  if [ "$CONFIG_CONTENT" != "word" ]; then
    echo "❌ Default config value not set correctly. Got: '$CONFIG_CONTENT'"
    teardown
    return 1
  fi

  echo "bad worse worst" | just edit_config

  CONFIG_CONTENT=$(cat "$TEST_HOOKS_DIR/oddupiacz.conf")
  if [ "$CONFIG_CONTENT" != "bad worse worst" ]; then
    echo "❌ Custom config value not set correctly. Got: '$CONFIG_CONTENT'"
    teardown
    return 1
  fi

  echo "✅ Edit config test passed"
  teardown
}

test_forbidden_words_in_diff() {
  setup
  just install

  echo "badword anotherword" > "$TEST_HOOKS_DIR/oddupiacz.conf"

  echo "This contains badword in it" > test_file1.txt
  git add test_file1.txt

  if git commit -m "Test commit 1" 2>/dev/null; then
    echo "❌ Forbidden word test failed: commit succeeded when it should fail (first word)"
    teardown
    return 1
  fi

  git reset
  echo "This contains anotherword in it" > test_file2.txt
  git add test_file2.txt

  if git commit -m "Test commit 2" 2>/dev/null; then
    echo "❌ Forbidden word test failed: commit succeeded when it should fail (second word)"
    teardown
    return 1
  fi

  echo "✅ Forbidden words in diff test passed"
  teardown
}

test_forbidden_word_in_file_names() {
  setup
  just install

  echo "badname" > "$TEST_HOOKS_DIR/oddupiacz.conf"

  echo "This is a test file" > file_with_badname.txt
  git add file_with_badname.txt

  if git commit -m "Test commit" 2>/dev/null; then
    echo "❌ Forbidden word in filename test failed: commit succeeded when it should fail"
    teardown
    return 1
  fi

  echo "✅ Forbidden word in filename test passed"
  teardown
}

test_successful_commit() {
  setup
  just install

  echo "badword anotherword" > "$TEST_HOOKS_DIR/oddupiacz.conf"

  echo "This is a perfectly fine text" > good_file.txt
  git add good_file.txt

  if ! git commit -m "Test commit" >/dev/null 2>&1; then
    echo "❌ Successful commit test failed: commit failed when it should succeed"
    teardown
    return 1
  fi

  COMMIT_COUNT=$(git log --oneline | wc -l | tr -d ' ')
  if [ "$COMMIT_COUNT" -ne 1 ]; then
    echo "❌ Successful commit test failed: expected 1 commit, got $COMMIT_COUNT"
    teardown
    return 1
  fi

  echo "✅ Successful commit test passed"
  teardown
}

run_tests() {
  test_install
  test_edit_config
  test_forbidden_words_in_diff
  test_forbidden_word_in_file_names
  test_successful_commit

  echo "✅ All tests completed"
}

run_tests
