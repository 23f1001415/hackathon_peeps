import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function AdminLogin() {
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = e => {
    e.preventDefault();
    // Very simple hardcoded check — replace with real auth later
    if (password === 'admin123') {
      localStorage.setItem('isAdmin', 'true');
      navigate('/admin');
    } else {
      alert('Incorrect password');
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-80">
        <h2 className="text-xl font-bold mb-4">Admin Login</h2>
        <input
          type="password"
          placeholder="Enter Admin Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full p-2 border rounded mb-4"
          required
        />
        <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
          Login
        </button>
      </form>
    </div>
  );
}

export default AdminLogin;
