"""Test what /api/users/me/avatar actually returns"""
import requests

# Test the API endpoint
response = requests.get('http://localhost:5000/api/users/me/avatar')
data = response.json()

print("=" * 70)
print("🔍 /api/users/me/avatar RESPONSE")
print("=" * 70)
print(f"Status: {data.get('status')}")
print(f"Use Mascot: {data.get('use_mascot')}")

avatar = data.get('avatar', {})
print(f"\nAvatar ID: {avatar.get('avatar_id')}")
print(f"Avatar Name: {avatar.get('name')}")
print(f"Variant: {avatar.get('variant')}")

urls = avatar.get('urls', {})
print(f"\nURLs:")
print(f"  - GLB: {urls.get('glb')}")
print(f"  - Thumbnail: {urls.get('thumbnail')}")
print(f"  - Preview: {urls.get('preview')}")

# Check if it's GLB or OBJ
glb_url = urls.get('glb', '')
if '.glb' in glb_url:
    print(f"\n✅ Correct! Using GLB format: {glb_url}")
elif '.obj' in glb_url:
    print(f"\n❌ ERROR! Still using OBJ format: {glb_url}")
else:
    print(f"\n⚠️ Unknown format: {glb_url}")
