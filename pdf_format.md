PDF faylni yaratish va yuklab olish jarayoni uchun to'liq texnik va dizayn talablari.
PDF Umumiy Talablari
1. Fayl Parametrlari
javascriptconst pdfConfig = {
  format: 'A4',           // 210mm x 297mm
  orientation: 'portrait', // vertikal
  unit: 'mm',
  compress: true,         // fayl hajmini kamaytirish
  precision: 2,           // aniqlik
  putOnlyUsedFonts: true,
  floatPrecision: 2
}
```

### 2. **Fayl Nomi va Metadata**

**Fayl nomi formati:**
```
[ImtihonNomi]_Toplam[A/B/C/D]_[Sana].pdf

Misol: 
- Matematika_Oraliq_ToplamA_2025-01-13.pdf
- Fizika_Yakuniy_ToplamB_2025-01-13.pdf
PDF Metadata:
javascriptpdf.setProperties({
  title: 'Imtihon Titul Varag\'i - [Imtihon Nomi]',
  subject: '[Fan Nomi] - To\'plam [A/B/C/D]',
  author: 'Imtihon Tizimi',
  keywords: 'imtihon, test, OMR',
  creator: 'Exam System v1.0',
  creationDate: new Date()
});
```

## PDF Strukturasi

### 1. **Birinchi Sahifa: Titul Varaq**

To'liq titul varaq (yuqorida tavsiflangan format):
- Header (logo, QR, barcode)
- Talaba ma'lumotlari
- Yo'riqnoma
- Javoblar jadvali
- Corner markers
- Footer

**Texnik talablar:**
- Resolution: 300 DPI (yuqori sifat)
- Rang: RGB yoki Grayscale
- Font embedding: true (shriftlar PDF ichida)
- Compression: JPEG quality 90%

### 2. **Ikkinchi Sahifa: To'g'ri Javoblar Kaliti (Optional)**

Faqat o'qituvchi uchun:
```
╔═══════════════════════════════════════════════════════════╗
║           TO'G'RI JAVOBLAR KALITI - TOPLAM A              ║
║                  (Faqat o'qituvchi uchun)                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║ MAVZU 1: Algebra                                          ║
║ ───────────────────────────────────────────────────────   ║
║ Bo'lim 1.1: Tenglamalar (+3/-1 ball)                      ║
║   1-B  2-A  3-D  4-C  5-A  6-B  7-D  8-C  9-A  10-B      ║
║                                                            ║
║ Bo'lim 1.2: Funksiyalar (+5/-0 ball)                      ║
║   11-C  12-A  13-B  14-D  15-A  16-C  17-B  18-D         ║
║                                                            ║
║ MAVZU 2: Geometriya                                       ║
║ ───────────────────────────────────────────────────────   ║
║ Bo'lim 2.1: Uchburchaklar (+4/-1 ball)                    ║
║   19-A  20-D  21-B  22-C  23-A  24-D  25-B               ║
║                                                            ║
╠═══════════════════════════════════════════════════════════╣
║ UMUMIY STATISTIKA:                                        ║
║ • Jami savollar: 25                                       ║
║ • Maksimal ball: 100                                      ║
║ • O'tish balli: 56                                        ║
║                                                            ║
║ BALL TAQSIMOTI:                                           ║
║ • 86-100: A'lo (5)                                        ║
║ • 71-85:  Yaxshi (4)                                      ║
║ • 56-70:  Qoniqarli (3)                                   ║
║ • 0-55:   Qoniqarsiz (2)                                  ║
╚═══════════════════════════════════════════════════════════╝
```

### 3. **Uchinchi Sahifa: Statistika va Ma'lumotlar (Optional)**
```
╔═══════════════════════════════════════════════════════════╗
║                 IMTIHON MA'LUMOTLARI                      ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║ Imtihon: [Matematika Oraliq Nazorat]                      ║
║ Fan: [Oliy matematika]                                     ║
║ Sana: [13.01.2025]                                         ║
║ Vaqt: [90 daqiqa]                                          ║
║ To'plam: [A]                                               ║
║                                                            ║
║ ───────────────────────────────────────────────────────   ║
║                                                            ║
║ MAVZULAR BO'YICHA TAQSIMOT:                               ║
║                                                            ║
║ 📊 Mavzu 1: Algebra (40 ball)                             ║
║    └─ Bo'lim 1.1: Tenglamalar (10 savol, 30 ball)        ║
║    └─ Bo'lim 1.2: Funksiyalar (8 savol, 10 ball)         ║
║                                                            ║
║ 📊 Mavzu 2: Geometriya (35 ball)                          ║
║    └─ Bo'lim 2.1: Uchburchaklar (7 savol, 28 ball)       ║
║    └─ Bo'lim 2.2: Doiralar (5 savol, 7 ball)             ║
║                                                            ║
║ 📊 Mavzu 3: Trigonometriya (25 ball)                      ║
║    └─ Bo'lim 3.1: Formulalar (6 savol, 25 ball)          ║
║                                                            ║
║ ───────────────────────────────────────────────────────   ║
║                                                            ║
║ QIYINCHILIK DARAJASI:                                     ║
║ • Oson: 40%                                               ║
║ • O'rta: 45%                                              ║
║ • Qiyin: 15%                                              ║
║                                                            ║
║ ───────────────────────────────────────────────────────   ║
║                                                            ║
║ O'qituvchi: [___________________]                         ║
║ Kafedra: [___________________]                            ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

## Ko'p To'plamlar uchun PDF

Agar bir nechta to'plam (A, B, C, D) yaratilgan bo'lsa:

### **Variant 1: Alohida PDF fayllar**
```
Matematika_ToplamA_2025-01-13.pdf (3 sahifa)
Matematika_ToplamB_2025-01-13.pdf (3 sahifa)
Matematika_ToplamC_2025-01-13.pdf (3 sahifa)
Matematika_ToplamD_2025-01-13.pdf (3 sahifa)
```

### **Variant 2: Bitta ZIP arxiv**
```
Matematika_Imtihon_2025-01-13.zip
  ├── ToplamA.pdf
  ├── ToplamB.pdf
  ├── ToplamC.pdf
  └── ToplamD.pdf
```

### **Variant 3: Bitta ko'p sahifali PDF**
```
Matematika_Barcha_Toplamlar_2025-01-13.pdf
  ├── Sahifa 1-3: To'plam A
  ├── Sahifa 4-6: To'plam B
  ├── Sahifa 7-9: To'plam C
  └── Sahifa 10-12: To'plam D
```

Har bir to'plam orasida separator sahifa:
```
╔═══════════════════════════════════════════════════════════╗
║                                                            ║
║                                                            ║
║                        TO'PLAM B                           ║
║                                                            ║
║                  Keyingi sahifadan boshlanadi              ║
║                                                            ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
PDF Generatsiya Kodi Strukturasi
javascriptasync function generatePDF(examData) {
  // jsPDF kutubxonasidan foydalanish
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  // Metadata qo'shish
  pdf.setProperties({
    title: `${examData.name} - To'plam ${examData.variant}`,
    subject: examData.subject,
    author: 'Exam System',
    keywords: 'exam, test, omr',
    creator: 'Exam System v1.0'
  });

  // SAHIFA 1: Titul varaq
  drawTitleSheet(pdf, examData);

  // SAHIFA 2: Javoblar kaliti (yangi sahifa)
  pdf.addPage();
  drawAnswerKey(pdf, examData);

  // SAHIFA 3: Statistika (yangi sahifa)
  pdf.addPage();
  drawStatistics(pdf, examData);

  // PDF ni saqlash
  const fileName = `${examData.name}_Toplam${examData.variant}_${formatDate(new Date())}.pdf`;
  pdf.save(fileName);
}

// Titul varaqni chizish
function drawTitleSheet(pdf, data) {
  let y = 15; // boshlang'ich Y pozitsiya

  // 1. Header
  y = drawHeader(pdf, data, y);
  
  // 2. Student Info
  y = drawStudentInfo(pdf, y);
  
  // 3. Instructions
  y = drawInstructions(pdf, y);
  
  // 4. Answer Grid
  y = drawAnswerGrid(pdf, data, y);
  
  // 5. Corner Markers
  drawCornerMarkers(pdf);
  
  // 6. Footer
  drawFooter(pdf, data);
}

// Header qismini chizish
function drawHeader(pdf, data, startY) {
  // Logo (agar mavjud bo'lsa)
  if (data.logo) {
    pdf.addImage(data.logo, 'PNG', 15, startY, 20, 20);
  }

  // Sarlavha
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text('IMTIHON VARAG\'I', 105, startY + 10, { align: 'center' });

  // Imtihon nomi
  pdf.setFontSize(14);
  pdf.text(data.name, 105, startY + 18, { align: 'center' });

  // QR kod
  if (data.qrCode) {
    pdf.addImage(data.qrCode, 'PNG', 175, startY, 25, 25);
  }

  // Sana va to'plam
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`Sana: ${data.date}`, 15, startY + 28);
  pdf.text(`To'plam: ${data.variant}`, 90, startY + 28);
  pdf.text(`Vaqt: ${data.duration} daq.`, 140, startY + 28);

  return startY + 35; // keyingi qism uchun Y
}

// Talaba ma'lumotlari
function drawStudentInfo(pdf, startY) {
  // Border
  pdf.setDrawColor(0);
  pdf.rect(15, startY, 180, 50);

  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'bold');
  pdf.text('TALABA MA\'LUMOTLARI', 20, startY + 7);

  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(10);
  
  // Ma'lumotlar joylar
  pdf.text('FAMILIYA:', 20, startY + 15);
  pdf.line(45, startY + 16, 190, startY + 16); // chiziq

  pdf.text('ISMI:', 20, startY + 23);
  pdf.line(45, startY + 24, 190, startY + 24);

  pdf.text('GURUH:', 20, startY + 31);
  pdf.line(45, startY + 32, 90, startY + 32);
  
  pdf.text('KURS:', 100, startY + 31);
  pdf.line(120, startY + 32, 150, startY + 32);

  // Talaba ID doirachalari
  pdf.text('TALABA ID:', 20, startY + 40);
  drawIDGrid(pdf, 50, startY + 36);

  return startY + 55;
}

// Yo'riqnoma
function drawInstructions(pdf, startY) {
  pdf.setFillColor(255, 250, 205); // och sariq
  pdf.rect(15, startY, 180, 20, 'F');
  pdf.rect(15, startY, 180, 20, 'S');

  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('⚠️ DIQQAT! JAVOBLARNI BELGILASH QOIDALARI:', 20, startY + 6);

  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(9);
  
  // To'g'ri va noto'g'ri misollar
  pdf.text('✓ To\'g\'ri:', 20, startY + 12);
  drawFilledBubble(pdf, 40, startY + 10, 3);
  
  pdf.text('✗ Noto\'g\'ri:', 80, startY + 12);
  drawPartialBubble(pdf, 105, startY + 10, 3);
  drawCrossedBubble(pdf, 115, startY + 10, 3);

  pdf.text('• Faqat qora/ko\'k ruchka ishlatilsin', 20, startY + 17);
  pdf.text('• Doirachani to\'liq to\'ldiring', 100, startY + 17);

  return startY + 25;
}

// Javoblar jadvali
function drawAnswerGrid(pdf, data, startY) {
  let currentY = startY;

  data.topics.forEach((topic, topicIndex) => {
    // Mavzu sarlavhasi
    pdf.setFillColor(240, 240, 240);
    pdf.rect(15, currentY, 180, 8, 'F');
    pdf.rect(15, currentY, 180, 8, 'S');

    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'bold');
    pdf.text(`MAVZU ${topicIndex + 1}: ${topic.name}`, 20, currentY + 5);
    pdf.text(`Jami: ${topic.totalScore} ball`, 170, currentY + 5);

    currentY += 10;

    // Bo'limlar
    topic.sections.forEach((section, sectionIndex) => {
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Bo'lim ${topicIndex + 1}.${sectionIndex + 1}: ${section.name}`, 20, currentY + 4);
      pdf.text(`(+${section.correctScore} ball / ${section.incorrectScore} ball)`, 130, currentY + 4);

      currentY += 6;

      // Savollar grid
      const questionsPerRow = 2;
      const bubbleSize = 3;
      const bubbleSpacing = 8;
      const rowHeight = 6;

      for (let i = 0; i < section.questionCount; i += questionsPerRow) {
        const xStart = 25;
        
        for (let j = 0; j < questionsPerRow && (i + j) < section.questionCount; j++) {
          const questionNum = section.startQuestion + i + j;
          const xPos = xStart + (j * 90);

          // Savol raqami
          pdf.setFont('helvetica', 'bold');
          pdf.text(`${questionNum}.`, xPos, currentY + 4);

          // Variant doirachalari
          const variants = ['A', 'B', 'C', 'D', 'E'];
          variants.forEach((variant, vIndex) => {
            const bubbleX = xPos + 8 + (vIndex * bubbleSpacing);
            drawEmptyBubble(pdf, bubbleX, currentY + 2, bubbleSize);
            pdf.setFontSize(8);
            pdf.text(variant, bubbleX - 1, currentY);
          });
        }

        currentY += rowHeight;
      }

      currentY += 3; // bo'limlar orasida bo'sh joy
    });

    currentY += 5; // mavzular orasida bo'sh joy

    // Yangi sahifa kerakmi?
    if (currentY > 250 && topicIndex < data.topics.length - 1) {
      pdf.addPage();
      currentY = 15;
    }
  });

  return currentY;
}

// Corner markers
function drawCornerMarkers(pdf) {
  const size = 10;
  const margin = 5;
  
  // Yuqori chap
  pdf.setFillColor(0);
  pdf.rect(margin, margin, size, size, 'F');
  
  // Yuqori o'ng
  pdf.rect(210 - margin - size, margin, size, size, 'F');
  
  // Pastki chap
  pdf.rect(margin, 297 - margin - size, size, size, 'F');
  
  // Pastki o'ng
  pdf.rect(210 - margin - size, 297 - margin - size, size, size, 'F');
}

// Footer
function drawFooter(pdf, data) {
  const footerY = 275;

  pdf.setDrawColor(0);
  pdf.line(15, footerY, 195, footerY);

  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.text('BALL HISOBI (O\'qituvchi to\'ldiradi)', 20, footerY + 5);

  // Ball jadvali
  pdf.rect(15, footerY + 7, 180, 10);
  pdf.line(60, footerY + 7, 60, footerY + 17);
  pdf.line(105, footerY + 7, 105, footerY + 17);
  pdf.line(150, footerY + 7, 150, footerY + 17);

  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(9);
  pdf.text('To\'g\'ri: ___', 20, footerY + 14);
  pdf.text('Noto\'g\'ri: ___', 65, footerY + 14);
  pdf.text('Ball: ___/___', 110, footerY + 14);
  pdf.text('Baho: _____', 155, footerY + 14);

  // Tekshiruvchi
  pdf.text('Tekshiruvchi: ________________', 15, footerY + 23);
  pdf.text('Imzo: ________', 100, footerY + 23);
  pdf.text('Sana: ______', 150, footerY + 23);

  // ID va versiya
  pdf.setFontSize(7);
  pdf.text(`ID: ${data.examId}`, 15, footerY + 28);
  pdf.text('Versiya: 1.0', 180, footerY + 28);
}

// Yordamchi funksiyalar
function drawEmptyBubble(pdf, x, y, radius) {
  pdf.setDrawColor(0);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius, 'S');
}

function drawFilledBubble(pdf, x, y, radius) {
  pdf.setFillColor(0);
  pdf.circle(x, y, radius, 'F');
}

function drawPartialBubble(pdf, x, y, radius) {
  pdf.circle(x, y, radius, 'S');
  pdf.setFillColor(128);
  pdf.circle(x, y, radius / 2, 'F');
}

function drawCrossedBubble(pdf, x, y, radius) {
  pdf.circle(x, y, radius, 'S');
  pdf.line(x - radius, y - radius, x + radius, y + radius);
  pdf.line(x - radius, y + radius, x + radius, y - radius);
}

function drawIDGrid(pdf, startX, startY) {
  const bubbleSize = 2;
  const spacing = 6;
  
  for (let col = 0; col < 10; col++) {
    pdf.setFontSize(7);
    pdf.text(`${col}`, startX + (col * spacing) - 0.5, startY - 1);
    
    for (let row = 0; row < 10; row++) {
      drawEmptyBubble(pdf, startX + (col * spacing), startY + (row * 4), bubbleSize);
    }
  }
}
Yuklab Olish Variantlari
1. Oddiy Yuklab Olish (Bir dona PDF)
javascriptfunction downloadSinglePDF(examData, variant) {
  const pdf = generatePDF(examData, variant);
  const fileName = `${examData.name}_Toplam${variant}_${formatDate()}.pdf`;
  pdf.save(fileName);
}
2. Ko'p To'plamlarni Yuklab Olish (Alohida fayllar)
javascriptasync function downloadAllVariants(examData) {
  for (let variant of ['A', 'B', 'C', 'D']) {
    const pdf = generatePDF(examData, variant);
    const fileName = `${examData.name}_Toplam${variant}_${formatDate()}.pdf`;
    pdf.save(fileName);
    
    // Har bir yuklab olish orasida 500ms kutish
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}
3. ZIP Arxiv sifatida Yuklab Olish
javascript// JSZip kutubxonasi kerak
async function downloadAsZip(examData) {
  const zip = new JSZip();
  const folder = zip.folder(examData.name);

  for (let variant of ['A', 'B', 'C', 'D']) {
    const pdf = generatePDF(examData, variant);
    const pdfBlob = pdf.output('blob');
    folder.file(`Toplam${variant}.pdf`, pdfBlob);
  }

  const zipBlob = await zip.generateAsync({ type: 'blob' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(zipBlob);
  link.download = `${examData.name}_${formatDate()}.zip`;
  link.click();
}
4. Browser Print Dialog
javascriptfunction printPDF(examData, variant) {
  const pdf = generatePDF(examData, variant);
  
  // Yangi oynada ochish va print
  const pdfBlob = pdf.output('blob');
  const pdfUrl = URL.createObjectURL(pdfBlob);
  
  const printWindow = window.open(pdfUrl);
  printWindow.addEventListener('load', () => {
    printWindow.print();
  });
}
UI Komponentlari (Yuklab Olish Tugmalari)
javascript<div className="flex gap-3 mt-6">
  {/* Bitta to'plamni yuklab olish */}
  <button 
    onClick={() => downloadSinglePDF(examData, 'A')}
    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
  >
    <Download className="w-5 h-5" />
    To'plam A ni Yuklab Olish
  </button>

  {/* Barcha to'plamlarni yuklab olish */}
  <button 
    onClick={() => downloadAllVariants(examData)}
    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
  >
    <Download className="w-5 h-5" />
    Barcha To'plamlarni Yuklab Olish
  </button>

  {/* ZIP sifatida yuklab olish */}
  <button 
    onClick={() => downloadAsZip(examData)}
    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
  >
    <FileArchive className="w-5 h-5" />
    ZIP Arxiv
  </button>

  {/* Print */}
  <button 
    onClick={() => printPDF(examData, 'A')}
    className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
  >
    <Printer className="w-5 h-5" />
    Chop Etish
  </button>
</div>
Xulosa
PDF fayl:

✅ Professional va o'qish uchun qulay
✅ Print-ready (300 DPI)
✅ OMR texnologiyasi bilan mos
✅ Metadata to'liq
✅ Ko'p variantli yuklab olish
✅ Minimal fayl hajmi (compression)
✅ Barcha qurilmalarda ochiladi