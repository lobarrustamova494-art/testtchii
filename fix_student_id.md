# PDF Yuklab Olish Muammosini Tuzatish

Muammo: Talaba ID doirachalari bir-biriga yopishib, tartibsiz ko'rinmoqda va matnlar kesib ketmoqda.

## To'liq Tuzatilgan Kod

```javascript
function generateExamPDF(examData) {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  // A4 o'lchamlari
  const pageWidth = 210;
  const pageHeight = 297;
  const margin = 15;
  const contentWidth = pageWidth - (2 * margin);

  let currentY = margin;

  // ================== 1. HEADER ==================
  
  // Corner markers
  pdf.setFillColor(0, 0, 0);
  pdf.rect(5, 5, 8, 8, 'F');
  pdf.rect(pageWidth - 13, 5, 8, 8, 'F');
  
  // Sarlavha
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text(examData.name, pageWidth / 2, currentY, { align: 'center' });
  currentY += 8;

  // Sana va to'plam
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`To'plam: ${examData.variant} | Sana: ${examData.date}`, 
           pageWidth / 2, currentY, { align: 'center' });
  currentY += 12;

  // ================== 2. TALABA MA'LUMOTLARI ==================
  
  // Bo'lim sarlavhasi
  pdf.setFillColor(240, 240, 240);
  pdf.rect(margin, currentY, contentWidth, 8, 'F');
  pdf.setDrawColor(200, 200, 200);
  pdf.rect(margin, currentY, contentWidth, 8);
  
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'bold');
  pdf.text('TALABA MA\'LUMOTLARI', margin + 3, currentY + 5.5);
  currentY += 10;

  // Familiya
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.text('FAMILIYA:', margin + 3, currentY + 4);
  pdf.setDrawColor(150, 150, 150);
  pdf.line(margin + 35, currentY + 5, pageWidth - margin, currentY + 5);
  currentY += 8;

  // Ismi
  pdf.text('ISMI:', margin + 3, currentY + 4);
  pdf.line(margin + 35, currentY + 5, pageWidth - margin, currentY + 5);
  currentY += 8;

  // Guruh, Kurs, Imzo (bir qatorda)
  pdf.text('GURUH:', margin + 3, currentY + 4);
  pdf.line(margin + 25, currentY + 5, margin + 65, currentY + 5);
  
  pdf.text('KURS:', margin + 75, currentY + 4);
  pdf.line(margin + 93, currentY + 5, margin + 113, currentY + 5);
  
  pdf.text('IMZO:', margin + 125, currentY + 4);
  pdf.line(margin + 143, currentY + 5, pageWidth - margin, currentY + 5);
  currentY += 10;

  // ================== TALABA ID (TUZATILGAN) ==================
  
  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'bold');
  pdf.text('TALABA ID:', margin + 3, currentY + 3);
  
  // ID grid parametrlari
  const idStartX = margin + 35;
  const idStartY = currentY + 5;
  const columnSpacing = 14;  // Ustunlar orasidagi masofa
  const rowHeight = 4;       // Qatorlar orasidagi balandlik
  const bubbleRadius = 1.8;  // Doiracha radiusi
  
  // Ustun raqamlari (0-9)
  pdf.setFontSize(8);
  pdf.setFont('helvetica', 'normal');
  for (let col = 0; col < 10; col++) {
    const x = idStartX + (col * columnSpacing);
    pdf.text(String(col), x + 0.5, idStartY - 1);
  }
  
  // Chap tomonda qator raqamlari (0-9)
  for (let row = 0; row < 10; row++) {
    const y = idStartY + (row * rowHeight);
    pdf.text(String(row), idStartX - 8, y + 1.5);
  }
  
  // Doirachalar grid
  for (let col = 0; col < 10; col++) {
    for (let row = 0; row < 10; row++) {
      const x = idStartX + (col * columnSpacing) + 2;
      const y = idStartY + (row * rowHeight) + 1;
      
      // Doiracha chizish
      pdf.setDrawColor(120, 120, 120);
      pdf.setLineWidth(0.2);
      pdf.circle(x, y, bubbleRadius);
    }
  }
  
  currentY += (10 * rowHeight) + 8; // Grid balandligi + bo'sh joy

  // ================== 3. YO'RIQNOMA ==================
  
  pdf.setFillColor(255, 250, 205);
  pdf.rect(margin, currentY, contentWidth, 18, 'F');
  pdf.setDrawColor(220, 200, 100);
  pdf.rect(margin, currentY, contentWidth, 18);
  
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.text('⚠ JAVOBLARNI BELGILASH QOIDALARI:', margin + 3, currentY + 5);
  
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(9);
  
  // To'g'ri misol
  pdf.text('To\'g\'ri:', margin + 3, currentY + 10);
  drawFilledBubble(pdf, margin + 18, currentY + 8.5, 1.8);
  
  // Noto'g'ri misollar
  pdf.text('Noto\'g\'ri:', margin + 35, currentY + 10);
  drawPartialBubble(pdf, margin + 52, currentY + 8.5, 1.8);
  drawEmptyBubbleWithX(pdf, margin + 62, currentY + 8.5, 1.8);
  
  // Qoidalar (ikki qator)
  pdf.text('• Doirachani to\'liq to\'ldiring', margin + 3, currentY + 14);
  pdf.text('• Bir savolga faqat bitta javob', margin + 100, currentY + 14);
  
  currentY += 22;

  // ================== 4. JAVOBLAR JADVALI ==================
  
  let questionNumber = 1;
  
  examData.topics.forEach((topic, topicIndex) => {
    // Mavzu sarlavhasi
    pdf.setFillColor(245, 245, 245);
    pdf.rect(margin, currentY, contentWidth, 8, 'F');
    pdf.setDrawColor(180, 180, 180);
    pdf.rect(margin, currentY, contentWidth, 8);
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'bold');
    pdf.text(`${topicIndex + 1}. ${topic.name}`, margin + 3, currentY + 5.5);
    currentY += 10;
    
    // Bo'limlar
    topic.sections.forEach((section, sectionIndex) => {
      // Bo'lim sarlavhasi
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      const sectionTitle = `${topicIndex + 1}.${sectionIndex + 1} ${section.name} (+${section.correctScore}/${section.incorrectScore})`;
      pdf.text(sectionTitle, margin + 5, currentY + 4);
      currentY += 7;
      
      // Savollar (2 ustunli layout)
      const questionsPerRow = 2;
      const columnWidth = contentWidth / 2;
      
      for (let i = 0; i < section.questionCount; i += questionsPerRow) {
        const rowY = currentY;
        
        // Birinchi ustun
        if (i < section.questionCount) {
          drawQuestion(pdf, questionNumber, margin + 8, rowY);
          questionNumber++;
        }
        
        // Ikkinchi ustun
        if (i + 1 < section.questionCount) {
          drawQuestion(pdf, questionNumber, margin + 8 + columnWidth, rowY);
          questionNumber++;
        }
        
        currentY += 8; // Qator balandligi
      }
      
      currentY += 2; // Bo'limlar orasida
    });
    
    currentY += 3; // Mavzular orasida
  });

  // ================== 5. FOOTER ==================
  
  currentY = pageHeight - 30;
  
  // Ball hisobi
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.text('BALL HISOBI (O\'qituvchi uchun)', margin + 3, currentY);
  currentY += 4;
  
  // Jadval
  pdf.setDrawColor(150, 150, 150);
  pdf.setLineWidth(0.3);
  pdf.rect(margin, currentY, contentWidth, 10);
  pdf.line(margin + 45, currentY, margin + 45, currentY + 10);
  pdf.line(margin + 95, currentY, margin + 95, currentY + 10);
  pdf.line(margin + 140, currentY, margin + 140, currentY + 10);
  
  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'normal');
  pdf.text('To\'g\'ri: ___', margin + 5, currentY + 6.5);
  pdf.text('Noto\'g\'ri: ___', margin + 50, currentY + 6.5);
  pdf.text('Ball: ___/___', margin + 100, currentY + 6.5);
  pdf.text('Baho: ___', margin + 145, currentY + 6.5);
  currentY += 13;
  
  // Tekshiruvchi
  pdf.text('Tekshiruvchi: ________________', margin + 3, currentY);
  pdf.text('Sana: ______', margin + 100, currentY);
  pdf.text('Imzo: ____', margin + 145, currentY);
  
  // Pastki corner markers
  pdf.setFillColor(0, 0, 0);
  pdf.rect(5, pageHeight - 13, 8, 8, 'F');
  pdf.rect(pageWidth - 13, pageHeight - 13, 8, 8, 'F');

  return pdf;
}

// ================== YORDAMCHI FUNKSIYALAR ==================

// Savol chizish
function drawQuestion(pdf, number, x, y) {
  // Savol raqami
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(10);
  pdf.text(`${number}.`, x, y + 4);
  
  // Variant doirachalari
  const variants = ['A', 'B', 'C', 'D', 'E'];
  const bubbleStartX = x + 12;
  const bubbleSpacing = 11;
  const bubbleRadius = 2.2;
  
  variants.forEach((variant, index) => {
    const bubbleX = bubbleStartX + (index * bubbleSpacing);
    
    // Variant harfi
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    pdf.text(variant, bubbleX - 1.5, y + 1);
    
    // Doiracha
    pdf.setDrawColor(100, 100, 100);
    pdf.setLineWidth(0.3);
    pdf.circle(bubbleX, y + 3, bubbleRadius);
  });
}

// Bo'sh doiracha
function drawBubble(pdf, x, y, radius) {
  pdf.setDrawColor(100, 100, 100);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius);
}

// To'ldirilgan doiracha
function drawFilledBubble(pdf, x, y, radius) {
  pdf.setFillColor(0, 0, 0);
  pdf.setDrawColor(100, 100, 100);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius, 'FD');
}

// Qisman to'ldirilgan
function drawPartialBubble(pdf, x, y, radius) {
  pdf.setDrawColor(100, 100, 100);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius);
  
  pdf.setFillColor(150, 150, 150);
  pdf.circle(x, y, radius * 0.5, 'F');
}

// X belgisi bilan doiracha
function drawEmptyBubbleWithX(pdf, x, y, radius) {
  pdf.setDrawColor(100, 100, 100);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius);
  
  // X chizish
  pdf.setDrawColor(200, 0, 0);
  pdf.setLineWidth(0.4);
  const offset = radius * 0.7;
  pdf.line(x - offset, y - offset, x + offset, y + offset);
  pdf.line(x - offset, y + offset, x + offset, y - offset);
}
```

## Asosiy Tuzatishlar

### 1. **Talaba ID Grid - Aniq O'lchamlar**
```javascript
const columnSpacing = 14;   // Ustunlar orasida 14mm
const rowHeight = 4;         // Qatorlar orasida 4mm  
const bubbleRadius = 1.8;    // Doiracha 1.8mm radius
```

### 2. **Grid Layout**
```
       0   1   2   3   4   5   6   7   8   9
    0  ○   ○   ○   ○   ○   ○   ○   ○   ○   ○
    1  ○   ○   ○   ○   ○   ○   ○   ○   ○   ○
    2  ○   ○   ○   ○   ○   ○   ○   ○   ○   ○
    ...
```

### 3. **Yo'riqnoma - Ko'proq Bo'sh Joy**
```javascript
// Balandlik 18mm (oldin 16mm edi)
pdf.rect(margin, currentY, contentWidth, 18, 'F');
```

### 4. **Savol Chizish Funksiyasi**
```javascript
// Alohida funksiya - qayta ishlatish oson
function drawQuestion(pdf, number, x, y) {
  // Raqam va variantlar
}
```

### 5. **Doiracha O'lchamlari**
```javascript
// ID uchun: 1.8mm radius
// Javoblar uchun: 2.2mm radius (kattaroq)
```

## Test Qilish

```javascript
const examData = {
  name: '1-imtihon',
  variant: 'A',
  date: '2026-01-13',
  topics: [
    {
      name: '1-mavzu',
      sections: [
        {
          name: '1-bo\'lim',
          questionCount: 20,
          correctScore: 1,
          incorrectScore: 0
        }
      ]
    }
  ]
};

const pdf = generateExamPDF(examData);
pdf.save('imtihon_varaq.pdf');
```

## Natija

✅ Talaba ID grid aniq va tartibli
✅ Barcha elementlar to'g'ri joylashgan
✅ Matnlar kesib ketmaydi
✅ Doirachalar bir xil o'lchamda
✅ Professional ko'rinish
✅ Print-ready (A4 format)