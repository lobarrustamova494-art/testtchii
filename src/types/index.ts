export interface User {
  id: string;
  name: string;
  email: string;
  password: string;
}

export interface Section {
  id: string;
  name: string;
  questionCount: number;
  questionType: 'multiple-choice' | 'multiple-select' | 'open-ended';
  correctScore: number;
  wrongScore: number;
}

export interface Subject {
  id: string;
  name: string;
  sections: Section[];
}

export interface Exam {
  id: string;
  name: string;
  date: string;
  sets: number;
  subjects: Subject[];
  createdBy: string;
  createdAt: string;
}

export interface AnswerKey {
  examId: string;
  variant: string;
  answers: { [questionNumber: number]: string };
  createdAt: string;
  updatedAt: string;
}

export interface StudentAnswer {
  [questionNumber: number]: string;
}

export interface ExamResult {
  id: string;
  studentId: string;
  examId: string;
  answers: StudentAnswer;
  score: number;
  correctCount: number;
  wrongCount: number;
  percentage: number;
  submittedAt: string;
}

export interface UploadedImage {
  id: string;
  name: string;
  data: string;
  processed: boolean;
  studentId: string;
  answers: StudentAnswer;
  score: number;
  correctCount?: number;
  wrongCount?: number;
}

export interface Toast {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

export type ViewType = 'dashboard' | 'create-exam' | 'exam-preview' | 'exam-grading' | 'answer-key-manager';