#!/bin/bash

echo "Running unit tests..."
python3 -m unittest discover tests

status=$?

if [ $status -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed."
fi

exit $status