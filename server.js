const express = require('express');
const http = require('http');
const { setupWebSocket } = require('./websocket'); // Import setupWebSocket
const connectDB = require('./config/db');
const errorHandler = require('./middlewares/errorHandler');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Connect to database
connectDB();

// Define routes
app.use('/api', require('./routes/scheduleRoutes'));
app.use('/api', require('./routes/roiMetricsRoutes'));
app.use('/api', require('./routes/settingsRoutes'));
app.use('/api', require('./routes/templateScheduleRoutes'));
app.use('/api', require('./routes/notificationRoutes'));

// Error handling middleware
app.use(errorHandler);

app.get("/", (req, res) => res.send("Express on Vercel"));

const PORT = process.env.PORT || 4000;
const server = http.createServer(app);

// Setup WebSocket server
setupWebSocket(server);

server.listen(PORT, () => console.log(`Server started on port ${PORT}`));

module.exports = app;
