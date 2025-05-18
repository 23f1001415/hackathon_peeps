import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function EventDetails() {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [interest, setInterest] = useState({
    name: '',
    email: '',
    phone: '',
    people: 1,
  });

  useEffect(() => {
    fetch(`http://localhost:5000/events/${id}`)
      .then(res => res.json())
      .then(data => setEvent(data))
      .catch(() => setEvent(null));
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInterest(prev => ({
      ...prev,
      [name]: name === 'people' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:5000/events/${id}/interest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(interest),
      });
      if (res.ok) {
        alert('Interest registered!');
        // Optionally reset form here:
        setInterest({ name: '', email: '', phone: '', people: 1 });
      } else {
        alert('Failed to register interest');
      }
    } catch {
      alert('Error submitting interest');
    }
  };

  if (!event) return <p>Loading...</p>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">{event.title}</h1>
      <p>{event.date} at {event.time} - {event.location}</p>
      <p>{event.description}</p>

      <h2 className="mt-4 text-xl font-semibold">Mark Your Interest</h2>
      <form onSubmit={handleSubmit} className="grid gap-4 mt-2 max-w-md">
        <input
          name="name"
          placeholder="Your Name"
          value={interest.name}
          onChange={handleChange}
          required
          className="p-2 border rounded"
        />
        <input
          name="email"
          placeholder="Email"
          type="email"
          value={interest.email}
          onChange={handleChange}
          required
          className="p-2 border rounded"
        />
        <input
          name="phone"
          placeholder="Phone"
          type="tel"
          value={interest.phone}
          onChange={handleChange}
          required
          className="p-2 border rounded"
        />
        <input
          name="people"
          type="number"
          placeholder="Number of people"
          value={interest.people}
          min={1}
          onChange={handleChange}
          required
          className="p-2 border rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          Submit
        </button>
      </form>
    </div>
  );
}

export default EventDetails;
