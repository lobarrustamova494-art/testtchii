import { Eye, FileText, Plus, Trash2 } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Exam, Toast as ToastType, User } from '../types';
import { formatDate, storage } from '../utils/storage';
import Toast from './Toast';

interface DashboardProps {
  user: User;
  onLogout: () => void;
  onCreateExam: () => void;
  onViewExam: (exam: Exam) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  user, 
  onLogout, 
  onCreateExam, 
  onViewExam 
}) => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [toast, setToast] = useState<ToastType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExams();
  }, [user.id]);

  const loadExams = () => {
    try {
      const userExams = storage.get<Exam[]>(`exams:${user.id}`) || [];
      setExams(userExams);
    } catch (error) {
      setToast({ message: 'Imtihonlarni yuklashda xatolik!', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const deleteExam = (examId: string) => {
    if (confirm('Imtihonni o\'chirmoqchimisiz?')) {
      try {
        const updatedExams = exams.filter(exam => exam.id !== examId);
        setExams(updatedExams);
        storage.set(`exams:${user.id}`, updatedExams);
        storage.remove(`results:${examId}`);
        setToast({ message: 'Imtihon o\'chirildi!', type: 'success' });
      } catch (error) {
        setToast({ message: 'Imtihonni o\'chirishda xatolik!', type: 'error' });
      }
    }
  };

  const getExamStats = (exam: Exam) => {
    const totalQuestions = exam.subjects.reduce((total, subject) => 
      total + subject.sections.reduce((sectionTotal, section) => 
        sectionTotal + section.questionCount, 0), 0);
    
    const totalSections = exam.subjects.reduce((total, subject) => 
      total + subject.sections.length, 0);

    return { totalQuestions, totalSections };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">EvallBee Dashboard</h1>
              <p className="text-gray-600">Xush kelibsiz, {user.name}</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={onCreateExam}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Yangi Imtihon</span>
              </button>
              <button
                onClick={onLogout}
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                Chiqish
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {exams.length === 0 ? (
          <div className="text-center py-12 animate-fade-in">
            <div className="text-gray-400 text-6xl mb-4">
              <FileText className="w-24 h-24 mx-auto" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Hech qanday imtihon yo'q
            </h3>
            <p className="text-gray-600 mb-6">
              Birinchi imtihoningizni yarating va talabalarni baholashni boshlang
            </p>
            <button
              onClick={onCreateExam}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              <Plus className="w-4 h-4" />
              <span>Imtihon Yaratish</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {exams.map(exam => {
              const { totalQuestions } = getExamStats(exam);
              
              return (
                <div key={exam.id} className="card p-6 animate-slide-up">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                      {exam.name}
                    </h3>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => onViewExam(exam)}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="Ko'rish"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteExam(exam.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="O'chirish"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Sana:</span> {formatDate(exam.date)}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">To'plamlar:</span> {exam.sets}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Mavzular:</span> {exam.subjects.length}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Savollar:</span> {totalQuestions}
                    </p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => onViewExam(exam)}
                      className="flex-1 bg-blue-50 text-blue-600 px-3 py-2 rounded-md hover:bg-blue-100 transition-colors text-sm font-medium"
                    >
                      Ko'rish
                    </button>
                    <button
                      onClick={() => deleteExam(exam.id)}
                      className="flex-1 bg-red-50 text-red-600 px-3 py-2 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
                    >
                      O'chirish
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;