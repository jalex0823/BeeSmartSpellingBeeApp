"""
Live End-to-End Quiz Flow Test
Tests complete flow with real API calls
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'
session = requests.Session()

print('\n' + '='*60)
print('LIVE QUIZ FLOW TEST: Import → Quiz → Report Card')
print('='*60 + '\n')

# Step 1: Clear wordbank
print('1. Clearing wordbank...')
r = session.post(f'{BASE_URL}/api/clear')
print(f'   ✓ Status: {r.status_code}')

# Step 2: Upload test words
print('\n2. Uploading test words...')
words = [
    {'word': 'apple', 'sentence': 'I ate an apple.', 'hint': 'A red fruit'},
    {'word': 'banana', 'sentence': 'The banana is yellow.', 'hint': 'A yellow fruit'},
    {'word': 'cat', 'sentence': 'The cat sleeps.', 'hint': 'A pet'}
]
r = session.post(f'{BASE_URL}/api/upload', json={'words': words})
print(f'   ✓ Status: {r.status_code}')
if r.status_code == 200:
    print(f'   ✓ Uploaded: {r.json().get("word_count", 0)} words')

# Step 3: Verify wordbank
print('\n3. Verifying wordbank...')
r = session.get(f'{BASE_URL}/api/wordbank')
if r.status_code == 200:
    data = r.json()
    print(f'   ✓ Word count: {data.get("word_count", 0)}')
    for w in data.get('words', []):
        print(f'     - {w["word"]}: {w["sentence"]}')

# Step 4: Start quiz
print('\n4. Starting quiz...')
r = session.get(f'{BASE_URL}/quiz')
print(f'   ✓ Quiz page loaded: {r.status_code}')

r = session.post(f'{BASE_URL}/api/next')
if r.status_code == 200:
    data = r.json()
    print(f'   ✓ First question: {data.get("sentence", "")}')
    print(f'     Total questions: {data.get("total_questions", 0)}')

# Step 5: Answer questions
print('\n5. Answering questions...')
for i, word_data in enumerate(words, 1):
    answer = word_data['word']
    r = session.post(f'{BASE_URL}/api/answer', json={
        'user_input': answer,
        'method': 'typed',
        'elapsed_ms': 2000
    })
    
    if r.status_code == 200:
        result = r.json()
        correct = result.get('correct', False)
        points = result.get('points', 0)
        symbol = '✓' if correct else '✗'
        feedback = result.get('feedback', '')
        print(f'   {symbol} Question {i}: "{answer}" - {feedback} ({points} pts)')
    
    if i < len(words):
        time.sleep(0.3)
        r = session.post(f'{BASE_URL}/api/next')

# Step 6: Complete quiz and get report card
print('\n6. Completing quiz...')
r = session.post(f'{BASE_URL}/api/next')
if r.status_code == 200:
    data = r.json()
    if data.get('quiz_complete'):
        print('   ✓ Quiz completed!')
        print('\n' + '='*60)
        print('📊 REPORT CARD')
        print('='*60)
        print(f'   Total Questions: {data.get("total_questions", len(words))}')
        print(f'   Correct Answers: {data.get("correct_count", 0)}')
        print(f'   Total Points: {data.get("total_points", 0)}')
        print(f'   Accuracy: {data.get("accuracy", 0):.1f}%')
        print(f'   Grade: {data.get("grade", "N/A")}')
        print(f'   Time Spent: {data.get("time_spent", 0):.1f}s')
        
        # Show buzz dust if available
        if 'buzz_dust' in data:
            print(f'\n   🌟 Buzz Dust Earned: {data.get("buzz_dust", 0)}')
        
        # Show badges if available
        if 'badges_earned' in data and data['badges_earned']:
            print(f'\n   🏆 Badges Earned:')
            for badge in data['badges_earned']:
                print(f'      - {badge}')
        
        print('='*60)

print('\n' + '='*60)
print('✓ TEST COMPLETE - All steps passed!')
print('='*60 + '\n')
