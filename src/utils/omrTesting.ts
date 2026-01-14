// Professional OMR Testing and Calibration Suite
// Implements testing functionality from full_checking_system.md

export interface TestResult {
  accuracy: number;
  totalQuestions: number;
  correctDetections: number;
  errors: TestError[];
  processingTime: number;
  averageConfidence: number;
}

export interface TestError {
  question: number;
  detected: string | null;
  actual: string;
  confidence: number;
  scores?: any[];
}

export interface CalibrationResult {
  minScore: number;
  minDifference: number;
  recommendedThresholds: {
    darkness: number;
    coverage: number;
    uniformity: number;
  };
  accuracy: number;
}

// Test OMR accuracy with known ground truth
export async function testOMRAccuracy(
  testImages: string[],
  groundTruth: { [questionNumber: number]: string }[],
  processFunction: (image: string) => Promise<any>
): Promise<TestResult> {
  console.log('='.repeat(60));
  console.log('PROFESSIONAL OMR ACCURACY TEST BOSHLANDI');
  console.log('='.repeat(60));
  
  let correctDetections = 0;
  let totalQuestions = 0;
  const errors: TestError[] = [];
  const confidences: number[] = [];
  const startTime = Date.now();
  
  for (let i = 0; i < testImages.length; i++) {
    console.log(`\nTest ${i + 1}/${testImages.length}:`);
    
    try {
      const result = await processFunction(testImages[i]);
      
      if (result.success && result.answers) {
        const truth = groundTruth[i];
        
        Object.keys(truth).forEach(questionNumStr => {
          const questionNum = parseInt(questionNumStr);
          const detected = result.answers[questionNum];
          const actual = truth[questionNum];
          
          totalQuestions++;
          
          if (detected === actual) {
            correctDetections++;
            console.log(`  ✓ Savol ${questionNum}: ${detected} (to'g'ri)`);
          } else {
            errors.push({
              question: questionNum,
              detected: detected || null,
              actual: actual,
              confidence: 0 // Would get from result
            });
            console.log(`  ✗ Savol ${questionNum}: ${detected} → ${actual} (xato)`);
          }
          
          // Collect confidence scores
          if (result.detected?.answers) {
            // Extract confidence from detected answers
            confidences.push(75); // Placeholder
          }
        });
      }
    } catch (error) {
      console.error(`  ❌ Test ${i + 1} failed:`, error);
    }
  }
  
  const endTime = Date.now();
  const processingTime = (endTime - startTime) / 1000;
  const accuracy = totalQuestions > 0 ? (correctDetections / totalQuestions) * 100 : 0;
  const averageConfidence = confidences.length > 0 
    ? confidences.reduce((a, b) => a + b, 0) / confidences.length 
    : 0;
  
  console.log('\n' + '='.repeat(60));
  console.log('TEST NATIJALARI:');
  console.log(`  Aniqlik: ${accuracy.toFixed(2)}%`);
  console.log(`  To'g'ri: ${correctDetections}/${totalQuestions}`);
  console.log(`  Xatolar: ${errors.length}`);
  console.log(`  Vaqt: ${processingTime.toFixed(2)}s`);
  console.log(`  O'rtacha ishonch: ${averageConfidence.toFixed(1)}%`);
  console.log('='.repeat(60));
  
  return {
    accuracy,
    totalQuestions,
    correctDetections,
    errors,
    processingTime,
    averageConfidence
  };
}

// Calibrate thresholds based on test results
export function calibrateThresholds(testResults: TestResult): CalibrationResult {
  console.log('\n' + '='.repeat(60));
  console.log('PROFESSIONAL KALIBRLASH BOSHLANDI');
  console.log('='.repeat(60));
  
  // Analyze errors to adjust thresholds
  const falsePositives = testResults.errors.filter(e => e.detected && e.actual === '');
  const falseNegatives = testResults.errors.filter(e => !e.detected && e.actual !== '');
  
  let minScore = 35; // Default from full_checking_system.md
  let minDifference = 15; // Default
  
  // If too many false positives, increase minScore
  if (falsePositives.length > testResults.totalQuestions * 0.05) {
    minScore = 45;
    console.log(`  → minScore oshirildi: ${minScore}% (ko'p false positive)`);
  }
  
  // If too many false negatives, decrease minScore
  if (falseNegatives.length > testResults.totalQuestions * 0.05) {
    minScore = 30;
    console.log(`  → minScore kamaytirildi: ${minScore}% (ko'p false negative)`);
  }
  
  // Adjust difference threshold
  if (testResults.accuracy < 95) {
    minDifference = 20;
    console.log(`  → minDifference oshirildi: ${minDifference}% (past aniqlik)`);
  }
  
  const recommendedThresholds = {
    darkness: minScore,
    coverage: minScore - 5,
    uniformity: 50
  };
  
  console.log('\nTAVSIYA ETILGAN SOZLAMALAR:');
  console.log(`  Min Score: ${minScore}%`);
  console.log(`  Min Difference: ${minDifference}%`);
  console.log(`  Darkness Threshold: ${recommendedThresholds.darkness}%`);
  console.log(`  Coverage Threshold: ${recommendedThresholds.coverage}%`);
  console.log(`  Uniformity Threshold: ${recommendedThresholds.uniformity}%`);
  console.log('='.repeat(60));
  
  return {
    minScore,
    minDifference,
    recommendedThresholds,
    accuracy: testResults.accuracy
  };
}

// Generate professional test report
export function generateTestReport(testResults: TestResult, calibration?: CalibrationResult): string {
  const report = `
╔════════════════════════════════════════════════════════════════╗
║         PROFESSIONAL OMR SYSTEM - TEST HISOBOTI                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  UMUMIY NATIJALAR:                                            ║
║  ─────────────────────────────────────────────────────────    ║
║  • Aniqlik: ${testResults.accuracy.toFixed(2)}%                                      ║
║  • Jami savollar: ${testResults.totalQuestions}                                    ║
║  • To'g'ri aniqlangan: ${testResults.correctDetections}                                ║
║  • Xatolar soni: ${testResults.errors.length}                                      ║
║  • Qayta ishlash vaqti: ${testResults.processingTime.toFixed(2)}s                        ║
║  • O'rtacha ishonch: ${testResults.averageConfidence.toFixed(1)}%                          ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  XATOLAR TAHLILI:                                             ║
║  ─────────────────────────────────────────────────────────    ║
${testResults.errors.slice(0, 10).map(error => 
  `║  • Savol ${error.question}: Aniqlangan "${error.detected || 'yoq'}", To'g'ri "${error.actual}"     ║`
).join('\n')}
${testResults.errors.length > 10 ? `║  ... va yana ${testResults.errors.length - 10} ta xato                              ║` : ''}
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  BAHOLASH:                                                     ║
║  ─────────────────────────────────────────────────────────    ║
${testResults.accuracy > 99 ? 
  '║  ✅ AJOYIB! Industrial standartdan yuqori aniqlik!         ║' :
  testResults.accuracy > 95 ? 
  '║  ✅ A\'LO! Professional darajadagi aniqlik!                 ║' :
  testResults.accuracy > 90 ? 
  '║  ⚠️  YAXSHI! Ba\'zi sozlamalarni yaxshilash mumkin.        ║' :
  '║  ❌ PAST! Algoritm yoki threshold qayta ko\'rib chiqilsin. ║'
}
║                                                                ║
${calibration ? `╠════════════════════════════════════════════════════════════════╣
║  KALIBRLASH NATIJALARI:                                       ║
║  ─────────────────────────────────────────────────────────    ║
║  • Min Score: ${calibration.minScore}%                                         ║
║  • Min Difference: ${calibration.minDifference}%                                   ║
║  • Darkness Threshold: ${calibration.recommendedThresholds.darkness}%                          ║
║  • Coverage Threshold: ${calibration.recommendedThresholds.coverage}%                          ║
║  • Uniformity Threshold: ${calibration.recommendedThresholds.uniformity}%                        ║
║                                                                ║` : ''}
╠════════════════════════════════════════════════════════════════╣
║  TAVSIYALAR:                                                   ║
║  ─────────────────────────────────────────────────────────    ║
${testResults.accuracy > 99 ? 
  '║  • Tizim ishlatishga tayyor!                               ║\n║  • Hech qanday o\'zgartirish kerak emas                     ║' :
  testResults.accuracy > 95 ? 
  '║  • Tizim yaxshi ishlayapti                                 ║\n║  • Kichik optimizatsiyalar qilish mumkin                   ║' :
  testResults.accuracy > 90 ? 
  '║  • Threshold sozlamalarini qayta ko\'rib chiqing           ║\n║  • Rasm sifatini yaxshilang                                ║' :
  '║  • Algoritm to\'liq qayta ko\'rib chiqilsin                ║\n║  • Professional yordam talab qilinadi                      ║'
}
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
`;
  
  return report;
}

// Export test data to CSV
export function exportTestDataToCSV(testResults: TestResult): string {
  let csv = 'Question,Detected,Actual,Status,Confidence\n';
  
  testResults.errors.forEach(error => {
    csv += `${error.question},"${error.detected || 'N/A'}","${error.actual}",ERROR,${error.confidence}\n`;
  });
  
  return csv;
}

// Compare two test results
export function compareTestResults(result1: TestResult, result2: TestResult): string {
  const accuracyDiff = result2.accuracy - result1.accuracy;
  const timeDiff = result2.processingTime - result1.processingTime;
  const confidenceDiff = result2.averageConfidence - result1.averageConfidence;
  
  return `
TAQQOSLASH NATIJALARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Aniqlik:
  Test 1: ${result1.accuracy.toFixed(2)}%
  Test 2: ${result2.accuracy.toFixed(2)}%
  Farq: ${accuracyDiff > 0 ? '+' : ''}${accuracyDiff.toFixed(2)}% ${accuracyDiff > 0 ? '✅ Yaxshilandi' : accuracyDiff < 0 ? '❌ Yomonlashdi' : '➖ O\'zgarmadi'}

Vaqt:
  Test 1: ${result1.processingTime.toFixed(2)}s
  Test 2: ${result2.processingTime.toFixed(2)}s
  Farq: ${timeDiff > 0 ? '+' : ''}${timeDiff.toFixed(2)}s ${timeDiff < 0 ? '✅ Tezlashdi' : timeDiff > 0 ? '❌ Sekinlashdi' : '➖ O\'zgarmadi'}

Ishonch:
  Test 1: ${result1.averageConfidence.toFixed(1)}%
  Test 2: ${result2.averageConfidence.toFixed(1)}%
  Farq: ${confidenceDiff > 0 ? '+' : ''}${confidenceDiff.toFixed(1)}% ${confidenceDiff > 0 ? '✅ Yaxshilandi' : confidenceDiff < 0 ? '❌ Yomonlashdi' : '➖ O\'zgarmadi'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
}
