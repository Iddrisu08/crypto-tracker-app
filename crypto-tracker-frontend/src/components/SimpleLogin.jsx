import { useState } from 'react';
import { useAuthStore } from '../store/authStore';

const SimpleLogin = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const { login, logout, user, isAuthenticated, error } = useAuthStore();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoggingIn(true);
    try {
      await login({ username, password });
    } catch (err) {
      console.error('Login failed:', err);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (isAuthenticated) {
    return (
      <div className="bg-gradient-to-r from-green-800/50 to-gray-700 rounded-xl p-6 shadow-lg border border-green-500/50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white mb-2">✅ Logged In</h3>
            <p className="text-green-300">Welcome, {user?.username}!</p>
            <p className="text-gray-400 text-sm">Enhanced backend authentication active</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-800/50 to-gray-700 rounded-xl p-6 shadow-lg border border-blue-500/50">
      <h3 className="text-xl font-bold text-white mb-4">🔐 Login to Enhanced Backend</h3>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500/50 rounded-lg p-3 mb-4">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}
      
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-gray-300 text-sm mb-2">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            required
          />
        </div>
        <div>
          <label className="block text-gray-300 text-sm mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            required
          />
        </div>
        <button
          type="submit"
          disabled={isLoggingIn}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoggingIn ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <div className="mt-4 text-xs text-gray-400 bg-gray-800/50 rounded p-3">
        <p><strong>Default Admin:</strong></p>
        <p>Username: admin</p>
        <p>Password: admin123</p>
      </div>
    </div>
  );
};

export default SimpleLogin;