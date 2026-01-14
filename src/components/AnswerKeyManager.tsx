import { ArrowLeft, Edit, RotateCcw, Save, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { AnswerKey, Exam, Toast as ToastType } from '../types';
import { getAnswerKey, saveAnswerKey } from '../utils/storage';
import Toast from './Toast';

interface AnswerKeyManagerProps {
  exam: Exam;
  onBack: () => void;
}

const AnswerKeyManager: React.FC<AnswerKeyManagerProps> = ({ exam, onBack }) => {
  const [answerKeys, setAnswerKeys] = useState<{ [variant: string]: AnswerKey }>({});
  const [activeVariant, setActiveVariant] = useState('A');
  const [isEditing, setIsEditing] = useState(false);
  const [toast, setToast] = useState<ToastType | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize answer keys for all variants
  useEffect(() => {
    const initializeAnswerKeys = () => {
      const keys: { [variant: string]: AnswerKey } = {};
      
      for (let i = 1; i <= exam.sets; i++) {
        const variant = String.fromCharCode(64 + i); // A, B, C, D
        const existingKey = getAnswerKey(exam.id, variant);
        
        if (existingKey) {
          keys[variant] = existingKey;
        } else {
          // Create empty answer key
          const answers: { [questionNumber: number]: string } = {};
          let questionNumber = 1;
          
          exam.subjects.forEach(subject => {
            subject.sections.forEach(section => {
              for (let q = 0; q < section.questionCount; q++) {
                answers[questionNumber] = ''; // Empty by default
                questionNumber++;
              }
            });
          });
          
          keys[variant] = {
            examId: exam.id,
            variant,
            answers,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
        }
      }
      
      setAnswerKeys(keys);
    };

    initializeAnswerKeys();
  }, [exam]);

  const handleAnswerChange = (questionNumber: number, answer: string) => {
    setAnswerKeys(prev => ({
      ...prev,
      [activeVariant]: {
        ...prev[activeVariant],
        answers: {
          ...prev[activeVariant].answers,
          [questionNumber]: answer
        },
        updatedAt: new Date().toISOString()
      }
    }));
    setHasChanges(true);
  };

  const handleSave = () => {
    try {
      Object.values(answerKeys).forEach(key => {
        saveAnswerKey(key);
      });
      
      setHasChanges(false);
      setIsEditing(false);
      setToast({
        message: 'Javob kalitlari muvaffaqiyatli saqlandi!',
        type: 'success'
      });
    } catch (error) {
      setToast({
        message: 'Saqlashda xatolik yuz berdi!',
        type: 'error'
      });
    }
  };

  const handleGenerateRandom = () => {
    const options = ['A', 'B', 'C', 'D', 'E'];
    const updatedKeys = { ...answerKeys };
    
    Object.keys(updatedKeys).forEach(variant => {
      const answers = { ...updatedKeys[variant].answers };
      Object.keys(answers).forEach(questionNum => {
        answers[parseInt(questionNum)] = options[Math.floor(Math.random() * options.length)];
      });
      
      updatedKeys[variant] = {
        ...updatedKeys[variant],
        answers,
        updatedAt: new Date().toISOString()
      };
    });
    
    setAnswerKeys(updatedKeys);
    setHasChanges(true);
    setToast({
      message: 'Tasodifiy javoblar yaratildi!',
      type: 'success'
    });
  };

  const getTotalQuestions = () => {
    return exam.subjects.reduce((total, subject) => 
      total + subject.sections.reduce((sectionTotal, section) => 
        sectionTotal + section.questionCount, 0), 0);
  };

  const getCompletedAnswers = (variant: string) => {
    if (!answerKeys[variant]) return 0;
    return Object.values(answerKeys[variant].answers).filter(answer => answer !== '').length;
  };

  const renderAnswerGrid = () => {
    const currentKey = answerKeys[activeVariant];
    if (!currentKey) return null;

    let questionNumber = 1;
    const options = ['A', 'B', 'C', 'D', 'E'];

    return (
      <div className="space-y-6">
        {exam.subjects.map((subject, topicIndex) => (
          <div key={subject.id} className="bg-white rounded-lg border p-4">
            <h3 className="font-bold text-lg mb-4 text-blue-600">
              {topicIndex + 1}. {subject.name}
            </h3>
            
            {subject.sections.map((section, sectionIndex) => (
              <div key={section.id} className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">
                  {topicIndex + 1}.{sectionIndex + 1} {section.name} 
                  <span className="text-sm text-gray-500 ml-2">
                    (+{section.correctScore}/{section.wrongScore} ball)
                  </span>
                </h4>
                
                <div className="grid grid-cols-5 gap-3">
                  {Array.from({ length: section.questionCount }, (_, q) => {
                    const currentQuestionNum = questionNumber + q;
                    const currentAnswer = currentKey.answers[currentQuestionNum] || '';
                    
                    return (
                      <div key={currentQuestionNum} className="bg-gray-50 rounded-lg p-3">
                        <div className="text-sm font-medium text-gray-600 mb-2 text-center">
                          Savol {currentQuestionNum}
                        </div>
                        
                        <div className="flex justify-center space-x-1">
                          {options.map(option => (
                            <button
                              key={option}
                              onClick={() => isEditing && handleAnswerChange(currentQuestionNum, option)}
                              disabled={!isEditing}
                              className={`
                                w-8 h-8 rounded-full border-2 text-sm font-bold transition-all
                                ${currentAnswer === option
                                  ? 'bg-blue-600 text-white border-blue-600'
                                  : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                                }
                                ${isEditing ? 'cursor-pointer' : 'cursor-default'}
                                ${!isEditing && 'opacity-75'}
                              `}
                            >
                              {option}
                            </button>
                          ))}
                        </div>
                        
                        {currentAnswer && (
                          <div className="text-center mt-2">
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {currentAnswer}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
                
                {(() => { questionNumber += section.questionCount; return null; })()}
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Javob Kalitlari</h1>
              <p className="text-gray-600">{exam.name}</p>
            </div>
            <div className="flex items-center space-x-4">
              {hasChanges && (
                <span className="text-sm text-orange-600 bg-orange-100 px-3 py-1 rounded-full">
                  Saqlanmagan o'zgarishlar
                </span>
              )}
              
              {isEditing ? (
                <>
                  <button
                    onClick={handleSave}
                    className="btn-success flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>Saqlash</span>
                  </button>
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setHasChanges(false);
                      // Reset to saved state
                      const initializeAnswerKeys = () => {
                        const keys: { [variant: string]: AnswerKey } = {};
                        for (let i = 1; i <= exam.sets; i++) {
                          const variant = String.fromCharCode(64 + i);
                          const existingKey = getAnswerKey(exam.id, variant);
                          if (existingKey) {
                            keys[variant] = existingKey;
                          }
                        }
                        setAnswerKeys(keys);
                      };
                      initializeAnswerKeys();
                    }}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <X className="w-4 h-4" />
                    <span>Bekor qilish</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Edit className="w-4 h-4" />
                  <span>Tahrirlash</span>
                </button>
              )}
              
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Variant Tabs */}
        <div className="bg-white rounded-lg border mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {Array.from({ length: exam.sets }, (_, i) => {
                const variant = String.fromCharCode(65 + i);
                const completed = getCompletedAnswers(variant);
                const total = getTotalQuestions();
                
                return (
                  <button
                    key={variant}
                    onClick={() => setActiveVariant(variant)}
                    className={`
                      py-4 px-2 border-b-2 font-medium text-sm transition-colors
                      ${activeVariant === variant
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    To'plam {variant}
                    <span className="ml-2 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      {completed}/{total}
                    </span>
                  </button>
                );
              })}
            </nav>
          </div>
          
          {/* Variant Statistics */}
          <div className="p-6">
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {getCompletedAnswers(activeVariant)}
                </div>
                <div className="text-sm text-gray-600">Belgilangan</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {getTotalQuestions() - getCompletedAnswers(activeVariant)}
                </div>
                <div className="text-sm text-gray-600">Qolgan</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {getTotalQuestions()}
                </div>
                <div className="text-sm text-gray-600">Jami</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round((getCompletedAnswers(activeVariant) / getTotalQuestions()) * 100)}%
                </div>
                <div className="text-sm text-gray-600">Tayyor</div>
              </div>
            </div>
            
            {isEditing && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={handleGenerateRandom}
                  className="btn-outline flex items-center space-x-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Tasodifiy Javoblar</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Answer Grid */}
        {renderAnswerGrid()}
      </main>
    </div>
  );
};

export default AnswerKeyManager;