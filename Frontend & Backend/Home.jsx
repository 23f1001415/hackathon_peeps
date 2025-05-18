import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/events')
      .then(res => res.json())
      .then(data => setEvents(data))
      .catch(err => console.error('Failed to fetch events:', err));
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto font-sans">
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Community Events</h1>
        <Link
          to="/admin-login"
          className="text-sm text-red-600 hover:underline font-semibold"
          aria-label="Admin Login"
        >
          Admin Login
        </Link>
      </header>

      <Link
        to="/create"
        className="btn mb-6 inline-block bg-blue-600 text-white px-5 py-3 rounded hover:bg-blue-700 font-semibold"
      >
        Create Event
      </Link>

      {events.length === 0 ? (
        <p className="text-gray-600 font-normal">No events available at the moment.</p>
      ) : (
        <div className="grid gap-6">
          {events.map(event => (
            <div
              key={event.id}
              className="p-4 border rounded shadow hover:shadow-lg transition"
            >
              <h2 className="text-xl font-semibold mb-1">{event.title}</h2>
              <p className="text-gray-700 mb-1 font-medium">
                {event.date} at {event.time}
              </p>
              <p className="text-gray-600 mb-2 font-normal">{event.location}</p>
              <Link
                to={`/event/${event.id}`}
                className="text-blue-600 underline hover:text-blue-800 font-medium"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Home;
