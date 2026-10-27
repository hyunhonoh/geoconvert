#!/usr/bin/env bash
# Builds geoconvert-<version>.tar.gz for install via Apps -> Install app from file.
#
# Usage:   ./make_package.sh [OUTPUT_DIR]     (default: ./dist)
set -euo pipefail

APP_ID="geoconvert"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${1:-$SRC/dist}"

VERSION="$(awk -F'= *' '/^\[/{s=$0} /^version *=/ && s=="[launcher]"{print $2; exit}' "$SRC/default/app.conf")"
VERSION="${VERSION:-0.0.0}"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/$APP_ID"
mkdir -p "$PKG"

# '.*' drops every dotfile/dotdir (.git, .DS_Store, ._* …); AppInspect rejects them.
rsync -a \
  --exclude '.*' \
  --exclude '/local/' \
  --exclude '/dist/' \
  --exclude 'make_package.sh' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'metadata/local.meta' \
  "$SRC/" "$PKG/"

# macOS tar turns xattrs into AppleDouble "._<file>" members otherwise.
xattr -cr "$PKG" 2>/dev/null || true
find "$PKG" \( -name '._*' -o -name '.DS_Store' \) -delete
# AppInspect rejects execute bits outside bin/.
find "$PKG" -type d -exec chmod 755 {} + && find "$PKG" -type f -exec chmod 644 {} +

cat > "$PKG/app.manifest" <<MANIFEST
{
  "schemaVersion": "2.0.0",
  "info": {
    "title": "GeoConvert",
    "id": { "group": null, "name": "$APP_ID", "version": "$VERSION" },
    "author": [ { "name": "HyunHo Noh", "email": null, "company": null } ],
    "releaseDate": null,
    "description": "Search command that converts KATEC (Naver TM128) coordinates to WGS84.",
    "classification": { "intendedAudience": null, "categories": [], "developmentStatus": null },
    "commonInformationModels": null,
    "license": { "name": "Apache-2.0", "text": "LICENSE", "uri": null },
    "privacyPolicy": { "name": null, "text": null, "uri": null },
    "releaseNotes": { "name": null, "text": null, "uri": null }
  },
  "dependencies": null,
  "tasks": null,
  "inputGroups": null,
  "incompatibleApps": null,
  "platformRequirements": null
}
MANIFEST

mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/${APP_ID}-${VERSION}.tar.gz"
rm -f "$OUT"
COPYFILE_DISABLE=1 tar --uid 0 --gid 0 --uname root --gname wheel -czf "$OUT" -C "$STAGE" "$APP_ID"

# `tar -tzf` hides AppleDouble members on macOS, so check with Python.
python3 - "$OUT" <<'CHECK'
import sys, tarfile
names = tarfile.open(sys.argv[1]).getnames()
bad = [n for n in names
       if any(p.startswith('.') for p in n.split('/'))
       or n.split('/')[1:2] == ['local']]
if bad:
    sys.exit('Hidden files or local/ in package:\n  ' + '\n  '.join(bad))
CHECK

echo "Package: $OUT"
