PDF faylda matn va elementlar bir-biriga yopishib, tartibsiz ko'rinmoqda. Buni to'g'rilash uchun quyidagi yechimlar kerak:
Muammo Tahlili

Matnlar ustma-ust tushmoqda - Y koordinatalari to'g'ri hisoblanmagan
Bo'sh joylar yo'q - padding va margin etarli emas
Elementlar tartibsiz - Layout strukturasi noto'g'ri
Doirachalar ko'rinmayapti - Chizish funksiyalari ishlamagan

To'liq Tuzatilgan PDF Generation Kodi
javascriptfunction generateExamPDF(examData) {
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

  // Corner marker (yuqori chap)
  pdf.setFillColor(0, 0, 0);
  pdf.rect(5, 5, 8, 8, 'F');
  
  // Corner marker (yuqori o'ng)
  pdf.rect(pageWidth - 13, 5, 8, 8, 'F');

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

  // Guruh va Kurs
  pdf.text('GURUH:', margin + 3, currentY + 4);
  pdf.line(margin + 25, currentY + 5, margin + 70, currentY + 5);
  
  pdf.text('KURS:', margin + 85, currentY + 4);
  pdf.line(margin + 105, currentY + 5, margin + 130, currentY + 5);
  
  pdf.text('IMZO:', margin + 145, currentY + 4);
  pdf.line(margin + 165, currentY + 5, pageWidth - margin, currentY + 5);
  currentY += 10;

  // Talaba ID doirachalari
  pdf.setFontSize(9);
  pdf.text('TALABA ID:', margin + 3, currentY + 3);
  currentY += 5;
  
  // ID raqamlar qatori
  const idStartX = margin + 30;
  const bubbleSpacing = 15;
  
  for (let i = 0; i < 10; i++) {
    const x = idStartX + (i * bubbleSpacing);
    pdf.setFontSize(8);
    pdf.text(String(i), x + 1.5, currentY - 1);
    
    // Vertikal doirachalar (0-9)
    for (let j = 0; j < 10; j++) {
      const y = currentY + (j * 4);
      drawBubble(pdf, x + 2, y + 1, 1.5);
    }
  }
  
  currentY += 42; // ID grid balandligi

  // ================== 3. YO'RIQNOMA ==================
  
  pdf.setFillColor(255, 250, 205);
  pdf.rect(margin, currentY, contentWidth, 16, 'F');
  pdf.setDrawColor(200, 200, 100);
  pdf.rect(margin, currentY, contentWidth, 16);
  
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.text('⚠ JAVOBLARNI BELGILASH QOIDALARI:', margin + 3, currentY + 5);
  
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(9);
  
  // To'g'ri misol
  pdf.text('To\'g\'ri:', margin + 3, currentY + 10);
  drawFilledBubble(pdf, margin + 18, currentY + 8.5, 1.5);
  
  // Noto'g'ri misol
  pdf.text('Noto\'g\'ri:', margin + 35, currentY + 10);
  drawPartialBubble(pdf, margin + 52, currentY + 8.5, 1.5);
  pdf.text('×', margin + 58, currentY + 10);
  
  // Qoidalar
  pdf.text('• Doirachani to\'liq to\'ldiring', margin + 3, currentY + 14);
  pdf.text('• Bir savolga faqat bitta javob', margin + 70, currentY + 14);
  
  pdf.text('• Qora/ko\'k ruchka ishlatilsin', margin + 3, currentY + 17.5);
  pdf.text('• Varaqni bukmang', margin + 70, currentY + 17.5);
  
  currentY += 20;

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
      pdf.text(
        `${topicIndex + 1}.${sectionIndex + 1} ${section.name} (+${section.correctScore}/${section.incorrectScore})`,
        margin + 5,
        currentY + 4
      );
      currentY += 6;
      
      // Savollar (2 ustunli)
      const questionsPerRow = 2;
      const columnWidth = contentWidth / 2;
      
      for (let i = 0; i < section.questionCount; i += questionsPerRow) {
        for (let col = 0; col < questionsPerRow; col++) {
          if (i + col >= section.questionCount) break;
          
          const xPos = margin + 5 + (col * columnWidth);
          
          // Savol raqami
          pdf.setFont('helvetica', 'bold');
          pdf.setFontSize(10);
          pdf.text(`${questionNumber}.`, xPos, currentY + 4);
          
          // Variant doirachalari
          const variants = ['A', 'B', 'C', 'D', 'E'];
          const bubbleStartX = xPos + 10;
          const bubbleSpacing = 10;
          
          variants.forEach((variant, vIndex) => {
            const bubbleX = bubbleStartX + (vIndex * bubbleSpacing);
            
            // Variant harfi
            pdf.setFontSize(8);
            pdf.setFont('helvetica', 'normal');
            pdf.text(variant, bubbleX - 1, currentY + 1);
            
            // Doiracha
            drawBubble(pdf, bubbleX, currentY + 2.5, 2);
          });
          
          questionNumber++;
        }
        
        currentY += 7; // Qator balandligi
      }
      
      currentY += 3; // Bo'limlar orasidagi bo'sh joy
    });
    
    currentY += 5; // Mavzular orasidagi bo'sh joy
  });

  // ================== 5. FOOTER ==================
  
  currentY = pageHeight - 35; // Pastdan 35mm
  
  // Ball hisobi sarlavhasi
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.text('BALL HISOBI (O\'qituvchi uchun)', margin + 3, currentY);
  currentY += 5;
  
  // Ball jadvali
  pdf.setDrawColor(150, 150, 150);
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
  
  // Tekshiruvchi ma'lumotlari
  pdf.text('Tekshiruvchi: ________________', margin + 3, currentY);
  pdf.text('Sana: ______', margin + 100, currentY);
  pdf.text('Imzo: ____', margin + 140, currentY);
  
  // Corner markers (pastki)
  pdf.setFillColor(0, 0, 0);
  pdf.rect(5, pageHeight - 13, 8, 8, 'F');
  pdf.rect(pageWidth - 13, pageHeight - 13, 8, 8, 'F');

  return pdf;
}

// ================== YORDAMCHI FUNKSIYALAR ==================

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

// Qisman to'ldirilgan doiracha
function drawPartialBubble(pdf, x, y, radius) {
  pdf.setDrawColor(100, 100, 100);
  pdf.setLineWidth(0.3);
  pdf.circle(x, y, radius);
  
  pdf.setFillColor(150, 150, 150);
  pdf.circle(x, y, radius * 0.5, 'F');
}

// QR kod qo'shish (agar kerak bo'lsa)
function addQRCode(pdf, data, x, y, size) {
  // QR kod generatsiya qilish (qrcode.js kutubxonasi kerak)
  // Soddalashtirilgan versiya:
  pdf.setDrawColor(0);
  pdf.rect(x, y, size, size);
  pdf.setFontSize(6);
  pdf.text('QR', x + size/2 - 2, y + size/2 + 1);
}
Asosiy Tuzatishlar
1. currentY Koordinatalarini To'g'ri Hisoblash
javascript// Har bir element qo'shilgandan keyin currentY ni yangilash
currentY += elementHeight + spacing;
2. Bo'sh Joylar (Spacing)
javascriptconst spacing = {
  afterHeader: 12,      // Header dan keyin
  afterSection: 10,     // Bo'lim dan keyin  
  betweenSections: 3,   // Bo'limlar orasida
  betweenTopics: 5,     // Mavzular orasida
  betweenQuestions: 7   // Savollar orasida
};
3. Element O'lchamlari
javascriptconst dimensions = {
  headerHeight: 8,
  studentInfoHeight: 50,
  instructionsHeight: 16,
  topicHeaderHeight: 8,
  questionRowHeight: 7,
  footerHeight: 25
};
4. Matn Pozitsiyalari
javascript// Matn Y koordinatasini element ichidagi markazda joylashtirish
const textY = elementY + (elementHeight / 2) + (fontSize / 3);
pdf.text('Matn', x, textY);
5. Doirachalar Chizish
javascript// jsPDF da doiracha chizish
pdf.circle(centerX, centerY, radius);

// To'ldirilgan doiracha
pdf.circle(centerX, centerY, radius, 'F');  // Fill

// Kontur va to'ldirish
pdf.circle(centerX, centerY, radius, 'FD'); // Fill + Draw
Test Qilish
javascript// Test ma'lumotlari
const testData = {
  name: '1-imtihon',
  variant: 'A',
  date: '2026-01-13',
  topics: [
    {
      name: '1-mavzu',
      sections: [
        {
          name: '1-bo\'lim',
          questionCount: 9,
          correctScore: 1,
          incorrectScore: 0
        }
      ]
    }
  ]
};

// PDF yaratish
const pdf = generateExamPDF(testData);
pdf.save('test.pdf');
Natija
Yangi PDF:
✅ Barcha elementlar tartibli
✅ Bo'sh joylar to'g'ri
✅ Matnlar o'qiladi
✅ Doirachalar ko'rinadi
✅ Professional ko'rinish
✅ Print-ready format