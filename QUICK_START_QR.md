# 🚀 Quick Start - QR Code System

## Tezkor Ishga Tushirish (5 daqiqa)

### 1. Dependencies O'rnatish

```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
cd ..
```

**Tekshirish**: `qrcode` va `pyzbar` o'rnatilganligini tekshiring:

```bash
# Frontend
npm list qrcode

# Backend
pip show pyzbar
```

### 2. Backend Ishga Tushirish

```bash
cd backend
python main.py
```

**Expected Output**:

```
============================================================
PROFESSIONAL OMR GRADING SYSTEM v3.0
============================================================
Host: 0.0.0.0
Port: 8000
AI Verification: ENABLED/DISABLED
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Frontend Ishga Tushirish

Yangi terminal oching:

```bash
npm run dev
```

**Expected Output**:

```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 4. Tizimni Test Qilish

#### A. Exam Yaratish

1. Browser'da oching: http://localhost:5173
2. Login qiling (istalgan username/password)
3. "Yangi Imtihon" tugmasini bosing
4. Exam ma'lumotlarini kiriting:
   ```
   Nomi: Test QR System
   Sana: bugun
   Vaqt: 90 daq
   Variantlar: 1
   ```
5. Subject qo'shing:
   ```
   Mavzu: Matematika
   ```
6. Section qo'shing:
   ```
   Bo'lim: Algebra
   Savollar: 10
   To'g'ri: +5 ball
   Noto'g'ri: -1 ball
   ```
7. "Imtihonni Saqlash" tugmasini bosing

#### B. PDF Yuklab Olish

1. Dashboard'da exam'ni toping
2. "Ko'rish" tugmasini bosing
3. "Varaqlarni Yuklab Olish" tugmasini bosing
4. PDF yuklab olinadi: `Test_QR_System_ToplamA_2026-01-14.pdf`

#### C. QR Code Tekshirish

1. PDF'ni oching
2. Top-right corner'da QR code'ni ko'ring
3. Telefon bilan scan qiling
4. JSON ma'lumot ko'rinishi kerak:
   ```json
   {
     "examId": "...",
     "examName": "Test QR System",
     "layout": {...},
     "structure": {...}
   }
   ```

#### D. Backend Test (Optional)

1. PDF'ni print qiling yoki screenshot oling
2. Image'ni `backend/temp/` ga qo'ying
3. Test qiling:
   ```bash
   cd backend
   python test_qr.py temp/test_sheet.jpg
   ```
4. "✅ QR CODE DETECTED!" ko'rinishi kerak

#### E. Full Grading Test

1. PDF'ni print qiling
2. Random javoblar bilan to'ldiring (qora qalam)
3. Scan qiling (min 800x1100px)
4. Frontend'da "Varaqlarni Tekshirish" bo'limiga o'ting
5. Image'ni upload qiling
6. Natijalarni kuzating

**Expected Result**:

```
✅ QR Code detected!
✅ Layout from QR code
✅ 10/10 questions detected
✅ Accuracy: 95%+
✅ Processing time: ~2s
```

## 🎯 Qisqa Test Checklist

- [ ] Backend ishga tushdi (port 8000)
- [ ] Frontend ishga tushdi (port 5173)
- [ ] Exam yaratildi
- [ ] PDF yuklab olindi
- [ ] QR code PDF'da ko'rinadi
- [ ] QR code scan qilinadi (telefon bilan)
- [ ] Backend test_qr.py ishlaydi
- [ ] Full grading ishlaydi
- [ ] QR code detected log'da

## 🐛 Tez Muammolarni Hal Qilish

### Backend ishlamayapti

```bash
# Port band bo'lsa
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Dependencies yo'q
cd backend
pip install -r requirements.txt
```

### Frontend ishlamayapti

```bash
# Dependencies yo'q
npm install

# Port band bo'lsa
# Ctrl+C bilan to'xtating va qayta ishga tushiring
```

### QR code topilmayapti

1. Image quality tekshiring (min 800x1100px)
2. QR code aniq ko'rinishini tekshiring
3. Yaxshi yorug'likda photo oling
4. PDF'ni qayta generate qiling

### pyzbar o'rnatilmayapti (Windows)

```bash
# Visual C++ Redistributable kerak
# Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Yoki conda ishlatib ko'ring
conda install -c conda-forge pyzbar
```

## 📊 Expected Performance

| Metric                | Value  |
| --------------------- | ------ |
| QR Detection Time     | <100ms |
| Full Processing       | ~2s    |
| Accuracy (with QR)    | 95-99% |
| Accuracy (without QR) | 70-85% |

## 🎉 Success!

Agar barcha qadamlar muvaffaqiyatli bo'lsa:

**✅ QR CODE SYSTEM ISHGA TUSHDI!**

Keyingi qadamlar:

1. Real exam'lar yarating
2. Print va test qiling
3. Natijalarni tahlil qiling
4. Production'ga deploy qiling

## 📚 Qo'shimcha Ma'lumot

- **To'liq dokumentatsiya**: `QR_CODE_SYSTEM_COMPLETE.md`
- **Test guide**: `TESTING_GUIDE.md`
- **System status**: `SYSTEM_STATUS.md`
- **Backend API**: http://localhost:8000/docs

## 💡 Pro Tips

1. **High Quality Scans**: Minimum 800x1100px, yaxshisi 1200x1600px
2. **Good Lighting**: QR code detection uchun yaxshi yorug'lik kerak
3. **Clean Sheets**: Iflos yoki burilgan varaqlar muammo yaratishi mumkin
4. **Test First**: Har doim birinchi marta test qiling
5. **Check Logs**: Muammo bo'lsa, backend log'larni tekshiring

---

**Savol yoki muammo bo'lsa**: Backend log'larni tekshiring yoki `TESTING_GUIDE.md` ga qarang.
