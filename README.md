# IMG API

A high-performance REST API for AI-powered text-to-image generation. Built with FastAPI and Playwright, this service converts natural language prompts into high-quality images using advanced AI models.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

IMG API provides a simple HTTP interface for generating images from text descriptions. The service leverages browser automation to interact with AI image generation platforms, returning results as Base64-encoded images. This approach eliminates the need for complex API keys or authentication tokens.

**Base URL:** `http://localhost:8001`

---

## Features

- **Simple REST Interface** - Single GET endpoint for image generation
- **No Authentication Required** - Open access for development and testing
- **Base64 Response** - Images delivered as Base64 strings, ready for embedding or storage
- **Error Handling** - Automatic detection of rate limits and service errors
- **Headless Operation** - Runs without visible browser window
- **CORS Enabled** - Cross-origin requests supported out of the box
- **Static File Serving** - Built-in web interface for testing

---

## Architecture

```
IMG-API/
├── API/
│   ├── __init__.py          # Package initialization
│   ├── generator.py         # Core image generation logic
│   ├── server.py            # FastAPI server and endpoints
│   └── .env                 # Environment variables (URL configuration)
├── index.html               # Web interface for testing
└── requirements.txt         # Python dependencies
```

**Technology Stack:**
- **Framework:** FastAPI (Python 3.10+)
- **Browser Automation:** Playwright
- **Server:** Uvicorn (ASGI)
- **Language:** Python

---

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Internet connection (for initial AI model loading)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/img-api.git
cd img-api
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
python -m playwright install chromium
```

### 5. Configure Environment

Edit `API/.env` to set your target configuration:

```env
TARGET_URL=<base64-encoded-url>
```

---

## Configuration

The application uses environment variables for configuration. Create or modify the `.env` file in the `API/` directory:

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `TARGET_URL` | string | Yes | Base64-encoded URL of the target service |

### Encoding a URL

To encode your target URL:

```python
import base64

url = "https://your-target-service.com/generate"
encoded = base64.b64encode(url.encode()).decode()
print(encoded)
```

---

## Usage

### Starting the Server

```bash
cd API
python server.py
```

The server will start on `http://localhost:8001` and display:

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
Iniciando ImageGenerator...
ImageGenerator listo
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Web Interface

Open `http://localhost:8001` in your browser to access the web interface for testing.

### Making API Calls

#### cURL

```bash
curl "http://localhost:8001/api/generate?prompt=A%20futuristic%20city%20at%20sunset"
```

#### Python

```python
import requests

response = requests.get(
    "http://localhost:8001/api/generate",
    params={"prompt": "A futuristic city at sunset"}
)
data = response.json()

if data["success"]:
    print(f"Image generated successfully")
    print(f"Base64 length: {len(data['image'])} characters")
else:
    print(f"Error: {data['error']}")
```

#### JavaScript (Node.js)

```javascript
const axios = require('axios');

const response = await axios.get('http://localhost:8001/api/generate', {
    params: { prompt: 'A futuristic city at sunset' }
});

const data = response.data;
if (data.success) {
    console.log(`Image generated successfully`);
    console.log(`Base64 length: ${data.image.length} characters`);
} else {
    console.log(`Error: ${data.error}`);
}
```

#### JavaScript (Browser)

```javascript
const response = await fetch(
    `http://localhost:8001/api/generate?prompt=${encodeURIComponent('A futuristic city at sunset')}`
);
const data = await response.json();

if (data.success) {
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${data.image}`;
    document.body.appendChild(img);
}
```

---

## API Reference

### Generate Image

```
GET /api/generate
```

Generates an image from a text prompt.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the image to generate (minimum 1 character) |

#### Example Request

```
GET /api/generate?prompt=A%20serene%20mountain%20landscape%20at%20sunrise
```

---

## Response Format

### Success Response

```json
{
    "success": true,
    "image": "iVBORw0KGgoAAAANSUhEUg..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `image` | string | Base64-encoded PNG image data |

### Error Response

```json
{
    "success": false,
    "error": "Error message describing the issue"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` for errors |
| `error` | string | Human-readable error message |

---

## Error Handling

The API handles various error scenarios:

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Demasiadas solicitudes, intenta de nuevo en ~12 segundos." | Rate limit exceeded | Wait 12 seconds before retrying |
| "Servidor no inicializado correctamente" | Server startup failure | Restart the server |
| "Timeout exceeded" | Image generation took too long | Retry the request |
| "Element not found" | Page structure changed | Check for service updates |

---

## Rate Limits

The underlying AI service enforces rate limits. When exceeded, the API returns an error message indicating when to retry. 

**Recommended:** Wait at least 12 seconds between requests if you receive a rate limit error.

---

## Deployment

### Production Considerations

1. **Process Manager:** Use a process manager like `systemd` or `supervisor` to keep the server running
2. **Reverse Proxy:** Deploy behind Nginx or Apache for SSL termination and load balancing
3. **Monitoring:** Implement health checks and logging
4. **Scaling:** Run multiple instances behind a load balancer

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

COPY . .

CMD ["python", "API/server.py"]
```

### Systemd Service (Linux)

```ini
[Unit]
Description=IMG API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/img-api
ExecStart=/opt/img-api/.venv/bin/python API/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Project Structure

```
img-api/
├── API/
│   ├── __init__.py          # Package exports
│   ├── generator.py         # Browser automation and image generation
│   ├── server.py            # FastAPI application and routes
│   └── .env                 # Environment configuration
├── index.html               # Web interface
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.104.0 | Web framework |
| uvicorn | >=0.24.0 | ASGI server |
| playwright | >=1.40.0 | Browser automation |
| python-dotenv | >=1.0.0 | Environment variable management |

---

## License

This project is proprietary software. Unauthorized distribution or reproduction is prohibited.

---

## Support

For issues and inquiries, please contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** August 2026
