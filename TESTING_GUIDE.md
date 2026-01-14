# QR Code System - Testing Guide

## 🎯 Maqsad

QR code tizimini to'liq test qilish va ishlashini tekshirish.

## 📋 Prerequisites

### Frontend

```bash
npm install
# qrcode library allaqachon o'rnatilgan (package.json'da)
```

### Backend

```bash
cd backend
pip install -r requirements.txt
# pyzbar library allaqachon o'rnatilgan (requirements.txt'da)
```

## 🧪 Test Bosqichlari

### 1. Frontend Test - QR Code Generation

**Maqsad**: PDF'da QR code to'g'ri generate bo'lishini tekshirish

**Qadamlar**:

1. Frontend'ni ishga tushiring:

```bash
npm run dev
```

2. Browser'da ochiladi: http://localhost:5173

3. Login qiling (istalgan username/password)

4. Yangi exam yarating:

   - Exam nomi: "Test Matematika"
   - Sana: bugun
   - Subjects: 1 ta (masalan "Algebra")
   - Sections: 1 ta (masalan "Tenglamalar", 10 savol)

5. "Varaqlarni Yuklab Olish" tugmasini bosing

6. PDF yuklab olinadi

7. PDF'ni oching va tekshiring:

   - ✅ Top-right corner'da QR code bor
   - ✅ QR code aniq ko'rinadi
   - ✅ QR code 25mm x 25mm atrofida

8. QR code'ni telefon bilan scan qiling:
   - ✅ JSON ma'lumot ko'rinadi
   - ✅ examId, examName, layout, structure bor
   - ✅ Ma'lumotlar to'g'ri

**Expected Result**:

```json
{
  "examId": "...",
  "examName": "Test Matematika",
  "setNumber": 1,
  "version": "2.0",
  "layout": {
    "questionsPerRow": 2,
    "bubbleSpacing": 8,
    ...
  }
}
```

### 2. Backend Test - QR Code Detection

**Maqsad**: Backend QR code'ni to'g'ri o'qishini tekshirish

**Qadamlar**:

1. PDF'ni print qiling (yoki screenshot oling)

2. Scan qiling yoki photo oling (minimum 800x1100px)

3. Image'ni backend/temp/ papkasiga qo'ying:

```bash
# Windows
copy exam_sheet.jpg backend\temp\
```

4. Test script'ni ishga tushiring:

```bash
cd backend
python test_qr.py temp/exam_sheet.jpg
```

5. Output'ni tekshiring:

**Expected Output**:

```
============================================================
QR CODE SYSTEM TEST
============================================================

1. Loading image: temp/exam_sheet.jpg
   ✅ Image loaded: (1754, 1240, 3)

2. Initializing QR Reader...
   ✅ QR Reader initialized

3. Reading QR code...
   Searching for QR code...
   QR code found! Data length: 450 bytes
   ✅ QR code successfully read: Exam 'Test Matematika', Version 2.0
      Total questions: 10
   ✅ QR CODE DETECTED!

   Exam Info:
   - Exam ID: exam-...
   - Exam Name: Test Matematika
   - Set Number: 1
   - Version: 2.0
   - Total Questions: 10

   Layout Parameters:
   - questionsPerRow: 2
   - bubbleSpacing: 8
   - bubbleRadius: 3
   - rowHeight: 6
   - gridStartX: 25
   - gridStartY: 113
   - questionSpacing: 90
   - firstBubbleOffset: 8

4. Extracting layout for coordinate mapper...
   ✅ Layout extracted:
   - questions_per_row: 2
   - bubble_spacing_mm: 8
   - bubble_radius_mm: 3
   - row_height_mm: 6
   - grid_start_x_mm: 25
   - grid_start_y_mm: 113
   - question_spacing_mm: 90
   - first_bubble_offset_mm: 8

5. Testing coordinate calculation...
   ✅ First question coordinates:
   - Question: 1
   - Bubbles: 5
     A: (123.4, 567.8) r=8.9
     B: (145.6, 567.8) r=8.9
     C: (167.8, 567.8) r=8.9
     D: (190.0, 567.8) r=8.9
     E: (212.2, 567.8) r=8.9

============================================================
✅ QR CODE SYSTEM TEST PASSED!
============================================================
```

### 3. Full Integration Test

**Maqsad**: To'liq tizimni test qilish (PDF → Print → Scan → Grade)

**Qadamlar**:

1. Backend'ni ishga tushiring:

```bash
cd backend
python main.py
```

2. Frontend'da exam yarating va PDF yuklab oling

3. PDF'ni print qiling

4. Varaqni to'ldiring (random javoblar)

5. Scan qiling (yoki photo oling)

6. Frontend'da "Varaqlarni Tekshirish" bo'limiga o'ting

7. Image'ni upload qiling

8. Processing log'ni kuzating:

**Expected Log**:

```
=== NEW GRADING REQUEST ===
File: exam_sheet.jpg
File saved: ...

STEP 1/6: Image Processing...
✅ Image processed successfully

STEP 2/6: QR Code Detection...
Searching for QR code...
QR code found! Data length: 450 bytes
✅ QR code successfully read: Exam 'Test Matematika', Version 2.0
   Total questions: 10
✅ QR Code detected! Using QR layout data
   QR Layout: {'questions_per_row': 2, 'bubble_spacing_mm': 8, ...}

STEP 3/6: Coordinate Calculation...
Using layout from QR code
Calculated coordinates for 10 questions

STEP 4/6: OMR Detection...
OMR Detection complete: 10/10 detected, 0 uncertain, 0 multiple marks

STEP 5/6: AI Verification skipped

STEP 6/6: Grading...
=== GRADING COMPLETE ===
Duration: 1.8s
Score: 8/10 (80%)
```

9. Natijalarni tekshiring:
   - ✅ QR code detected
   - ✅ Barcha savollar o'qildi
   - ✅ Confidence yuqori (90%+)
   - ✅ No warnings

### 4. Fallback Test (QR code bo'lmasa)

**Maqsad**: QR code bo'lmaganda default layout ishlatishini tekshirish

**Qadamlar**:

1. QR code'siz PDF yarating (eski versiya yoki QR code'ni o'chiring)

2. Backend'ga upload qiling

3. Log'ni kuzating:

**Expected Log**:

```
STEP 2/6: QR Code Detection...
Searching for QR code...
First attempt failed, trying enhanced detection...
Trying top-right corner region...
No QR code found in image after all attempts
⚠️  No QR code found, using default layout

STEP 3/6: Coordinate Calculation...
Using default layout (no QR code)
```

4. Tizim default layout bilan ishlashda davom etadi

## 📊 Success Criteria

### QR Code Generation (Frontend)

- ✅ QR code PDF'da ko'rinadi
- ✅ QR code scan qilinadi
- ✅ Ma'lumotlar to'g'ri

### QR Code Detection (Backend)

- ✅ QR code topiladi
- ✅ JSON parse qilinadi
- ✅ Layout extract qilinadi
- ✅ Coordinates hisoblanadi

### Full Integration

- ✅ QR code detected log'da
- ✅ Layout from QR code ishlatiladi
- ✅ Accuracy 95%+
- ✅ No uncertain answers

### Fallback

- ✅ QR code bo'lmasa warning
- ✅ Default layout ishlatiladi
- ✅ Tizim ishlashda davom etadi

## 🐛 Troubleshooting

### QR Code topilmayapti

**Sabablari**:

1. Image quality past
2. QR code damaged
3. QR code juda kichik
4. Scan quality past

**Yechimlar**:

1. Yuqori resolution scan qiling (min 800x1100px)
2. QR code aniq ko'rinishini tekshiring
3. Yaxshi yorug'likda photo oling
4. PDF'ni qayta generate qiling

### Layout ma'lumotlari noto'g'ri

**Sabablari**:

1. PDF generator'da xato
2. QR code data corrupted
3. JSON parse error

**Yechimlar**:

1. PDF'ni qayta generate qiling
2. QR code'ni telefon bilan scan qilib tekshiring
3. Log'larni tekshiring

### Coordinates noto'g'ri

**Sabablari**:

1. QR layout noto'g'ri
2. Image dimensions noto'g'ri
3. Coordinate mapper xatosi

**Yechimlar**:

1. test_qr.py script bilan test qiling
2. Image dimensions tekshiring
3. Log'larda coordinate calculation'ni kuzating

## 📝 Test Checklist

- [ ] Frontend: QR code generate bo'ladi
- [ ] Frontend: QR code PDF'da ko'rinadi
- [ ] Frontend: QR code scan qilinadi
- [ ] Backend: pyzbar o'rnatilgan
- [ ] Backend: test_qr.py ishlaydi
- [ ] Backend: QR code topiladi
- [ ] Backend: Layout extract qilinadi
- [ ] Backend: Coordinates hisoblanadi
- [ ] Integration: Full workflow ishlaydi
- [ ] Integration: Accuracy 95%+
- [ ] Fallback: Default layout ishlaydi

## 🎉 Success!

Agar barcha testlar o'tsa:

**✅ QR CODE SYSTEM FULLY OPERATIONAL!**

Tizim production uchun tayyor! 🚀
