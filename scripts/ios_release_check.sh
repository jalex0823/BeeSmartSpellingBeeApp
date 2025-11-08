#!/usr/bin/env bash
set -euo pipefail

if ! command -v node >/dev/null 2>&1; then
  echo "❌ Node is not installed. Install via: brew install node" >&2
  exit 1
fi
if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "❌ Xcode command line tools are missing. Run: xcode-select --install" >&2
  exit 1
fi

pushd "$(dirname "$0")/../mobile-wrapper" >/dev/null
if [ ! -f package.json ]; then
  echo "❌ package.json missing in mobile-wrapper/" >&2
  exit 1
fi

jq .name package.json >/dev/null 2>&1 || {
  echo "ℹ️  Installing jq for JSON parsing (optional)"; brew install jq || true;
}

echo "📦 Ensuring npm deps…"
npm ci

echo "🔄 Syncing Capacitor…"
npx cap sync

echo "✅ Environment looks good. Next steps:"
echo "  1) npx cap add ios  # if ios/ missing"
echo "  2) npx cap open ios"
echo "  3) In Xcode: set Team/Bundle ID, version 1.7 (build 7), add icons/splash"
echo "  4) Archive and upload via Organizer"

popd >/dev/null
