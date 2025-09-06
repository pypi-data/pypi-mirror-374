#!/bin/bash

echo "Setting up Docuvert..."

USE_UV=true

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    read -p "uv is not installed. Would you like to install it? (y/N): " INSTALL_UV_CHOICE
    if [[ "$INSTALL_UV_CHOICE" =~ ^[Yy]$ ]]; then
        echo "Please install uv by running:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "Then, add uv to your PATH according to the uv installation instructions."
        echo "After installing uv, please re-run this setup script."
        exit 1
    else
        echo "Proceeding with pip for dependency installation."
        USE_UV=false
    fi
fi

# Install dependencies into the current environment
echo "Installing dependencies into the current environment..."
if [ "$USE_UV" = true ]; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Get the absolute path of the current directory
PROJECT_DIR=$(pwd)

# Create a wrapper script for docuvert in the project directory
WRAPPER_SCRIPT_PATH="$PROJECT_DIR/docuvert"
WRAPPER_SCRIPT_CONTENT="""
#!/bin/bash
SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\"
cd \"\$SCRIPT_DIR\"
uv run python3 -m docuvert.cli \"\$@\"
"""

echo "$WRAPPER_SCRIPT_CONTENT" > "$WRAPPER_SCRIPT_PATH"
chmod +x "$WRAPPER_SCRIPT_PATH"

echo "Docuvert setup complete!"
echo "A 'docuvert' executable wrapper has been created in your project directory: $WRAPPER_SCRIPT_PATH"
echo "To use the 'docuvert' command directly, add an alias to your shell's RC file (e.g., ~/.bashrc, ~/.zshrc):"
echo "  alias docuvert=\"$WRAPPER_SCRIPT_PATH\""
echo "Then, run 'source ~/.bashrc' (or ~/.zshrc) or open a new terminal for changes to take effect."
echo "You can then run: docuvert <input_file> <output_file>"
