import jsPDF from 'jspdf'
import QRCode from 'qrcode'
import { Exam } from '../types'

/**
 * PDF Configuration according to pdf_format.md
 */
const pdfConfig = {
	format: 'a4' as const,
	orientation: 'portrait' as const,
	unit: 'mm' as const,
	compress: true,
	precision: 2,
	putOnlyUsedFonts: true,
	floatPrecision: 2,
}

/**
 * Generate exam PDF with single page format
 */
export const generateExamPDF = async (
	exam: Exam,
	setNumber: number = 1
): Promise<jsPDF> => {
	const doc = new jsPDF(pdfConfig)

	// Set PDF metadata according to specifications
	const variant = String.fromCharCode(64 + setNumber)

	doc.setProperties({
		title: `Imtihon Titul Varag'i - ${exam.name}`,
		subject: `${exam.name} - To'plam ${variant}`,
		author: 'Imtihon Tizimi',
		keywords: 'imtihon, test, OMR',
		creator: 'Exam System v1.0',
	})

	// Generate and add QR code with layout information
	await addQRCodeToSheet(doc, exam, setNumber)

	// Only draw title sheet (single page)
	drawTitleSheet(doc, exam, setNumber)

	return doc
}

/**
 * Add QR code with layout information to PDF
 */
async function addQRCodeToSheet(
	pdf: jsPDF,
	exam: Exam,
	setNumber: number
): Promise<void> {
	// Prepare layout data for QR code
	const layoutData = {
		examId: exam.id,
		examName: exam.name,
		setNumber: setNumber,
		version: '2.0',
		timestamp: new Date().toISOString(),
		layout: {
			questionsPerRow: 2,
			bubbleSpacing: 8,
			bubbleRadius: 2.5, // Updated: 3 → 2.5mm to prevent overlap
			rowHeight: 5.5, // Updated: 5 → 5.5mm for proper spacing
			gridStartX: 25,
			gridStartY: 149, // Corrected: actual Y where answer grid starts
			questionSpacing: 90,
			firstBubbleOffset: 8,
		},
		structure: {
			totalQuestions: exam.subjects.reduce(
				(sum, subject) =>
					sum +
					subject.sections.reduce(
						(sectionSum, section) => sectionSum + section.questionCount,
						0
					),
				0
			),
			subjects: exam.subjects.map(subject => ({
				id: subject.id,
				name: subject.name,
				sections: subject.sections.map(section => ({
					id: section.id,
					name: section.name,
					questionCount: section.questionCount,
				})),
			})),
		},
	}

	try {
		// Generate QR code as data URL
		const qrDataURL = await QRCode.toDataURL(JSON.stringify(layoutData), {
			errorCorrectionLevel: 'H',
			type: 'image/png',
			width: 150,
			margin: 1,
		})

		// Add QR code to PDF (top-right area, away from corner marker)
		// Corner marker is at 190mm (210 - 5 - 15), so QR should end before that
		// QR code: 25mm width, positioned at 160mm (160 + 25 = 185mm, safe distance from marker)
		pdf.addImage(qrDataURL, 'PNG', 160, 10, 25, 25)

		// Add small label
		pdf.setFontSize(6)
		pdf.setFont('helvetica', 'normal')
		pdf.text('QR Code', 172.5, 37, { align: 'center' })
	} catch (error) {
		console.error('Error generating QR code:', error)
		// Continue without QR code if generation fails
	}
}

/**
 * SAHIFA 1: Draw title sheet (titul varaq)
 */
function drawTitleSheet(pdf: jsPDF, exam: Exam, setNumber: number): void {
	let currentY = 15

	// 1. Header
	currentY = drawHeader(pdf, exam, setNumber, currentY)

	// 2. Student Info
	currentY = drawStudentInfo(pdf, currentY)

	// 3. Instructions
	currentY = drawInstructions(pdf, currentY)

	// 4. Answer Grid
	currentY = drawAnswerGrid(pdf, exam, currentY)

	// 5. Corner Markers
	drawCornerMarkers(pdf)

	// 6. Footer
	drawFooter(pdf, exam)
}

/**
 * Draw header section with corrected positioning
 */
function drawHeader(
	pdf: jsPDF,
	exam: Exam,
	setNumber: number,
	startY: number
): number {
	let currentY = startY

	// Main title
	pdf.setFontSize(20)
	pdf.setFont('helvetica', 'bold')
	pdf.text("IMTIHON VARAG'I", 105, currentY, { align: 'center' })
	currentY += 8

	// Exam name
	pdf.setFontSize(14)
	pdf.text(exam.name, 105, currentY, { align: 'center' })
	currentY += 10

	// Date, variant, and duration info - corrected positioning
	pdf.setFontSize(10)
	pdf.setFont('helvetica', 'normal')
	const dateStr = new Date(exam.date).toLocaleDateString('uz-UZ')

	// Left aligned
	pdf.text(`Sana: ${dateStr}`, 15, currentY)
	// Center aligned
	pdf.text(`To'plam: ${String.fromCharCode(64 + setNumber)}`, 105, currentY, {
		align: 'center',
	})
	// Right aligned
	// pdf.text(`Vaqt: 90 daq.`, 195, currentY, { align: 'right' })

	return currentY + 10
}

/**
 * Draw student info section with corrected ID grid
 */
function drawStudentInfo(pdf: jsPDF, startY: number): number {
	let currentY = startY

	// Section background
	pdf.setFillColor(240, 240, 240)
	pdf.rect(15, currentY, 180, 8, 'F')
	pdf.setDrawColor(200, 200, 200)
	pdf.rect(15, currentY, 180, 8)

	// Section title
	pdf.setFontSize(12)
	pdf.setFont('helvetica', 'bold')
	pdf.text("TALABA MA'LUMOTLARI", 18, currentY + 5.5)
	currentY += 10

	// Student fields
	pdf.setFont('helvetica', 'normal')
	pdf.setFontSize(10)

	// FAMILIYA
	pdf.text('FAMILIYA:', 18, currentY + 4)
	pdf.setDrawColor(150, 150, 150)
	pdf.line(50, currentY + 5, 195, currentY + 5)
	currentY += 8

	// ISMI
	pdf.text('ISMI:', 18, currentY + 4)
	pdf.line(50, currentY + 5, 195, currentY + 5)
	currentY += 8

	// GURUH, KURS, IMZO (in one row)
	pdf.text('GURUH:', 18, currentY + 4)
	pdf.line(40, currentY + 5, 80, currentY + 5)

	pdf.text('KURS:', 90, currentY + 4)
	pdf.line(108, currentY + 5, 128, currentY + 5)

	pdf.text('IMZO:', 140, currentY + 4)
	pdf.line(158, currentY + 5, 195, currentY + 5)
	currentY += 10

	// TALABA ID - corrected grid
	pdf.setFontSize(9)
	pdf.setFont('helvetica', 'bold')
	pdf.text('TALABA ID:', 18, currentY + 3)

	// Draw corrected ID grid
	drawCorrectedIDGrid(pdf, 50, currentY + 5)

	currentY += 48 // Grid height + spacing

	return currentY
}

/**
 * Draw corrected ID grid according to fix_student_id.md
 */
function drawCorrectedIDGrid(pdf: jsPDF, startX: number, startY: number): void {
	// Grid parameters from fix_student_id.md
	const columnSpacing = 14 // 14mm between columns
	const rowHeight = 4 // 4mm between rows
	const bubbleRadius = 1.8 // 1.8mm radius

	// Column numbers (0-9) at the top
	pdf.setFontSize(8)
	pdf.setFont('helvetica', 'normal')
	for (let col = 0; col < 10; col++) {
		const x = startX + col * columnSpacing
		pdf.text(String(col), x + 0.5, startY - 1)
	}

	// Row numbers (0-9) on the left
	for (let row = 0; row < 10; row++) {
		const y = startY + row * rowHeight
		pdf.text(String(row), startX - 8, y + 1.5)
	}

	// Bubble grid
	for (let col = 0; col < 10; col++) {
		for (let row = 0; row < 10; row++) {
			const x = startX + col * columnSpacing + 2
			const y = startY + row * rowHeight + 1

			// Draw bubble
			pdf.setDrawColor(120, 120, 120)
			pdf.setLineWidth(0.2)
			pdf.circle(x, y, bubbleRadius)
		}
	}
}

/**
 * Draw instructions section with corrected height
 */
function drawInstructions(pdf: jsPDF, startY: number): number {
	let currentY = startY

	// Background with increased height (18mm)
	pdf.setFillColor(255, 250, 205)
	pdf.rect(15, currentY, 180, 18, 'F')
	pdf.setDrawColor(220, 200, 100)
	pdf.rect(15, currentY, 180, 18)

	// Title with warning symbol
	pdf.setFontSize(10)
	pdf.setFont('helvetica', 'bold')
	pdf.text('⚠ JAVOBLARNI BELGILASH QOIDALARI:', 18, currentY + 5)

	// Examples and rules with corrected positioning
	pdf.setFont('helvetica', 'normal')
	pdf.setFontSize(9)

	// Left side - correct example
	pdf.text("To'g'ri:", 18, currentY + 10)
	drawFilledBubble(pdf, 33, currentY + 8.5, 1.8)

	// Center - incorrect examples
	pdf.text("Noto'g'ri:", 50, currentY + 10)
	drawPartialBubble(pdf, 67, currentY + 8.5, 1.8)
	drawEmptyBubbleWithX(pdf, 77, currentY + 8.5, 1.8)

	// Rules in one row
	pdf.text("• Doirachani to'liq to'ldiring", 18, currentY + 14)
	pdf.text('• Bir savolga faqat bitta javob', 115, currentY + 14)

	return currentY + 22
}

/**
 * Draw answer grid for all questions
 */
function drawAnswerGrid(pdf: jsPDF, exam: Exam, startY: number): number {
	let currentY = startY
	let questionNumber = 1

	exam.subjects.forEach((subject, topicIndex) => {
		// Topic header - COMPACT
		pdf.setFillColor(240, 240, 240)
		pdf.rect(15, currentY, 180, 6, 'F') // Reduced from 8mm to 6mm
		pdf.setDrawColor(0, 0, 0)
		pdf.rect(15, currentY, 180, 6)

		const topicTotalScore = subject.sections.reduce(
			(sum, section) => sum + section.questionCount * section.correctScore,
			0
		)

		pdf.setFontSize(10) // Reduced from 11
		pdf.setFont('helvetica', 'bold')
		pdf.text(`MAVZU ${topicIndex + 1}: ${subject.name}`, 20, currentY + 4) // Adjusted
		pdf.text(`Jami: ${topicTotalScore} ball`, 170, currentY + 4)

		currentY += 8 // Reduced from 10mm to 8mm

		// Sections
		subject.sections.forEach((section, sectionIndex) => {
			pdf.setFontSize(9) // Reduced from 10
			pdf.setFont('helvetica', 'normal')
			pdf.text(
				`Bo'lim ${topicIndex + 1}.${sectionIndex + 1}: ${section.name}`,
				20,
				currentY + 3 // Adjusted
			)
			pdf.text(
				`(+${section.correctScore} ball / ${section.wrongScore} ball)`,
				130,
				currentY + 3 // Adjusted
			)

			currentY += 5 // Reduced from 6mm to 5mm

			// Questions grid - COMPACT with proper spacing
			const questionsPerRow = 2
			const bubbleSize = 2.5 // Reduced from 3mm to 2.5mm to prevent overlap
			const bubbleSpacing = 8
			const rowHeight = 5.5 // Increased from 5mm to 5.5mm for proper vertical spacing

			for (let i = 0; i < section.questionCount; i += questionsPerRow) {
				// Check if we need a new page - ONLY for footer space
				// Footer starts at 275mm, so we stop at 270mm to be safe
				if (currentY > 270) {
					pdf.addPage()
					currentY = 15

					// Redraw corner markers on new page
					drawCornerMarkers(pdf)
				}

				const xStart = 25

				for (
					let j = 0;
					j < questionsPerRow && i + j < section.questionCount;
					j++
				) {
					const xPos = xStart + j * 90

					// Question number
					pdf.setFont('helvetica', 'bold')
					pdf.setFontSize(9) // Slightly smaller
					pdf.text(`${questionNumber}.`, xPos, currentY + 3.5) // Adjusted

					// Answer bubbles with letters inside
					const variants = ['A', 'B', 'C', 'D', 'E']
					variants.forEach((variant, vIndex) => {
						const bubbleX = xPos + 8 + vIndex * bubbleSpacing
						drawEmptyBubble(pdf, bubbleX, currentY + 2, bubbleSize)

						// Letter inside bubble
						pdf.setFontSize(7) // Reduced from 8
						pdf.setFont('helvetica', 'bold')
						pdf.text(variant, bubbleX, currentY + 2.8, { align: 'center' }) // Adjusted
					})

					questionNumber++
				}

				currentY += rowHeight
			}

			currentY += 2 // Reduced from 3mm to 2mm - space between sections
		})

		currentY += 3 // Reduced from 5mm to 3mm - space between topics
	})

	return currentY
}

/**
 * Draw corner markers for OMR alignment
 * Increased size for better detection
 */
function drawCornerMarkers(pdf: jsPDF): void {
	const size = 15 // Increased from 10mm to 15mm for better detection
	const margin = 5

	pdf.setFillColor(0, 0, 0)

	// Top left
	pdf.rect(margin, margin, size, size, 'F')

	// Top right
	pdf.rect(210 - margin - size, margin, size, size, 'F')

	// Bottom left
	pdf.rect(margin, 297 - margin - size, size, size, 'F')

	// Bottom right
	pdf.rect(210 - margin - size, 297 - margin - size, size, size, 'F')
}

/**
 * Draw footer section
 */
function drawFooter(pdf: jsPDF, exam: Exam): void {
	const footerY = 275

	pdf.setDrawColor(0, 0, 0)
	pdf.line(15, footerY, 195, footerY)

	pdf.setFontSize(10)
	pdf.setFont('helvetica', 'bold')
	pdf.text("BALL HISOBI (O'qituvchi to'ldiradi)", 20, footerY + 5)

	// Score table
	pdf.rect(15, footerY + 7, 180, 10)
	pdf.line(60, footerY + 7, 60, footerY + 17)
	pdf.line(105, footerY + 7, 105, footerY + 17)
	pdf.line(150, footerY + 7, 150, footerY + 17)

	pdf.setFont('helvetica', 'normal')
	pdf.setFontSize(9)
	pdf.text("To'g'ri: ___", 20, footerY + 14)
	pdf.text("Noto'g'ri: ___", 65, footerY + 14)
	pdf.text('Ball: ___/___', 110, footerY + 14)
	pdf.text('Baho: _____', 155, footerY + 14)

	// Teacher signature
	pdf.text('Tekshiruvchi: ________________', 15, footerY + 23)
	pdf.text('Imzo: ________', 100, footerY + 23)
	pdf.text('Sana: ______', 150, footerY + 23)

	// ID and version
	pdf.setFontSize(7)
	pdf.text(`ID: ${exam.id}`, 15, footerY + 28)
	pdf.text('Versiya: 1.0', 180, footerY + 28)
}
/**
 * Draw empty bubble
 */
function drawEmptyBubble(
	pdf: jsPDF,
	x: number,
	y: number,
	radius: number
): void {
	pdf.setDrawColor(0, 0, 0)
	pdf.setLineWidth(0.3)
	pdf.circle(x, y, radius)
}

/**
 * Draw filled bubble
 */
function drawFilledBubble(
	pdf: jsPDF,
	x: number,
	y: number,
	radius: number
): void {
	pdf.setFillColor(0, 0, 0)
	pdf.circle(x, y, radius, 'F')
}

/**
 * Draw partially filled bubble
 */
function drawPartialBubble(
	pdf: jsPDF,
	x: number,
	y: number,
	radius: number
): void {
	pdf.setDrawColor(100, 100, 100)
	pdf.setLineWidth(0.3)
	pdf.circle(x, y, radius)

	pdf.setFillColor(150, 150, 150)
	pdf.circle(x, y, radius * 0.5, 'F')
}

/**
 * Draw empty bubble with X mark
 */
function drawEmptyBubbleWithX(
	pdf: jsPDF,
	x: number,
	y: number,
	radius: number
): void {
	pdf.setDrawColor(100, 100, 100)
	pdf.setLineWidth(0.3)
	pdf.circle(x, y, radius)

	// Draw X mark
	pdf.setDrawColor(200, 0, 0)
	pdf.setLineWidth(0.4)
	const offset = radius * 0.7
	pdf.line(x - offset, y - offset, x + offset, y + offset)
	pdf.line(x - offset, y + offset, x + offset, y - offset)
}

/**
 * Generate filename according to pdf_format.md
 */
export const generateFileName = (exam: Exam, setNumber: number): string => {
	const variant = String.fromCharCode(64 + setNumber)
	const dateStr = new Date().toISOString().split('T')[0]
	const cleanName = exam.name
		.replace(/[^a-zA-Z0-9\u0400-\u04FF\s]/g, '')
		.replace(/\s+/g, '_')
	return `${cleanName}_Toplam${variant}_${dateStr}.pdf`
}

/**
 * Download single PDF
 */
export const downloadPDF = async (
	exam: Exam,
	setNumber: number
): Promise<void> => {
	try {
		const doc = await generateExamPDF(exam, setNumber)
		const fileName = generateFileName(exam, setNumber)
		doc.save(fileName)
	} catch (error) {
		console.error('Error generating PDF:', error)
		throw new Error('PDF yaratishda xatolik yuz berdi')
	}
}

/**
 * Download all PDF sets with delay
 */
export const downloadAllPDFs = async (exam: Exam): Promise<void> => {
	for (let i = 1; i <= exam.sets; i++) {
		try {
			await downloadPDF(exam, i)
			// 500ms delay between downloads
			if (i < exam.sets) {
				await new Promise(resolve => setTimeout(resolve, 500))
			}
		} catch (error) {
			console.error(`Error downloading set ${i}:`, error)
			throw new Error(`To'plam ${i} yuklab olishda xatolik`)
		}
	}
}
