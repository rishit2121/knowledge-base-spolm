#!/bin/bash

# Script to sync contents from knowledge_base_SPOLM folder from upstream repo
# This copies all contents directly to the root directory (not as a subfolder)
# Usage: ./sync_knowledge_base.sh

set -e

REPO_URL="https://github.com/Tanrocode/spolm.git"
FOLDER_NAME="knowledge_base_SPOLM"
TEMP_DIR=".sync_temp_spolm"
CURRENT_DIR=$(pwd)

# Files/directories to preserve during sync
PRESERVE_ITEMS=(".git" ".gitignore" "sync_knowledge_base.sh" "SYNC_INSTRUCTIONS.md" ".sync_temp_spolm")

echo "🔄 Syncing contents from $FOLDER_NAME from $REPO_URL..."

# Remove temp directory if it exists
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Clone the repo to a temporary directory
echo "📥 Cloning repository..."
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TEMP_DIR" 2>/dev/null || \
git clone --depth 1 "$REPO_URL" "$TEMP_DIR"

cd "$TEMP_DIR"

# Use sparse checkout to get only the folder we need (if supported)
if git sparse-checkout init --cone 2>/dev/null; then
    echo "📂 Using sparse checkout to get only $FOLDER_NAME..."
    git sparse-checkout set "$FOLDER_NAME"
    git checkout 2>/dev/null || true
fi

# Check if folder exists in the repo
if [ ! -d "$FOLDER_NAME" ]; then
    echo "❌ Error: Folder '$FOLDER_NAME' not found in the repository"
    echo "Available folders:"
    ls -la | grep "^d" | awk '{print $NF}' | grep -v "^\.$" | grep -v "^\.\.$" | grep -v "^\.git$" | grep -v "^$TEMP_DIR$"
    cd "$CURRENT_DIR"
    rm -rf "$TEMP_DIR"
    exit 1
fi

cd "$CURRENT_DIR"

# Remove all files/directories except preserved ones
echo "🗑️  Cleaning existing files (preserving sync script and git files)..."
for item in * .*; do
    # Skip if item doesn't exist, is "." or "..", or is in preserve list
    [ ! -e "$item" ] && continue
    [ "$item" = "." ] && continue
    [ "$item" = ".." ] && continue
    [[ " ${PRESERVE_ITEMS[@]} " =~ " ${item} " ]] && continue
    
    echo "  Removing: $item"
    rm -rf "$item"
done

# Copy all contents from the folder directly to root
echo "📋 Copying contents from $FOLDER_NAME to root..."
cp -r "$TEMP_DIR/$FOLDER_NAME"/* .
# Copy hidden files (but skip .git)
cp -r "$TEMP_DIR/$FOLDER_NAME"/.[!.]* . 2>/dev/null || true

# Clean up
rm -rf "$TEMP_DIR"

echo "✅ Successfully synced contents from $FOLDER_NAME!"
echo ""
echo "To commit the changes:"
echo "  git add ."
echo "  git commit -m 'Update from upstream knowledge_base_SPOLM'"
