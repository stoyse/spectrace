# Windows Setup Guide for Spectrace with Ghidra Integration

This guide will walk you through setting up Spectrace on Windows with full Ghidra binary analysis support.

## 📋 Prerequisites

### Required Software
- [ ] Windows 10/11
- [ ] Git for Windows
- [ ] Python 3.11+ 
- [ ] Node.js 18+
- [ ] Java 17+ (for Ghidra)
- [ ] OpenAI API Key

## 🚀 Step-by-Step Installation

### Step 1: Install Required Software

#### 1.1 Install Git for Windows
1. Download from: https://git-scm.com/download/win
2. Run installer with default settings
3. Verify: Open Command Prompt and run `git --version`

#### 1.2 Install Python 3.11+
1. Download from: https://www.python.org/downloads/windows/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Run installer as Administrator
4. Verify: Open Command Prompt and run `python --version`

#### 1.3 Install Node.js 18+
1. Download from: https://nodejs.org/en/download/
2. Run installer with default settings
3. Verify: Open Command Prompt and run `node --version` and `npm --version`

#### 1.4 Install Java 17+
1. Download OpenJDK 17 from: https://adoptium.net/temurin/releases/
2. Download the `.msi` installer for Windows x64
3. Run installer with default settings
4. Verify: Open Command Prompt and run `java --version`

### Step 2: Download and Install Ghidra

#### 2.1 Download Ghidra
1. Go to: https://github.com/NationalSecurityAgency/ghidra/releases
2. Download `ghidra_11.0.3_PUBLIC_20240410.zip` (or latest version)
3. Extract to `C:\ghidra` (create the folder if needed)
4. Your Ghidra path should be: `C:\ghidra\ghidra_11.0.3_PUBLIC`

#### 2.2 Set Environment Variables
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. In "System Variables" section, click "New" and add:
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot` (adjust version)
5. Add another variable:
   - Variable name: `GHIDRA_INSTALL_DIR`
   - Variable value: `C:\ghidra\ghidra_11.0.3_PUBLIC`
6. Edit the `PATH` variable and add:
   - `%JAVA_HOME%\bin`
   - `%GHIDRA_INSTALL_DIR%\support`
7. Click OK to save

#### 2.3 Verify Ghidra Installation
1. Open a **new** Command Prompt (important for environment variables)
2. Run: `analyzeHeadless`
3. You should see Ghidra usage information (not an error)

### Step 3: Clone and Setup the Project

#### 3.1 Clone Repository
```cmd
cd C:\
git clone https://github.com/your-repo/spectrace.git
cd spectrace
```

#### 3.2 Setup Backend (API)
```cmd
cd api
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.3 Setup Frontend (Dashboard)
```cmd
cd ..\dashboard
npm install
```

### Step 4: Configure Environment

#### 4.1 Create API Environment File
1. In the `api` folder, create a file called `.env`
2. Add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### 4.2 Create Temporary Directories
```cmd
mkdir C:\temp\ghidra_projects
mkdir C:\temp\spectrace_uploads
```

### Step 5: Test Installation

#### 5.1 Test Ghidra Service
```cmd
cd api
python -c "from services.ghidra_service import GhidraDecompiler; print('Ghidra service imported successfully')"
```

#### 5.2 Start Backend
```cmd
cd api
python main.py
```
- Keep this terminal open
- You should see: "Uvicorn running on http://127.0.0.1:8000"
- Test by opening: http://localhost:8000/docs

#### 5.3 Start Frontend (New Terminal)
```cmd
cd dashboard
npm run dev
```
- Keep this terminal open
- You should see: "Local: http://localhost:5173/"
- Open: http://localhost:5173

## 🔧 Windows-Specific Configuration

### PowerShell Alternative Commands
If using PowerShell instead of Command Prompt:

#### Set Environment Variables (PowerShell)
```powershell
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot', [System.EnvironmentVariableTarget]::Machine)
[System.Environment]::SetEnvironmentVariable('GHIDRA_INSTALL_DIR', 'C:\ghidra\ghidra_11.0.3_PUBLIC', [System.EnvironmentVariableTarget]::Machine)
```

#### Test Commands (PowerShell)
```powershell
# Test Java
java -version

# Test Python
python --version

# Test Node
node --version

# Test Ghidra (from any directory)
analyzeHeadless
```

### Windows Firewall Configuration
If you encounter connection issues:
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Add Python and Node.js to allowed apps

## 📝 Common Windows Issues & Solutions

### Issue 1: "Python not found"
**Solution**: 
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`

### Issue 2: "Java not found" 
**Solution**:
1. Verify Java installation: `where java`
2. Set JAVA_HOME to the JDK directory (not JRE)
3. Restart Command Prompt after setting environment variables

### Issue 3: "analyzeHeadless not recognized"
**Solution**:
1. Verify Ghidra extraction path
2. Check GHIDRA_INSTALL_DIR environment variable
3. Add `%GHIDRA_INSTALL_DIR%\support` to PATH
4. Restart Command Prompt

### Issue 4: Port already in use
**Solution**:
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 5: Permission denied errors
**Solution**:
1. Run Command Prompt as Administrator
2. Or change temp directories to user folder:
   ```cmd
   mkdir %USERPROFILE%\temp\ghidra_projects
   mkdir %USERPROFILE%\temp\spectrace_uploads
   ```

## 🧪 Testing Your Setup

### Test 1: API Health Check
Visit: http://localhost:8000/
You should see a welcome message with API information.

### Test 2: Frontend Connection
Visit: http://localhost:5173/
You should see the Spectrace dashboard.

### Test 3: Binary Upload (Create Test Binary)
Create a simple test binary:
```cmd
echo "This is a test binary file" > test.bin
```
Try uploading this through the dashboard in binary mode.

### Test 4: Ghidra Integration
The real test is uploading a small ELF or PE file, but you can test the service:
```cmd
cd api
python -c "
import asyncio
from services.ghidra_service import GhidraDecompiler
async def test():
    gd = GhidraDecompiler()
    print('Ghidra service initialized successfully')
    print(f'Install dir: {gd.ghidra_install_dir}')
    print(f'Java home: {gd.java_home}')
    print(f'Analyzer path exists: {gd.analyze_headless_path.exists()}')
asyncio.run(test())
"
```

## 📞 Getting Help

If you encounter issues:

1. **Check Prerequisites**: Ensure all software is properly installed
2. **Environment Variables**: Restart Command Prompt after setting variables
3. **Permissions**: Try running as Administrator
4. **Paths**: Use full paths, avoid spaces in folder names
5. **Firewall**: Check Windows Firewall settings

## 🎯 Success Checklist

- [ ] Python 3.11+ installed and in PATH
- [ ] Node.js 18+ installed 
- [ ] Java 17+ installed and JAVA_HOME set
- [ ] Ghidra extracted to C:\ghidra
- [ ] GHIDRA_INSTALL_DIR environment variable set
- [ ] analyzeHeadless command works
- [ ] API starts on http://localhost:8000
- [ ] Frontend starts on http://localhost:5173
- [ ] Can access both URLs in browser
- [ ] OpenAI API key configured in .env file

Once all items are checked, your Windows installation is complete! 🎉

## 🚀 Next Steps

1. Upload some test files (both text and binary modes)
2. Try the analysis features
3. Check the API documentation at http://localhost:8000/docs
4. Review the logs for any warnings or errors

---

*Windows Setup Guide for Spectrace v2.0 with Ghidra Integration*