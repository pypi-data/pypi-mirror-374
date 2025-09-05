#!/bin/bash
# SubForge - Local Development Installation Script
# Created: 2025-09-02 20:00 UTC-3 São Paulo
#
# This script installs SubForge in development mode with all optional dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo " ____        _     _____                    "
echo "/ ___| _   _| |__ |  ___|__  _ __ __ _  ___ "
echo "\___ \| | | | '_ \| |_ / _ \| '__/ _\` |/ _ \\"
echo " ___) | |_| | |_) |  _| (_) | | | (_| |  __/"
echo "|____/ \__,_|_.__/|_|  \___/|_|  \__, |\___|"
echo "                                 |___/      "
echo -e "${NC}"
echo -e "${GREEN}SubForge Development Installation Script${NC}\n"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo -e "${RED}Error: Python $required_version or higher is required (found $python_version)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version${NC}"

# Check if we're in the SubForge directory
if [ ! -f "setup.py" ] || [ ! -d "subforge" ]; then
    echo -e "${RED}Error: Please run this script from the SubForge root directory${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "\n${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install SubForge in development mode with all extras
echo -e "\n${YELLOW}Installing SubForge in development mode...${NC}"
pip install -e ".[full]"
echo -e "${GREEN}✓ SubForge installed${NC}"

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"

# Check if subforge command is available
if command -v subforge &> /dev/null; then
    echo -e "${GREEN}✓ 'subforge' command is available${NC}"
    subforge_location=$(which subforge)
    echo -e "  Location: $subforge_location"
else
    echo -e "${YELLOW}⚠ 'subforge' command not in PATH${NC}"
    echo -e "  Run 'source venv/bin/activate' to use it"
fi

# Check if module import works
if python3 -c "import subforge" 2>/dev/null; then
    echo -e "${GREEN}✓ SubForge module can be imported${NC}"
    version=$(python3 -c "import subforge; print(subforge.__version__)")
    echo -e "  Version: $version"
else
    echo -e "${RED}✗ Failed to import SubForge module${NC}"
fi

# Check if templates are accessible
template_count=$(find subforge/templates -name "*.md" 2>/dev/null | wc -l)
if [ "$template_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Templates are accessible ($template_count templates found)${NC}"
else
    echo -e "${YELLOW}⚠ No templates found${NC}"
fi

echo -e "\n${GREEN}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation complete!${NC}\n"
echo -e "To use SubForge, you can now:"
echo -e "  ${BLUE}1. Activate the virtual environment:${NC}"
echo -e "     source venv/bin/activate"
echo -e ""
echo -e "  ${BLUE}2. Use the command line interface:${NC}"
echo -e "     subforge --help"
echo -e "     subforge init"
echo -e "     subforge analyze"
echo -e ""
echo -e "  ${BLUE}3. Or use as a Python module:${NC}"
echo -e "     python -m subforge --help"
echo -e ""
echo -e "  ${BLUE}4. For system-wide installation:${NC}"
echo -e "     pip install ."
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}\n"