# dep

## Usage
```
/dep ready for production
```

## Status: Deployment Ready ✅

---

## Pre-Flight Checklist (Local)

### Code Quality (5 min)
```bash
# Run type checks
python -m mypy app --strict
python -m mypy ui --strict

# Run linter
pylint app ui

# Check for hardcoded secrets
grep -r "api_key\|password\|secret" app ui | grep -v "# env"
```

### Test Suite (10 min)
```bash
# All tests
pytest --cov=app --cov=ui --cov-fail-under=90

# Check test passing rate
pytest -v --tb=short
```

### Build & Dependencies (5 min)
```bash
# Verify dependencies
pip list

# Check for security vulnerabilities
pip-audit

# Test Streamlit startup
streamlit run ui/main.py --logger.level=debug
```

**✅ All checks passing? Continue to Phase 1**

---

## Phase 1: Local Pre-Flight (10 min)

### Checklist
- [ ] `pytest` passing with >90% coverage
- [ ] `mypy` returns zero errors
- [ ] `pylint` returns zero errors
- [ ] No console errors in `streamlit run`
- [ ] No secrets detected in code
- [ ] CHANGELOG.md updated
- [ ] Type hints on all functions

### Verification
```bash
# Run pre-flight script
./scripts/pre-flight-check.sh

# Output should be:
# ✓ Type checking passed
# ✓ Tests passed (coverage: 92%)
# ✓ Linting passed
# ✓ No secrets detected
# ✓ Ready for deployment
```

---

## Phase 2: Commit & Push (5 min)

### Git Workflow
```bash
# Ensure clean working directory
git status

# Stage all changes
git add -A

# Commit with conventional format
git commit -m "feat(auth): add Google Sign-in with Firebase"
# or
git commit -m "fix(ocr): handle EasyOCR model download timeout"

# Verify commit message
git log --oneline -1

# Push to dev branch
git push origin dev
```

### Commit Message Format
```
type(scope): description

[optional body with more details]

[optional footer with issue reference]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `security`

---

## Phase 3: GitHub Actions & Review

### Automated Checks
GitHub Actions will run:
1. Python type checking (`mypy`)
2. Test suite (`pytest`)
3. Linting (`pylint`)
4. Security scanning (`pip-audit`)
5. Build verification

### Review Checklist
- [ ] All checks ✅ passing
- [ ] Code review approved
- [ ] No conflicts with main
- [ ] CHANGELOG.md present
- [ ] Tests passing >90%

**✅ All checks pass? Continue to Phase 4**

---

## Phase 4: Deployment (15 min)

### Option 1: Streamlit Cloud
```bash
# 1. Push to GitHub main branch
git checkout main
git pull origin dev
git push origin main

# 2. Streamlit Cloud auto-deploys
# Monitor at https://share.streamlit.io/[username]/[repo]
```

### Option 2: Docker Local
```bash
# 1. Build Docker image
docker build -t text-mining-app .

# 2. Run container
docker run -p 8501:8501 \
  -e FIREBASE_CREDENTIALS_PATH=/config/firebase_config.json \
  -v $(pwd)/config:/config \
  text-mining-app

# 3. Test at http://localhost:8501
```

### Option 3: Cloud Run (Google Cloud)
```bash
# 1. Authenticate with Google Cloud
gcloud auth login

# 2. Build and deploy
gcloud run deploy text-mining-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# 3. Set environment variables
gcloud run deploy text-mining-app \
  --set-env-vars=ENVIRONMENT=production \
  --update-secrets=FIREBASE_CREDENTIALS=firebase_config:latest
```

---

## Phase 5: Verification & Monitoring (10 min)

### Health Check
```bash
# Test main page loads
curl -I https://your-app.com
# Expected: HTTP/1.1 200 OK

# Test API health
curl https://your-app.com/api/health
# Expected: {"status": "healthy"}

# Test authentication
# Open in browser, try Google Sign-in
```

### UI Testing
1. Open https://your-app.com
2. Test main features:
   - [ ] Google Sign-in works
   - [ ] Can upload keywords file
   - [ ] Can upload documents
   - [ ] Can process files
   - [ ] Can download results
3. Check browser console for errors
4. Check Streamlit logs

### Log Monitoring
```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/app.log

# View system logs (Cloud Run)
gcloud run logs read text-mining-app

# Check for errors
grep -i "error" ~/.streamlit/logs/app.log
```

---

## Phase 6: Rollback (if needed)

### Quick Rollback
```bash
# Streamlit Cloud
# Redeploy previous commit via Streamlit Cloud dashboard

# Docker
docker run -p 8501:8501 text-mining-app:previous-version

# Cloud Run
gcloud run deploy text-mining-app \
  --image gcr.io/project/text-mining-app:previous-version
```

**Post-Rollback:**
1. Verify site is back online
2. Check health endpoints
3. Document what failed in incident report
4. Don't retry until root cause fixed

---

## Deployment Decision Tree

```
Is deployment ready?
├─ Yes: Continue to Phase 1
└─ No:
   ├─ Tests failing? Fix tests, commit, push
   ├─ Type errors? Add type hints, commit, push
   ├─ Linting errors? Fix code style, commit, push
   ├─ Secrets detected? Remove, re-test, push new commit
   └─ Other issues? Debug locally, fix, test, commit, push

All pre-flight checks pass?
├─ Yes: Commit → GitHub Actions → Deploy
└─ No: Fix issues locally, re-run checks

Deployment successful?
├─ Yes: 🎉 Production live
└─ No: Rollback (Phase 6) → Investigate

Errors in production?
├─ Minor: Monitor and create bug fix PR
├─ Major: Immediate rollback
└─ Security: Rollback + notify team
```

---

## Typical Deployment Time

| Phase | Time | Action |
|-------|------|--------|
| Pre-Flight | 5 min | Run local checks |
| Code Review | 10-30 min | GitHub checks + review |
| Deployment | 5-10 min | Deploy to platform |
| Verification | 5 min | Health checks + testing |
| **Total** | **25-55 min** | Typically 30-40 min |

---

## Quick Checklist Before Deploying

```
Pre-Flight (Local):
□ pytest passing (>90%)
□ mypy passing
□ pylint passing
□ No console errors

Code:
□ Committed with conventional message
□ Pushed to dev branch
□ CHANGELOG.md updated

GitHub:
□ All checks passing ✅
□ Code review approved

Deployment:
□ Selected deployment platform
□ Environment variables configured
□ Secrets properly set

Verification:
□ https://your-app loads
□ Google Sign-in works
□ File upload works
□ Processing works
□ Browser console clean
```

---

*Last Updated: December 31, 2025*
*Project: TEXT-MINING v1.0*
*Deployment: Streamlit Cloud / Docker / Cloud Run*
*Status: Production Ready*
