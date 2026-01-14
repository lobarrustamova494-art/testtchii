# OMR Imtihon Tekshirish Tizimi

Professional OMR (Optical Mark Recognition) tizimi - imtihon varaqlarini avtomatik tekshirish uchun.

## 🚀 Xususiyatlar

- ✅ **PDF Generator**: Imtihon varaqlarini avtomatik yaratish
- ✅ **OMR Detection**: Yuqori aniqlikda javoblarni aniqlash
- ✅ **QR Code System**: Layout ma'lumotlarini QR code orqali uzatish
- ✅ **Visual Feedback**: Tekshirilgan varaqni rangli annotatsiya bilan ko'rsatish
- ✅ **Hybrid System**: OMR + AI verification (ixtiyoriy)
- ✅ **Responsive UI**: Zamonaviy va qulay interfeys

## 📋 Talablar

### Frontend

- Node.js 18+
- npm yoki yarn

### Backend

- Python 3.9+
- pip

## 🛠️ O'rnatish

### 1. Repository'ni Clone Qilish

```bash
git clone https://github.com/lobarrustamova494-art/testtchii.git
cd testtchii
```

### 2. Frontend O'rnatish

```bash
# Dependencies o'rnatish
npm install

# Development server ishga tushirish
npm run dev
```

Frontend `http://localhost:5173` da ishga tushadi.

### 3. Backend O'rnatish

```bash
cd backend

# Virtual environment yaratish (ixtiyoriy)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependencies o'rnatish
pip install -r requirements.txt

# .env fayl yaratish
copy .env.example .env

# Backend ishga tushirish
python main.py
```

Backend `http://localhost:8000` da ishga tushadi.

### 4. Environment Variables

Backend `.env` faylida:

```env
# Groq API (AI verification uchun - ixtiyoriy)
GROQ_API_KEY=your_api_key_here

# Server settings
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📖 Foydalanish

### 1. Imtihon Yaratish

1. Login qiling (demo: admin/admin)
2. "Yangi Imtihon" tugmasini bosing
3. Imtihon ma'lumotlarini kiriting:
   - Nomi
   - Mavzular va bo'limlar
   - Har bir bo'lim uchun savol soni va ball tizimi

### 2. PDF Yaratish

1. Imtihon yaratilgandan keyin "PDF Yuklab Olish" tugmasini bosing
2. PDF yuklab olinadi
3. PDF'ni chop eting (100% scale, A4 qog'oz)

### 3. Varaqni To'ldirish

- Qora qalam ishlating
- Doirachalarni to'liq to'ldiring
- Bir savolga faqat bitta javob

### 4. Tekshirish

1. To'ldirilgan varaqni skan qiling (300+ DPI)
2. "Tekshirish" bo'limiga o'ting
3. Rasmni yuklang
4. To'g'ri javoblar kalitini kiriting
5. "Tekshirish" tugmasini bosing

### 5. Natijalarni Ko'rish

- Umumiy ball va foiz
- Har bir mavzu bo'yicha natijalar
- Tekshirilgan varaq rasmi (rangli annotatsiya bilan)
- Batafsil statistika

## 🎨 Annotatsiya Ranglari

- **Yashil**: To'g'ri javob
- **Ko'k**: Student to'g'ri belgilagan
- **Qizil**: Student xato belgilagan

## 📁 Loyiha Strukturasi

```
testtchii/
├── backend/                 # Python FastAPI backend
│   ├── services/           # OMR, grading, annotation
│   ├── utils/              # Coordinate mapper
│   ├── main.py             # FastAPI app
│   └── requirements.txt
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── services/           # API services
│   ├── utils/              # PDF generator, storage
│   └── types/              # TypeScript types
├── docs/                   # Documentation (MD files)
└── README.md
```

## 🔧 Texnik Tafsilotlar

### PDF Layout

- **Format**: A4 (210mm x 297mm)
- **Grid Start**: X=25mm, Y=149mm
- **Questions per Row**: 2
- **Bubble Radius**: 2.5mm
- **Row Height**: 5.5mm
- **Corner Markers**: 15mm x 15mm

### OMR Detection

- **Algorithm**: Multi-parameter comparative analysis
- **Parameters**: Darkness (50%), Coverage (30%), Uniformity (20%)
- **Accuracy**: 95%+ (yuqori sifatli skan bilan)

### Image Processing

- Perspective correction
- Adaptive thresholding
- Noise reduction
- CLAHE contrast enhancement

## 📚 Hujjatlar

- [FINAL_ALIGNMENT_GUIDE.md](FINAL_ALIGNMENT_GUIDE.md) - To'liq yo'riqnoma
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Test qilish bo'yicha qo'llanma
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deploy qilish yo'riqnomasi

## 🐛 Muammolarni Hal Qilish

### PDF Alignment Muammolari

Agar to'rtburchaklar bubble'larga mos kelmasa:

1. **Yangi PDF yarating** (eng muhim!)
2. Yuqori sifatli chop eting (100% scale)
3. Yuqori sifatli skan qiling (300+ DPI)

Batafsil: [FINAL_ALIGNMENT_GUIDE.md](FINAL_ALIGNMENT_GUIDE.md)

### Backend Ishlamasa

```bash
# Loglarni tekshiring
cd backend
python main.py

# Dependencies qayta o'rnating
pip install -r requirements.txt --force-reinstall
```

### Frontend Ishlamasa

```bash
# Dependencies qayta o'rnating
npm install

# Cache tozalash
npm run build
```

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. Commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📝 Litsenziya

MIT License

## 👥 Muallif

Lobar Rustamova - [GitHub](https://github.com/lobarrustamova494-art)

## 🙏 Minnatdorchilik

- OpenCV - Image processing
- FastAPI - Backend framework
- React - Frontend framework
- jsPDF - PDF generation
- Groq - AI verification (ixtiyoriy)

## 📞 Aloqa

Savollar yoki muammolar bo'lsa, GitHub Issues orqali murojaat qiling.

---

**Eslatma**: Bu loyiha doimiy ravishda yangilanmoqda. Eng so'nggi versiyani olish uchun repository'ni pull qiling.
