import React, { useState } from 'react';

function EventForm() {
  const [form, setForm] = useState({
    title: '',
    category: '',
    date: '',
    time: '',
    location: '',
    description: ''
  });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      if(res.ok) {
        alert('Event created!');
        window.location.href = '/';
      } else {
        alert('Failed to create event.');
      }
    } catch (error) {
      alert('Error submitting event');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Post an Event</h1>
      <form onSubmit={handleSubmit} className="grid gap-4">
        <input name="title" placeholder="Title" onChange={handleChange} required className="p-2 border rounded" />
        <select name="category" onChange={handleChange} required className="p-2 border rounded">
          <option value="">Select Category</option>
          <option>Garage Sales</option>
          <option>Sports Matches</option>
          <option>Community Classes</option>
          <option>Volunteer Opportunities</option>
          <option>Exhibitions</option>
          <option>Festivals</option>
        </select>
        <input name="date" type="date" onChange={handleChange} required className="p-2 border rounded" />
        <input name="time" type="time" onChange={handleChange} required className="p-2 border rounded" />
        <input name="location" placeholder="Location" onChange={handleChange} required className="p-2 border rounded" />
        <textarea name="description" placeholder="Description" onChange={handleChange} required className="p-2 border rounded" />
        <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">Post Event</button>
      </form>
    </div>
  );
}

export default EventForm;
