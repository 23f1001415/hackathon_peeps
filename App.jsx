import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';
import Home from './pages/Home';
import EventForm from './pages/EventForm';
import AdminDashboard from './pages/AdminDashboard';
import EventDetails from './pages/EventDetails';
import AdminLogin from './pages/AdminLogin';  // Import AdminLogin page


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/create" element={<EventForm />} />
        <Route path="/admin-login" element={<AdminLogin />} /> {/* Admin login route */}
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/event/:id" element={<EventDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
