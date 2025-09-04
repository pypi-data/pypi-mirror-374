#!/bin/sh

# This script uninstalls the 'code-speak' project using
# either uvx (preferred) or pipx.

PACKAGE_NAME="code_speak"

echo "[CHECK] Looking for a global package installer..."

INSTALLER=""
if command -v uvx >/dev/null 2>&1; then
    INSTALLER="uvx"
elif command -v pipx >/dev/null 2>&1; then
    INSTALLER="pipx"
else
    echo "Error: Neither 'uvx' nor 'pipx' is installed or in your PATH"
    echo "Please install one of them to continue"
    echo "  - To install pipx: 'pip install pipx'"
    echo "  - To install uv: 'pip install uv'"
    exit 1
fi

echo " + '${INSTALLER}' will be used to un-install 'code_speak' in 5s..."
sleep 5

echo "[UNINSTALL] Attempting to uninstall '$PACKAGE_NAME'..."

sh -c "$INSTALLER uninstall '$PACKAGE_NAME'"

if [ $? -eq 0 ]; then
  echo "[DONE] Uninstallation successful!"
  echo "'$PACKAGE_NAME' has been removed from your system."
else
  echo "[ERROR] Uninstall command failed"
  echo "It's possible '$PACKAGE_NAME' was not installed or was installed with a different tool"
fi