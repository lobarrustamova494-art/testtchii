import { AlertCircle, AlertTriangle, Camera, Check, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

interface CameraCaptureProps {
	onCapture: (imageFile: File) => void
	onClose: () => void
	examStructure?: any
}

interface PreviewResponse {
	success: boolean
	corners_found: number
	preview_image: string
	ready_to_capture: boolean
	message: string
}

interface QuickAnalysisResult {
	totalQuestions: number
	detectedAnswers: number
	blankQuestions: number
	invalidQuestions: number
	warnings: string[]
	readyToSubmit: boolean
}

export default function CameraCaptureNew({
	onCapture,
	onClose,
	examStructure,
}: CameraCaptureProps) {
	const videoRef = useRef<HTMLVideoElement>(null)
	const canvasRef = useRef<HTMLCanvasElement>(null)
	const [stream, setStream] = useState<MediaStream | null>(null)
	const [previewImage, setPreviewImage] = useState<string | null>(null)
	const [cornersFound, setCornersFound] = useState(0)
	const [readyToCapture, setReadyToCapture] = useState(false)
	const [message, setMessage] = useState('Initializing camera...')
	const [isProcessing, setIsProcessing] = useState(false)
	const [capturedImage, setCapturedImage] = useState<string | null>(null)
	const [quickAnalysis, setQuickAnalysis] =
		useState<QuickAnalysisResult | null>(null)
	const [showConfirmation, setShowConfirmation] = useState(false)
	const previewIntervalRef = useRef<number | null>(null)

	// Start camera
	useEffect(() => {
		startCamera()
		return () => {
			stopCamera()
		}
	}, [])

	// Auto-preview loop - real-time edge detection
	useEffect(() => {
		if (stream && !showConfirmation) {
			previewIntervalRef.current = window.setInterval(() => {
				sendFrameForPreview()
			}, 200)
		}

		return () => {
			if (previewIntervalRef.current) {
				clearInterval(previewIntervalRef.current)
			}
		}
	}, [stream, showConfirmation])

	const startCamera = async () => {
		try {
			const mediaStream = await navigator.mediaDevices.getUserMedia({
				video: {
					facingMode: 'environment',
					width: { ideal: 1280 },
					height: { ideal: 720 },
				},
			})

			setStream(mediaStream)

			if (videoRef.current) {
				videoRef.current.srcObject = mediaStream
			}

			setMessage('Align paper with A4 frame - 4 corners must be visible')
		} catch (error) {
			console.error('Camera error:', error)
			setMessage('Failed to access camera. Please check permissions.')
		}
	}

	const stopCamera = () => {
		if (stream) {
			stream.getTracks().forEach(track => track.stop())
			setStream(null)
		}

		if (previewIntervalRef.current) {
			clearInterval(previewIntervalRef.current)
		}
	}

	const sendFrameForPreview = async () => {
		if (!videoRef.current || !canvasRef.current || isProcessing) return

		const video = videoRef.current
		const canvas = canvasRef.current
		const context = canvas.getContext('2d')

		if (!context) return

		const maxWidth = 800
		const scale = maxWidth / video.videoWidth
		canvas.width = maxWidth
		canvas.height = video.videoHeight * scale

		context.drawImage(video, 0, 0, canvas.width, canvas.height)

		canvas.toBlob(
			async blob => {
				if (!blob) return

				try {
					const formData = new FormData()
					formData.append('file', blob, 'preview.jpg')

					const response = await fetch(
						'http://localhost:8000/api/camera/preview',
						{
							method: 'POST',
							body: formData,
						}
					)

					const data: PreviewResponse = await response.json()

					if (data.success) {
						setPreviewImage(data.preview_image)
						setCornersFound(data.corners_found)
						setReadyToCapture(data.ready_to_capture)
						setMessage(data.message)
					}
				} catch (error) {
					console.error('Preview error:', error)
				}
			},
			'image/jpeg',
			0.5
		)
	}

	const handleCapture = async () => {
		if (!videoRef.current || !canvasRef.current || isProcessing) return

		setIsProcessing(true)
		setMessage('Capturing and analyzing...')

		const video = videoRef.current
		const canvas = canvasRef.current
		const context = canvas.getContext('2d')

		if (!context) return

		canvas.width = video.videoWidth
		canvas.height = video.videoHeight
		context.drawImage(video, 0, 0)

		canvas.toBlob(
			async blob => {
				if (!blob) {
					setIsProcessing(false)
					return
				}

				try {
					const reader = new FileReader()
					reader.onload = async e => {
						const capturedBase64 = e.target?.result as string
						setCapturedImage(capturedBase64)

						const analysis = await performQuickAnalysis(blob)
						setQuickAnalysis(analysis)
						setShowConfirmation(true)
						setIsProcessing(false)
					}
					reader.readAsDataURL(blob)
				} catch (error) {
					console.error('Capture error:', error)
					setIsProcessing(false)
				}
			},
			'image/jpeg',
			0.95
		)
	}

	const performQuickAnalysis = async (
		imageBlob: Blob
	): Promise<QuickAnalysisResult> => {
		try {
			const formData = new FormData()
			formData.append('file', imageBlob, 'captured.jpg')
			if (examStructure) {
				formData.append('exam_structure', JSON.stringify(examStructure))
			}

			const response = await fetch(
				'http://localhost:8000/api/camera/quick-analysis',
				{
					method: 'POST',
					body: formData,
				}
			)

			if (response.ok) {
				const data = await response.json()
				return data
			}
		} catch (error) {
			console.error('Quick analysis error:', error)
		}

		return {
			totalQuestions:
				examStructure?.subjects?.reduce(
					(sum: number, s: any) =>
						sum +
						s.sections.reduce(
							(sSum: number, sec: any) => sSum + sec.questionCount,
							0
						),
					0
				) || 0,
			detectedAnswers: 0,
			blankQuestions: 0,
			invalidQuestions: 0,
			warnings: ['Could not perform quick analysis'],
			readyToSubmit: false,
		}
	}

	const handleConfirm = () => {
		if (!capturedImage) return

		fetch(capturedImage)
			.then(res => res.blob())
			.then(blob => {
				const file = new File([blob], 'captured-image.jpg', {
					type: 'image/jpeg',
				})

				stopCamera()
				onCapture(file)
			})
	}

	const handleRetake = () => {
		setCapturedImage(null)
		setQuickAnalysis(null)
		setShowConfirmation(false)
		setIsProcessing(false)
	}

	if (showConfirmation && capturedImage && quickAnalysis) {
		return (
			<div className='fixed inset-0 bg-black z-50 flex flex-col'>
				<div className='bg-gray-900 p-4 flex items-center justify-between'>
					<h2 className='text-white text-lg font-semibold'>Confirm Capture</h2>
					<button onClick={onClose} className='text-white hover:text-gray-300'>
						<X className='w-6 h-6' />
					</button>
				</div>

				<div className='flex-1 overflow-auto bg-gray-900'>
					<div className='max-w-4xl mx-auto p-6 space-y-6'>
						<div className='bg-white rounded-lg p-4'>
							<h3 className='font-semibold mb-3'>Captured Image</h3>
							<img
								src={capturedImage}
								alt='Captured'
								className='w-full rounded border'
							/>
						</div>

						<div className='bg-white rounded-lg p-6'>
							<h3 className='font-semibold text-lg mb-4'>
								Quick Analysis Results
							</h3>

							<div className='grid grid-cols-4 gap-4 mb-6'>
								<div className='text-center p-4 bg-blue-50 rounded-lg'>
									<div className='text-3xl font-bold text-blue-600'>
										{quickAnalysis.totalQuestions}
									</div>
									<div className='text-sm text-blue-700'>Total Questions</div>
								</div>
								<div className='text-center p-4 bg-green-50 rounded-lg'>
									<div className='text-3xl font-bold text-green-600'>
										{quickAnalysis.detectedAnswers}
									</div>
									<div className='text-sm text-green-700'>Detected</div>
								</div>
								<div className='text-center p-4 bg-gray-50 rounded-lg'>
									<div className='text-3xl font-bold text-gray-600'>
										{quickAnalysis.blankQuestions}
									</div>
									<div className='text-sm text-gray-700'>Blank</div>
								</div>
								<div className='text-center p-4 bg-red-50 rounded-lg'>
									<div className='text-3xl font-bold text-red-600'>
										{quickAnalysis.invalidQuestions}
									</div>
									<div className='text-sm text-red-700'>Invalid</div>
								</div>
							</div>

							{quickAnalysis.warnings.length > 0 && (
								<div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4'>
									<div className='flex items-start gap-3'>
										<AlertTriangle className='w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5' />
										<div>
											<div className='font-medium text-yellow-900 mb-2'>
												Warnings
											</div>
											<ul className='text-sm text-yellow-800 space-y-1'>
												{quickAnalysis.warnings.map((warning, idx) => (
													<li key={idx}>• {warning}</li>
												))}
											</ul>
										</div>
									</div>
								</div>
							)}

							<div
								className={`p-4 rounded-lg ${
									quickAnalysis.readyToSubmit
										? 'bg-green-50 border border-green-200'
										: 'bg-red-50 border border-red-200'
								}`}
							>
								<div className='flex items-center gap-3'>
									{quickAnalysis.readyToSubmit ? (
										<Check className='w-6 h-6 text-green-600' />
									) : (
										<AlertCircle className='w-6 h-6 text-red-600' />
									)}
									<div>
										<div
											className={`font-semibold ${
												quickAnalysis.readyToSubmit
													? 'text-green-900'
													: 'text-red-900'
											}`}
										>
											{quickAnalysis.readyToSubmit
												? 'Ready to Submit'
												: 'Not Ready - Please Retake'}
										</div>
										<div
											className={`text-sm ${
												quickAnalysis.readyToSubmit
													? 'text-green-700'
													: 'text-red-700'
											}`}
										>
											{quickAnalysis.readyToSubmit
												? 'Image quality and detection are good'
												: 'Image has issues that may affect grading'}
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div className='bg-gray-900 p-6 border-t border-gray-700'>
					<div className='max-w-4xl mx-auto flex gap-4'>
						<button
							onClick={handleRetake}
							className='flex-1 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold text-lg'
						>
							Retake Photo
						</button>
						<button
							onClick={handleConfirm}
							disabled={!quickAnalysis.readyToSubmit}
							className={`flex-1 py-4 rounded-lg font-semibold text-lg ${
								quickAnalysis.readyToSubmit
									? 'bg-green-500 hover:bg-green-600 text-white'
									: 'bg-gray-600 text-gray-400 cursor-not-allowed'
							}`}
						>
							{quickAnalysis.readyToSubmit
								? 'Confirm & Submit'
								: 'Cannot Submit - Retake Required'}
						</button>
					</div>
				</div>
			</div>
		)
	}

	return (
		<div className='fixed inset-0 bg-black z-50 flex flex-col'>
			<div className='bg-gray-900 p-4 flex items-center justify-between'>
				<h2 className='text-white text-lg font-semibold flex items-center gap-2'>
					<Camera className='w-5 h-5' />
					EvalBee Camera - Strict Alignment Required
				</h2>
				<button onClick={onClose} className='text-white hover:text-gray-300'>
					<X className='w-6 h-6' />
				</button>
			</div>

			<div className='flex-1 relative overflow-hidden'>
				<video
					ref={videoRef}
					autoPlay
					playsInline
					className='absolute inset-0 w-full h-full object-contain hidden'
				/>

				<canvas ref={canvasRef} className='hidden' />

				{previewImage ? (
					<img
						src={previewImage}
						alt='Preview'
						className='w-full h-full object-contain'
					/>
				) : (
					<div className='w-full h-full flex items-center justify-center'>
						<div className='text-white text-center'>
							<Camera className='w-16 h-16 mx-auto mb-4 animate-pulse' />
							<p>Starting camera...</p>
						</div>
					</div>
				)}

				<div className='absolute inset-0 flex items-center justify-center pointer-events-none'>
					<div
						className='relative'
						style={{ width: '70%', aspectRatio: '210/297' }}
					>
						<div className='absolute inset-0 border-4 border-dashed border-white opacity-50 rounded-lg'></div>

						<div className='absolute -top-3 -left-3 w-8 h-8 border-t-4 border-l-4 border-white'></div>
						<div className='absolute -top-3 -right-3 w-8 h-8 border-t-4 border-r-4 border-white'></div>
						<div className='absolute -bottom-3 -left-3 w-8 h-8 border-b-4 border-l-4 border-white'></div>
						<div className='absolute -bottom-3 -right-3 w-8 h-8 border-b-4 border-r-4 border-white'></div>
					</div>
				</div>

				<div className='absolute top-4 left-4 right-4'>
					<div
						className={`p-4 rounded-lg ${
							readyToCapture
								? 'bg-green-500'
								: cornersFound > 0
								? 'bg-yellow-500'
								: 'bg-red-500'
						} text-white`}
					>
						<div className='flex items-center gap-2'>
							{readyToCapture ? (
								<Check className='w-5 h-5' />
							) : (
								<AlertCircle className='w-5 h-5' />
							)}
							<span className='font-semibold'>{message}</span>
						</div>
						<div className='mt-2 text-sm'>
							Corners: {cornersFound}/4
							{readyToCapture && ' - Hold steady'}
						</div>
					</div>
				</div>

				<div className='absolute bottom-32 left-4 right-4'>
					<div className='bg-black bg-opacity-70 text-white p-4 rounded-lg text-sm space-y-2'>
						<div className='font-semibold mb-2'>EvalBee Requirements:</div>
						<div className='flex items-start gap-2'>
							<div className='w-5 h-5 flex-shrink-0 mt-0.5'>
								{cornersFound === 4 ? '✓' : '○'}
							</div>
							<div>All 4 corner markers visible</div>
						</div>
						<div className='flex items-start gap-2'>
							<div className='w-5 h-5 flex-shrink-0 mt-0.5'>
								{readyToCapture ? '✓' : '○'}
							</div>
							<div>Paper flat and aligned</div>
						</div>
						<div className='flex items-start gap-2'>
							<div className='w-5 h-5 flex-shrink-0 mt-0.5'>○</div>
							<div>No skew or rotation</div>
						</div>
						<div className='flex items-start gap-2'>
							<div className='w-5 h-5 flex-shrink-0 mt-0.5'>○</div>
							<div>Entire paper in frame</div>
						</div>
					</div>
				</div>
			</div>

			<div className='bg-gray-900 p-6'>
				<div className='max-w-md mx-auto'>
					<button
						onClick={handleCapture}
						disabled={!readyToCapture || isProcessing}
						className={`w-full py-4 rounded-lg font-semibold text-lg ${
							readyToCapture && !isProcessing
								? 'bg-green-500 hover:bg-green-600 text-white'
								: 'bg-gray-600 text-gray-400 cursor-not-allowed'
						}`}
					>
						{isProcessing
							? 'Capturing & Analyzing...'
							: readyToCapture
							? 'Capture Image'
							: 'Align Paper to Capture'}
					</button>

					<div className='text-gray-400 text-xs text-center mt-4'>
						EvalBee enforces strict alignment for accurate OMR detection
					</div>
				</div>
			</div>
		</div>
	)
}
