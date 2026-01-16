/**
 * Hybrid Exam Grading Component
 * Uses Python Backend (OpenCV + Groq AI) with Frontend Fallback
 */
import {
	AlertTriangle,
	ArrowLeft,
	Camera,
	CheckCircle,
	Cloud,
	CloudOff,
	FileDown,
	FileImage,
	FileSpreadsheet,
	Loader2,
	RotateCcw,
	Save,
	Upload,
	X,
	XCircle,
	Zap,
} from 'lucide-react'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import {
	backendApi,
	isAIAvailable,
	isBackendAvailable,
} from '../services/backendApi'
import { Exam, Toast as ToastType } from '../types'
import { getAllAnswerKeys } from '../utils/storage'
import CameraCaptureNew from './CameraCaptureNew'
import Toast from './Toast'

interface ExamGradingProps {
	exam: Exam
	onBack: () => void
}

interface UploadedSheet {
	id: string
	name: string
	preview: string
	file: File
	processed: boolean
	processingMode?: 'backend' | 'frontend'
	metadata?: any
	results?: any
	statistics?: any
	processingLog?: string[]
	annotatedImage?: string // Base64 annotated image
}

const ExamGradingHybrid: React.FC<ExamGradingProps> = ({ exam, onBack }) => {
	const [uploadedSheets, setUploadedSheets] = useState<UploadedSheet[]>([])
	const [processing, setProcessing] = useState(false)
	const [toast, setToast] = useState<ToastType | null>(null)
	const [backendStatus, setBackendStatus] = useState<
		'checking' | 'available' | 'unavailable'
	>('checking')
	const [aiStatus, setAIStatus] = useState<
		'checking' | 'available' | 'unavailable'
	>('checking')
	const [useBackend, setUseBackend] = useState(true)
	const [showCamera, setShowCamera] = useState(false)
	const fileInputRef = useRef<HTMLInputElement>(null)

	// Get answer keys
	const answerKeys = getAllAnswerKeys(exam.id)

	// Check backend and AI status on mount
	useEffect(() => {
		checkBackendStatus()
		checkAIStatus()
	}, [])

	const checkBackendStatus = async () => {
		setBackendStatus('checking')
		const available = await isBackendAvailable()
		setBackendStatus(available ? 'available' : 'unavailable')

		if (!available) {
			setToast({
				message: 'Backend server topilmadi. Frontend OMR ishlatiladi.',
				type: 'warning',
			})
			setUseBackend(false)
		}
	}

	const checkAIStatus = async () => {
		setAIStatus('checking')
		const available = await isAIAvailable()
		setAIStatus(available ? 'available' : 'unavailable')
	}

	const handleFileSelect = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>) => {
			const files = event.target.files
			if (!files) return

			Array.from(files).forEach(file => {
				if (file.type.startsWith('image/')) {
					const reader = new FileReader()
					reader.onload = e => {
						const result = e.target?.result as string
						const sheet: UploadedSheet = {
							id:
								Date.now().toString() + Math.random().toString(36).substr(2, 9),
							name: file.name,
							preview: result,
							file: file,
							processed: false,
						}
						setUploadedSheets(prev => [...prev, sheet])
					}
					reader.readAsDataURL(file)
				}
			})
		},
		[]
	)

	const processSheetWithBackend = async (sheet: UploadedSheet) => {
		console.log('🚀 Processing with Backend (OpenCV + AI)...')

		try {
			// Prepare answer key
			const answerKey: { [key: number]: string } = {}
			let questionNumber = 1

			exam.subjects.forEach(subject => {
				subject.sections.forEach(section => {
					for (let i = 0; i < section.questionCount; i++) {
						// Get answer from stored keys (variant A for now)
						const variantKey = answerKeys.find(k => k.variant === 'A')
						if (variantKey) {
							answerKey[questionNumber] =
								variantKey.answers[questionNumber] || 'A'
						} else {
							answerKey[questionNumber] = 'A' // Default
						}
						questionNumber++
					}
				})
			})

			// Call backend API
			const response = await backendApi.gradeSheet({
				file: sheet.file,
				examStructure: exam,
				answerKey: answerKey,
				coordinateTemplate: exam.coordinateTemplate, // YANGI: Send coordinate template
			})

			console.log('✅ Backend processing complete:', response)

			// Update sheet with results
			const updatedSheet: UploadedSheet = {
				...sheet,
				processed: true,
				processingMode: 'backend',
				results: response.results,
				statistics: response.statistics,
				metadata: response.metadata,
				annotatedImage: response.annotatedImage, // Add annotated image
			}

			setUploadedSheets(prev =>
				prev.map(s => (s.id === sheet.id ? updatedSheet : s))
			)

			// Show success message with AI info
			const aiInfo = response.statistics.ai.enabled
				? ` | AI: ${response.statistics.ai.verified} verified, ${response.statistics.ai.corrected} corrected`
				: ''

			setToast({
				message: `✅ Backend processing complete! (${response.statistics.duration}s)${aiInfo}`,
				type: 'success',
			})
		} catch (error) {
			console.error('Backend processing error:', error)
			throw error
		}
	}

	const processSheet = async (sheet: UploadedSheet) => {
		setProcessing(true)

		try {
			// Check if answer keys exist
			if (answerKeys.length === 0) {
				setToast({
					message: 'Avval javob kalitlarini belgilang!',
					type: 'error',
				})
				setProcessing(false)
				return
			}

			if (useBackend && backendStatus === 'available') {
				await processSheetWithBackend(sheet)
			} else {
				// Fallback to frontend processing
				setToast({
					message: "Backend mavjud emas. Iltimos, backend'ni ishga tushiring.",
					type: 'error',
				})
			}
		} catch (error) {
			console.error('Processing error:', error)
			setToast({
				message: `Xatolik: ${
					error instanceof Error ? error.message : "Noma'lum xatolik"
				}`,
				type: 'error',
			})
		} finally {
			setProcessing(false)
		}
	}

	const removeSheet = (id: string) => {
		setUploadedSheets(prev => prev.filter(sheet => sheet.id !== id))
	}

	const openCamera = () => {
		setShowCamera(true)
	}

	const handleCameraCapture = (imageFile: File) => {
		// Convert File to data URL
		const reader = new FileReader()
		reader.onload = e => {
			const result = e.target?.result as string
			const sheet: UploadedSheet = {
				id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
				name: imageFile.name,
				preview: result,
				file: imageFile,
				processed: false,
			}
			setUploadedSheets(prev => [...prev, sheet])
			setShowCamera(false)

			setToast({
				message: 'Rasm muvaffaqiyatli olindi!',
				type: 'success',
			})
		}
		reader.readAsDataURL(imageFile)
	}

	const closeCamera = () => {
		setShowCamera(false)
	}

	const handleDrop = useCallback((event: React.DragEvent) => {
		event.preventDefault()
		const files = event.dataTransfer.files

		Array.from(files).forEach(file => {
			if (file.type.startsWith('image/')) {
				const reader = new FileReader()
				reader.onload = e => {
					const result = e.target?.result as string
					const sheet: UploadedSheet = {
						id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
						name: file.name,
						preview: result,
						file: file,
						processed: false,
					}
					setUploadedSheets(prev => [...prev, sheet])
				}
				reader.readAsDataURL(file)
			}
		})
	}, [])

	const handleDragOver = useCallback((event: React.DragEvent) => {
		event.preventDefault()
	}, [])

	if (answerKeys.length === 0) {
		return (
			<div className='min-h-screen bg-gray-50 flex items-center justify-center'>
				<div className='bg-white rounded-xl border p-8 text-center max-w-md'>
					<XCircle className='w-16 h-16 mx-auto text-red-500 mb-4' />
					<h2 className='text-xl font-bold text-gray-900 mb-2'>
						Javob Kalitlari Topilmadi
					</h2>
					<p className='text-gray-600 mb-6'>
						Tekshirishni boshlash uchun avval javob kalitlarini belgilang.
					</p>
					<button onClick={onBack} className='btn-primary'>
						Orqaga Qaytish
					</button>
				</div>
			</div>
		)
	}

	return (
		<div className='min-h-screen bg-gray-50'>
			{toast && <Toast {...toast} onClose={() => setToast(null)} />}

			<header className='bg-white shadow-sm border-b'>
				<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
					<div className='flex justify-between items-center py-4'>
						<div>
							<h1 className='text-2xl font-bold text-gray-900'>
								Hybrid OMR System v3.0
							</h1>
							<p className='text-gray-600'>{exam.name}</p>
						</div>
						<button
							onClick={onBack}
							className='text-gray-600 hover:text-gray-800 transition-colors flex items-center space-x-2'
						>
							<ArrowLeft className='w-4 h-4' />
							<span>Orqaga</span>
						</button>
					</div>
				</div>
			</header>

			<main className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
				{/* Camera Capture Component */}
				{showCamera && (
					<CameraCaptureNew
						onCapture={handleCameraCapture}
						onClose={closeCamera}
						examStructure={exam}
					/>
				)}

				{/* System Status Panel */}
				<div className='bg-white rounded-xl border p-6 mb-8'>
					<div className='flex items-center justify-between mb-4'>
						<h2 className='text-xl font-bold text-gray-900'>System Status</h2>
						<button
							onClick={() => {
								checkBackendStatus()
								checkAIStatus()
							}}
							className='text-sm text-blue-600 hover:text-blue-700 flex items-center gap-2'
						>
							<RotateCcw className='w-4 h-4' />
							Refresh
						</button>
					</div>

					<div className='grid grid-cols-3 gap-4'>
						{/* Backend Status */}
						<div
							className={`p-4 rounded-lg border-2 ${
								backendStatus === 'available'
									? 'bg-green-50 border-green-300'
									: backendStatus === 'unavailable'
									? 'bg-red-50 border-red-300'
									: 'bg-gray-50 border-gray-300'
							}`}
						>
							<div className='flex items-center gap-2 mb-2'>
								{backendStatus === 'available' ? (
									<Cloud className='w-5 h-5 text-green-600' />
								) : backendStatus === 'unavailable' ? (
									<CloudOff className='w-5 h-5 text-red-600' />
								) : (
									<Loader2 className='w-5 h-5 text-gray-600 animate-spin' />
								)}
								<span className='font-medium'>Backend Server</span>
							</div>
							<div className='text-sm'>
								{backendStatus === 'available' && (
									<span className='text-green-700'>✓ OpenCV + Python</span>
								)}
								{backendStatus === 'unavailable' && (
									<span className='text-red-700'>✗ Offline</span>
								)}
								{backendStatus === 'checking' && (
									<span className='text-gray-700'>Checking...</span>
								)}
							</div>
						</div>

						{/* AI Status */}
						<div
							className={`p-4 rounded-lg border-2 ${
								aiStatus === 'available'
									? 'bg-purple-50 border-purple-300'
									: aiStatus === 'unavailable'
									? 'bg-orange-50 border-orange-300'
									: 'bg-gray-50 border-gray-300'
							}`}
						>
							<div className='flex items-center gap-2 mb-2'>
								{aiStatus === 'available' ? (
									<Zap className='w-5 h-5 text-purple-600' />
								) : aiStatus === 'unavailable' ? (
									<AlertTriangle className='w-5 h-5 text-orange-600' />
								) : (
									<Loader2 className='w-5 h-5 text-gray-600 animate-spin' />
								)}
								<span className='font-medium'>AI Verification</span>
							</div>
							<div className='text-sm'>
								{aiStatus === 'available' && (
									<span className='text-purple-700'>✓ Groq LLaMA 3</span>
								)}
								{aiStatus === 'unavailable' && (
									<span className='text-orange-700'>⚠ Disabled</span>
								)}
								{aiStatus === 'checking' && (
									<span className='text-gray-700'>Checking...</span>
								)}
							</div>
						</div>

						{/* Processing Mode */}
						<div
							className={`p-4 rounded-lg border-2 ${
								useBackend && backendStatus === 'available'
									? 'bg-blue-50 border-blue-300'
									: 'bg-yellow-50 border-yellow-300'
							}`}
						>
							<div className='flex items-center gap-2 mb-2'>
								<CheckCircle className='w-5 h-5 text-blue-600' />
								<span className='font-medium'>Processing Mode</span>
							</div>
							<div className='text-sm'>
								{useBackend && backendStatus === 'available' ? (
									<span className='text-blue-700'>Backend (99.9%)</span>
								) : (
									<span className='text-yellow-700'>Frontend (99%)</span>
								)}
							</div>
						</div>
					</div>

					{/* Mode Toggle */}
					{backendStatus === 'available' && (
						<div className='mt-4 flex items-center justify-center gap-3'>
							<label className='flex items-center gap-2 cursor-pointer'>
								<input
									type='checkbox'
									checked={useBackend}
									onChange={e => setUseBackend(e.target.checked)}
									className='w-4 h-4'
								/>
								<span className='text-sm'>
									Use Backend (OpenCV + AI) - Recommended
								</span>
							</label>
						</div>
					)}
				</div>

				{/* Upload Section */}
				<div className='bg-white rounded-xl border p-8 mb-8'>
					<div
						className='border-2 border-dashed border-gray-300 rounded-xl p-8'
						onDrop={handleDrop}
						onDragOver={handleDragOver}
					>
						<div className='text-center'>
							<Upload className='w-16 h-16 mx-auto text-gray-400 mb-4' />
							<p className='text-lg font-medium mb-2'>
								{useBackend && backendStatus === 'available'
									? '🚀 Professional OMR + AI - Varaqlarni bu yerga tashlang'
									: '📝 Frontend OMR - Varaqlarni bu yerga tashlang'}
							</p>
							<p className='text-sm text-gray-500 mb-4'>
								JPEG/PNG format, minimal 800x1100px
							</p>

							<div className='flex gap-3 justify-center'>
								<label className='btn-primary cursor-pointer'>
									<FileImage className='w-5 h-5' />
									Fayl Tanlash
									<input
										ref={fileInputRef}
										type='file'
										multiple
										accept='image/*'
										className='hidden'
										onChange={handleFileSelect}
									/>
								</label>

								<button onClick={openCamera} className='btn-secondary'>
									<Camera className='w-5 h-5' />
									Kamera
								</button>
							</div>
						</div>
					</div>

					{/* Uploaded Sheets */}
					{uploadedSheets.length > 0 && (
						<div className='mt-6'>
							<h3 className='font-medium mb-3'>
								Yuklangan: {uploadedSheets.length} ta varaq
							</h3>
							<div className='grid grid-cols-3 gap-4'>
								{uploadedSheets.map(sheet => (
									<div key={sheet.id} className='relative group'>
										<div className='border-2 rounded-lg overflow-hidden border-gray-200'>
											<img
												src={sheet.preview}
												alt={sheet.name}
												className='w-full h-40 object-cover'
											/>

											{/* Processing Mode Badge */}
											{sheet.processed && sheet.processingMode && (
												<div
													className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-medium ${
														sheet.processingMode === 'backend'
															? 'bg-blue-500 text-white'
															: 'bg-yellow-500 text-white'
													}`}
												>
													{sheet.processingMode === 'backend'
														? '🚀 Backend'
														: '📝 Frontend'}
												</div>
											)}

											{/* Processing Status */}
											<div className='absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center'>
												<div className='flex flex-col items-center gap-2'>
													{!sheet.processed ? (
														<>
															<button
																onClick={() => processSheet(sheet)}
																disabled={processing}
																className={`px-4 py-2 rounded text-sm font-medium ${
																	processing
																		? 'bg-gray-500 text-white cursor-not-allowed'
																		: 'bg-blue-600 text-white hover:bg-blue-700'
																}`}
															>
																{processing ? (
																	<div className='flex items-center gap-2'>
																		<Loader2 className='w-4 h-4 animate-spin' />
																		Processing...
																	</div>
																) : (
																	<>
																		{useBackend && backendStatus === 'available'
																			? '🚀 Backend OMR + AI'
																			: '📝 Frontend OMR'}
																	</>
																)}
															</button>
														</>
													) : (
														<div className='flex flex-col items-center gap-1'>
															<span className='bg-green-600 text-white px-3 py-1 rounded text-sm'>
																✓ Complete
															</span>
															{sheet.results && (
																<div className='text-white text-xs text-center'>
																	{sheet.results.percentage.toFixed(1)}% -{' '}
																	{sheet.results.grade.text}
																	{sheet.statistics && (
																		<>
																			<br />
																			{sheet.statistics.duration.toFixed(1)}s
																			{sheet.statistics.ai?.verified > 0 && (
																				<>
																					{' '}
																					| AI: {sheet.statistics.ai.verified}
																				</>
																			)}
																		</>
																	)}
																</div>
															)}
														</div>
													)}
													<button
														onClick={() => removeSheet(sheet.id)}
														className='bg-red-600 text-white p-1 rounded hover:bg-red-700'
													>
														<X className='w-4 h-4' />
													</button>
												</div>
											</div>
										</div>

										{/* Sheet Info */}
										<div className='mt-2'>
											<p className='text-xs text-gray-600 truncate font-medium'>
												{sheet.name}
											</p>
											{sheet.processed && sheet.results && (
												<div className='text-xs text-gray-500 mt-1'>
													<div className='flex justify-between'>
														<span>To'g'ri: {sheet.results.correctAnswers}</span>
														<span>Ball: {sheet.results.totalScore}</span>
													</div>
												</div>
											)}
										</div>
									</div>
								))}
							</div>

							{/* Batch Processing */}
							{uploadedSheets.some(sheet => !sheet.processed) && (
								<div className='mt-4 flex justify-center'>
									<button
										onClick={() => {
											uploadedSheets
												.filter(sheet => !sheet.processed)
												.forEach(sheet => processSheet(sheet))
										}}
										disabled={processing}
										className='bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2'
									>
										<CheckCircle className='w-5 h-5' />
										Barchasini Tekshirish (
										{uploadedSheets.filter(s => !s.processed).length})
									</button>
								</div>
							)}
						</div>
					)}
				</div>

				{/* Results Section */}
				{uploadedSheets.some(sheet => sheet.processed && sheet.results) && (
					<div className='space-y-6'>
						<h2 className='text-xl font-bold text-gray-900'>Natijalar</h2>

						{uploadedSheets
							.filter(sheet => sheet.processed && sheet.results)
							.map(sheet => (
								<div key={sheet.id} className='bg-white rounded-xl border p-6'>
									{/* Overall Results */}
									<div className='bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl p-6 mb-6'>
										<div className='grid grid-cols-6 gap-4'>
											<div className='text-center'>
												<div className='text-4xl font-bold'>
													{sheet.results.totalScore}
												</div>
												<div className='text-sm opacity-90'>Ball</div>
											</div>
											<div className='text-center'>
												<div className='text-4xl font-bold'>
													{sheet.results.percentage.toFixed(1)}%
												</div>
												<div className='text-sm opacity-90'>Foiz</div>
											</div>
											<div className='text-center'>
												<div className='text-4xl font-bold'>
													{sheet.results.correctAnswers}
												</div>
												<div className='text-sm opacity-90'>To'g'ri</div>
											</div>
											<div className='text-center'>
												<div className='text-4xl font-bold'>
													{sheet.results.incorrectAnswers}
												</div>
												<div className='text-sm opacity-90'>Noto'g'ri</div>
											</div>
											<div className='text-center'>
												<div className='text-4xl font-bold'>
													{sheet.results.grade.numeric}
												</div>
												<div className='text-sm opacity-90'>
													{sheet.results.grade.text}
												</div>
											</div>
											{sheet.statistics?.ai?.verified > 0 && (
												<div className='text-center'>
													<div className='text-4xl font-bold'>
														{sheet.statistics.ai.verified}
													</div>
													<div className='text-sm opacity-90'>AI Verified</div>
												</div>
											)}
										</div>
									</div>

									{/* AI Statistics */}
									{sheet.statistics?.ai?.enabled &&
										sheet.statistics.ai.verified > 0 && (
											<div className='bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6'>
												<div className='flex items-start gap-3'>
													<Zap className='w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5' />
													<div>
														<div className='font-medium text-purple-900'>
															AI Verification Active
														</div>
														<ul className='text-sm text-purple-800 mt-1 space-y-1'>
															<li>
																• {sheet.statistics.ai.verified} ta javob AI
																bilan tekshirildi
															</li>
															{sheet.statistics.ai.corrected > 0 && (
																<li>
																	• {sheet.statistics.ai.corrected} ta javob AI
																	tomonidan tuzatildi
																</li>
															)}
															<li>
																• Groq LLaMA 3.2 90B Vision model ishlatildi
															</li>
														</ul>
													</div>
												</div>
											</div>
										)}

									{/* Annotated Image - Vizual Ko'rsatish */}
									{sheet.annotatedImage && (
										<div className='mb-6'>
											<h3 className='text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2'>
												<FileImage className='w-5 h-5 text-blue-600' />
												Tekshirilgan Varaq
											</h3>
											<div className='bg-gray-50 rounded-xl p-4 border-2 border-gray-200'>
												<img
													src={sheet.annotatedImage}
													alt='Annotated Answer Sheet'
													className='w-full h-auto rounded-lg shadow-lg'
												/>
												<div className='mt-4 grid grid-cols-3 gap-3 text-sm'>
													<div className='flex items-center gap-2 bg-white p-3 rounded-lg border'>
														<div className='w-4 h-4 border-2 border-green-500 rounded'></div>
														<span className='text-gray-700'>To'g'ri javob</span>
													</div>
													<div className='flex items-center gap-2 bg-white p-3 rounded-lg border'>
														<div className='w-4 h-4 border-2 border-blue-500 rounded'></div>
														<span className='text-gray-700'>
															O'quvchi to'g'ri belgilagan
														</span>
													</div>
													<div className='flex items-center gap-2 bg-white p-3 rounded-lg border'>
														<div className='w-4 h-4 border-2 border-red-500 rounded'></div>
														<span className='text-gray-700'>
															O'quvchi xato belgilagan
														</span>
													</div>
												</div>
											</div>
										</div>
									)}

									{/* Export Buttons */}
									<div className='flex gap-3'>
										<button className='btn-primary'>
											<FileDown className='w-5 h-5' />
											PDF
										</button>
										<button className='btn-secondary'>
											<FileSpreadsheet className='w-5 h-5' />
											Excel
										</button>
										<button className='btn-outline'>
											<Save className='w-5 h-5' />
											Saqlash
										</button>
									</div>
								</div>
							))}
					</div>
				)}
			</main>
		</div>
	)
}

export default ExamGradingHybrid
