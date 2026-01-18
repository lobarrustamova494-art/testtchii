"""
Get exam data from MongoDB
Run this to get 5-imtihon data
"""
import json

# INSTRUCTIONS:
# 1. Open MongoDB Compass or mongosh
# 2. Connect to your database
# 3. Find the exam with ID "5-imtihon" or name "5-imtihon"
# 4. Copy the exam data
# 5. Paste it below

# Example query for MongoDB:
# db.exams.findOne({ $or: [{ _id: "5-imtihon" }, { name: "5-imtihon" }] })

# Or if you're using localStorage in frontend:
# 1. Open browser console (F12)
# 2. Run: localStorage.getItem('exams')
# 3. Find the exam with ID "5-imtihon"
# 4. Copy the data

print("=" * 80)
print("📋 GET EXAM DATA FROM MONGODB")
print("=" * 80)
print()
print("Option 1: MongoDB Compass")
print("-" * 40)
print("1. Open MongoDB Compass")
print("2. Connect to your database")
print("3. Go to 'exams' collection")
print("4. Find exam with ID or name '5-imtihon'")
print("5. Copy the document")
print()
print("Option 2: mongosh (MongoDB Shell)")
print("-" * 40)
print("Run this command:")
print()
print('  db.exams.findOne({ $or: [{ _id: "5-imtihon" }, { name: "5-imtihon" }] })')
print()
print("Option 3: Browser localStorage")
print("-" * 40)
print("1. Open your app in browser")
print("2. Press F12 (Developer Tools)")
print("3. Go to Console tab")
print("4. Run: localStorage.getItem('exams')")
print("5. Find exam with ID '5-imtihon'")
print()
print("Option 4: Check src/utils/storage.ts")
print("-" * 40)
print("The exam might be stored in localStorage")
print()
print("=" * 80)
print()
print("After getting the data, save it to:")
print("  backend/test_images/5-imtihon-data.json")
print()
print("Format:")
print("{")
print('  "id": "5-imtihon",')
print('  "name": "5-imtihon",')
print('  "totalQuestions": 40,')
print('  "answerKey": {')
print('    "1": "A",')
print('    "2": "B",')
print('    ...')
print('  }')
print("}")
print()
