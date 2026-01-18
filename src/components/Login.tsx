import React, { useState } from 'react'
import { authApi } from '../services/authApi'
import { Toast as ToastType, User } from '../types'
import Toast from './Toast'

interface LoginProps {
	onLogin: (user: User) => void
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
	const [formData, setFormData] = useState({
		username: '',
		password: '',
	})
	const [toast, setToast] = useState<ToastType | null>(null)
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setLoading(true)

		try {
			const response = await authApi.login({
				username: formData.username,
				password: formData.password,
			})

			// Convert authApi User to app User format
			const user: User = {
				id: response.user.username,
				name: response.user.full_name,
				email: response.user.email,
				password: '', // Not stored on frontend
				role: response.user.role as 'admin' | 'teacher',
			}

			onLogin(user)
			setToast({ message: 'Muvaffaqiyatli kirildi!', type: 'success' })
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : 'Xatolik yuz berdi!'
			setToast({ message: errorMessage, type: 'error' })
		} finally {
			setLoading(false)
		}
	}

	const handleInputChange =
		(field: keyof typeof formData) =>
		(e: React.ChangeEvent<HTMLInputElement>) => {
			setFormData(prev => ({ ...prev, [field]: e.target.value }))
		}

	return (
		<div className='min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4'>
			{toast && <Toast {...toast} onClose={() => setToast(null)} />}

			<div className='bg-white rounded-2xl shadow-xl p-8 w-full max-w-md animate-fade-in'>
				<div className='text-center mb-8'>
					<h1 className='text-3xl font-bold text-gray-800 mb-2'>EvallBee</h1>
					<p className='text-gray-600'>Imtihon yaratish va tekshirish tizimi</p>
				</div>

				<form onSubmit={handleSubmit} className='space-y-4'>
					<div>
						<label className='block text-sm font-medium text-gray-700 mb-1'>
							Foydalanuvchi nomi
						</label>
						<input
							type='text'
							required
							className='input-field'
							value={formData.username}
							onChange={handleInputChange('username')}
							placeholder='admin yoki teacher'
						/>
					</div>

					<div>
						<label className='block text-sm font-medium text-gray-700 mb-1'>
							Parol
						</label>
						<input
							type='password'
							required
							className='input-field'
							value={formData.password}
							onChange={handleInputChange('password')}
							placeholder='Parolingizni kiriting'
						/>
					</div>

					<button
						type='submit'
						disabled={loading}
						className={`w-full btn-primary ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
					>
						{loading ? 'Yuklanmoqda...' : 'Kirish'}
					</button>
				</form>

				<div className='mt-6 p-4 bg-gray-50 rounded-lg'>
					<h3 className='text-sm font-medium text-gray-700 mb-2'>
						Demo hisoblar:
					</h3>
					<div className='text-xs text-gray-600 space-y-1'>
						<div>
							<strong>Admin:</strong> admin / admin123
						</div>
						<div>
							<strong>O'qituvchi:</strong> teacher / teacher123
						</div>
					</div>
				</div>
			</div>
		</div>
	)
}

export default Login
