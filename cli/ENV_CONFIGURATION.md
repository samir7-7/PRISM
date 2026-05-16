# Environment Configuration Guide

This document describes the environment variables used by the PRISM CLI and provides the template for `.env.example`.

---

## Environment Variables

### Required Variables

#### `PRISM_BACKEND_URL`

- **Description:** URL of the PRISM backend API
- **Default:** `http://localhost:8000`
- **Example:** `http://localhost:8000`, `https://api.prism.dev`
- **Required:** Yes (for production use)

#### `PRISM_GITHUB_TOKEN`

- **Description:** GitHub Personal Access Token for API access
- **Default:** None
- **Example:** `ghp_1234567890abcdefghijklmnopqrstuvwxyz`
- **Required:** Yes (for private repositories)
- **Scopes needed:**
  - `repo` - Full control of private repositories
  - `public_repo` - Access to public repositories (if only analyzing public repos)

### Optional Variables

#### `PRISM_REPO_URL`

- **Description:** Default repository URL to analyze
- **Default:** None
- **Example:** `https://github.com/your-org/your-repo`
- **Required:** No (can be provided via `--repo` flag)

---

## `.env.example` Template

Create this file as `cli/.env.example`:

```env
# ============================================
# PRISM CLI Environment Configuration
# ============================================
# Copy this file to .env and fill in your values
# cp .env.example .env

# --------------------------------------------
# Backend Configuration
# --------------------------------------------

# PRISM Backend API URL
# The URL where the PRISM backend is running
# Default: http://localhost:8000
PRISM_BACKEND_URL=http://localhost:8000

# --------------------------------------------
# GitHub Configuration
# --------------------------------------------

# GitHub Personal Access Token
# Generate at: https://github.com/settings/tokens
# Required scopes:
#   - repo (for private repositories)
#   - public_repo (for public repositories only)
PRISM_GITHUB_TOKEN=ghp_your_token_here

# Default Repository URL (optional)
# If set, you don't need to specify --repo flag
# Format: https://github.com/owner/repository
PRISM_REPO_URL=https://github.com/your-org/your-repo

# --------------------------------------------
# Advanced Configuration (optional)
# --------------------------------------------

# Request timeout in seconds
# Default: 60
# PRISM_TIMEOUT=60

# Default output format
# Options: pretty, json
# Default: pretty
# PRISM_OUTPUT_FORMAT=pretty

# Auto-open browser after analysis
# Options: true, false
# Default: false
# PRISM_AUTO_OPEN=false
```

---

## Setup Instructions

### 1. Create `.env` File

```bash
# Navigate to CLI directory
cd cli/

# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.
```

### 2. Generate GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name: "PRISM CLI"
4. Select scopes:
   - ✅ `repo` (if analyzing private repositories)
   - ✅ `public_repo` (if only analyzing public repositories)
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)
7. Paste into `.env` file

### 3. Configure Backend URL

**For local development:**

```env
PRISM_BACKEND_URL=http://localhost:8000
```

**For staging:**

```env
PRISM_BACKEND_URL=http://staging.prism.dev:8000
```

**For production:**

```env
PRISM_BACKEND_URL=https://api.prism.dev
```

### 4. Verify Configuration

```bash
# Test with demo mode (doesn't require GitHub token)
prism demo

# Test with real analysis
prism analyze pr-142 --repo https://github.com/owner/repo
```

---

## Configuration Priority

Settings are resolved in this order (highest to lowest priority):

1. **CLI Flags** - Explicitly passed via command line

   ```bash
   prism analyze pr-142 --backend http://localhost:8000 --token ghp_xxx
   ```

2. **Environment Variables** - Set in shell

   ```bash
   export PRISM_BACKEND_URL=http://localhost:8000
   prism analyze pr-142
   ```

3. **`.env` File** - In current directory

   ```bash
   # Reads from ./cli/.env
   prism analyze pr-142
   ```

4. **`.env` File** - In home directory

   ```bash
   # Reads from ~/.prism/.env
   prism analyze pr-142
   ```

5. **Defaults** - Built-in defaults
   - `PRISM_BACKEND_URL`: `http://localhost:8000`
   - `PRISM_TIMEOUT`: `60`
   - `PRISM_OUTPUT_FORMAT`: `pretty`
   - `PRISM_AUTO_OPEN`: `false`

---

## Security Best Practices

### ⚠️ Never Commit `.env` Files

The `.env` file contains sensitive tokens and should **never** be committed to version control.

**Verify `.gitignore` includes:**

```gitignore
# Environment files
.env
.env.local
.env.*.local
```

### 🔒 Token Security

1. **Use fine-grained tokens** when possible
2. **Set expiration dates** on tokens
3. **Rotate tokens regularly** (every 90 days)
4. **Revoke unused tokens** immediately
5. **Never share tokens** via chat, email, or screenshots

### 🔐 Token Storage Alternatives

For production environments, consider:

1. **Environment variables** in CI/CD

   ```yaml
   # GitHub Actions
   env:
     PRISM_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

2. **Secret management services**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

3. **OS keychain** (future enhancement)
   ```bash
   # Store in macOS keychain
   security add-generic-password -s prism-cli -a github-token -w ghp_xxx
   ```

---

## Troubleshooting

### Token Not Working

**Symptom:**

```
✗ GitHub authentication failed
  Hint: check your PRISM_GITHUB_TOKEN in .env
```

**Solutions:**

1. Verify token starts with `ghp_`
2. Check token hasn't expired
3. Verify required scopes are enabled
4. Try generating a new token

### Backend Unreachable

**Symptom:**

```
✗ Cannot reach PRISM backend at http://localhost:8000
```

**Solutions:**

1. Check backend is running: `curl http://localhost:8000/healthz`
2. Verify URL in `.env` matches backend port
3. Check firewall settings
4. Try `--backend` flag to override

### Configuration Not Loading

**Symptom:**
CLI uses defaults instead of `.env` values

**Solutions:**

1. Verify `.env` file exists in CLI directory
2. Check file permissions: `chmod 600 .env`
3. Ensure no syntax errors in `.env`
4. Try absolute path: `PRISM_CONFIG=/path/to/.env prism analyze pr-142`

---

## Example Configurations

### Local Development

```env
PRISM_BACKEND_URL=http://localhost:8000
PRISM_GITHUB_TOKEN=ghp_dev_token_here
PRISM_REPO_URL=https://github.com/your-org/your-repo
PRISM_AUTO_OPEN=true
```

### CI/CD Pipeline

```env
PRISM_BACKEND_URL=https://api.prism.dev
PRISM_GITHUB_TOKEN=${GITHUB_TOKEN}
PRISM_OUTPUT_FORMAT=json
PRISM_TIMEOUT=120
```

### Demo/Presentation

```env
PRISM_BACKEND_URL=http://localhost:8000
# No token needed for demo mode
PRISM_AUTO_OPEN=true
```

### Multi-Repository Analysis

```env
PRISM_BACKEND_URL=http://localhost:8000
PRISM_GITHUB_TOKEN=ghp_token_with_org_access
# Don't set PRISM_REPO_URL - specify per command
```

---

## Implementation Notes

When implementing `cli/config.py`, use this structure:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    """PRISM CLI configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PRISM_",
        case_sensitive=False,
    )

    # Required settings
    backend_url: str = "http://localhost:8000"
    github_token: str | None = None

    # Optional settings
    repo_url: str | None = None
    timeout: int = 60
    output_format: Literal["pretty", "json"] = "pretty"
    auto_open: bool = False
```

---

## Related Documentation

- **Setup Guide:** [`README.md`](README.md#configuration)
- **Architecture:** [`CLI_PLAN.md`](CLI_PLAN.md)
- **Troubleshooting:** [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- **Development:** [`DEVELOPMENT.md`](DEVELOPMENT.md)
