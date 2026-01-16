import { CoordinateTemplate, Exam } from '../types'

/**
 * Generate Coordinate Template for an Exam
 * Bu template har bir imtihon uchun koordinata ma'lumotlarini saqlaydi
 * EvalBee kabi professional tizim
 */
export const generateCoordinateTemplate = (exam: Exam): CoordinateTemplate => {
	// PDF Layout Constants (Fixed values)
	const PAPER_WIDTH_MM = 210
	const PAPER_HEIGHT_MM = 297
	const CORNER_SIZE_MM = 15
	const CORNER_MARGIN_MM = 5

	// Corner marker positions (center of each marker)
	const cornerMarkers = {
		topLeft: {
			x: CORNER_MARGIN_MM + CORNER_SIZE_MM / 2, // 12.5mm
			y: CORNER_MARGIN_MM + CORNER_SIZE_MM / 2, // 12.5mm
		},
		topRight: {
			x: PAPER_WIDTH_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2, // 197.5mm
			y: CORNER_MARGIN_MM + CORNER_SIZE_MM / 2, // 12.5mm
		},
		bottomLeft: {
			x: CORNER_MARGIN_MM + CORNER_SIZE_MM / 2, // 12.5mm
			y: PAPER_HEIGHT_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2, // 284.5mm
		},
		bottomRight: {
			x: PAPER_WIDTH_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2, // 197.5mm
			y: PAPER_HEIGHT_MM - CORNER_MARGIN_MM - CORNER_SIZE_MM / 2, // 284.5mm
		},
	}

	// Distance between corners
	const widthBetweenCorners = cornerMarkers.topRight.x - cornerMarkers.topLeft.x // 185.0mm
	const heightBetweenCorners =
		cornerMarkers.bottomLeft.y - cornerMarkers.topLeft.y // 272.0mm

	// Layout parameters (from pdfGenerator.ts)
	const layout = {
		paperWidth: PAPER_WIDTH_MM,
		paperHeight: PAPER_HEIGHT_MM,
		questionsPerRow: 2,
		bubbleSpacing: 8,
		bubbleRadius: 2.5,
		rowHeight: 5.5,
		gridStartX: 25,
		gridStartY: 149,
		questionSpacing: 90,
		firstBubbleOffset: 8,
	}

	// Calculate coordinates for all questions
	const questions: CoordinateTemplate['questions'] = {}
	let questionNumber = 1
	let currentY = layout.gridStartY

	for (const subject of exam.subjects) {
		// Topic header
		currentY += 8

		for (const section of subject.sections) {
			// Section header
			currentY += 5

			// Calculate questions in this section
			for (let i = 0; i < section.questionCount; i++) {
				const row = Math.floor(i / layout.questionsPerRow)
				const col = i % layout.questionsPerRow

				// Question position
				const questionY = currentY + row * layout.rowHeight
				const questionX = layout.gridStartX + col * layout.questionSpacing

				// Calculate bubble positions
				const bubbles = []
				const variants = ['A', 'B', 'C', 'D', 'E']

				for (let vIdx = 0; vIdx < variants.length; vIdx++) {
					const variant = variants[vIdx]

					// Absolute position in PDF (mm)
					const absoluteX =
						questionX + layout.firstBubbleOffset + vIdx * layout.bubbleSpacing
					const absoluteY = questionY + 2 // +2mm offset

					// Relative to top-left corner (mm)
					const relativeXMm = absoluteX - cornerMarkers.topLeft.x
					const relativeYMm = absoluteY - cornerMarkers.topLeft.y

					// Normalized (0.0 to 1.0)
					const relativeX = relativeXMm / widthBetweenCorners
					const relativeY = relativeYMm / heightBetweenCorners

					bubbles.push({
						variant,
						relativeX: Number(relativeX.toFixed(6)),
						relativeY: Number(relativeY.toFixed(6)),
						absoluteX: Number(absoluteX.toFixed(2)),
						absoluteY: Number(absoluteY.toFixed(2)),
					})
				}

				questions[questionNumber] = {
					questionNumber,
					bubbles,
				}

				questionNumber++
			}

			// Update Y for next section
			const rowsInSection = Math.ceil(
				section.questionCount / layout.questionsPerRow
			)
			currentY += rowsInSection * layout.rowHeight + 2
		}

		// Space between topics
		currentY += 3
	}

	// Create coordinate template
	const template: CoordinateTemplate = {
		version: '2.0',
		timestamp: new Date().toISOString(),
		cornerMarkers,
		layout,
		questions,
	}

	return template
}

/**
 * Save coordinate template to exam
 */
export const saveCoordinateTemplateToExam = (exam: Exam): Exam => {
	const template = generateCoordinateTemplate(exam)

	return {
		...exam,
		coordinateTemplate: template,
	}
}

/**
 * Get coordinate template from exam
 * Agar yo'q bo'lsa, generate qiladi
 */
export const getCoordinateTemplate = (exam: Exam): CoordinateTemplate => {
	if (exam.coordinateTemplate) {
		return exam.coordinateTemplate
	}

	// Generate if not exists
	return generateCoordinateTemplate(exam)
}
