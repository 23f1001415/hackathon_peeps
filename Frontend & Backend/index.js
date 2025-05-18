import express from 'express';
import fs from 'fs';
import cors from 'cors';
import bodyParser from 'body-parser';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const PORT = 5000;
const DATA_FILE = './backend/events.json';

app.use(cors());
app.use(bodyParser.json());

// Utility to read and write JSON
debugger;
const readData = () => JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
const writeData = (data) => fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));

// Get all events
app.get('/events', (req, res) => {
  const data = readData();
  res.json(data);
});

// Get single event
app.get('/events/:id', (req, res) => {
  const data = readData();
  const event = data.find(e => e.id === req.params.id);
  event ? res.json(event) : res.status(404).send('Event not found');
});

// Create new event
app.post('/events', (req, res) => {
  const data = readData();
  const newEvent = { id: uuidv4(), interests: [], ...req.body };
  data.push(newEvent);
  writeData(data);
  res.status(201).json(newEvent);
});

// Delete event
app.delete('/events/:id', (req, res) => {
  let data = readData();
  data = data.filter(e => e.id !== req.params.id);
  writeData(data);
  res.status(204).send();
});

// Register interest in event
app.post('/events/:id/interest', (req, res) => {
  const data = readData();
  const eventIndex = data.findIndex(e => e.id === req.params.id);
  if (eventIndex === -1) return res.status(404).send('Event not found');
  data[eventIndex].interests.push(req.body);
  writeData(data);
  res.status(201).send('Interest registered');
});

app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
