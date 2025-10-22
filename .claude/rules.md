# Critical Safety Rules for Claude Code

**Context:** These rules were created after a serious incident where personal information was committed to GitHub due to violations of basic safety protocols.

## Git Operation Rules

### 🔴 CRITICAL: Repository Context Pinning
**NEVER** rely on ambient working directory for git operations.

**Required pattern:**
```bash
# GOOD - explicit repository
git -C ~/git/tommcd/notes status

# GOOD - verify then operate
cd ~/git/tommcd/notes
git status
cd -

# BAD - ambient cwd (DO NOT USE)
git status
```

**Before ANY git command:**
1. State which repository you're operating in
2. Use absolute path or verify pwd
3. Confirm remote if pushing: `git remote -v`

---

### 🔴 CRITICAL: Commit Gating
**NEVER** commit without explicit user verification.

**Required workflow:**
```bash
# 1. Show status
git status

# 2. Show what will be committed
git diff --staged

# 3. Present to user with clear message:
# "I'm about to commit these changes to [repository]:
# [show diff output]
#
# Proceed with commit? (yes/no)"

# 4. WAIT for explicit approval

# 5. Only then commit
git commit -m "message"
```

**No exceptions.** Even for "obvious" changes.

---

### 🔴 CRITICAL: Tool Rejection = Full Stop
If ANY tool use is rejected by user:

1. ✋ **STOP** all related workflows immediately
2. 🚫 **DO NOT** proceed with dependent operations
3. ❓ **ASK** user explicitly: "Tool was rejected. How should I proceed?"
4. ⏸️ **WAIT** for explicit instruction

**Example:**
```
User: [rejects Edit tool]
Claude: "I see the edit was rejected. Should I:
  A) Try a different approach
  B) Skip this step
  C) Stop and wait for instructions

Please advise before I continue."
```

---

### 🔴 CRITICAL: Explicit File Paths in Git
**ALWAYS** use explicit paths relative to repo root.

```bash
# GOOD
git add ./README.md
git add ./docs/notes/index.md

# BAD - ambiguous
git add README.md

# REQUIRED before add
git rev-parse --show-toplevel  # verify you're in correct repo
```

---

### 🔴 CRITICAL: Re-read Files Before Commits
If user has edited a file manually:

1. **MUST** re-read file from disk using Read tool
2. **MUST** verify staged content matches user's intent
3. **MUST** show diff to user
4. **MUST** wait for confirmation

**Never trust cached/earlier versions.**

---

## Communication Rules

### 🔴 CRITICAL: Read Complete Messages
**Process user's ENTIRE message before acting.**

**Required workflow:**
1. Read FULL message to end
2. Note ALL questions, instructions, feedback
3. Formulate complete response addressing ALL points
4. Execute only after full understanding

**User quote:** *"Please, you must actually read my entire response before proceeding"*

---

### 🔴 CRITICAL: Clarify Ambiguous Instructions
If user says "continue" or similar:

1. ❓ Check context: what were they waiting for?
2. 🤔 If unclear, ask: "Continue with [specific action]?"
3. ✅ Get explicit confirmation
4. 🚫 **DO NOT ASSUME**

**Example:**
```
User: "continue"
Claude: "Just to confirm - should I:
  A) Commit the changes now, or
  B) Wait while you finish editing the file?

I want to make sure I understand correctly."
```

---

## Sensitive Information Rules

### 🔴 CRITICAL: Personal Information Review
This repository uses conditional git config for personal email (tcmcdermott@gmail.com).

**Before committing files that might contain personal info:**

1. Check for email addresses
2. Check for names/phone numbers
3. Check for API keys/tokens/credentials
4. Check for file paths that reveal username
5. **Show findings to user**
6. **Wait for explicit approval**

**High-risk files:**
- README.md, CONTRIBUTING.md (may contain contact info)
- .env, .env.*, credentials.* (secrets)
- Config files (may contain paths/emails)

---

### 🔴 CRITICAL: Multi-Repo Operation Tracking
When working with multiple repositories:

**Current repos:**
- `~/git/tommcd/notes` - knowledge base (this repo)
- `~/git/tommcd/tommcd` - profile README
- `~/git/tommcd/tommcd.github.io` - landing page

**Required workflow:**
```bash
# 1. State current repo at start of operation
echo "Operating in: notes repository"

# 2. Use absolute paths for cross-repo operations
git -C ~/git/tommcd/notes status
git -C ~/git/tommcd/tommcd status

# 3. Verify remote before push
git remote -v
# Expected output shows tommcd/* repos

# 4. Confirm with user which repo you're pushing to
echo "About to push to: [repository name]"
```

---

## Enforcement

⚠️ **These rules are MANDATORY safety requirements, not suggestions.**

**Historical violations led to:**
- ❌ Personal information exposed on GitHub
- ❌ Commits made without user approval
- ❌ Operations performed on wrong repositories
- ❌ User instructions ignored

**When in doubt:** ❓ **ASK THE USER** before proceeding.

**Zero tolerance:** If you cannot follow these rules, stop and ask for help.
