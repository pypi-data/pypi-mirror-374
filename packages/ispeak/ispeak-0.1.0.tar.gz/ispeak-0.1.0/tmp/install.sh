#!/bin/sh

# exit immediately if a command exits with a non-zero status
set -e

echo "[CHECK] Verifying dependencies..."

# check for hatch
if ! command -v hatch >/dev/null 2>&1; then
    echo "Error: 'hatch' is not installed or not in your PATH"
    echo "Please install it first, e.g: pipx install hatch"
    exit 1
fi
echo "  + hatch is installed"

# check for
INSTALLER=""
if command -v pipx >/dev/null 2>&1; then
    INSTALLER="pipx"
else
    echo "[ERROR] 'pipx' is not installed or in your PATH"
    echo "Please install one of them to continue"
    echo "  - To install pipx: 'pip install pipx'"
    exit 1
fi
INSTALLER="pipx"

echo "  + '${INSTALLER}' will be used for global installation in 5s..."
sleep 5


# build
echo "[BUILD] Building 'code_speak' via hatch..."
WHEEL=$(hatch build -t wheel)
if [ -z "$WHEEL" ]; then
    echo "[ERROR] Build failed! Try running manually for more details:"
    echo "  hatch --verbose build -t wheel"
    exit 1
fi
echo "[SUCCESS] Built package: $WHEEL"

# install
echo "[INSTALL] Installing globally via '$INSTALLER'..."
# use 'sh -c' to correctly execute the command and --force flag to overwrite existing
sh -c "$INSTALLER install '$WHEEL' --force"

if [ $? -eq 0 ]; then
  echo "[DONE] You can now run 'code_speak' from anywhere in your terminal"
else
  echo "[ERROR] Installation failed. Please check the output above."
  exit 1
fi
