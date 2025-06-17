#!/bin/bash

# Create a temporary file for commands that should be ignored
IGNORE_FILE=".doignore"
touch "$IGNORE_FILE"

echo "Testing commands in Docker container..."
echo "=================================="

# Function to test a single command
test_command() {
    local cmd="$1"

    echo -e "\nTesting command: $cmd"
    echo "----------------------------"

    # Prepare the command to be executed in the container
    local docker_cmd=""

    # Handle different types of commands
    if [[ "$cmd" == *'`'* || "$cmd" == *'$('* ]]; then
        # Commands with backticks or subshells need to be evaluated
        docker_cmd="eval $cmd"
    else
        docker_cmd="$cmd"
    fi

    # Run the command in a basic Ubuntu container
    # Use timeout to prevent hanging commands
    # Disable TTY for non-interactive commands
    if [[ "$cmd" == *'['* && "$cmd" == *']'* ]]; then
        # Handle markdown task items
        echo "Skipping markdown task item"
        echo "$cmd" >> "$IGNORE_FILE"
        echo "Added to $IGNORE_FILE"
        return 1
    elif [[ "$cmd" == /* || "$cmd" == "./"* ]]; then
        # Handle file paths
        echo "Skipping file path"
        echo "$cmd" >> "$IGNORE_FILE"
        echo "Added to $IGNORE_FILE"
        return 1
    elif [[ "$cmd" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}.*\[.*\].*$ ]]; then
        # Handle timestamped logs
        echo "Skipping timestamped log"
        echo "$cmd" >> "$IGNORE_FILE"
        echo "Added to $IGNORE_FILE"
        return 1
    elif [[ "$cmd" =~ ^[A-Z][a-z]+[^:]*$ || "$cmd" =~ ^[A-Z][a-z]+[^:]*:$ ]]; then
        # Handle plain text (starts with capital letter, no special chars)
        echo "Skipping plain text"
        echo "$cmd" >> "$IGNORE_FILE"
        echo "Added to $IGNORE_FILE"
        return 1
    else
        # Try to execute the command
        if docker run --rm ubuntu:22.04 bash -c "set -e; $docker_cmd" 2>/dev/null; then
            echo -e "\n✅ Command succeeded in Docker"
            return 0
        else
            echo -e "\n❌ Command failed in Docker"
            echo "$cmd" >> "$IGNORE_FILE"
            echo "Added to $IGNORE_FILE"
            return 1
        fi
    fi
}

# Read commands from test_commands.txt, skipping comments and empty lines
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue

    # Test the command
    test_command "$line"
done < test_commands.txt

echo -e "\nTesting complete. Check $IGNORE_FILE for commands that should be ignored."
echo -e "\nSummary of commands to ignore:"
cat "$IGNORE_FILE"
