/**
 * Authentication API Service
 * JWT-based authentication with backend
 */

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export interface LoginRequest {
	username: string
	password: string
}

export interface LoginResponse {
	access_token: string
	token_type: string
	expires_in: number
	user: {
		username: string
		role: string
		full_name: string
		email: string
	}
}

export interface User {
	username: string
	role: string
	full_name: string
	email: string
}

export interface ChangePasswordRequest {
	old_password: string
	new_password: string
}

class AuthApiService {
	private baseUrl: string

	constructor() {
		this.baseUrl = `${API_BASE_URL}/auth`
	}

	/**
	 * Get stored JWT token
	 */
	getToken(): string | null {
		return localStorage.getItem('access_token')
	}

	/**
	 * Store JWT token
	 */
	setToken(token: string): void {
		localStorage.setItem('access_token', token)
	}

	/**
	 * Remove JWT token
	 */
	removeToken(): void {
		localStorage.removeItem('access_token')
		localStorage.removeItem('current_user')
	}

	/**
	 * Get stored user data
	 */
	getCurrentUser(): User | null {
		const userStr = localStorage.getItem('current_user')
		return userStr ? JSON.parse(userStr) : null
	}

	/**
	 * Store user data
	 */
	setCurrentUser(user: User): void {
		localStorage.setItem('current_user', JSON.stringify(user))
	}

	/**
	 * Get authorization headers
	 */
	private getAuthHeaders(): HeadersInit {
		const token = this.getToken()
		return {
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` }),
		}
	}

	/**
	 * Login user
	 */
	async login(credentials: LoginRequest): Promise<LoginResponse> {
		const response = await fetch(`${this.baseUrl}/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(credentials),
		})

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Login failed')
		}

		const data: LoginResponse = await response.json()

		// Store token and user data
		this.setToken(data.access_token)
		this.setCurrentUser(data.user)

		return data
	}

	/**
	 * Logout user
	 */
	async logout(): Promise<void> {
		try {
			const token = this.getToken()
			if (token) {
				await fetch(`${this.baseUrl}/logout`, {
					method: 'POST',
					headers: this.getAuthHeaders(),
				})
			}
		} catch (error) {
			console.warn('Logout request failed:', error)
		} finally {
			// Always clear local storage
			this.removeToken()
		}
	}

	/**
	 * Get current user info from server
	 */
	async getMe(): Promise<User> {
		const response = await fetch(`${this.baseUrl}/me`, {
			headers: this.getAuthHeaders(),
		})

		if (!response.ok) {
			throw new Error('Failed to get user info')
		}

		return response.json()
	}

	/**
	 * Change password
	 */
	async changePassword(request: ChangePasswordRequest): Promise<void> {
		const response = await fetch(`${this.baseUrl}/change-password`, {
			method: 'POST',
			headers: this.getAuthHeaders(),
			body: JSON.stringify(request),
		})

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Password change failed')
		}
	}

	/**
	 * Verify token validity
	 */
	async verifyToken(): Promise<{ valid: boolean; user: User }> {
		const response = await fetch(`${this.baseUrl}/verify-token`, {
			headers: this.getAuthHeaders(),
		})

		if (!response.ok) {
			throw new Error('Token verification failed')
		}

		return response.json()
	}

	/**
	 * Check if user is authenticated
	 */
	isAuthenticated(): boolean {
		const token = this.getToken()
		const user = this.getCurrentUser()
		return !!(token && user)
	}

	/**
	 * Check if user has specific role
	 */
	hasRole(role: string): boolean {
		const user = this.getCurrentUser()
		return user?.role === role || user?.role === 'admin'
	}

	/**
	 * Check if user is admin
	 */
	isAdmin(): boolean {
		const user = this.getCurrentUser()
		return user?.role === 'admin'
	}
}

export const authApi = new AuthApiService()
