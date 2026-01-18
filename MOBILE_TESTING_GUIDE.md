# 📱 Mobil Test Qo'llanmasi

## 🚀 Loyiha Holati

- **Backend**: ✅ Ishlamoqda (Process ID: 9)
- **Frontend**: ✅ Ishlamoqda (Process ID: 10)
- **Firewall**: ✅ Portlar ochilgan (3000, 8000)
- **Network**: ✅ Tashqi qurilmalar uchun ochiq

## 📡 Manzillar

### Noutbuk IP: `10.64.226.226`

### Frontend (React + Vite)

- **Local**: http://localhost:3000/
- **Network**: **http://10.64.226.226:3000/**

### Backend (FastAPI)

- **Local**: http://localhost:8000/
- **Network**: **http://10.64.226.226:8000/**

## 📱 Telefondan Test Qilish

### 1. Tarmoq Ulanishi

- Telefon va noutbuk **bir xil Wi-Fi** tarmoqda bo'lishi kerak
- Noutbuk IP: `10.64.226.226`

### 2. Brauzerda Ochish

Telefonning brauzerida quyidagi manzilni oching:

```
http://10.64.226.226:3000
```

### 3. Kamera Tizimini Sinash

#### A) Login qiling

- Username/Email: admin yoki test
- Password: mavjud parol

#### B) Imtihon yarating yoki mavjudini tanlang

#### C) ExamGradingHybrid sahifasiga o'ting

#### D) "Kamera Tizimi" tugmasini bosing

#### E) Kamera ruxsatini bering

- Brauzer kamera ruxsatini so'raydi
- "Allow" yoki "Ruxsat berish" tugmasini bosing

#### F) Qog'ozni joylashtiring

- A4 o'lchamdagi qog'ozni kameraga ko'rsating
- Qog'oz A4 ramka ichiga to'liq kirishi kerak
- 4 ta burchak ko'rinishi kerak
- Qog'ozni harakatsiz ushlab turing

#### G) Rasm oling

- Barqarorlik 80%+ bo'lganda "Rasm Olish" tugmasi faol bo'ladi
- Tugmani bosib rasm oling
- Rasmni tasdiqlang yoki qayta oling

## 🔧 Texnik Talablar

### Telefon Talablari

- **Brauzer**: Chrome, Safari, Firefox (zamonaviy versiya)
- **Kamera**: Orqa kamera (environment) tavsiya etiladi
- **Ruxsatlar**: Kamera va mikrofon ruxsati
- **Internet**: Wi-Fi ulanish (mobil internet ham ishlaydi)

### Kamera Talablari

- **Masofa**: Qog'ozdan 30-50cm
- **Yorug'lik**: Yaxshi, bir xil yorug'lik
- **Fon**: Qog'oz va fon o'rtasida kontrast
- **Barqarorlik**: Qo'lni qimirlatmaslik

### Qog'oz Talablari

- **O'lcham**: A4 (210x297mm)
- **Corner Markerlar**: 4 ta qora kvadrat burchaklarda
- **Sifat**: Toza, burishtirilmagan qog'oz
- **Fon**: Oq qog'oz, qora yoki to'q rangli stol

## 🧪 Test Senariylari

### 1. Asosiy Funksionallik

- ✅ Sahifa yuklanishi
- ✅ Login jarayoni
- ✅ Kamera tizimi ochilishi
- ✅ Kamera ruxsati
- ✅ Qog'oz aniqlash
- ✅ Rasm olish
- ✅ Backend bilan bog'lanish

### 2. Kamera Tizimi

- ✅ Real-time paper detection
- ✅ 4-corner validation
- ✅ Stability checking
- ✅ A4 frame overlay
- ✅ Capture pipeline
- ✅ Image processing

### 3. OMR Processing

- ✅ Perspective correction
- ✅ Corner marker detection
- ✅ Coordinate mapping
- ✅ Bubble detection
- ✅ Answer grading
- ✅ Visual annotation

## 🚨 Muammolarni Hal Qilish

### Sahifa Ochilmasa

1. IP manzilni tekshiring: `10.64.226.226`
2. Wi-Fi ulanishni tekshiring
3. Firewall sozlamalarini tekshiring
4. Noutbukda antivirus dasturini vaqtincha o'chiring

### Kamera Ishlamasa

1. Brauzer ruxsatlarini tekshiring
2. HTTPS talab qilinishi mumkin (localhost uchun HTTP yetarli)
3. Boshqa brauzer sinab ko'ring
4. Telefon sozlamalarida kamera ruxsatini tekshiring

### Backend Bog'lanmasa

1. Backend jarayoni ishlab turganini tekshiring
2. Port 8000 ochiq ekanini tekshiring
3. Antivirus/Firewall sozlamalarini tekshiring

## 📊 Kutilgan Natijalar

### Muvaffaqiyatli Test

- Kamera tizimi ochiladi
- Qog'oz real-time aniqlanadi
- 4 ta burchak ko'rsatiladi
- Barqarorlik hisoblanadi
- Rasm olinadi va qayta ishlanadi
- OMR natijalari ko'rsatiladi
- Vizual annotatsiya ishlaydi

### Performance Metrics

- **Sahifa yuklash**: < 3 soniya
- **Kamera ochilish**: < 2 soniya
- **Paper detection**: Real-time (10 FPS)
- **Image processing**: < 5 soniya
- **OMR grading**: < 3 soniya

## 🎯 Test Maqsadlari

1. **Mobil Uyg'unlik**: Telefonda to'liq funksionallik
2. **Kamera Sifati**: Professional document scanner experience
3. **Network Performance**: Wi-Fi orqali tez ishlash
4. **User Experience**: Oson va intuitiv interfeys
5. **Accuracy**: Yuqori aniqlik bilan OMR processing

## 📝 Test Hisoboti

Test jarayonida quyidagilarni qayd eting:

- [ ] Sahifa yuklash vaqti
- [ ] Kamera ochilish vaqti
- [ ] Paper detection aniqligi
- [ ] Capture sifati
- [ ] Processing vaqti
- [ ] OMR aniqligi
- [ ] Umumiy user experience

---

**Eslatma**: Agar biror muammo yuzaga kelsa, noutbukdagi terminal/console loglarini tekshiring va xatolik xabarlarini qayd eting.
