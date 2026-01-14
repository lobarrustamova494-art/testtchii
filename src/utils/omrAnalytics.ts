// Professional OMR Analytics and Statistics
// Advanced analytics for OMR system performance

export interface OMRStatistics {
  totalSheets: number;
  totalQuestions: number;
  averageAccuracy: number;
  averageProcessingTime: number;
  averageConfidence: number;
  qualityDistribution: {
    excellent: number;  // 95-100%
    good: number;       // 85-95%
    fair: number;       // 75-85%
    poor: number;       // <75%
  };
  warningDistribution: {
    noMark: number;
    multipleMarks: number;
    lowDifference: number;
    total: number;
  };
  confidenceDistribution: {
    high: number;       // 90-100%
    medium: number;     // 70-90%
    low: number;        // <70%
  };
}

export interface QuestionAnalytics {
  questionNumber: number;
  totalAttempts: number;
  correctRate: number;
  averageConfidence: number;
  commonErrors: { [variant: string]: number };
  warningRate: number;
}

export interface PerformanceMetrics {
  throughput: number;           // sheets per minute
  averageLatency: number;       // seconds per sheet
  errorRate: number;            // percentage
  systemUptime: number;         // percentage
  qualityScore: number;         // 0-100
}

// Calculate comprehensive OMR statistics
export function calculateOMRStatistics(results: any[]): OMRStatistics {
  const stats: OMRStatistics = {
    totalSheets: results.length,
    totalQuestions: 0,
    averageAccuracy: 0,
    averageProcessingTime: 0,
    averageConfidence: 0,
    qualityDistribution: {
      excellent: 0,
      good: 0,
      fair: 0,
      poor: 0
    },
    warningDistribution: {
      noMark: 0,
      multipleMarks: 0,
      lowDifference: 0,
      total: 0
    },
    confidenceDistribution: {
      high: 0,
      medium: 0,
      low: 0
    }
  };
  
  if (results.length === 0) return stats;
  
  let totalAccuracy = 0;
  let totalTime = 0;
  let totalConfidence = 0;
  let totalQuestions = 0;
  
  results.forEach(result => {
    if (!result.results) return;
    
    // Accuracy
    const accuracy = result.results.percentage;
    totalAccuracy += accuracy;
    
    // Quality distribution
    if (accuracy >= 95) stats.qualityDistribution.excellent++;
    else if (accuracy >= 85) stats.qualityDistribution.good++;
    else if (accuracy >= 75) stats.qualityDistribution.fair++;
    else stats.qualityDistribution.poor++;
    
    // Processing time
    totalTime += result.results.duration || 0;
    
    // Questions and confidence
    if (result.results.detailedResults) {
      result.results.detailedResults.forEach((q: any) => {
        totalQuestions++;
        totalConfidence += q.confidence;
        
        // Confidence distribution
        if (q.confidence >= 90) stats.confidenceDistribution.high++;
        else if (q.confidence >= 70) stats.confidenceDistribution.medium++;
        else stats.confidenceDistribution.low++;
        
        // Warning distribution
        if (q.warning) {
          stats.warningDistribution.total++;
          if (q.warning === 'NO_MARK') stats.warningDistribution.noMark++;
          else if (q.warning === 'MULTIPLE_MARKS') stats.warningDistribution.multipleMarks++;
          else if (q.warning === 'LOW_DIFFERENCE') stats.warningDistribution.lowDifference++;
        }
      });
    }
  });
  
  stats.totalQuestions = totalQuestions;
  stats.averageAccuracy = totalAccuracy / results.length;
  stats.averageProcessingTime = totalTime / results.length;
  stats.averageConfidence = totalQuestions > 0 ? totalConfidence / totalQuestions : 0;
  
  return stats;
}

// Analyze question-level performance
export function analyzeQuestionPerformance(results: any[]): QuestionAnalytics[] {
  const questionMap = new Map<number, {
    attempts: number;
    correct: number;
    confidences: number[];
    errors: { [variant: string]: number };
    warnings: number;
  }>();
  
  results.forEach(result => {
    if (!result.results?.detailedResults) return;
    
    result.results.detailedResults.forEach((q: any) => {
      if (!questionMap.has(q.questionNumber)) {
        questionMap.set(q.questionNumber, {
          attempts: 0,
          correct: 0,
          confidences: [],
          errors: {},
          warnings: 0
        });
      }
      
      const qData = questionMap.get(q.questionNumber)!;
      qData.attempts++;
      
      if (q.isCorrect) {
        qData.correct++;
      } else if (q.studentAnswer) {
        qData.errors[q.studentAnswer] = (qData.errors[q.studentAnswer] || 0) + 1;
      }
      
      qData.confidences.push(q.confidence);
      
      if (q.warning) {
        qData.warnings++;
      }
    });
  });
  
  const analytics: QuestionAnalytics[] = [];
  
  questionMap.forEach((data, questionNumber) => {
    analytics.push({
      questionNumber,
      totalAttempts: data.attempts,
      correctRate: (data.correct / data.attempts) * 100,
      averageConfidence: data.confidences.reduce((a, b) => a + b, 0) / data.confidences.length,
      commonErrors: data.errors,
      warningRate: (data.warnings / data.attempts) * 100
    });
  });
  
  return analytics.sort((a, b) => a.questionNumber - b.questionNumber);
}

// Calculate performance metrics
export function calculatePerformanceMetrics(
  results: any[],
  startTime: Date,
  endTime: Date
): PerformanceMetrics {
  const totalTime = (endTime.getTime() - startTime.getTime()) / 1000; // seconds
  const totalSheets = results.length;
  
  const throughput = totalSheets > 0 ? (totalSheets / totalTime) * 60 : 0; // sheets per minute
  
  const totalProcessingTime = results.reduce((sum, r) => 
    sum + (r.results?.duration || 0), 0
  );
  const averageLatency = totalSheets > 0 ? totalProcessingTime / totalSheets : 0;
  
  const totalQuestions = results.reduce((sum, r) => 
    sum + (r.results?.totalQuestions || 0), 0
  );
  const totalErrors = results.reduce((sum, r) => 
    sum + (r.results?.incorrectAnswers || 0) + (r.results?.unanswered || 0), 0
  );
  const errorRate = totalQuestions > 0 ? (totalErrors / totalQuestions) * 100 : 0;
  
  const totalQuality = results.reduce((sum, r) => 
    sum + (r.results?.quality?.overall || 0), 0
  );
  const qualityScore = totalSheets > 0 ? totalQuality / totalSheets : 0;
  
  return {
    throughput,
    averageLatency,
    errorRate,
    systemUptime: 99.9, // Placeholder
    qualityScore
  };
}

// Generate professional analytics report
export function generateAnalyticsReport(
  stats: OMRStatistics,
  performance: PerformanceMetrics,
  _questionAnalytics?: QuestionAnalytics[]
): string {
  const report = `
╔════════════════════════════════════════════════════════════════╗
║       PROFESSIONAL OMR SYSTEM - ANALYTICS HISOBOTI             ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  UMUMIY STATISTIKA:                                           ║
║  ─────────────────────────────────────────────────────────    ║
║  • Jami varaqlar: ${stats.totalSheets.toString().padEnd(43)} ║
║  • Jami savollar: ${stats.totalQuestions.toString().padEnd(43)} ║
║  • O'rtacha aniqlik: ${stats.averageAccuracy.toFixed(1)}%${' '.repeat(36)} ║
║  • O'rtacha vaqt: ${stats.averageProcessingTime.toFixed(2)}s${' '.repeat(38)} ║
║  • O'rtacha ishonch: ${stats.averageConfidence.toFixed(1)}%${' '.repeat(34)} ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  SIFAT TAQSIMOTI:                                             ║
║  ─────────────────────────────────────────────────────────    ║
║  • A'lo (95-100%): ${stats.qualityDistribution.excellent} varaq${' '.repeat(30)} ║
║  • Yaxshi (85-95%): ${stats.qualityDistribution.good} varaq${' '.repeat(29)} ║
║  • O'rtacha (75-85%): ${stats.qualityDistribution.fair} varaq${' '.repeat(27)} ║
║  • Past (<75%): ${stats.qualityDistribution.poor} varaq${' '.repeat(33)} ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  OGOHLANTIRISH STATISTIKASI:                                  ║
║  ─────────────────────────────────────────────────────────    ║
║  • Belgi yo'q: ${stats.warningDistribution.noMark}${' '.repeat(42)} ║
║  • Ko'p belgi: ${stats.warningDistribution.multipleMarks}${' '.repeat(42)} ║
║  • Aniq emas: ${stats.warningDistribution.lowDifference}${' '.repeat(43)} ║
║  • Jami: ${stats.warningDistribution.total}${' '.repeat(48)} ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  ISHONCH TAQSIMOTI:                                           ║
║  ─────────────────────────────────────────────────────────    ║
║  • Yuqori (90-100%): ${stats.confidenceDistribution.high} savol${' '.repeat(27)} ║
║  • O'rtacha (70-90%): ${stats.confidenceDistribution.medium} savol${' '.repeat(26)} ║
║  • Past (<70%): ${stats.confidenceDistribution.low} savol${' '.repeat(32)} ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  TIZIM ISHLASHI:                                              ║
║  ─────────────────────────────────────────────────────────    ║
║  • Throughput: ${performance.throughput.toFixed(1)} varaq/min${' '.repeat(30)} ║
║  • Latency: ${performance.averageLatency.toFixed(2)}s/varaq${' '.repeat(34)} ║
║  • Xatolik darajasi: ${performance.errorRate.toFixed(1)}%${' '.repeat(32)} ║
║  • Sifat ko'rsatkichi: ${performance.qualityScore.toFixed(1)}%${' '.repeat(29)} ║
║  • System Uptime: ${performance.systemUptime.toFixed(1)}%${' '.repeat(32)} ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  BAHOLASH:                                                     ║
║  ─────────────────────────────────────────────────────────    ║
${stats.averageAccuracy > 99 ? 
  '║  ✅ PROFESSIONAL: Industrial standart darajasida!          ║' :
  stats.averageAccuracy > 95 ? 
  '║  ✅ A\'LO: Juda yaxshi natijalar!                          ║' :
  stats.averageAccuracy > 90 ? 
  '║  ⚠️  YAXSHI: Yaxshilash imkoniyatlari mavjud              ║' :
  '║  ❌ PAST: Tizimni qayta sozlash kerak                     ║'
}
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
`;
  
  return report;
}

// Export analytics to JSON
export function exportAnalyticsToJSON(
  stats: OMRStatistics,
  performance: PerformanceMetrics,
  questionAnalytics?: QuestionAnalytics[]
): string {
  return JSON.stringify({
    timestamp: new Date().toISOString(),
    statistics: stats,
    performance: performance,
    questionAnalytics: questionAnalytics || []
  }, null, 2);
}

// Generate trend analysis
export function analyzeTrends(historicalData: OMRStatistics[]): {
  accuracyTrend: 'improving' | 'declining' | 'stable';
  speedTrend: 'improving' | 'declining' | 'stable';
  qualityTrend: 'improving' | 'declining' | 'stable';
} {
  if (historicalData.length < 2) {
    return {
      accuracyTrend: 'stable',
      speedTrend: 'stable',
      qualityTrend: 'stable'
    };
  }
  
  const recent = historicalData[historicalData.length - 1];
  const previous = historicalData[historicalData.length - 2];
  
  const accuracyChange = recent.averageAccuracy - previous.averageAccuracy;
  const speedChange = recent.averageProcessingTime - previous.averageProcessingTime;
  const qualityChange = recent.averageConfidence - previous.averageConfidence;
  
  return {
    accuracyTrend: accuracyChange > 1 ? 'improving' : accuracyChange < -1 ? 'declining' : 'stable',
    speedTrend: speedChange < -0.1 ? 'improving' : speedChange > 0.1 ? 'declining' : 'stable',
    qualityTrend: qualityChange > 2 ? 'improving' : qualityChange < -2 ? 'declining' : 'stable'
  };
}
