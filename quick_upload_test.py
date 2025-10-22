import requests

# Upload the 10-word list
words = """Admire
Brisk
Curious
Dazzle
Eager
Fragile
Glimpse
Humble
Mingle
Timid"""

print("Uploading 10-word list...")
session = requests.Session()

response = session.post(
    "http://localhost:15000/api/upload",
    files={'file': ('10words.txt', words.encode())}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Check wordbank
print("\nChecking wordbank...")
wb_response = session.get("http://localhost:15000/api/wordbank")
print(f"Wordbank status: {wb_response.status_code}")

if wb_response.status_code == 200:
    data = wb_response.json()
    words_list = data.get('words', [])
    print(f"Words count: {len(words_list)}")
    
    if words_list:
        print(f"First word: {words_list[0]}")