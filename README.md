# Salon Services Extraction API

A Python/FastAPI service that extracts salon services from menu images using Google Gemini Flash and matches them with existing salon service variations in MongoDB.

## Overview

This service allows salon owners to upload images of their service menus and receive structured data about their services, matched with existing service variations in the database. The output is a flattened list of service variation objects that can be consumed by the Unque backend or other systems.

## Features

- Image upload endpoint accepting JPEG, PNG, and other common formats
- Gemini Flash integration for accurate service extraction from menu images
- MongoDB integration for matching extracted services with existing salon service variations
- Flexible matching strategy: exact match first, fallback to text search
- Structured response matching the expected salon service variation format
- Health check endpoints
- Comprehensive error handling

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your configuration:
   ```bash
   cp .env.example .env
   ```
4. Update the `.env` file with your actual values

## Usage

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Extract Services from Image

**Endpoint:** `POST /api/v1/extract-services`

**Parameters:**
- `file`: The menu image file (required)
- `salon_id`: Optional salon identifier for filtering variations

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "serviceId": "shaving",
      "name": "abcdxyz",
      "category": "Shaving",
      "categoryServiceId": "shaving",
      "duration": 15,
      "gender": "M",
      "personType": "A",
      "price": 50,
      "tagNameAndValues": [],
      "variationId": "",
      // ... additional fields
    }
  ],
  "metadata": {
    "processed_image": "menu.jpg",
    "categories_found": 3,
    "total_variations_matched": 15
  }
}
```

## Health Check

**Endpoint:** `GET /health` or `GET /api/v1/health`

Returns:
```json
{
  "status": "healthy",
  "service": "salon-services-extraction"
}
```

## Configuration

Create a `.env` file with the following variables:

- `GOOGLE_AI_API_KEY`: Your Google Gemini API key
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DATABASE`: Database name (default: `test`)
- `PORT`: Server port (default: `8000`)
- `NODE_ENV`: Environment (`development` or `production`)
- `DEFAULT_SALON_ID`: Optional default salon ID for testing

## Database Structure

This service expects the following MongoDB collections (matching the Unque database dump):

- `services`: Master list of services
- `salonservices`: Links salons to services they offer
- `salonservicevariations`: Specific variations/options within a salon service
- `variationnameandserviceid`: Search index mapping variation names to service IDs

## Integration with Unque System

This service is designed to integrate with the Unque backend system through:

1. **Database-level integration**: Direct access to the same MongoDB collections
2. **API-level integration**: Can be called by the Unque backend via HTTP
3. **Data compatibility**: Output format matches expected salon service variation objects

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

## License

MIT