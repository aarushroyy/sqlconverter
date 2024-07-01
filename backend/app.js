const express = require('express');
const path = require('path');

const app = express();

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, '../public')));

// Serve index.html for the root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// For local development, you might want to add a proxy for the /api/upload route
// This would forward requests to your Python script when running locally
if (process.env.NODE_ENV === 'development') {
  const { createProxyMiddleware } = require('http-proxy-middleware');
  app.use('/api/upload', createProxyMiddleware({ target: 'http://localhost:5000', changeOrigin: true }));
}

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something went wrong!');
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});