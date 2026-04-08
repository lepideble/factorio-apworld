#!/bin/sh

set -e

cd $(dirname $(dirname $0))

CONFIG="$1"
VERSION="$2"

WORLD="factorio_$CONFIG"

# Create build folders
mkdir --parents build output

# Remove old builds
rm --force --recursive "build/$WORLD"
rm --force "output/$WORLD.apworld"

# Build
cp --recursive base "build/$WORLD"

rm "build/$WORLD/debug.py"

rm --force "build/$WORLD/config"
cp --recursive "config/$CONFIG" "build/$WORLD/config"

if [ -d "build/$WORLD/config/mod" ]; then
    rsync --recursive "build/$WORLD/config/mod/" "build/$WORLD/mod/"
    rm -r "build/$WORLD/config/mod"
fi

GAME_NAME=$(PYTHONPATH="build/$WORLD" python3 -c "from config import game_name ; print(game_name)")

cat << EOF > "build/$WORLD/archipelago.json"
{
    "game": "$GAME_NAME",
    "world_version": "$VERSION",
    "compatible_version": 7
}
EOF

(cd build && zip --recurse-paths "../output/$WORLD.apworld" "$WORLD" --exclude \*__pycache__\*)
