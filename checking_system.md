# Imtihon Varaqlarini Tekshirish Tizimi uchun To'liq Prompt

Avtomatik va qo'lda tekshirish imkoniyati bo'lgan professional varaq tekshirish tizimini yarating.

## Texnik Yondashuv

### 1. **OMR (Optical Mark Recognition) Simulatsiyasi**

Haqiqiy OMR texnologiyasini simulyatsiya qilish uchun:

```javascript
// Canvas API orqali varaqni tahlil qilish
const omrConfig = {
  bubbleDetectionThreshold: 0.6,  // 60% qora bo'lsa belgilangan
  cornerMarkerSize: 10,            // 10mm x 10mm
  bubbleRadius: 8,                 // 8mm diametr
  minContrast: 0.3,                // minimal kontrast
  noiseReduction: true,            // shovqinni kamaytirish
  autoRotation: true,              // avtomatik burish
  perspectiveCorrection: true      // perspektivani to'g'rilash
}
```

## Tekshirish Jarayoni Bosqichlari

### **BOSQICH 1: Varaq Yuklash**

```
╔═══════════════════════════════════════════════════════════╗
║               VARAQ YUKLASH VA SKANERLASH                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  📁 Variantlar:                                           ║
║                                                            ║
║  1️⃣ Fayldan yuklash:                                      ║
║     • PNG, JPG, JPEG formatlar                            ║
║     • PDF (har bir sahifa alohida)                        ║
║     • Ko'plab varaqlarni bir vaqtda yuklash               ║
║     • Drag & Drop qo'llab-quvvatlash                      ║
║                                                            ║
║  2️⃣ Kameradan skanerlash:                                 ║
║     • Real-time kamera yoqish                             ║
║     • Avtomatik chegaralarni aniqlash                     ║
║     • Snapshot olish                                      ║
║     • Bir nechta varaqni ketma-ket skanerlash            ║
║                                                            ║
║  3️⃣ Demo varaqlar:                                        ║
║     • Namuna varaqlar bilan test qilish                   ║
║     • Turli xil belgilash uslublari                       ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

**UI Komponenti:**
```javascript
<div className="border-2 border-dashed border-gray-300 rounded-xl p-8">
  {/* Drag & Drop Zone */}
  <div 
    className="text-center"
    onDrop={handleDrop}
    onDragOver={handleDragOver}
  >
    <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
    <p className="text-lg font-medium mb-2">
      Varaqlarni bu yerga tashlang
    </p>
    <p className="text-sm text-gray-500 mb-4">
      yoki faylni tanlang
    </p>
    
    <div className="flex gap-3 justify-center">
      {/* Fayl tanlash */}
      <label className="btn-primary">
        <FileImage className="w-5 h-5" />
        Fayl Tanlash
        <input 
          type="file" 
          multiple 
          accept="image/*,application/pdf"
          className="hidden"
          onChange={handleFileSelect}
        />
      </label>
      
      {/* Kamera */}
      <button 
        onClick={openCamera}
        className="btn-secondary"
      >
        <Camera className="w-5 h-5" />
        Kamera
      </button>
      
      {/* Demo */}
      <button 
        onClick={loadDemoSheets}
        className="btn-outline"
      >
        <FileText className="w-5 h-5" />
        Demo Varaqlar
      </button>
    </div>
  </div>
  
  {/* Yuklangan varaqlar ro'yxati */}
  {uploadedSheets.length > 0 && (
    <div className="mt-6">
      <h3 className="font-medium mb-3">
        Yuklangan: {uploadedSheets.length} ta varaq
      </h3>
      <div className="grid grid-cols-4 gap-3">
        {uploadedSheets.map((sheet, i) => (
          <div key={i} className="relative group">
            <img 
              src={sheet.preview} 
              className="w-full h-32 object-cover rounded-lg"
            />
            <button 
              onClick={() => removeSheet(i)}
              className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )}
</div>
```

### **BOSQICH 2: Rasm Qayta Ishlash (Pre-processing)**

```javascript
async function preprocessImage(imageData) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // 1. Rasmni yuklash
  const img = await loadImage(imageData);
  canvas.width = img.width;
  canvas.height = img.height;
  ctx.drawImage(img, 0, 0);
  
  // 2. Corner markers orqali varaqni aniqlash
  const corners = detectCornerMarkers(ctx, canvas.width, canvas.height);
  
  if (!corners || corners.length !== 4) {
    throw new Error('Varaq chegaralari topilmadi. Iltimos, rasmni qayta oling.');
  }
  
  // 3. Perspektivani to'g'rilash (Perspective Correction)
  const correctedCanvas = correctPerspective(canvas, corners);
  
  // 4. Grayscale ga o'tkazish
  const grayscale = convertToGrayscale(correctedCanvas);
  
  // 5. Kontrast oshirish
  const enhanced = enhanceContrast(grayscale);
  
  // 6. Shovqinni kamaytirish (Noise Reduction)
  const denoised = reduceNoise(enhanced);
  
  // 7. Binary (qora-oq) ga o'tkazish
  const binary = applyThreshold(denoised, 128);
  
  return {
    original: canvas,
    processed: binary,
    corners: corners,
    quality: calculateImageQuality(binary)
  };
}

// Corner markers aniqlash
function detectCornerMarkers(ctx, width, height) {
  const markerSize = 40; // 10mm ≈ 40 pixels @ 96 DPI
  const corners = [];
  
  // To'rtta burchakni tekshirish
  const positions = [
    { x: 0, y: 0, name: 'top-left' },
    { x: width - markerSize, y: 0, name: 'top-right' },
    { x: 0, y: height - markerSize, name: 'bottom-left' },
    { x: width - markerSize, y: height - markerSize, name: 'bottom-right' }
  ];
  
  positions.forEach(pos => {
    const imageData = ctx.getImageData(pos.x, pos.y, markerSize, markerSize);
    const blackPixels = countBlackPixels(imageData);
    const ratio = blackPixels / (markerSize * markerSize);
    
    // 70%+ qora bo'lsa, marker topildi
    if (ratio > 0.7) {
      corners.push({
        x: pos.x + markerSize / 2,
        y: pos.y + markerSize / 2,
        name: pos.name
      });
    }
  });
  
  return corners.length === 4 ? corners : null;
}

// Perspektivani to'g'rilash
function correctPerspective(canvas, corners) {
  // A4 nisbati: 210mm / 297mm = 0.707
  const targetWidth = 1240;  // px
  const targetHeight = 1754; // px
  
  const correctedCanvas = document.createElement('canvas');
  correctedCanvas.width = targetWidth;
  correctedCanvas.height = targetHeight;
  const ctx = correctedCanvas.getContext('2d');
  
  // Perspective transform matrix
  // Bu murakkab matematik operatsiya, oddiy tushuntirish:
  // 4 ta corner nuqtadan to'rtburchak yasash
  
  // Sodda variant: agar corners to'g'ri joylashgan bo'lsa
  ctx.drawImage(
    canvas,
    corners[0].x, corners[0].y, // source x, y
    corners[1].x - corners[0].x, // source width
    corners[3].y - corners[0].y, // source height
    0, 0, // destination x, y
    targetWidth, targetHeight // destination width, height
  );
  
  return correctedCanvas;
}

// Grayscale konvertatsiya
function convertToGrayscale(canvas) {
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  
  for (let i = 0; i < data.length; i += 4) {
    const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
    data[i] = data[i + 1] = data[i + 2] = avg;
  }
  
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}

// Kontrast oshirish
function enhanceContrast(canvas, factor = 1.5) {
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, (data[i] - 128) * factor + 128);
    data[i + 1] = Math.min(255, (data[i + 1] - 128) * factor + 128);
    data[i + 2] = Math.min(255, (data[i + 2] - 128) * factor + 128);
  }
  
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}

// Threshold (qora-oq qilish)
function applyThreshold(canvas, threshold = 128) {
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  
  for (let i = 0; i < data.length; i += 4) {
    const value = data[i] < threshold ? 0 : 255;
    data[i] = data[i + 1] = data[i + 2] = value;
  }
  
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

### **BOSQICH 3: QR/Barcode O'qish**

```javascript
async function readSheetMetadata(processedImage) {
  // QR kod orqali imtihon ID va to'plam aniqlash
  const qrRegion = extractRegion(processedImage, {
    x: 175, y: 15, width: 25, height: 25
  });
  
  const qrData = await decodeQR(qrRegion);
  // qrData: { examId: "exam_123", variant: "A" }
  
  // Barcode orqali talaba ID (agar kiritilgan bo'lsa)
  const barcodeRegion = extractRegion(processedImage, {
    x: 160, y: 40, width: 35, height: 10
  });
  
  const studentId = await decodeBarcode(barcodeRegion);
  
  return {
    examId: qrData.examId,
    variant: qrData.variant,
    studentId: studentId,
    timestamp: new Date().toISOString()
  };
}

// QR kod dekodlash (soddalashtirilgan)
async function decodeQR(imageData) {
  // Haqiqiy dasturda jsQR kutubxonasidan foydalaniladi
  // Bu yerda simulyatsiya
  
  try {
    // const code = jsQR(imageData.data, imageData.width, imageData.height);
    // return JSON.parse(code.data);
    
    // Demo uchun:
    return {
      examId: "exam_" + Math.random().toString(36).substr(2, 9),
      variant: "A"
    };
  } catch (error) {
    throw new Error("QR kod o'qilmadi. Varaq sifatini tekshiring.");
  }
}
```

### **BOSQICH 4: Doirachalarni Aniqlash va O'qish**

```javascript
async function detectAnswers(processedImage, examStructure) {
  const answers = {};
  
  // Har bir mavzu bo'yicha
  for (const topic of examStructure.topics) {
    answers[topic.id] = {};
    
    // Har bir bo'lim bo'yicha
    for (const section of topic.sections) {
      const sectionAnswers = [];
      
      // Har bir savol uchun
      for (let q = 0; q < section.questionCount; q++) {
        const questionNum = section.startQuestion + q;
        
        // Savol koordinatalarini hisoblash
        const coords = calculateQuestionCoordinates(
          questionNum, 
          examStructure
        );
        
        // Har bir variant (A, B, C, D, E) doirachasini tekshirish
        const markedVariant = detectMarkedBubble(
          processedImage, 
          coords
        );
        
        sectionAnswers.push({
          questionNumber: questionNum,
          markedAnswer: markedVariant, // 'A', 'B', 'C', 'D', 'E' yoki null
          confidence: markedVariant ? calculateConfidence(processedImage, coords, markedVariant) : 0
        });
      }
      
      answers[topic.id][section.id] = sectionAnswers;
    }
  }
  
  return answers;
}

// Savol koordinatalarini hisoblash
function calculateQuestionCoordinates(questionNum, structure) {
  // A4 o'lchamlari (pikselda)
  const pageWidth = 1240;
  const margin = 100;
  const startY = 400; // Javoblar jadvali boshlangan joy
  
  // 2 ustun layout
  const questionsPerRow = 2;
  const columnWidth = (pageWidth - 2 * margin) / 2;
  
  const row = Math.floor((questionNum - 1) / questionsPerRow);
  const col = (questionNum - 1) % questionsPerRow;
  
  const x = margin + (col * columnWidth) + 40; // 40 = raqam uchun joy
  const y = startY + (row * 30); // 30 = qator balandligi
  
  return {
    questionNumber: questionNum,
    x: x,
    y: y,
    bubbles: [
      { variant: 'A', x: x, y: y },
      { variant: 'B', x: x + 30, y: y },
      { variant: 'C', x: x + 60, y: y },
      { variant: 'D', x: x + 90, y: y },
      { variant: 'E', x: x + 120, y: y }
    ]
  };
}

// Belgilangan doirachani aniqlash
function detectMarkedBubble(image, coords) {
  const ctx = image.getContext('2d');
  const bubbleRadius = 12; // pikselda
  let maxDarkness = 0;
  let markedVariant = null;
  
  // Har bir variant doirachasini tekshirish
  coords.bubbles.forEach(bubble => {
    // Doiracha ichidagi pixellarni olish
    const centerX = bubble.x;
    const centerY = bubble.y;
    
    const imageData = ctx.getImageData(
      centerX - bubbleRadius,
      centerY - bubbleRadius,
      bubbleRadius * 2,
      bubbleRadius * 2
    );
    
    // Qora pixellar sonini hisoblash
    const darkness = calculateDarkness(imageData, bubbleRadius);
    
    // Eng qora doiracha = belgilangan javob
    if (darkness > maxDarkness && darkness > 0.6) { // 60% threshold
      maxDarkness = darkness;
      markedVariant = bubble.variant;
    }
  });
  
  return markedVariant;
}

// Doiracha qoraligini hisoblash
function calculateDarkness(imageData, radius) {
  const data = imageData.data;
  let darkPixels = 0;
  let totalPixels = 0;
  
  const centerX = radius;
  const centerY = radius;
  
  for (let y = 0; y < imageData.height; y++) {
    for (let x = 0; x < imageData.width; x++) {
      // Faqat doiracha ichidagi pixellar
      const distance = Math.sqrt(
        Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)
      );
      
      if (distance <= radius) {
        const index = (y * imageData.width + x) * 4;
        const brightness = data[index]; // grayscale bo'lgani uchun
        
        if (brightness < 128) { // qora pixel
          darkPixels++;
        }
        totalPixels++;
      }
    }
  }
  
  return darkPixels / totalPixels;
}

// Ishonchlilik darajasini hisoblash
function calculateConfidence(image, coords, variant) {
  const bubble = coords.bubbles.find(b => b.variant === variant);
  const ctx = image.getContext('2d');
  const radius = 12;
  
  const imageData = ctx.getImageData(
    bubble.x - radius,
    bubble.y - radius,
    radius * 2,
    radius * 2
  );
  
  const darkness = calculateDarkness(imageData, radius);
  
  // 0.6-1.0 oralig'ini 0-100% ga konvertatsiya
  const confidence = Math.min(100, Math.max(0, (darkness - 0.6) / 0.4 * 100));
  
  return Math.round(confidence);
}
```

### **BOSQICH 5: Javoblarni Tekshirish va Ball Hisoblash**

```javascript
function gradeAnswers(detectedAnswers, answerKey, examStructure) {
  const results = {
    totalQuestions: 0,
    correctAnswers: 0,
    incorrectAnswers: 0,
    unanswered: 0,
    totalScore: 0,
    maxScore: 0,
    percentage: 0,
    topicResults: [],
    detailedResults: []
  };
  
  // Har bir mavzu bo'yicha
  examStructure.topics.forEach(topic => {
    const topicResult = {
      topicId: topic.id,
      topicName: topic.name,
      correct: 0,
      incorrect: 0,
      unanswered: 0,
      score: 0,
      maxScore: 0,
      sections: []
    };
    
    // Har bir bo'lim bo'yicha
    topic.sections.forEach(section => {
      const sectionResult = {
        sectionId: section.id,
        sectionName: section.name,
        correct: 0,
        incorrect: 0,
        unanswered: 0,
        score: 0,
        maxScore: section.questionCount * section.correctScore,
        questions: []
      };
      
      // Har bir savol uchun
      const sectionAnswers = detectedAnswers[topic.id][section.id];
      
      sectionAnswers.forEach(answer => {
        const questionNum = answer.questionNumber;
        const studentAnswer = answer.markedAnswer;
        const correctAnswer = answerKey[questionNum];
        
        const questionResult = {
          questionNumber: questionNum,
          studentAnswer: studentAnswer,
          correctAnswer: correctAnswer,
          isCorrect: studentAnswer === correctAnswer,
          confidence: answer.confidence,
          pointsEarned: 0
        };
        
        results.totalQuestions++;
        
        if (!studentAnswer) {
          // Javob berilmagan
          results.unanswered++;
          sectionResult.unanswered++;
          questionResult.pointsEarned = 0;
        } else if (studentAnswer === correctAnswer) {
          // To'g'ri javob
          results.correctAnswers++;
          sectionResult.correct++;
          questionResult.pointsEarned = section.correctScore;
          sectionResult.score += section.correctScore;
        } else {
          // Noto'g'ri javob
          results.incorrectAnswers++;
          sectionResult.incorrect++;
          questionResult.pointsEarned = section.incorrectScore; // manfiy
          sectionResult.score += section.incorrectScore;
        }
        
        sectionResult.questions.push(questionResult);
        results.detailedResults.push(questionResult);
      });
      
      topicResult.score += sectionResult.score;
      topicResult.maxScore += sectionResult.maxScore;
      topicResult.correct += sectionResult.correct;
      topicResult.incorrect += sectionResult.incorrect;
      topicResult.unanswered += sectionResult.unanswered;
      topicResult.sections.push(sectionResult);
    });
    
    results.totalScore += topicResult.score;
    results.maxScore += topicResult.maxScore;
    results.topicResults.push(topicResult);
  });
  
  // Foiz hisoblash
  results.percentage = (results.totalScore / results.maxScore) * 100;
  
  // Baho aniqlash
  results.grade = calculateGrade(results.percentage);
  
  return results;
}

// Baho aniqlash
function calculateGrade(percentage) {
  if (percentage >= 86) return { numeric: 5, text: "A'lo" };
  if (percentage >= 71) return { numeric: 4, text: "Yaxshi" };
  if (percentage >= 56) return { numeric: 3, text: "Qoniqarli" };
  return { numeric: 2, text: "Qoniqarsiz" };
}
```

### **BOSQICH 6: Natijalarni Ko'rsatish**

```javascript
<div className="space-y-6">
  {/* Umumiy Natija */}
  <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl p-6">
    <div className="grid grid-cols-4 gap-4">
      <div className="text-center">
        <div className="text-4xl font-bold">{results.totalScore}</div>
        <div className="text-sm opacity-90">Ball</div>
      </div>
      <div className="text-center">
        <div className="text-4xl font-bold">{results.percentage.toFixed(1)}%</div>
        <div className="text-sm opacity-90">Foiz</div>
      </div>
      <div className="text-center">
        <div className="text-4xl font-bold">{results.correctAnswers}</div>
        <div className="text-sm opacity-90">To'g'ri</div>
      </div>
      <div className="text-center">
        <div className="text-4xl font-bold">{results.grade.numeric}</div>
        <div className="text-sm opacity-90">{results.grade.text}</div>
      </div>
    </div>
  </div>
  
  {/* Vizual Statistika */}
  <div className="grid grid-cols-3 gap-4">
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-2xl font-bold text-green-700">
            {results.correctAnswers}
          </div>
          <div className="text-sm text-green-600">To'g'ri javoblar</div>
        </div>
        <CheckCircle className="w-12 h-12 text-green-500" />
      </div>
    </div>
    
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-2xl font-bold text-red-700">
            {results.incorrectAnswers}
          </div>
          <div className="text-sm text-red-600">Noto'g'ri javoblar</div>
        </div>
        <XCircle className="w-12 h-12 text-red-500" />
      </div>
    </div>
    
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-2xl font-bold text-gray-700">
            {results.unanswered}
          </div>
          <div className="text-sm text-gray-600">Javobsiz</div>
        </div>
        <MinusCircle className="w-12 h-12 text-gray-500" />
      </div>
    </div>
  </div>
  
  {/* Mavzular bo'yicha natijalar */}
  <div className="bg-white rounded-xl border p-6">
    <h3 className="text-lg font-bold mb-4">Mavzular bo'yicha natijalar</h3>
    
    {results.topicResults.map(topic => (
      <div key={topic.topicId} className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium">{topic.topicName}</h4>
          <span className="text-sm text-gray-600">
            {topic.score} / {topic.maxScore} ball
          </span>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all"
            style={{ width: `${(topic.score / topic.maxScore) * 100}%` }}
          />
        </div>
        
        {/* Bo'limlar */}
        <div className="mt-3 ml-4 space-y-2">
          {topic.sections.map(section => (
            <div key={section.sectionId} className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{section.sectionName}</span>
              <div className="flex items-center gap-3">
                <span className="text-green-600">✓ {section.correct}</span>
                <span className="text-red-600">✗ {section.incorrect}</span>
                <span className="text-gray-500">— {section.unanswered}</span>
                <span className="font-medium">{section.score} ball</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
  
  {/* Batafsil javoblar */}
  <div className="bg-white rounded-xl border p-6">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-bold">Batafsil natijalar</h3>
      <button 
        onClick={() => setShowDetails(!showDetails)}
        className="text-blue-600 text-sm"
      >
        {showDetails ? 'Yashirish' : 'Ko\'rsatish'}
      </button>
    </div>
    
    {showDetails && (
      <div className="grid grid-cols-5 gap-2">
        {results.detailedResults.map(q => (
          <div 
            key={q.questionNumber}
            className={`
              p-3 rounded-lg border-2 text-center
              ${q.isCorrect ? 'bg-green-50 border-green-300' : 
                !q.studentAnswer ? 'bg-gray-50 border-gray-300' :
                'bg-red-50 border-red-300'}
            `}
          >
            <div className="text-xs text-gray-600 mb-1">
              Savol {q.questionNumber}
            </div>
            <div className="font-bold text-lg">
              {q.studentAnswer || '—'}
            </div>
            <div className="text-xs text-gray-500">
              To'g'ri: {q.correctAnswer}
            </div>
            {q.confidence > 0 && (
              <div className="text-xs text-gray-400 mt-1">
                {q.confidence}%
              </div>
            )}
          </div>
        ))}
      </div>
    )}
  </div>
  
  {/* Eksport tugmalari */}
  <div className="flex gap-3">
    <button 
      onClick={() => exportToPDF(results)}
      className="btn-primary"
    >
      <FileDown className="w-5 h-5" />
      PDF Yuklab Olish
    </button>
    
    <button 
      onClick={() => exportToExcel(results)}
      className="btn-secondary"
    >
      <FileSpreadsheet className="w-5 h-5" />
      Excel Yuklab Olish
    </button>
    
    <button 
      onClick={() => saveToDatabase(results)}
      className="btn-outline"
    >
      <Save className="w-5 h-5" />
      Saqlash
    </button>
  </div>
</div>
```
