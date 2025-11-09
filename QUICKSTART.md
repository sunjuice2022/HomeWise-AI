# HomeWise AI - Quick Start Guide

This guide will help you get HomeWise AI up and running in minutes.

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- OpenAI API key (required)
- Optional: Domain.com.au, CoreLogic, or other property data API keys

## Option 1: Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
cd HomeWiseAI
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-openai-key-here
```

Create a `.env` file in the `frontend` directory:

```bash
cp frontend/.env.example frontend/.env
```

### 3. Start with Docker

```bash
docker-compose up -d
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000
- PostgreSQL database
- Redis cache

### 4. Access the Application

Open your browser and go to: http://localhost:3000

## Option 2: Manual Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Start the backend:
```bash
python -m app.main
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory (in a new terminal):
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
```

4. Start the frontend:
```bash
npm start
```

Frontend will be available at http://localhost:3000

## Testing the Application

### 1. Chat Interface

Try these example queries:

- "What's the current market price for properties in Melbourne?"
- "I have a $100,000 deposit and earn $85,000 per year. What can I afford?"
- "Tell me about the Sydney property market"

### 2. Property Price Estimator

- Click on "Property Price Estimator" tab
- Enter an address (e.g., "123 Smith Street, Melbourne VIC 3000")
- Add property details (bedrooms, bathrooms, etc.)
- Click "Get Price Estimate"

### 3. Buying Power Calculator

- Click on "Buying Power Calculator" tab
- Enter your financial details:
  - Deposit: $100,000
  - Annual Income: $85,000
  - Monthly Expenses: $3,000
- Click "Calculate Buying Power"

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

### Backend Configuration (backend/.env)

Required:
```
OPENAI_API_KEY=your-key-here
```

Optional (for enhanced features):
```
DOMAIN_API_KEY=your-domain-key
REALESTATE_API_KEY=your-realestate-key
CORELOGIC_API_KEY=your-corelogic-key
PINECONE_API_KEY=your-pinecone-key
```

### Frontend Configuration (frontend/.env)

```
REACT_APP_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start

1. Check Python version: `python --version` (should be 3.9+)
2. Check if OpenAI API key is set in backend/.env
3. Check if port 8000 is available

### Frontend won't start

1. Check Node version: `node --version` (should be 16+)
2. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
3. Check if port 3000 is available

### API errors

1. Ensure backend is running and accessible
2. Check CORS settings in backend/app/config.py
3. Check browser console for errors
4. Verify REACT_APP_API_URL in frontend/.env

### Docker issues

1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs -f`
3. Rebuild containers: `docker-compose down && docker-compose up --build`

## Development Mode

### Backend with auto-reload

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend with hot-reload

```bash
cd frontend
npm start
```

## Production Deployment

### Build Frontend

```bash
cd frontend
npm run build
```

The production build will be in `frontend/build/`

### Backend Production

Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Next Steps

1. **Customize the AI**: Edit prompts in `backend/app/agents/` to customize agent behavior
2. **Add Real Data**: Integrate with actual property APIs (Domain, CoreLogic, etc.)
3. **Enhance RAG**: Add more property data to the vector store
4. **Deploy**: Deploy to cloud platforms (AWS, GCP, Azure, Heroku, etc.)

## Support

For issues and questions:
- Check the main [README.md](README.md)
- Review [API documentation](http://localhost:8000/docs)
- Check logs: `docker-compose logs -f`

## Sample Data

The application comes with sample data for testing. To add more data to the RAG system, you can:

1. Add property listings to `backend/app/agents/orchestrator.py` in the `_seed_sample_data()` method
2. Use the API to programmatically add data
3. Integrate with real property data APIs

Enjoy using HomeWise AI! 🏠✨
