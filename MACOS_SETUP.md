# 🍎 macOS Setup Guide for SpecTrace with Ghidra Integration

This comprehensive guide will help you install SpecTrace on macOS with full Ghidra binary analysis capabilities.

---

## 📋 **Prerequisites**

### **System Requirements**
- **macOS**: 10.15+ (Catalina or newer)
- **Architecture**: Intel (x86_64) or Apple Silicon (arm64)
- **RAM**: 8GB+ recommended (4GB minimum)
- **Disk Space**: 5GB+ free space
- **Internet**: Required for downloads and API calls

### **Required Software**
- [ ] **Xcode Command Line Tools** (for development tools)
- [ ] **Homebrew** (package manager)
- [ ] **Python 3.11+** (programming language)
- [ ] **Node.js 18+** (JavaScript runtime)
- [ ] **Java 17+** (for Ghidra)
- [ ] **OpenAI API Key** (for AI analysis)

---

## 🚀 **Installation Steps**

### **Step 1: Install Xcode Command Line Tools**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
# Should output: /Applications/Xcode.app/Contents/Developer
# or: /Library/Developer/CommandLineTools
```

### **Step 2: Install Homebrew**

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (follow the instructions shown after install)
# For Intel Macs:
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc

# For Apple Silicon Macs:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc

# Verify installation
brew --version
```

### **Step 3: Install Python 3.11+**

```bash
# Install Python using Homebrew
brew install python@3.11

# Create symlink for python command
brew link python@3.11

# Verify installation
python3 --version
python3 -m pip --version

# Optional: Create python alias
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc
```

### **Step 4: Install Node.js 18+**

```bash
# Install Node.js using Homebrew
brew install node

# Verify installation
node --version
npm --version

# Should show Node.js 18+ and corresponding npm version
```

### **Step 5: Install Java 17+**

```bash
# Install OpenJDK 17 using Homebrew
brew install openjdk@17

# Add Java to PATH
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc  # Apple Silicon
# OR for Intel Macs:
# echo 'export PATH="/usr/local/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

# Set JAVA_HOME
echo 'export JAVA_HOME="/opt/homebrew/opt/openjdk@17"' >> ~/.zshrc      # Apple Silicon
# OR for Intel Macs:
# echo 'export JAVA_HOME="/usr/local/opt/openjdk@17"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify installation
java --version
echo $JAVA_HOME
```

### **Step 6: Download and Install Ghidra**

```bash
# Create installation directory
sudo mkdir -p /opt/ghidra
sudo chown $(whoami) /opt/ghidra

# Download Ghidra
cd /opt/ghidra
curl -L -O https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.3_build/ghidra_11.0.3_PUBLIC_20240410.zip

# Extract Ghidra
unzip ghidra_11.0.3_PUBLIC_20240410.zip
rm ghidra_11.0.3_PUBLIC_20240410.zip

# Set Ghidra environment variables
echo 'export GHIDRA_INSTALL_DIR="/opt/ghidra/ghidra_11.0.3_PUBLIC"' >> ~/.zshrc
echo 'export PATH="$GHIDRA_INSTALL_DIR/support:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify Ghidra installation
analyzeHeadless
# Should display Ghidra usage information
```

---

## 📦 **Project Setup**

### **Step 7: Clone SpecTrace Repository**

```bash
# Clone the repository
git clone https://github.com/your-repo/spectrace.git
cd spectrace

# Verify project structure
ls -la
```

### **Step 8: Setup Backend (API)**

```bash
# Navigate to API directory
cd api

# Create Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment configuration
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
GHIDRA_INSTALL_DIR=/opt/ghidra/ghidra_11.0.3_PUBLIC
JAVA_HOME=/opt/homebrew/opt/openjdk@17
EOF

# Verify backend setup
python -c "
import sys
print(f'Python version: {sys.version}')
print('✅ Python environment ready!')

try:
    from services.ghidra_service import GhidraDecompiler
    gd = GhidraDecompiler()
    print('✅ Ghidra service imported successfully!')
    print(f'Java Home: {gd.java_home}')
    print(f'Ghidra Dir: {gd.ghidra_install_dir}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### **Step 9: Setup Frontend (Dashboard)**

```bash
# Navigate to dashboard directory
cd ../dashboard

# Install Node.js dependencies
npm install

# Verify frontend setup
npm run build
npm run lint

# Test development server (optional)
npm run dev
# Should start on http://localhost:5173
# Press Ctrl+C to stop
```

---

## 🎯 **Running SpecTrace**

### **Method 1: Development Mode**

**Terminal 1 - Backend:**
```bash
cd ~/path/to/spectrace/api
source venv/bin/activate  # If using virtual environment
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd ~/path/to/spectrace/dashboard
npm run dev
```

**Access Points:**
- **Frontend Dashboard**: http://localhost:5173
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **Method 2: Production Mode**

```bash
# Build frontend for production
cd dashboard
npm run build

# Start backend with production settings
cd ../api
uvicorn main:app --host 0.0.0.0 --port 8000

# Serve frontend (separate terminal)
cd ../dashboard
npm run preview
```

---

## 🔧 **macOS-Specific Configuration**

### **Apple Silicon (M1/M2/M3) Considerations**

If you're using Apple Silicon, some adjustments may be needed:

```bash
# Check your architecture
uname -m
# arm64 = Apple Silicon, x86_64 = Intel

# For Apple Silicon, ensure correct paths:
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export GHIDRA_INSTALL_DIR="/opt/ghidra/ghidra_11.0.3_PUBLIC"
export PATH="/opt/homebrew/bin:/opt/homebrew/opt/openjdk@17/bin:$GHIDRA_INSTALL_DIR/support:$PATH"

# If you encounter Rosetta-related issues with Node.js:
arch -arm64 brew install node  # Force ARM64 version
```

### **Intel Mac Considerations**

For Intel Macs, paths will be slightly different:

```bash
# Intel Mac paths:
export JAVA_HOME="/usr/local/opt/openjdk@17"
export PATH="/usr/local/bin:/usr/local/opt/openjdk@17/bin:$GHIDRA_INSTALL_DIR/support:$PATH"
```

### **Security Settings**

macOS may block unsigned applications. If you encounter security warnings:

```bash
# Allow unsigned applications (if needed)
sudo spctl --master-disable

# Or add specific exceptions in:
# System Preferences > Security & Privacy > General
```

---

## 🧪 **Testing Your Installation**

### **Test 1: Backend Health Check**
```bash
cd api
python -c "
import asyncio
from services.ghidra_service import GhidraDecompiler

async def test():
    try:
        decompiler = GhidraDecompiler()
        print('✅ Ghidra decompiler initialized')
        print(f'Java version: {decompiler.java_home}')
        print(f'Ghidra path: {decompiler.ghidra_install_dir}')
        print(f'Analyzer exists: {decompiler.analyze_headless_path.exists()}')
        return True
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

result = asyncio.run(test())
print(f'Backend test: {"PASSED" if result else "FAILED"}')
"
```

### **Test 2: Frontend Build**
```bash
cd dashboard
npm run build
echo "✅ Frontend build successful"
```

### **Test 3: Full Integration**
```bash
# Start backend (in background)
cd api && python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Test API endpoint
curl http://localhost:8000/ | grep -q "SpecTrace" && echo "✅ API accessible" || echo "❌ API failed"

# Test decompile endpoint (with dummy data)
curl -X POST http://localhost:8000/api/v1/decompile \
  -F "file=@/bin/ls" \
  -w "%{http_code}\n" | grep -q "200\|400" && echo "✅ Decompile endpoint responding" || echo "❌ Decompile endpoint failed"

# Stop background backend
kill $BACKEND_PID
```

---

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| **"command not found: brew"** | Install Homebrew following Step 2 |
| **"python3: command not found"** | Install Python using `brew install python@3.11` |
| **"java: command not found"** | Install Java using `brew install openjdk@17`, set JAVA_HOME |
| **"analyzeHeadless: command not found"** | Set GHIDRA_INSTALL_DIR and add to PATH |
| **"Module not found" errors** | Activate virtual environment: `source venv/bin/activate` |
| **Port 8000/5173 already in use** | Kill processes: `lsof -ti:8000 \| xargs kill -9` |
| **Permission denied errors** | Use `sudo` for system-level operations |
| **Rosetta/architecture issues** | Use `arch -arm64 brew install` for Apple Silicon |

### **Environment Debugging**

```bash
# Debug environment variables
echo "Python: $(which python3)"
echo "Node: $(which node)"  
echo "Java: $(which java)"
echo "Java Home: $JAVA_HOME"
echo "Ghidra Dir: $GHIDRA_INSTALL_DIR"
echo "PATH: $PATH"

# Test Ghidra specifically
ls -la "$GHIDRA_INSTALL_DIR/support/analyzeHeadless"
"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" 2>&1 | head -5
```

### **Performance Optimization**

```bash
# Increase Java heap size for large binaries
export JAVA_OPTS="-Xmx4g -Xms2g"

# Optimize npm for faster installs
npm config set progress=false
npm config set fund=false

# Use faster DNS (if experiencing slow downloads)
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

---

## 📝 **macOS Development Tips**

### **Shell Configuration**

Add this to your `~/.zshrc` for a complete setup:

```bash
# SpecTrace Environment
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"  # Apple Silicon
export GHIDRA_INSTALL_DIR="/opt/ghidra/ghidra_11.0.3_PUBLIC"
export PATH="$GHIDRA_INSTALL_DIR/support:$JAVA_HOME/bin:$PATH"

# Python aliases
alias python=python3
alias pip=pip3

# SpecTrace shortcuts
alias spectrace-api="cd ~/path/to/spectrace/api && source venv/bin/activate && python main.py"
alias spectrace-web="cd ~/path/to/spectrace/dashboard && npm run dev"
alias spectrace-test="cd ~/path/to/spectrace/api && pytest -v"
```

### **IDE Recommendations**

- **VS Code**: Excellent Python/TypeScript support
  ```bash
  brew install --cask visual-studio-code
  code --install-extension ms-python.python
  code --install-extension bradlc.vscode-tailwindcss
  ```

- **PyCharm**: Professional Python development
  ```bash
  brew install --cask pycharm
  ```

### **Homebrew Maintenance**

```bash
# Keep Homebrew updated
brew update && brew upgrade

# Clean up old versions
brew cleanup

# Check for issues
brew doctor
```

---

## ✅ **Success Checklist**

- [ ] Xcode Command Line Tools installed
- [ ] Homebrew installed and working
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Java 17+ installed (`java --version`)
- [ ] Ghidra downloaded and extracted
- [ ] Environment variables set correctly
- [ ] SpecTrace repository cloned
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] OpenAI API key configured
- [ ] Backend starts successfully (`python main.py`)
- [ ] Frontend starts successfully (`npm run dev`)
- [ ] Can access dashboard at http://localhost:5173
- [ ] Can access API at http://localhost:8000/docs

---

## 🎉 **You're Ready!**

Once all checklist items are complete, you have a fully functional SpecTrace installation on macOS! 

### **Next Steps:**
1. **🔬 Upload test files** to try both text and binary analysis modes
2. **📖 Read the main README** for usage instructions
3. **🐛 Report issues** if you encounter any problems
4. **⭐ Star the repo** if you find SpecTrace useful!

### **Getting Help:**
- **Documentation**: Check the main [README.md](README.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-repo/spectrace/issues)
- **Community**: Join discussions on [GitHub Discussions](https://github.com/your-repo/spectrace/discussions)

---

*macOS Setup Guide for SpecTrace v2.0 with Ghidra Integration*

**🍎 Happy analyzing on macOS! 🛡️**