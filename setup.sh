#!/bin/bash

# --- 7-Phase Sprint Roadmap: Foundation Setup ---
# This script installs system-level forensic tools and Python requirements.

set -e  # Exit on error

echo "-------------------------------------------------------"
echo "Initializing Forensic Sprint Environment..."
echo "-------------------------------------------------------"

# 1. Detect Operating System
OS_TYPE="$(uname)"

if [ "$OS_TYPE" == "Linux" ]; then
    if [ -f /etc/debian_version ]; then
        echo "[+] Linux (Debian/Ubuntu) detected."
        echo "[+] Updating package lists..."
        sudo apt-get update -y
        
        echo "[+] Installing ExifTool (libimage-exiftool-perl)..."
        sudo apt-get install -y libimage-exiftool-perl
    else
        echo "[!] Unsupported Linux distribution. Please install ExifTool manually."
    fi

elif [ "$OS_TYPE" == "Darwin" ]; then
    echo "[+] macOS detected."
    if command -v brew >/dev/null 2>&1; then
        echo "[+] Installing ExifTool via Homebrew..."
        brew install exiftool
    else
        echo "[!] Homebrew not found. Please install Homebrew or ExifTool manually."
        exit 1
    fi

else
    echo "[!] Unknown OS: $OS_TYPE. Manual installation of ExifTool required."
fi

# 2. Verify ExifTool Installation
if command -v exiftool >/dev/null 2>&1; then
    echo "[SUCCESS] ExifTool version $(exiftool -ver) is ready."
else
    echo "[ERROR] ExifTool installation failed."
    exit 1
fi

# 3. Setup Python Virtual Environment (Optional but Recommended)
if [ ! -d "venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "[+] Activating virtual environment..."
source venv/bin/activate

# 4. Install Python Dependencies
if [ -f "requirements.txt" ]; then
    echo "[+] Installing Python libraries from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[!] requirements.txt not found. Skipping Python library install."
fi

echo "-------------------------------------------------------"
echo "[COMPLETE] Environment is ready for Phase 2."
echo "Run 'source venv/bin/activate' to start developing."
echo "-------------------------------------------------------"