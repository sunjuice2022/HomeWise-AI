#!/bin/bash

# HomeWise AI Setup Script
# This script helps set up the HomeWise AI application

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         HomeWise AI - Setup Script                        ║"
echo "║   AI Property Price & Buying Power Chatbot                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running in project directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the HomeWiseAI project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Checking prerequisites...${NC}"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python detected: $PYTHON_VERSION"
else
    echo -e "${RED}✗ Python 3.9+ is required but not found${NC}"
    exit 1
fi

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js detected: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠ Node.js not found. Frontend setup will be skipped.${NC}"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker detected"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found. Docker setup will be skipped.${NC}"
    DOCKER_AVAILABLE=false
fi

echo ""
echo -e "${GREEN}Step 2: Setting up environment files...${NC}"

# Backend .env
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env from template"
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your OpenAI API key${NC}"
else
    echo "✓ backend/.env already exists"
fi

# Frontend .env
if [ -d "frontend" ] && [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✓ Created frontend/.env from template"
else
    echo "✓ frontend/.env already exists"
fi

echo ""
echo "Choose setup method:"
echo "1) Docker (recommended - includes all services)"
echo "2) Manual (Python + Node.js)"
echo "3) Backend only (Python)"
read -p "Enter choice (1-3): " SETUP_CHOICE

case $SETUP_CHOICE in
    1)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo -e "${RED}✗ Docker is not installed${NC}"
            exit 1
        fi

        echo ""
        echo -e "${GREEN}Step 3: Setting up with Docker...${NC}"

        # Check if .env has OpenAI key
        if ! grep -q "OPENAI_API_KEY=sk-" backend/.env 2>/dev/null; then
            echo -e "${YELLOW}⚠ Warning: OpenAI API key not found in backend/.env${NC}"
            read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_KEY
            if [ ! -z "$OPENAI_KEY" ]; then
                sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY/" backend/.env
                echo "✓ OpenAI API key added to backend/.env"
            fi
        fi

        echo "Building Docker containers..."
        docker-compose build

        echo "Starting services..."
        docker-compose up -d

        echo ""
        echo -e "${GREEN}✓ Setup complete!${NC}"
        echo ""
        echo "Services are running:"
        echo "  • Backend API: http://localhost:8000"
        echo "  • Frontend: http://localhost:3000"
        echo "  • API Docs: http://localhost:8000/docs"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;

    2)
        echo ""
        echo -e "${GREEN}Step 3: Setting up Backend (Python)...${NC}"

        cd backend

        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv venv
            echo "✓ Virtual environment created"
        fi

        # Activate virtual environment
        source venv/bin/activate

        # Install dependencies
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
        echo "✓ Dependencies installed"

        cd ..

        echo ""
        echo -e "${GREEN}Step 4: Setting up Frontend (Node.js)...${NC}"

        if command -v npm &> /dev/null; then
            cd frontend
            echo "Installing Node.js dependencies..."
            npm install
            echo "✓ Dependencies installed"
            cd ..
        else
            echo -e "${YELLOW}⚠ npm not found, skipping frontend setup${NC}"
        fi

        echo ""
        echo -e "${GREEN}✓ Setup complete!${NC}"
        echo ""
        echo "To start the application:"
        echo ""
        echo "Terminal 1 (Backend):"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  python -m app.main"
        echo ""
        echo "Terminal 2 (Frontend):"
        echo "  cd frontend"
        echo "  npm start"
        echo ""
        ;;

    3)
        echo ""
        echo -e "${GREEN}Step 3: Setting up Backend only...${NC}"

        cd backend

        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv venv
            echo "✓ Virtual environment created"
        fi

        # Activate virtual environment
        source venv/bin/activate

        # Install dependencies
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
        echo "✓ Dependencies installed"

        cd ..

        echo ""
        echo -e "${GREEN}✓ Setup complete!${NC}"
        echo ""
        echo "To start the backend:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  python -m app.main"
        echo ""
        echo "Backend will be available at: http://localhost:8000"
        echo "API Documentation: http://localhost:8000/docs"
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Important: Make sure you have added your OpenAI API key to backend/.env${NC}"
echo ""
echo "For more information, see QUICKSTART.md"
