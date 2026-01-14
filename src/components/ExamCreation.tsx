import { ArrowLeft, ArrowRight, Plus, Save, Trash2 } from 'lucide-react';
import React, { useState } from 'react';
import { Exam, Section, Subject, Toast as ToastType, User } from '../types';
import { generateId, storage } from '../utils/storage';
import Toast from './Toast';

interface ExamCreationProps {
  user: User;
  onBack: () => void;
  onExamCreated: (exam: Exam) => void;
}

const ExamCreation: React.FC<ExamCreationProps> = ({ 
  user, 
  onBack, 
  onExamCreated 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [toast, setToast] = useState<ToastType | null>(null);
  const [loading, setLoading] = useState(false);
  
  const [examData, setExamData] = useState({
    name: '',
    date: '',
    sets: 1,
    subjects: [] as Subject[]
  });

  const addSubject = () => {
    const newSubject: Subject = {
      id: generateId(),
      name: '',
      sections: []
    };
    
    setExamData(prev => ({
      ...prev,
      subjects: [...prev.subjects, newSubject]
    }));
  };

  const updateSubject = (subjectId: string, field: keyof Subject, value: any) => {
    setExamData(prev => ({
      ...prev,
      subjects: prev.subjects.map(subject =>
        subject.id === subjectId ? { ...subject, [field]: value } : subject
      )
    }));
  };

  const deleteSubject = (subjectId: string) => {
    setExamData(prev => ({
      ...prev,
      subjects: prev.subjects.filter(subject => subject.id !== subjectId)
    }));
  };

  const addSection = (subjectId: string) => {
    const newSection: Section = {
      id: generateId(),
      name: '',
      questionCount: 1,
      questionType: 'multiple-choice',
      correctScore: 1,
      wrongScore: 0
    };

    setExamData(prev => ({
      ...prev,
      subjects: prev.subjects.map(subject =>
        subject.id === subjectId
          ? { ...subject, sections: [...subject.sections, newSection] }
          : subject
      )
    }));
  };

  const updateSection = (
    subjectId: string, 
    sectionId: string, 
    field: keyof Section, 
    value: any
  ) => {
    setExamData(prev => ({
      ...prev,
      subjects: prev.subjects.map(subject =>
        subject.id === subjectId
          ? {
              ...subject,
              sections: subject.sections.map(section =>
                section.id === sectionId ? { ...section, [field]: value } : section
              )
            }
          : subject
      )
    }));
  };

  const deleteSection = (subjectId: string, sectionId: string) => {
    setExamData(prev => ({
      ...prev,
      subjects: prev.subjects.map(subject =>
        subject.id === subjectId
          ? {
              ...subject,
              sections: subject.sections.filter(section => section.id !== sectionId)
            }
          : subject
      )
    }));
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!examData.name.trim() || !examData.date) {
          setToast({ message: 'Barcha maydonlarni to\'ldiring!', type: 'error' });
          return false;
        }
        break;
      case 2:
        if (examData.subjects.length === 0) {
          setToast({ message: 'Kamida bitta mavzu qo\'shing!', type: 'error' });
          return false;
        }
        
        const hasEmptySubjects = examData.subjects.some(subject => 
          !subject.name.trim() || subject.sections.length === 0
        );
        
        if (hasEmptySubjects) {
          setToast({ message: 'Barcha mavzular va bo\'limlarni to\'ldiring!', type: 'error' });
          return false;
        }

        const hasEmptySections = examData.subjects.some(subject =>
          subject.sections.some(section => 
            !section.name.trim() || section.questionCount < 1
          )
        );

        if (hasEmptySections) {
          setToast({ message: 'Barcha bo\'limlarni to\'g\'ri to\'ldiring!', type: 'error' });
          return false;
        }
        break;
    }
    return true;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  const saveExam = async () => {
    if (!validateStep(2)) return;

    setLoading(true);
    try {
      const exam: Exam = {
        ...examData,
        id: generateId(),
        createdBy: user.id,
        createdAt: new Date().toISOString()
      };

      const userExams = storage.get<Exam[]>(`exams:${user.id}`) || [];
      userExams.push(exam);
      storage.set(`exams:${user.id}`, userExams);
      
      setToast({ message: 'Imtihon muvaffaqiyatli yaratildi!', type: 'success' });
      setTimeout(() => onExamCreated(exam), 1000);
    } catch (error) {
      setToast({ message: 'Imtihonni saqlashda xatolik!', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { number: 1, title: 'Asosiy Ma\'lumotlar' },
    { number: 2, title: 'Mavzular va Bo\'limlar' },
    { number: 3, title: 'Ko\'rib Chiqish' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Imtihon Yaratish</h1>
              <p className="text-gray-600">Bosqich {currentStep}/3</p>
            </div>
            <button
              onClick={onBack}
              className="text-gray-600 hover:text-gray-800 transition-colors flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Orqaga</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <React.Fragment key={step.number}>
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                    step.number <= currentStep 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step.number}
                  </div>
                  <span className="mt-2 text-sm text-gray-600 text-center">
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-4 transition-colors ${
                    step.number < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
        {/* Step 1: Basic Information */}
        {currentStep === 1 && (
          <div className="card p-6 animate-fade-in">
            <h2 className="text-xl font-semibold mb-6">Asosiy Ma'lumotlar</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Imtihon Nomi *
                </label>
                <input
                  type="text"
                  className="input-field"
                  value={examData.name}
                  onChange={(e) => setExamData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Masalan: Matematika Oraliq Nazorat"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Imtihon Sanasi *
                </label>
                <input
                  type="date"
                  className="input-field"
                  value={examData.date}
                  onChange={(e) => setExamData(prev => ({ ...prev, date: e.target.value }))}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  To'plamlar Soni (1-4)
                </label>
                <input
                  type="number"
                  min="1"
                  max="4"
                  className="input-field"
                  value={examData.sets}
                  onChange={(e) => setExamData(prev => ({ 
                    ...prev, 
                    sets: Math.max(1, Math.min(4, parseInt(e.target.value) || 1))
                  }))}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Har xil to'plam uchun alohida PDF yaratiladi
                </p>
              </div>
            </div>
            
            <div className="flex justify-end mt-8">
              <button
                onClick={nextStep}
                className="btn-primary flex items-center space-x-2"
              >
                <span>Keyingi</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Subjects and Sections */}
        {currentStep === 2 && (
          <div className="card p-6 animate-fade-in">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Mavzular va Bo'limlar</h2>
              <button
                onClick={addSubject}
                className="btn-success flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Mavzu Qo'shish</span>
              </button>
            </div>
            
            <div className="space-y-6">
              {examData.subjects.map((subject, _subjectIndex) => (
                <div key={subject.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex-1 mr-4">
                      <input
                        type="text"
                        placeholder="Mavzu nomi"
                        className="input-field"
                        value={subject.name}
                        onChange={(e) => updateSubject(subject.id, 'name', e.target.value)}
                      />
                    </div>
                    <button
                      onClick={() => deleteSubject(subject.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Mavzuni o'chirish"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="ml-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium text-gray-700">Bo'limlar</h4>
                      <button
                        onClick={() => addSection(subject.id)}
                        className="bg-blue-100 text-blue-600 px-3 py-1 rounded-md hover:bg-blue-200 transition-colors text-sm flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Bo'lim Qo'shish</span>
                      </button>
                    </div>
                    
                    <div className="space-y-3">
                      {subject.sections.map((section) => (
                        <div key={section.id} className="bg-white p-4 rounded-lg border">
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">
                                Bo'lim nomi
                              </label>
                              <input
                                type="text"
                                placeholder="Bo'lim nomi"
                                className="input-field text-sm"
                                value={section.name}
                                onChange={(e) => updateSection(subject.id, section.id, 'name', e.target.value)}
                              />
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">
                                Savollar soni
                              </label>
                              <input
                                type="number"
                                min="1"
                                placeholder="Savollar soni"
                                className="input-field text-sm"
                                value={section.questionCount}
                                onChange={(e) => updateSection(subject.id, section.id, 'questionCount', parseInt(e.target.value) || 1)}
                              />
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">
                                Savol turi
                              </label>
                              <select
                                className="input-field text-sm"
                                value={section.questionType}
                                onChange={(e) => updateSection(subject.id, section.id, 'questionType', e.target.value)}
                              >
                                <option value="multiple-choice">Bir tanlov</option>
                                <option value="multiple-select">Ko'p tanlov</option>
                                <option value="open-ended">Ochiq javob</option>
                              </select>
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">
                                To'g'ri javob balli
                              </label>
                              <input
                                type="number"
                                min="0"
                                step="0.1"
                                placeholder="To'g'ri ball"
                                className="input-field text-sm"
                                value={section.correctScore}
                                onChange={(e) => updateSection(subject.id, section.id, 'correctScore', parseFloat(e.target.value) || 0)}
                              />
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">
                                Noto'g'ri javob jarima
                              </label>
                              <input
                                type="number"
                                step="0.1"
                                placeholder="Jarima ball"
                                className="input-field text-sm"
                                value={section.wrongScore}
                                onChange={(e) => updateSection(subject.id, section.id, 'wrongScore', parseFloat(e.target.value) || 0)}
                              />
                            </div>
                            
                            <div className="flex items-end">
                              <button
                                onClick={() => deleteSection(subject.id, section.id)}
                                className="btn-danger text-sm flex items-center space-x-1"
                              >
                                <Trash2 className="w-3 h-3" />
                                <span>O'chirish</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {subject.sections.length === 0 && (
                        <div className="text-center py-4 text-gray-500 text-sm">
                          Bu mavzu uchun bo'lim qo'shing
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {examData.subjects.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Imtihon uchun mavzu qo'shing
                </div>
              )}
            </div>
            
            <div className="flex justify-between mt-8">
              <button
                onClick={prevStep}
                className="btn-secondary flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Orqaga</span>
              </button>
              <button
                onClick={nextStep}
                className="btn-primary flex items-center space-x-2"
              >
                <span>Keyingi</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Preview */}
        {currentStep === 3 && (
          <div className="card p-6 animate-fade-in">
            <h2 className="text-xl font-semibold mb-6">Ko'rib Chiqish</h2>
            
            <div className="space-y-6 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <span className="text-sm text-gray-600">Imtihon Nomi:</span>
                  <p className="font-medium text-gray-900">{examData.name}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Sana:</span>
                  <p className="font-medium text-gray-900">
                    {new Date(examData.date).toLocaleDateString('uz-UZ')}
                  </p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">To'plamlar:</span>
                  <p className="font-medium text-gray-900">{examData.sets}</p>
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-4">Mavzular va Bo'limlar:</h3>
                <div className="space-y-4">
                  {examData.subjects.map((subject, index) => {
                    const totalQuestions = subject.sections.reduce((sum, section) => sum + section.questionCount, 0);
                    const maxScore = subject.sections.reduce((sum, section) => sum + (section.questionCount * section.correctScore), 0);
                    
                    return (
                      <div key={subject.id} className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-800 mb-3 flex justify-between">
                          <span>{index + 1}. {subject.name}</span>
                          <span className="text-sm text-gray-600">
                            {totalQuestions} savol, {maxScore} ball
                          </span>
                        </h4>
                        <div className="ml-4 space-y-2">
                          {subject.sections.map((section, sectionIndex) => (
                            <div key={section.id} className="text-sm text-gray-600 flex justify-between">
                              <span>
                                <span className="font-medium">
                                  {index + 1}.{sectionIndex + 1} {section.name}
                                </span>
                                <span className="ml-2 text-gray-500">
                                  ({section.questionType === 'multiple-choice' ? 'Bir tanlov' : 
                                    section.questionType === 'multiple-select' ? 'Ko\'p tanlov' : 'Ochiq javob'})
                                </span>
                              </span>
                              <span>
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
            
            <div className="flex justify-between">
              <button
                onClick={prevStep}
                className="btn-secondary flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Orqaga</span>
              </button>
              <button
                onClick={saveExam}
                disabled={loading}
                className={`btn-success flex items-center space-x-2 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Save className="w-4 h-4" />
                <span>{loading ? 'Saqlanmoqda...' : 'Imtihonni Saqlash'}</span>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ExamCreation;