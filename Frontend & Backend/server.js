// server/server.js
import express from 'express';
import cors from 'cors';
import fs from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';
import nodemailer from 'nodemailer';
import cron from 'node-cron';

const app = express();
const PORT = 5000;
const DATA_FILE = './data/events.json';
const USERS_FILE = './data/users.json';

app.use(cors());
app.use(express.json());

// Helper: Read JSON from file
async function readData(file) {
  try {
    const data = await fs.readFile(file, 'utf-8');
    return JSON.parse(data || '[]');
  } catch {
    return [];
  }
}

// Helper: Write JSON to file
async function writeData(file, data) {
  await fs.writeFile(file, JSON.stringify(data, null, 2));
}

// Mailer setup
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'your.email@gmail.com',
    pass: 'your-app-password',
  },
});

async function sendEventStatusEmail(to, eventTitle, status) {
  const mailOptions = {
    from: '"Community Events" <your.email@gmail.com>',
    to,
    subject: `Event "${eventTitle}" ${status}`,
    text: `Hello,\n\nYour event "${eventTitle}" has been ${status}.\n\nThanks.`,
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log('Email sent to', to);
  } catch (error) {
    console.error('Email error:', error);
  }
}

// Routes

// Get all events
app.get('/events', async (req, res) => {
  const events = await readData(DATA_FILE);
  res.json(events);
});

// ✅ Get event by ID (NEW - Fixes "loading" issue)
app.get('/events/:id', async (req, res) => {
  const events = await readData(DATA_FILE);
  const event = events.find(e => e.id === req.params.id);
  if (!event) return res.status(404).json({ message: 'Event not found' });
  res.json(event);
});

// Create event
app.post('/events', async (req, res) => {
  const events = await readData(DATA_FILE);
  const newEvent = { id: uuidv4(), status: 'pending', ...req.body };
  events.push(newEvent);
  await writeData(DATA_FILE, events);
  res.status(201).json(newEvent);
});

// Update event
app.patch('/events/:id', async (req, res) => {
  const events = await readData(DATA_FILE);
  const users = await readData(USERS_FILE);
  const idx = events.findIndex(e => e.id === req.params.id);
  if (idx === -1) return res.status(404).json({ message: 'Event not found' });

  events[idx] = { ...events[idx], ...req.body };
  await writeData(DATA_FILE, events);

  const organizer = users.find(u => u.id === events[idx].userId);
  if (organizer?.email && req.body.status) {
    sendEventStatusEmail(organizer.email, events[idx].title, req.body.status);
  }

  res.json(events[idx]);
});

// Delete event
app.delete('/events/:id', async (req, res) => {
  let events = await readData(DATA_FILE);
  events = events.filter(e => e.id !== req.params.id);
  await writeData(DATA_FILE, events);
  res.status(204).end();
});

// Register interest in event (NEW)
app.post('/events/:id/interest', async (req, res) => {
  const { id } = req.params;
  const interestData = req.body;
  const filePath = `./data/interests-${id}.json`;

  const existing = await readData(filePath);
  existing.push(interestData);
  await writeData(filePath, existing);

  res.status(201).json({ message: 'Interest saved' });
});

// Get users
app.get('/users', async (req, res) => {
  const users = await readData(USERS_FILE);
  res.json(users);
});

// Ban user
app.patch('/users/:id/ban', async (req, res) => {
  const users = await readData(USERS_FILE);
  const idx = users.findIndex(u => u.id === req.params.id);
  if (idx === -1) return res.status(404).json({ message: 'User not found' });

  users[idx].banned = true;
  await writeData(USERS_FILE, users);
  res.json(users[idx]);
});

// Verify organizer
app.patch('/users/:id/verify', async (req, res) => {
  const users = await readData(USERS_FILE);
  const idx = users.findIndex(u => u.id === req.params.id);
  if (idx === -1) return res.status(404).json({ message: 'User not found' });

  users[idx].verifiedOrganizer = true;
  await writeData(USERS_FILE, users);
  res.json(users[idx]);
});

// Reminder cron job
cron.schedule('0 9 * * *', async () => {
  console.log('🔔 Running daily reminder check at 9:00 AM...');

  const events = await readData(DATA_FILE);
  const users = await readData(USERS_FILE);
  const tomorrow = dayjs().add(1, 'day').format('YYYY-MM-DD');

  const eventsTomorrow = events.filter(
    e => e.status === 'approved' && e.date === tomorrow
  );

  for (const event of eventsTomorrow) {
    const user = users.find(u => u.id === event.userId);
    if (user?.email) {
      const mailOptions = {
        from: '"Community Events" <your.email@gmail.com>',
        to: user.email,
        subject: `Reminder: "${event.title}" is happening tomorrow!`,
        text: `Hello,\n\nThis is a reminder that your event "${event.title}" is scheduled for tomorrow (${event.date}).\n\nLocation: ${event.location}\nTime: ${event.time}\n\nBest of luck!`,
      };

      try {
        await transporter.sendMail(mailOptions);
        console.log(`✅ Reminder sent to ${user.email} for "${event.title}"`);
      } catch (err) {
        console.error(`❌ Error sending reminder to ${user.email}:`, err);
      }
    }
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ Backend running at http://localhost:${PORT}`);
});
