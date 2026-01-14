import React, { useState } from 'react';
import { User, Toast as ToastType } from '../types';
import { storage, generateId } from '../utils/storage';
import Toast from './Toast';

interface LoginProps {
  onLogin: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [toast, setToast] = useState<ToastType | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        // Login logic
        const users = storage.get<Record<string, User>>('users') || {};
        const user = Object.values(users).find(u => u.email === formData.email);
        
        if (user && user.password === formData.password) {
          storage.set('currentUser', user);
          onLogin(user);
          setToast({ message: 'Muvaffaqiyatli kirildi!', type: 'success' });
        } else {
          setToast({ message: 'Email yoki parol noto\'g\'ri!', type: 'error' });
        }
      } else {
        // Register logic
        const users = storage.get<Record<string, User>>('users') || {};
        
        // Check if email already exists
        const existingUser = Object.values(users).find(u => u.email === formData.email);
        if (existingUser) {
          setToast({ message: 'Bu email allaqachon ro\'yxatdan o\'tgan!', type: 'error' });
          return;
        }

        const userId = generateId();
        const newUser: User = {
          id: userId,
          name: formData.name,
          email: formData.email,
          password: formData.password
        };
        
        users[userId] = newUser;
        storage.set('users', users);
        storage.set('currentUser', newUser);
        onLogin(newUser);
        setToast({ message: 'Ro\'yxatdan muvaffaqiyatli o\'tdingiz!', type: 'success' });
      }
    } catch (error) {
      setToast({ message: 'Xatolik yuz berdi!', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">EvallBee</h1>
          <p className="text-gray-600">Imtihon yaratish va tekshirish tizimi</p>
        </div>

        <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            type="button"
            className={`flex-1 py-2 px-4 rounded-md transition-all ${
              isLogin ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'
            }`}
            onClick={() => setIsLogin(true)}
          >
            Kirish
          </button>
          <button
            type="button"
            className={`flex-1 py-2 px-4 rounded-md transition-all ${
              !isLogin ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'
            }`}
            onClick={() => setIsLogin(false)}
          >
            Ro'yxatdan o'tish
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ism
              </label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.name}
                onChange={handleInputChange('name')}
                placeholder="Ismingizni kiriting"
              />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              className="input-field"
              value={formData.email}
              onChange={handleInputChange('email')}
              placeholder="email@example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parol
            </label>
            <input
              type="password"
              required
              className="input-field"
              value={formData.password}
              onChange={handleInputChange('password')}
              placeholder="Parolingizni kiriting"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className={`w-full btn-primary ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Yuklanmoqda...' : (isLogin ? 'Kirish' : 'Ro\'yxatdan o\'tish')}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;