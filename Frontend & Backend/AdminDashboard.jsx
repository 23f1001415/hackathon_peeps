import React, { useEffect, useState } from 'react';

function AdminDashboard() {
  const [events, setEvents] = useState([]);
  const [users, setUsers] = useState([]);
  const [viewUsers, setViewUsers] = useState(false);

  const fetchEvents = async () => {
    const res = await fetch('http://localhost:5000/events');
    const data = await res.json();
    setEvents(data);
  };

  const fetchUsers = async () => {
    const res = await fetch('http://localhost:5000/users');
    const data = await res.json();
    setUsers(data);
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const toggleView = () => {
    if (viewUsers) fetchEvents();
    else fetchUsers();
    setViewUsers(!viewUsers);
  };

  const updateEventStatus = async (id, status) => {
    await fetch(`http://localhost:5000/events/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    fetchEvents();
  };

  const deleteEvent = async (id) => {
    await fetch(`http://localhost:5000/events/${id}`, {
      method: 'DELETE',
    });
    fetchEvents();
  };

  const banUser = async (id) => {
    await fetch(`http://localhost:5000/users/${id}/ban`, {
      method: 'PATCH',
    });
    fetchUsers();
  };

  const verifyUser = async (id) => {
    await fetch(`http://localhost:5000/users/${id}/verify`, {
      method: 'PATCH',
    });
    fetchUsers();
  };

  const logout = () => {
    localStorage.removeItem('isAdmin');
    window.location.href = '/';
  };

  const getUserById = (id) => {
    return users.find((u) => u.id === id);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <button
        onClick={toggleView}
        className="mb-6 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
      >
        {viewUsers ? 'View Events' : 'View Users'}
      </button>

      {!viewUsers ? (
        <div>
          <h2 className="text-2xl mb-4">Events</h2>
          {events.length === 0 ? (
            <p>No events found.</p>
          ) : (
            events.map((event) => {
              const user = getUserById(event.userId) || {};
              return (
                <div
                  key={event.id}
                  className="border rounded p-4 mb-4 shadow-sm flex justify-between items-center"
                >
                  <div>
                    <h3 className="text-xl font-semibold">{event.title}</h3>
                    <p className="text-sm text-gray-700">
                      <strong>By:</strong> {user.name || 'Unknown'} ({user.email || 'N/A'})
                    </p>
                    <p>
                      Status:{' '}
                      <span
                        className={
                          event.status === 'approved'
                            ? 'text-green-600'
                            : event.status === 'rejected'
                            ? 'text-red-600'
                            : 'text-yellow-600'
                        }
                      >
                        {event.status || 'pending'}
                      </span>
                    </p>
                    <p>
                      {event.date} at {event.time} - {event.location}
                    </p>
                  </div>
                  <div className="space-x-2">
                    {event.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updateEventStatus(event.id, 'approved')}
                          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => updateEventStatus(event.id, 'rejected')}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => deleteEvent(event.id)}
                      className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => alert('Flagged content for moderation!')}
                      className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                    >
                      Flag
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      ) : (
        <div>
          <h2 className="text-2xl mb-4">Users</h2>
          {users.length === 0 ? (
            <p>No users found.</p>
          ) : (
            users.map((user) => (
              <div
                key={user.id}
                className="border rounded p-4 mb-4 shadow-sm flex justify-between items-center"
              >
                <div>
                  <p>
                    <strong>Name:</strong> {user.name || 'N/A'}
                  </p>
                  <p>
                    <strong>Email:</strong> {user.email || 'N/A'}
                  </p>
                  <p>
                    <strong>Status:</strong>{' '}
                    {user.banned ? (
                      <span className="text-red-600">Banned</span>
                    ) : (
                      <span className="text-green-600">Active</span>
                    )}
                  </p>
                  <p>
                    <strong>Verified Organizer:</strong>{' '}
                    {user.verifiedOrganizer ? (
                      <span className="text-green-600">Yes</span>
                    ) : (
                      <span className="text-gray-600">No</span>
                    )}
                  </p>
                </div>
                <div className="space-x-2">
                  {!user.banned && (
                    <button
                      onClick={() => banUser(user.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      Ban
                    </button>
                  )}
                  {!user.verifiedOrganizer && !user.banned && (
                    <button
                      onClick={() => verifyUser(user.id)}
                      className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Verify Organizer
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;
