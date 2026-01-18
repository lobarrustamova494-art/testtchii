import React, { useEffect, useState } from 'react'
import AnswerKeyManager from './components/AnswerKeyManager'
import Dashboard from './components/Dashboard'
import ExamCreation from './components/ExamCreation'
import ExamGradingHybrid from './components/ExamGradingHybrid'
import ExamPreview from './components/ExamPreview'
import Login from './components/Login'
import { authApi } from './services/authApi'
import { Exam, User, ViewType } from './types'

const App: React.FC = () => {
	const [currentUser, setCurrentUser] = useState<User | null>(null)
	const [currentView, setCurrentView] = useState<ViewType>('dashboard')
	const [selectedExam, setSelectedExam] = useState<Exam | null>(null)
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		// Check for existing JWT token and user session
		const initAuth = async () => {
			if (authApi.isAuthenticated()) {
				try {
					// Verify token is still valid
					const tokenData = await authApi.verifyToken()
					if (tokenData.valid) {
						// Convert authApi user to app user format
						const user: User = {
							id: tokenData.user.username,
							name: tokenData.user.full_name,
							email: tokenData.user.email,
							password: '',
							role: tokenData.user.role as 'admin' | 'teacher',
						}
						setCurrentUser(user)
					} else {
						// Token invalid, clear auth
						authApi.removeToken()
					}
				} catch (error) {
					// Token verification failed (expired or invalid) - this is normal
					// Just clear the token silently
					authApi.removeToken()
				}
			}
			setLoading(false)
		}

		initAuth()
	}, [])

	const handleLogin = (user: User) => {
		setCurrentUser(user)
		setCurrentView('dashboard')
	}

	const handleLogout = async () => {
		try {
			await authApi.logout()
		} catch (error) {
			console.warn('Logout request failed:', error)
		}
		setCurrentUser(null)
		setCurrentView('dashboard')
		setSelectedExam(null)
	}

	const handleCreateExam = () => {
		setCurrentView('create-exam')
		setSelectedExam(null)
	}

	const handleViewExam = (exam: Exam) => {
		setSelectedExam(exam)
		setCurrentView('exam-preview')
	}

	const handleExamCreated = (exam: Exam) => {
		setSelectedExam(exam)
		setCurrentView('exam-preview')
	}

	const handleEditExam = () => {
		setCurrentView('create-exam')
	}

	const handleGradeExam = () => {
		setCurrentView('exam-grading')
	}

	const handleManageAnswerKeys = () => {
		setCurrentView('answer-key-manager')
	}

	const handleBackToDashboard = () => {
		setCurrentView('dashboard')
		setSelectedExam(null)
	}

	if (loading) {
		return (
			<div className='min-h-screen bg-gray-50 flex items-center justify-center'>
				<div className='text-center'>
					<div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'></div>
					<p className='text-gray-600'>Yuklanmoqda...</p>
				</div>
			</div>
		)
	}

	if (!currentUser) {
		return <Login onLogin={handleLogin} />
	}

	switch (currentView) {
		case 'create-exam':
			return (
				<ExamCreation
					user={currentUser}
					onBack={handleBackToDashboard}
					onExamCreated={handleExamCreated}
				/>
			)

		case 'exam-preview':
			return (
				<ExamPreview
					exam={selectedExam!}
					onBack={handleBackToDashboard}
					onEdit={handleEditExam}
					onGrade={handleGradeExam}
					onManageAnswerKeys={handleManageAnswerKeys}
				/>
			)

		case 'answer-key-manager':
			return (
				<AnswerKeyManager
					exam={selectedExam!}
					onBack={() => setCurrentView('exam-preview')}
				/>
			)

		case 'exam-grading':
			return (
				<ExamGradingHybrid
					exam={selectedExam!}
					onBack={() => setCurrentView('exam-preview')}
				/>
			)

		default:
			return (
				<Dashboard
					user={currentUser}
					onLogout={handleLogout}
					onCreateExam={handleCreateExam}
					onViewExam={handleViewExam}
				/>
			)
	}
}

export default App
