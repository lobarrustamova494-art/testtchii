export interface User {
	id: string
	name: string
	email: string
	password: string
}

export interface Section {
	id: string
	name: string
	questionCount: number
	questionType: 'multiple-choice' | 'multiple-select' | 'open-ended'
	correctScore: number
	wrongScore: number
}

export interface Subject {
	id: string
	name: string
	sections: Section[]
}

// Coordinate Template - Har bir imtihon uchun koordinata ma'lumotlari
export interface CoordinateTemplate {
	version: string // "2.0"
	timestamp: string // ISO 8601

	// Corner marker positions (relative to paper)
	cornerMarkers: {
		topLeft: { x: number; y: number } // mm
		topRight: { x: number; y: number } // mm
		bottomLeft: { x: number; y: number } // mm
		bottomRight: { x: number; y: number } // mm
	}

	// Layout parameters
	layout: {
		paperWidth: number // 210mm (A4)
		paperHeight: number // 297mm (A4)
		questionsPerRow: number // 2
		bubbleSpacing: number // 8mm
		bubbleRadius: number // 2.5mm
		rowHeight: number // 5.5mm
		gridStartX: number // 25mm
		gridStartY: number // 149mm
		questionSpacing: number // 90mm
		firstBubbleOffset: number // 8mm
	}

	// Relative coordinates for each question (0-1 normalized)
	questions: {
		[questionNumber: number]: {
			questionNumber: number
			bubbles: {
				variant: string // 'A', 'B', 'C', 'D', 'E'
				relativeX: number // 0.0 to 1.0
				relativeY: number // 0.0 to 1.0
				absoluteX: number // mm
				absoluteY: number // mm
			}[]
		}
	}
}

export interface Exam {
	id: string
	name: string
	date: string
	sets: number
	subjects: Subject[]
	createdBy: string
	createdAt: string

	// YANGI: Koordinata template
	coordinateTemplate?: CoordinateTemplate
}

export interface AnswerKey {
	examId: string
	variant: string
	answers: { [questionNumber: number]: string }
	createdAt: string
	updatedAt: string
}

export interface StudentAnswer {
	[questionNumber: number]: string
}

export interface ExamResult {
	id: string
	studentId: string
	examId: string
	answers: StudentAnswer
	score: number
	correctCount: number
	wrongCount: number
	percentage: number
	submittedAt: string
}

export interface UploadedImage {
	id: string
	name: string
	data: string
	processed: boolean
	studentId: string
	answers: StudentAnswer
	score: number
	correctCount?: number
	wrongCount?: number
}

export interface Toast {
	message: string
	type: 'success' | 'error' | 'info' | 'warning'
}

export type ViewType =
	| 'dashboard'
	| 'create-exam'
	| 'exam-preview'
	| 'exam-grading'
	| 'answer-key-manager'
