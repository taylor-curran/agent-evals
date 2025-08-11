# SonarQube Scan Instructions - Agent Evals Project

## Objective
Run a SonarQube scan on the `taylor-curran/agent_evals` repository and analyze security vulnerabilities and code quality issues.

## Target Repository
- **Repository**: `taylor-curran/agent_evals`
- **Project Key**: `taylor-curran_agent_evals`
- **Organization**: `taylor-curran-1`
- **SonarCloud URL**: `https://sonarcloud.io/project/overview?id=taylor-curran_agent_evals`

## Prerequisites & Setup

### Step 1: Verify Java Version
SonarQube scanner requires **Java 17+**. Check current version:
```bash
java -version
```

**Install Java 17+ if needed:**
```bash
# macOS with Homebrew
brew install openjdk@17
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install -y openjdk-17-jdk
```

### Step 2: Install SonarQube Scanner

**macOS with Homebrew:**
```bash
brew install sonar-scanner
```

**Linux - Manual Installation:**
```bash
curl -L -o sonar-scanner-cli.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
unzip sonar-scanner-cli.zip
sudo mv sonar-scanner-6.2.1.4610-linux-x64 /opt/sonar-scanner
sudo ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
```

**Verify Installation:**
```bash
sonar-scanner --version
```

### Step 3: Authentication
- Access the `SONARQUBE_TOKEN` from your secrets/environment variables
- **Never hardcode the token** - always reference it as an environment variable

## Configuration

### Step 4: Create sonar-project.properties
Navigate to `/Users/taylorcurran/Documents/dev/agent_evals` and create `sonar-project.properties`:

```properties
# Project identification
sonar.projectKey=taylor-curran_agent_evals
sonar.organization=taylor-curran-1
sonar.host.url=https://sonarcloud.io

# Project metadata
sonar.projectName=Agent Evals
sonar.projectVersion=1.0

# Python source configuration
sonar.sources=src,data_ai_service
sonar.tests=tests,data_ai_service/tests

# Python version
sonar.python.version=3.12

# Exclusions (important for clean analysis)
sonar.exclusions=**/.venv/**,**/__pycache__/**,**/*.pyc,**/.pytest_cache/**,**/node_modules/**,**/.git/**,**/.scannerwork/**,**/plan/**,**/TEMP_*.md,**/*.db

# Test exclusions
sonar.test.exclusions=**/test_*.py,**/*_test.py,**/tests/**

# Coverage (if you have coverage reports)
# sonar.python.coverage.reportPaths=coverage.xml
```

### Step 5: Prepare the Project (Optional but Recommended)
```bash
cd /Users/taylorcurran/Documents/dev/agent_evals

# Activate virtual environment if needed
source .venv/bin/activate

# Install dependencies to ensure clean analysis
pip install -r requirements.txt

# Run tests to generate any test artifacts (optional)
python -m pytest data_ai_service/tests/ -v
```

## Execution

### Step 6: Run the Scanner
```bash
# Navigate to project root
cd /Users/taylorcurran/Documents/dev/agent_evals

# Ensure Java 17+ is in PATH
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"        # macOS
# OR
export PATH="/usr/lib/jvm/java-17-openjdk-amd64/bin:$PATH"  # Linux

# Run scanner with token
sonar-scanner -Dsonar.token=$SONARQUBE_TOKEN
```

## Troubleshooting (Critical Section)

### Common Issues & Solutions:

#### 1. "Automatic Analysis enabled" Error (Most Common Blocker)
**Error**: `"You are running manual analysis while Automatic Analysis is enabled"`

**Solutions:**
- **Option A**: Access existing results at: `https://sonarcloud.io/project/overview?id=taylor-curran_agent_evals`
- **Option B**: Disable Automatic Analysis in SonarCloud:
  1. Go to project settings: `https://sonarcloud.io/project/administration/analysis_method?id=taylor-curran_agent_evals`
  2. Switch from "Automatic Analysis" to "CI-based analysis"
- **Option C**: Ask user to disable automatic analysis

#### 2. Authentication Issues
**Symptoms**: 403 errors, authentication failures

**Solutions:**
- Verify token: `echo $SONARQUBE_TOKEN`
- Use `-Dsonar.token=$SONARQUBE_TOKEN` (NOT `-Dsonar.login=`)
- Ensure token has proper organization permissions

#### 3. Java Version Issues
**Symptoms**: Scanner fails to start, Java compatibility errors

**Solutions:**
- Verify Java 17+: `java -version`
- Set correct PATH before running scanner
- Ensure JAVA_HOME points to Java 17+

#### 4. Python Source Issues
**Symptoms**: "No sources found", empty analysis

**Solutions:**
- Verify directories exist: `ls -la src/ data_ai_service/`
- Check exclusions aren't too broad
- Ensure Python files are present in source directories

#### 5. Virtual Environment Issues
**Symptoms**: Import errors, missing dependencies

**Solutions:**
- Activate virtual environment: `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Verify Python version: `python --version`

## Results Analysis

### Step 7: Access Results
Navigate to: `https://sonarcloud.io/project/overview?id=taylor-curran_agent_evals`

### Key Areas to Review:
1. **Security Hotspots**: `https://sonarcloud.io/project/security_hotspots?id=taylor-curran_agent_evals`
2. **Vulnerabilities**: `https://sonarcloud.io/project/issues?id=taylor-curran_agent_evals&types=VULNERABILITY`
3. **Code Smells**: `https://sonarcloud.io/project/issues?id=taylor-curran_agent_evals&types=CODE_SMELL`
4. **Overall Issues**: `https://sonarcloud.io/project/issues?id=taylor-curran_agent_evals`

### Expected Analysis Focus for Python Project:
- **Security Hotspots** (require manual review)
- **High/Critical Vulnerabilities** (immediate attention)
- **Hardcoded credentials** (API keys, tokens)
- **SQL injection vulnerabilities** (database operations)
- **Insecure HTTP requests** (GitHub API, external calls)
- **Code complexity** and maintainability issues
- **Test coverage** gaps

## Success Criteria Checklist
- [ ] Java 17+ installed and verified
- [ ] SonarQube scanner installed and working
- [ ] Python virtual environment activated
- [ ] Dependencies installed from requirements.txt
- [ ] Scanner runs without "Automatic Analysis" conflict
- [ ] Scan completes with "ANALYSIS SUCCESSFUL" message
- [ ] Results accessible in SonarCloud dashboard
- [ ] Security analysis reviewed and documented
- [ ] Top vulnerabilities/hotspots identified

## Alternative: Accessing Existing Results
If CLI scan fails due to automatic analysis conflict:
1. Access SonarCloud project directly: `https://sonarcloud.io/project/overview?id=taylor-curran_agent_evals`
2. Review latest automatic analysis results
3. Export vulnerability data via SonarCloud web interface
4. Generate reports from existing scan data

## Project-Specific Notes

### Agent Evals Project Structure:
```
agent_evals/
├── src/                    # Main source code
├── data_ai_service/        # Microservice (FastAPI)
├── tests/                  # Test files
├── plan/                   # Documentation (excluded)
├── .venv/                  # Virtual environment (excluded)
└── requirements.txt        # Dependencies
```

### Key Security Areas to Focus On:
- **GitHub API integration** (token handling)
- **Database operations** (SQL injection risks)
- **OpenAI API calls** (API key security)
- **File I/O operations** (path traversal)
- **External HTTP requests** (SSRF risks)

## Quick Command Summary
```bash
# Full execution sequence
cd /Users/taylorcurran/Documents/dev/agent_evals
source .venv/bin/activate
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
sonar-scanner -Dsonar.token=$SONARQUBE_TOKEN
```

This configuration is specifically tailored for your Python-based agent evaluation platform with the Data+AI Service microservice architecture.
