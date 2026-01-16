# GitHub Setup and Deployment

## Step 1: Initialize Git Repository

```bash
# Initialize git (if not already)
git init

# Check status
git status
```

## Step 2: Add All Files

```bash
# Add all files
git add .

# Check what will be committed
git status
```

## Step 3: Create Initial Commit

```bash
# Commit with message
git commit -m "Initial commit: EvalBee Professional OMR System

Features:
- Professional OMR detection (99%+ accuracy)
- AI verification with Groq LLaMA 3.2 90B
- Real-time camera capture with corner detection
- QR code integration
- Template-based coordinate system
- Annotated results with visual feedback
- Render.com deployment ready
- Full TypeScript support
- Comprehensive documentation"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `evalbee-omr-system`
3. Description: `Professional OMR Exam System with AI Verification`
4. Visibility: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## Step 5: Connect to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/evalbee-omr-system.git

# Verify remote
git remote -v

# Rename branch to main (if needed)
git branch -M main
```

## Step 6: Push to GitHub

```bash
# Push to GitHub
git push -u origin main
```

## Step 7: Verify Upload

1. Go to your GitHub repository
2. Check that all files are uploaded
3. Verify README.md is displayed

## Step 8: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and configure automatically
5. Add environment variables:
   - `GROQ_API_KEY` (for backend)
   - `VITE_BACKEND_URL` (for frontend)
6. Click "Apply"

### Option B: Manual Setup

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

## Step 9: Configure Environment Variables

### Backend (Render Dashboard)

```
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

### Frontend (Render Dashboard)

```
NODE_VERSION=18
VITE_BACKEND_URL=https://evalbee-backend.onrender.com
```

## Step 10: Test Deployment

### Backend

```bash
curl https://evalbee-backend.onrender.com/
```

### Frontend

Visit: https://evalbee-frontend.onrender.com

## Future Updates

### To update deployment:

```bash
# Make changes to code
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically redeploy on push to main branch.

## Troubleshooting

### Push Rejected

```bash
# If push is rejected, pull first
git pull origin main --rebase
git push origin main
```

### Large Files

If you have large files (>100MB):

```bash
# Check file sizes
git ls-files -s | awk '{print $4, $2}' | sort -n -r | head -20

# Remove large files from git
git rm --cached path/to/large/file
echo "path/to/large/file" >> .gitignore
git commit -m "Remove large file"
```

### Authentication

If prompted for credentials:

1. Use Personal Access Token instead of password
2. Generate token: GitHub Settings → Developer settings → Personal access tokens
3. Use token as password

## Repository Settings

### Recommended Settings:

- ✅ Enable Issues
- ✅ Enable Projects
- ✅ Enable Wiki
- ✅ Enable Discussions (optional)
- ✅ Require pull request reviews
- ✅ Require status checks to pass

### Branch Protection:

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews
   - Require status checks
   - Include administrators

## Collaboration

### Adding Collaborators:

1. Go to Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username
4. Select permission level

### Creating Issues:

1. Go to Issues tab
2. Click "New issue"
3. Add title and description
4. Add labels (bug, enhancement, etc.)

## Documentation

All documentation is in the repository:

- `README.md` - Main documentation
- `RENDER_DEPLOYMENT.md` - Deployment guide
- `EVALBE_CAMERA_SYSTEM.md` - Camera system details
- `TIZIM_HAQIDA_TOLIQ.txt` - System overview (Uzbek)

## Success Checklist

- [ ] Git repository initialized
- [ ] All files committed
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] README.md visible on GitHub
- [ ] Render connected to GitHub
- [ ] Backend deployed and running
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] Camera working (HTTPS)
- [ ] OMR detection working
- [ ] AI verification working (if enabled)

---

**Ready for Production!** 🚀
