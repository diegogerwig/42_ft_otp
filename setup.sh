#!/bin/bash

B_BLUE='\033[1;34m'
B_CYAN='\033[1;36m'
B_GREEN='\033[1;32m'
B_YELLOW='\033[1;33m'
B_RED='\033[1;31m'
NC='\033[0m'

echo -e "\n${B_BLUE}╔═══════════════════════════════════╗${NC}"
echo -e   "${B_BLUE}║          FT_OTP SETUP             ║${NC}"
echo -e   "${B_BLUE}╚═══════════════════════════════════╝${NC}"

# ==========================================
# 1. OS DETECTION AND VENV PATH
# ==========================================
OS_NAME=$(uname -s)
KERNEL_RELEASE=$(uname -r)
USER_HOME=$HOME

if [[ "$KERNEL_RELEASE" == *"Microsoft"* || "$KERNEL_RELEASE" == *"WSL"* ]]; then
    TARGET_DIR="$USER_HOME"
    VENV_NAME=".ft_otp_venv"
    echo -e "\n${B_YELLOW}🖥️  Detected OS: Windows/WSL${NC}"
elif [[ "$OS_NAME" == "Linux" && -d "$USER_HOME/sgoinfre" ]]; then
    TARGET_DIR="$USER_HOME/sgoinfre"
    VENV_NAME="ft_otp_venv"
    echo -e "\n${B_YELLOW}🖥️  Detected OS: Linux (42 Campus)${NC}"
else
    TARGET_DIR="$USER_HOME"
    VENV_NAME="ft_otp_venv"
    echo -e "\n${B_YELLOW}🖥️  Detected OS: Other${NC}"
fi

VENV_PATH="$TARGET_DIR/$VENV_NAME"

echo -e "\n${B_CYAN}📂 Environment path: ${NC}$VENV_PATH"

# ==========================================
# 2. CLEANUP
# ==========================================
if [[ "$1" == "clean" ]]; then
    echo -ne "${B_CYAN}🧹 Cleaning caches...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    echo -e " ${B_GREEN}Done.${NC}"

    if [ -d "$VENV_PATH" ]; then
        echo -ne "${B_YELLOW}⚙️  Deleting old virtual environment...${NC}"
        rm -rf "$VENV_PATH"
        echo -e " ${B_GREEN}Done.${NC}"
    fi
fi

# ==========================================
# 3. VENV CREATION
# ==========================================
if [ ! -d "$VENV_PATH" ]; then
    echo -ne "${B_YELLOW}⚙️  Looking for modern Python...${NC}"

    PYTHON_BIN="python3"
    for py_ver in python3.13 python3.12 python3.11 python3.10 python3.9; do
        if command -v $py_ver >/dev/null 2>&1; then
            PYTHON_BIN=$py_ver
            break
        fi
    done
    echo -e " ${B_GREEN}Selected: $PYTHON_BIN${NC}"

    echo -ne "${B_YELLOW}⚙️  Creating virtual environment...${NC}"
    mkdir -p "$TARGET_DIR"
    $PYTHON_BIN -m venv "$VENV_PATH"

    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        echo -e "\n${B_RED}❌ Critical error: Could not create the virtual environment at $VENV_PATH.${NC}"
        exit 1
    fi
    echo -e " ${B_GREEN}Done.${NC}"
else
    echo -e "${B_GREEN}✅ Virtual environment already exists.${NC}"
fi

# ==========================================
# 4. VENV ACTIVATION & DEPENDENCIES
# ==========================================
echo -e "\n${B_GREEN}✅ Environment ready to use.${NC}"
echo -e "${B_CYAN}🚀 Entering the interactive environment...${NC}"
echo -e "${B_YELLOW}(Type 'exit' or press Ctrl+D to leave and deactivate)${NC}\n"

TMP_RC=$(mktemp)
cat ~/.bashrc > "$TMP_RC" 2>/dev/null
echo "source '$VENV_PATH/bin/activate'" >> "$TMP_RC"

echo "echo -ne '${B_CYAN}🔄 Upgrading pip...${NC}'" >> "$TMP_RC"
echo "python3 -m pip install --upgrade pip > /dev/null 2>&1" >> "$TMP_RC"
echo "echo -e ' ${B_GREEN}Done.${NC}'" >> "$TMP_RC"

echo "if [ -f 'requirements.txt' ]; then" >> "$TMP_RC"
echo "  echo -e '${B_YELLOW}📦 Installing dependencies (requirements.txt)...${NC}'" >> "$TMP_RC"
echo "  python3 -m pip install -r requirements.txt" >> "$TMP_RC"
echo "  if [ \$? -eq 0 ]; then" >> "$TMP_RC"
echo "      echo -e '\n${B_GREEN}✅ Dependencies installed successfully.${NC}'" >> "$TMP_RC"
echo "  else" >> "$TMP_RC"
echo "      echo -e '\n${B_RED}❌ Error installing dependencies. Check the output above.${NC}'" >> "$TMP_RC"
echo "  fi" >> "$TMP_RC"
echo "else" >> "$TMP_RC"
echo "  echo -e '${B_CYAN}ℹ️  No requirements.txt found. Skipping...${NC}'" >> "$TMP_RC"
echo "fi" >> "$TMP_RC"

echo "rm -f '$TMP_RC'" >> "$TMP_RC"
exec bash --rcfile "$TMP_RC"