/**
 * Backend API Service
 * Connects React frontend to Python FastAPI backend
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export interface BackendGradingRequest {
	file: File
	examStructure: any
	answerKey: { [questionNumber: number]: string }
	coordinateTemplate?: any // YANGI: Optional coordinate template
}

export interface BackendGradingResponse {
	success: boolean
	annotatedImage?: string // Base64 encoded annotated image
	results: {
		totalQuestions: number
		correctAnswers: number
		incorrectAnswers: number
		unanswered: number
		lowConfidence: number
		aiVerified: number
		aiCorrected: number
		warnings: number
		totalScore: number
		maxScore: number
		percentage: number
		grade: { numeric: number; text: string }
		topicResults: any[]
		detailedResults: any[]
	}
	statistics: {
		omr: {
			total: number
			detected: number
			uncertain: number
			no_mark: number
			multiple_marks: number
		}
		ai: {
			enabled: boolean
			verified: number
			corrected: number
			reason?: string
			error?: string
		}
		quality: {
			sharpness: number
			contrast: number
			brightness: number
			overall: number
		}
		duration: number
	}
	metadata: {
		timestamp: string
		filename: string
		system_version: string
	}
}

export class BackendApiService {
	private baseUrl: string

	constructor(baseUrl: string = BACKEND_URL) {
		this.baseUrl = baseUrl
	}

	/**
	 * Check if backend is available
	 */
	async healthCheck(): Promise<boolean> {
		try {
			const response = await fetch(`${this.baseUrl}/health`, {
				method: 'GET',
				headers: {
					Accept: 'application/json',
				},
			})

			if (!response.ok) {
				return false
			}

			const data = await response.json()
			return data.status === 'healthy'
		} catch (error) {
			console.error('Backend health check failed:', error)
			return false
		}
	}

	/**
	 * Test AI connection
	 */
	async testAI(): Promise<{
		success: boolean
		message: string
		model?: string
	}> {
		try {
			const response = await fetch(`${this.baseUrl}/api/test-ai`, {
				method: 'POST',
				headers: {
					Accept: 'application/json',
				},
			})

			return await response.json()
		} catch (error) {
			return {
				success: false,
				message: `Connection error: ${
					error instanceof Error ? error.message : 'Unknown error'
				}`,
			}
		}
	}

	/**
	 * Grade answer sheet with Professional OMR + AI
	 */
	async gradeSheet(
		request: BackendGradingRequest
	): Promise<BackendGradingResponse> {
		const formData = new FormData()
		formData.append('file', request.file)
		formData.append('exam_structure', JSON.stringify(request.examStructure))
		formData.append('answer_key', JSON.stringify(request.answerKey))

		// YANGI: Add coordinate template if provided
		if (request.coordinateTemplate) {
			formData.append(
				'coordinate_template',
				JSON.stringify(request.coordinateTemplate)
			)
			console.log('✅ Sending coordinate template to backend')
		}

		try {
			const response = await fetch(`${this.baseUrl}/api/grade-sheet`, {
				method: 'POST',
				body: formData,
			})

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}))
				throw new Error(
					errorData.detail || `HTTP ${response.status}: ${response.statusText}`
				)
			}

			const data = await response.json()

			if (!data.success) {
				throw new Error(data.error || 'Grading failed')
			}

			return data
		} catch (error) {
			console.error('Backend grading error:', error)
			throw error
		}
	}

	/**
	 * Get backend info
	 */
	async getInfo(): Promise<any> {
		try {
			const response = await fetch(`${this.baseUrl}/`, {
				method: 'GET',
				headers: {
					Accept: 'application/json',
				},
			})

			return await response.json()
		} catch (error) {
			console.error('Failed to get backend info:', error)
			return null
		}
	}
}

// Singleton instance
export const backendApi = new BackendApiService()

// Helper function to check backend availability
export async function isBackendAvailable(): Promise<boolean> {
	return await backendApi.healthCheck()
}

// Helper function to check AI availability
export async function isAIAvailable(): Promise<boolean> {
	const result = await backendApi.testAI()
	return result.success
}
