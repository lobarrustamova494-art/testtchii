import { ArrowLeft, Download, Edit, FileCheck, Key } from 'lucide-react';
import React, { useState } from 'react';
import { Exam, Toast as ToastType } from '../types';
import { downloadAllPDFs, downloadPDF } from '../utils/pdfGenerator';
import { calculateExamStats, formatDate } from '../utils/storage';
import Toast from './Toast';

interface ExamPreviewProps {
  exam: Exam;
  onBack: () => void;
  onEdit: () => void;
  onGrade: () => void;
  onManageAnswerKeys: () => void;
}

const ExamPreview: React.FC<ExamPreviewProps> = ({ 
  exam, 
  onBack, 
  onEdit, 
  onGrade,
  onManageAnswerKeys
}) => {
  const [toast, setToast] = useState<ToastType | null>(null);
  const [loading, setLoading] = useState(false);
  
  const { totalQuestions, maxScore } = calculateExamStats(exam);

  const handleDownloadPDF = async (setNumber: number) => {
    setLoading(true);
    try {
      downloadPDF(exam, setNumber);
      setToast({ 
        message: `To'plam ${setNumber} PDF yuklab olindi!`, 
        type: 'success' 
      });
    } catch (error) {
      setToast({ 
        message: 'PDF yaratishda xatolik!', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownloadAllPDFs = async () => {
    setLoading(true);
    try {
      downloadAllPDFs(exam);
      setToast({ 
        message: 'Barcha PDF\'lar yuklab olinmoqda!', 
        type: 'success' 
      });
    } catch (error) {
      setToast({ 
        message: 'PDF\'larni yaratishda xatolik!', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{exam.name}</h1>
              <p className="text-gray-600">Imtihon Ko'rinishi</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={onManageAnswerKeys}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
              >
                <Key className="w-4 h-4" />
                <span>Javob Kalitlari</span>
              </button>
              <button
                onClick={onGrade}
                className="btn-success flex items-center space-x-2"
              >
                <FileCheck className="w-4 h-4" />
                <span>Tekshirish</span>
              </button>
              <button
                onClick={onEdit}
                className="btn-primary flex items-center space-x-2"
              >
                <Edit className="w-4 h-4" />
                <span>Tahrirlash</span>
              </button>
              <button
                onClick={onBack}
                className="text-gray-600 hover:text-gray-800 transition-colors flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Orqaga</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Exam Statistics */}
        <div className="card p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{totalQuestions}</div>
              <div className="text-sm text-gray-600">Jami Savollar</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{maxScore}</div>
              <div className="text-sm text-gray-600">Maksimal Ball</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{exam.subjects.length}</div>
              <div className="text-sm text-gray-600">Mavzular</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{exam.sets}</div>
              <div className="text-sm text-gray-600">To'plamlar</div>
            </div>
          </div>
          
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={handleDownloadAllPDFs}
              disabled={loading}
              className={`btn-success flex items-center space-x-2 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <Download className="w-4 h-4" />
              <span>Barcha PDF'larni Yuklab Olish</span>
            </button>
            
            {Array.from({ length: exam.sets }, (_, i) => i + 1).map(setNum => (
              <button
                key={setNum}
                onClick={() => handleDownloadPDF(setNum)}
                disabled={loading}
                className={`btn-primary ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                To'plam {String.fromCharCode(64 + setNum)}
              </button>
            ))}
          </div>
          
          <div className="mt-4 text-sm text-gray-600 text-center">
            <p><strong>PDF Xususiyatlari:</strong></p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
              <div>
                <p className="font-medium">📄 Bitta Sahifali PDF</p>
                <ul className="text-xs mt-1">
                  <li>• Faqat titul varaq</li>
                  <li>• Barcha savollar</li>
                  <li>• Compact layout</li>
                </ul>
              </div>
              <div>
                <p className="font-medium">🎯 Professional Format</p>
                <ul className="text-xs mt-1">
                  <li>• A4 format</li>
                  <li>• OMR uchun tayyor</li>
                  <li>• Print-ready</li>
                </ul>
              </div>
              <div>
                <p className="font-medium">📊 To'liq Javob Jadvali</p>
                <ul className="text-xs mt-1">
                  <li>• Harflar doira ichida</li>
                  <li>• 2 ustunli format</li>
                  <li>• Ball ko'rsatkichlari</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Exam Details */}
        <div className="card p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Imtihon Tafsilotlari</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <span className="text-sm text-gray-600">Sana:</span>
              <p className="font-medium">{formatDate(exam.date)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Yaratilgan:</span>
              <p className="font-medium">{formatDate(exam.createdAt)}</p>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-4">Mavzular va Bo'limlar:</h3>
            <div className="space-y-4">
              {exam.subjects.map((subject, index) => {
                const subjectQuestions = subject.sections.reduce((sum, section) => sum + section.questionCount, 0);
                const subjectScore = subject.sections.reduce((sum, section) => sum + (section.questionCount * section.correctScore), 0);
                
                return (
                  <div key={subject.id} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-800 mb-3 flex justify-between">
                      <span>{index + 1}. {subject.name}</span>
                      <span className="text-sm text-gray-600">
                        {subjectQuestions} savol, {subjectScore} ball
                      </span>
                    </h4>
                    <div className="ml-4 space-y-2">
                      {subject.sections.map((section, sectionIndex) => (
                        <div key={section.id} className="text-sm text-gray-600 flex justify-between items-center">
                          <div>
                            <span className="font-medium">
                              {index + 1}.{sectionIndex + 1} {section.name}
                            </span>
                            <span className="ml-2 text-gray-500">
                              ({section.questionType === 'multiple-choice' ? 'Bir tanlov' : 
                                section.questionType === 'multiple-select' ? 'Ko\'p tanlov' : 'Ochiq javob'})
                            </span>
                          </div>
                          <span className="bg-white px-2 py-1 rounded text-xs">
                            {section.questionCount} savol, +{section.correctScore}/{section.wrongScore} ball
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Answer Sheet Preview */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-6">Javob Varag'i Ko'rinishi (Bitta Sahifali Format)</h2>
          
          <div className="border-2 border-gray-800 p-4 bg-white rounded-lg relative max-w-4xl mx-auto" style={{ fontFamily: 'Arial, sans-serif' }}>
            {/* Corner markers */}
            <div className="absolute top-1 left-1 w-3 h-3 bg-black"></div>
            <div className="absolute top-1 right-1 w-3 h-3 bg-black"></div>
            <div className="absolute bottom-1 left-1 w-3 h-3 bg-black"></div>
            <div className="absolute bottom-1 right-1 w-3 h-3 bg-black"></div>
            
            {/* Header with corrected positioning */}
            <div className="text-center mb-4">
              <h1 className="text-xl font-bold">IMTIHON VARAG'I</h1>
              <h2 className="text-lg font-semibold mt-2">{exam.name}</h2>
              <div className="flex justify-between text-sm mt-3 px-2">
                <span>Sana: {formatDate(exam.date)}</span>
                <span>To'plam: A</span>
                <span>Vaqt: 90 daq.</span>
              </div>
            </div>
            
            {/* Student Information Section with corrected layout */}
            <div className="border border-gray-300 mb-4">
              <div className="bg-gray-100 p-2">
                <h3 className="font-bold text-sm">TALABA MA'LUMOTLARI</h3>
              </div>
              <div className="bg-white p-3">
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="w-20 font-medium">FAMILIYA:</span>
                    <div className="flex-1 border-b border-black h-4"></div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-20 font-medium">ISMI:</span>
                    <div className="flex-1 border-b border-black h-4"></div>
                  </div>
                  <div className="flex items-center space-x-6">
                    <div className="flex items-center">
                      <span className="w-12 font-medium">GURUH:</span>
                      <div className="w-16 border-b border-black h-4"></div>
                    </div>
                    <div className="flex items-center">
                      <span className="w-12 font-medium">KURS:</span>
                      <div className="w-8 border-b border-black h-4"></div>
                    </div>
                    <div className="flex items-center">
                      <span className="w-12 font-medium">IMZO:</span>
                      <div className="w-20 border-b border-black h-4"></div>
                    </div>
                  </div>
                  
                  {/* Student ID grid - corrected according to fix_student_id.md */}
                  <div className="mt-4">
                    <span className="text-sm font-bold">TALABA ID:</span>
                    <div className="mt-2 ml-8">
                      {/* Column headers */}
                      <div className="flex justify-start mb-1">
                        <div className="w-8"></div> {/* Space for row numbers */}
                        {Array.from({length: 10}, (_, i) => (
                          <div key={i} className="w-8 text-center">
                            <span className="text-xs">{i}</span>
                          </div>
                        ))}
                      </div>
                      
                      {/* Rows with bubbles - 14mm spacing, 4mm row height */}
                      {Array.from({length: 10}, (_, row) => (
                        <div key={row} className="flex items-center mb-1">
                          <div className="w-8 text-right pr-2">
                            <span className="text-xs">{row}</span>
                          </div>
                          {Array.from({length: 10}, (_, col) => (
                            <div key={col} className="w-8 flex justify-center">
                              <div className="omr-circle w-3 h-3 border border-gray-400"></div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Instructions Section with corrected layout */}
            <div className="border border-gray-300 mb-4 bg-yellow-50">
              <div className="bg-yellow-50 p-3">
                <h3 className="font-bold text-sm mb-2">⚠ JAVOBLARNI BELGILASH QOIDALARI:</h3>
                <div className="flex items-center space-x-6 text-xs mb-2">
                  <div className="flex items-center space-x-2">
                    <span>To'g'ri:</span>
                    <div className="omr-circle omr-filled w-4 h-4"></div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>Noto'g'ri:</span>
                    <div className="omr-circle w-4 h-4 bg-gray-300"></div>
                    <div className="omr-circle w-4 h-4 relative">
                      <span className="absolute inset-0 flex items-center justify-center text-red-500 text-xs">×</span>
                    </div>
                  </div>
                </div>
                <div className="flex space-x-8 text-xs">
                  <div>• Doirachani to'liq to'ldiring</div>
                  <div>• Bir savolga faqat bitta javob</div>
                </div>
              </div>
            </div>
            
            {/* Answer Sections */}
            <div className="space-y-3">
              {exam.subjects.map((subject, subjectIndex) => (
                <div key={subject.id}>
                  {subject.sections.map((section, sectionIndex) => (
                    <div key={section.id} className="border-2 border-black">
                      <div className="bg-gray-100 p-2">
                        <h4 className="font-bold text-sm flex justify-between">
                          <span>MAVZU {subjectIndex + 1}: {subject.name}</span>
                          <span className="text-xs">Jami: {section.questionCount * section.correctScore} ball</span>
                        </h4>
                        <div className="text-xs mt-1">
                          Bo'lim {subjectIndex + 1}.{sectionIndex + 1}: {section.name} (+{section.correctScore}/{section.wrongScore} ball)
                        </div>
                      </div>
                      
                      <div className="bg-white p-3">
                        {/* Questions in 2 columns */}
                        <div className="grid grid-cols-2 gap-8">
                          {Array.from({length: Math.min(section.questionCount, 8)}, (_, q) => (
                            <div key={q} className="flex items-center space-x-2">
                              <span className="text-sm font-bold w-6">{q + 1}.</span>
                              <div className="flex space-x-2">
                                {['A', 'B', 'C', 'D', 'E'].map((option) => (
                                  <div key={option} className="flex flex-col items-center">
                                    <div className="omr-circle w-6 h-6 flex items-center justify-center border-2 border-black rounded-full">
                                      <span className="text-xs font-bold">{option}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                        
                        {section.questionCount > 8 && (
                          <div className="text-xs text-gray-500 text-center mt-3">
                            ... va yana {section.questionCount - 8} savol
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
            
            {/* Footer */}
            <div className="border-2 border-black mt-4">
              <div className="bg-white p-3">
                <h3 className="font-bold text-sm mb-2">BALL HISOBI (O'qituvchi to'ldiradi)</h3>
                <div className="grid grid-cols-4 gap-4 text-sm mb-2">
                  <span>To'g'ri: ___</span>
                  <span>Noto'g'ri: ___</span>
                  <span>Ball: ___/___</span>
                  <span>Baho: ___</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Tekshiruvchi: ________________</span>
                  <span>Imzo: ________</span>
                  <span>Sana: ______</span>
                </div>
                <div className="flex justify-between text-xs mt-2 text-gray-500">
                  <span>ID: {exam.id}</span>
                  <span>Versiya: 1.0</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600 text-center">
            <p><strong>Bitta Sahifali PDF Format:</strong></p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
              <div>
                <p className="font-medium">📄 Titul Varaq</p>
                <ul className="text-xs mt-1">
                  <li>• Talaba ma'lumotlari</li>
                  <li>• Barcha savollar</li>
                  <li>• Compact layout</li>
                </ul>
              </div>
              <div>
                <p className="font-medium">🎯 Professional Format</p>
                <ul className="text-xs mt-1">
                  <li>• A4 format</li>
                  <li>• OMR uchun tayyor</li>
                  <li>• Print-ready</li>
                </ul>
              </div>
              <div>
                <p className="font-medium">📊 To'liq Javob Jadvali</p>
                <ul className="text-xs mt-1">
                  <li>• Harflar doira ichida</li>
                  <li>• 2 ustunli format</li>
                  <li>• Ball ko'rsatkichlari</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ExamPreview;