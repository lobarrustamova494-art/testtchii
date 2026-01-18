import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	build: {
		outDir: 'dist',
		sourcemap: false,
		minify: 'esbuild',
		rollupOptions: {
			output: {
				manualChunks: {
					'react-vendor': ['react', 'react-dom'],
					lucide: ['lucide-react'],
					pdf: ['jspdf', 'qrcode'],
				},
			},
		},
	},
	server: {
		host: '0.0.0.0', // Tashqi qurilmalar uchun ochiq
		port: 3000,
		// Proxy faqat localhost uchun, telefon uchun to'g'ridan-to'g'ri API chaqiramiz
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
			},
		},
	},
})
