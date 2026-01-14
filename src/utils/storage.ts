/**
 * Local storage utility functions
 */
export const storage = {
  get: <T>(key: string): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  },

  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  },

  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
};

/**
 * Generate unique ID
 */
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

/**
 * Format date for display
 */
export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('uz-UZ', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

/**
 * Calculate exam statistics
 */
export const calculateExamStats = (exam: any) => {
  const totalQuestions = exam.subjects.reduce((total: number, subject: any) => 
    total + subject.sections.reduce((sectionTotal: number, section: any) => 
      sectionTotal + section.questionCount, 0), 0);

  const maxScore = exam.subjects.reduce((total: number, subject: any) => 
    total + subject.sections.reduce((sectionTotal: number, section: any) => 
      sectionTotal + (section.questionCount * section.correctScore), 0), 0);

  return { totalQuestions, maxScore };
};
/**
 * Answer Key Management Functions
 */
import { AnswerKey } from '../types';

export const getAnswerKey = (examId: string, variant: string): AnswerKey | null => {
  const key = `answerKey_${examId}_${variant}`;
  return storage.get<AnswerKey>(key);
};

export const saveAnswerKey = (answerKey: AnswerKey): void => {
  const key = `answerKey_${answerKey.examId}_${answerKey.variant}`;
  storage.set(key, answerKey);
};

export const getAllAnswerKeys = (examId: string): AnswerKey[] => {
  const keys: AnswerKey[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(`answerKey_${examId}_`)) {
      const answerKey = storage.get<AnswerKey>(key);
      if (answerKey) {
        keys.push(answerKey);
      }
    }
  }
  return keys;
};

export const deleteAnswerKey = (examId: string, variant: string): void => {
  const key = `answerKey_${examId}_${variant}`;
  storage.remove(key);
};