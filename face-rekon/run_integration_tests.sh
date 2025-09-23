#!/bin/bash
# Integration test runner for CI/CD
# Optimized for speed and reliability

echo "🧪 Integration Test Runner"
echo "==============================="

# Test files to run (ordered by execution time - fastest first)
test_files=(
    "tests/integration/test_database_integration_simple.py"
    "tests/integration/test_api_integration_simple.py"
)

failed_tests=()
total_tests=${#test_files[@]}
passed_tests=0
start_time=$(date +%s)

for test_file in "${test_files[@]}"; do
    echo ""
    echo "🔧 Running: $test_file"
    echo "----------------------------------------"
    file_start=$(date +%s)

    # Run single test file with optimized settings
    if docker compose -f docker-compose.test.yml run --rm integration-tests \
        pytest "$test_file" -c pytest-integration.ini --tb=short --maxfail=3 -q; then
        file_end=$(date +%s)
        duration=$((file_end - file_start))
        echo "✅ $test_file PASSED (${duration}s)"
        ((passed_tests++))
    else
        file_end=$(date +%s)
        duration=$((file_end - file_start))
        echo "❌ $test_file FAILED (${duration}s)"
        failed_tests+=("$test_file")
    fi

    # Minimal cleanup delay
    sleep 1
done

echo ""
end_time=$(date +%s)
total_duration=$((end_time - start_time))

echo "📊 Integration Test Summary"
echo "=========================="
echo "✅ Passed: $passed_tests/$total_tests"
echo "⏱️  Total time: ${total_duration}s"

if [ ${#failed_tests[@]} -gt 0 ]; then
    echo "❌ Failed tests:"
    printf "   - %s\n" "${failed_tests[@]}"
    exit 1
else
    echo "🎉 All integration tests passed!"
    exit 0
fi
