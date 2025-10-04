#!/bin/bash

# OLC Installation Script
set -e  # Exit on error

echo "Installing OLC - OSINT Link Collector..."

# Move to installation directory
mv ../olc ~/olc && mv ~/olc ~/.olc

# Cohere API key from environment
COHERE_API_KEY=$(env | grep COHERE_API_KEY | cut -d "=" -f2)

if [ -z "$COHERE_API_KEY" ]; then
    echo "Warning: COHERE_API_KEY not found in environment"
    echo "Please set it before running olc"
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/.olc/olcEnv

# Install dependencies
echo "Installing dependencies..."
source ~/.olc/olcEnv/bin/activate && pip install -r ~/.olc/requirements.txt

# Create executable wrapper
echo "Creating executable wrapper..."
mkdir -p ~/.local/bin
path="$HOME/.local/bin/olc"
cat > "$path" << 'EOF'
#!/bin/bash
export COHERE_API_KEY='COHERE_API_KEY_PLACEHOLDER'
source ~/.olc/olcEnv/bin/activate && python3 ~/.olc/olc.py "$@"
EOF

# Replace API key placeholder
sed -i "s/COHERE_API_KEY_PLACEHOLDER/$COHERE_API_KEY/" "$path"

# Make executable
chmod +x "$path"

echo "Installation complete!"
echo "Make sure ~/.local/bin is in your PATH"
echo "Run: export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "Or add it to your ~/.bashrc or ~/.zshrc"
