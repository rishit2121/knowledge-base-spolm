# Syncing Contents from knowledge_base_SPOLM

This document explains how to sync the contents from the `knowledge_base_SPOLM` folder from the upstream repository (https://github.com/Tanrocode/spolm.git).

**Important:** The sync script copies all contents directly to the root directory (not as a subfolder).

## Using the Sync Script (Recommended)

Run the sync script to copy all contents from the upstream repo:

```bash
./sync_knowledge_base.sh
```

This will:
1. Clone the upstream repository temporarily
2. Extract only the `knowledge_base_SPOLM` folder using sparse checkout
3. Copy all contents directly to the root directory (replacing existing files)
4. Preserve the sync script, `.gitignore`, and git files
5. Clean up temporary files

After running, commit the changes:
```bash
git add .
git commit -m "Update from upstream knowledge_base_SPOLM"
```

## What Gets Preserved

The sync script automatically preserves:
- `.git/` directory (your git history)
- `.gitignore` file
- `sync_knowledge_base.sh` (the sync script itself)
- `SYNC_INSTRUCTIONS.md` (this file)

Everything else will be replaced with the contents from the upstream repository.

## Manual Sync (Alternative)

If you prefer to manually sync:

```bash
# Clone the repo temporarily
git clone --depth 1 https://github.com/Tanrocode/spolm.git .sync_temp_spolm

# Use sparse checkout to get only the folder
cd .sync_temp_spolm
git sparse-checkout init --cone
git sparse-checkout set knowledge_base_SPOLM
git checkout

# Copy contents to root (from parent directory)
cd ..
cp -r .sync_temp_spolm/knowledge_base_SPOLM/* .
cp -r .sync_temp_spolm/knowledge_base_SPOLM/.[!.]* . 2>/dev/null || true

# Clean up
rm -rf .sync_temp_spolm
```

## Notes

- The sync script uses sparse checkout when available to minimize download size
- Make sure you have access to the upstream repository
- All contents are copied directly to root (not in a subfolder)
- Run the sync script whenever you want to update with the latest changes from upstream
