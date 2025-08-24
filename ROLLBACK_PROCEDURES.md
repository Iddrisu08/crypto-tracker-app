# Rollback Procedures

## Quick Rollback to Working Version

### Immediate Rollback (if development branch has issues)
```bash
# Switch back to working main branch
git checkout main

# Verify you're on main branch
git branch

# Start production version
cd crypto-tracker-backend
python3 app.py  # Runs on port 5000 (production)
```

### Discard Development Changes
```bash
# If you want to completely discard development branch
git checkout main
git branch -D feature/enhanced-analytics

# Start fresh development branch later
git checkout -b feature/enhanced-analytics-v2
```

## Selective Rollback (keep some changes, discard others)

### Rollback Specific Files
```bash
# Stay on development branch but reset specific files
git checkout main -- crypto-tracker-backend/app.py
git checkout main -- crypto-tracker-frontend/src/App.jsx
```

### Rollback Last Commit
```bash
# Undo last commit but keep changes in working directory
git reset --soft HEAD~1

# Undo last commit and discard changes
git reset --hard HEAD~1
```

## Emergency Procedures

### If Development Environment Won't Start
1. **Check ports**: Ensure ports 5001 and 3001 are not in use
   ```bash
   lsof -i :5001
   lsof -i :3001
   ```

2. **Switch to main immediately**:
   ```bash
   git checkout main
   cd crypto-tracker-backend && python3 app.py
   ```

3. **Kill any stuck processes**:
   ```bash
   pkill -f "python.*app.py"
   pkill -f "node.*vite"
   ```

### If Data Gets Corrupted
1. **Backup files to check**:
   - `manual_transactions.json`
   - `price_cache.json`

2. **Restore from main branch**:
   ```bash
   git checkout main -- crypto-tracker-backend/manual_transactions.json
   git checkout main -- crypto-tracker-backend/price_cache.json
   ```

### If Git Gets Confused
1. **See current status**:
   ```bash
   git status
   git log --oneline -5
   ```

2. **Force clean state**:
   ```bash
   git stash  # Save any unsaved changes
   git checkout main
   git reset --hard HEAD
   ```

## Safe Development Practices

### Before Making Changes
```bash
# Always verify you're on development branch
git branch

# Create checkpoint commits frequently
git add .
git commit -m "Checkpoint: before adding new feature X"
```

### Testing New Features
```bash
# Test in development environment first
git checkout feature/enhanced-analytics
# Start dev servers and test

# Only merge to main when satisfied
git checkout main
git merge feature/enhanced-analytics
```

## Recovery Commands

### View Available Branches
```bash
git branch -a
```

### See Recent Commits
```bash
git log --oneline -10
```

### Compare Branches
```bash
git diff main..feature/enhanced-analytics
```

### Restore Specific File from Main
```bash
git checkout main -- path/to/file
```

## Contact Information
- If issues persist, document the error and the steps that led to it
- Keep this file updated with any new procedures discovered during development