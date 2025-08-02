# 🍁 Maple AI Companion Backend v2.0

## World-Class AI Companion Service

A next-generation AI companion backend featuring advanced personality systems, long-term memory, emotion recognition, and multi-modal interactions. Built for production scale with enterprise-grade security and monitoring.

[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/mapleaiorg/AIC)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)

## 🚀 What Makes This the Best AI Companion Service

### 🧠 Advanced AI Personality System
- **Dynamic Personality**: Adapts based on Big Five personality traits + custom AI characteristics
- **Emotional Intelligence**: Real-time emotion recognition and appropriate responses
- **Context Awareness**: Maintains conversation flow with deep understanding
- **Multi-Provider Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini

### 💾 Sophisticated Memory System
- **Long-term Memory**: Remembers preferences, experiences, and important moments
- **Memory Consolidation**: Automatically organizes and prioritizes memories
- **Contextual Retrieval**: Brings up relevant memories during conversations
- **Emotional Weighting**: Stronger memories for emotionally significant events

### 🎭 Emotional Intelligence
- **Emotion Recognition**: Analyzes text and voice for emotional states
- **Empathetic Responses**: Matches emotional tone appropriately
- **Mood Tracking**: Monitors user and companion emotional journey
- **Therapeutic Support**: Provides appropriate emotional support

### 🎵 Advanced Voice Features
- **Multi-Provider TTS**: Edge-TTS (free), Google Cloud, Azure, AWS Polly
- **Voice Cloning**: Premium feature for personalized voices
- **Emotion in Speech**: Expressive voice synthesis
- **Real-time Processing**: Low-latency voice interactions

### 📊 Real-time Analytics
- **User Insights**: Comprehensive dashboard with growth metrics
- **Conversation Analytics**: Quality scoring and engagement tracking
- **Personality Evolution**: Track how the AI companion grows
- **Performance Monitoring**: Prometheus + Grafana integration

### 🔒 Enterprise Security
- **JWT Authentication**: Secure token-based auth with refresh tokens
- **Rate Limiting**: Prevents abuse with intelligent throttling
- **Data Encryption**: All sensitive data encrypted at rest
- **Privacy Controls**: Granular privacy settings for users

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Development](#-development)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL or SQLite
- Redis (optional, for caching)
- API keys for your chosen LLM provider

### 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/mapleaiorg/AIC.git
cd AIC

# Run the setup script
chmod +x setup.sh
./setup.sh

# Configure your environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
./run.sh
```

That's it! Your AI companion service is now running at `http://localhost:8000`

## 🌟 Features

### Core Features
- ✅ **Advanced AI Conversations** - Context-aware, personality-driven responses
- ✅ **Long-term Memory** - Remembers user preferences and experiences
- ✅ **Emotion Recognition** - Understands and responds to emotional cues
- ✅ **Voice Interactions** - High-quality text-to-speech with emotion
- ✅ **Multi-modal Chat** - Text, voice, and image support
- ✅ **Real-time Analytics** - Comprehensive user and system insights
- ✅ **Personality Adaptation** - AI grows and adapts over time

### Premium Features
- 💎 **Voice Cloning** - Personalized AI voice synthesis
- 💎 **Advanced Customization** - Deep personality trait modification
- 💎 **Unlimited History** - Complete conversation retention
- 💎 **Priority Support** - Fast response times and dedicated support
- 💎 **Custom Avatars** - Upload and use custom companion appearances
- 💎 **Advanced Analytics** - Detailed insights and growth tracking

### Enterprise Features
- 🏢 **Multi-tenant Support** - Isolated environments for organizations
- 🏢 **SSO Integration** - SAML, OAuth2, Active Directory support
- 🏢 **Advanced Monitoring** - Prometheus, Grafana, custom metrics
- 🏢 **Data Compliance** - GDPR, CCPA, HIPAA compliance options
- 🏢 **Custom Deployment** - On-premise or private cloud options
- 🏢 **API Rate Limiting** - Sophisticated rate limiting and quotas

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   iOS/Android   │    │   Web Client    │    │   API Client    │
│      Apps       │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │     (Nginx)     │
                    └─────────┬───────┘
                              │
                    ┌─────────────────┐
                    │   FastAPI App   │
                    │   (Python 3.11) │
                    └─────────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │      Redis      │ │  AI Providers   │
│   (Database)    │ │    (Cache)      │ │ OpenAI/Claude   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Service Architecture

```
app/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models and schemas
├── database.py          # SQLAlchemy models and database
├── auth.py              # Authentication and security
├── config.py            # Configuration management
├── services/            # Business logic services
│   ├── enhanced_llm_service.py    # AI conversation engine
│   ├── memory_service.py          # Long-term memory system
│   ├── emotion_service.py         # Emotion recognition
│   ├── analytics_service.py       # Analytics and insights
│   ├── tts_service.py            # Text-to-speech
│   └── companion_service.py       # Companion state management
├── middleware/          # Custom middleware
│   ├── rate_limiter.py           # Rate limiting
│   └── analytics.py              # Request analytics
└── utils/               # Utility functions
    ├── security.py              # Security helpers
    └── validation.py            # Data validation
```

## 📦 Installation

### Option 1: Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/mapleaiorg/AIC.git
cd AIC
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start development server
./dev.sh
```

### Option 2: Docker Deployment

```bash
# Clone repository
git clone https://github.com/mapleaiorg/AIC.git
cd AIC

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Deploy with Docker Compose
./deploy.sh
```

### Option 3: Manual Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
"

# Start server
uvicorn main:app --reload
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Basic Settings
APP_NAME="Maple AI Companion"
DEBUG=false
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/maple_ai

# AI Provider (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# TTS Provider
TTS_PROVIDER=edge  # Free option
# Or premium providers:
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# AZURE_SPEECH_KEY=your-azure-key

# Security
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Features
PREMIUM_FEATURES_ENABLED=true
VOICE_CLONING_ENABLED=false
ANALYTICS_ENABLED=true
```

### LLM Provider Setup

#### OpenAI (Recommended)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

#### Anthropic Claude
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Google Gemini
```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL=gemini-pro
```

### TTS Provider Setup

#### Edge-TTS (Free)
```bash
TTS_PROVIDER=edge
```

#### Google Cloud TTS
```bash
TTS_PROVIDER=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

#### Azure Cognitive Services
```bash
TTS_PROVIDER=azure
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus
```

## 📚 API Documentation

### Authentication

All API endpoints (except guest endpoints) require authentication:

```bash
# Login to get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/companion/state"
```

### Key Endpoints

#### Chat with AI
```bash
POST /chat/message
{
  "content": "Hello, how are you today?",
  "message_type": "text"
}
```

#### Voice Chat
```bash
POST /chat/voice
# Upload audio file for voice-to-voice interaction
```

#### Companion Interaction
```bash
POST /companion/interact
{
  "action": "play",
  "intensity": 1.0
}
```

#### Get User Analytics
```bash
GET /analytics/dashboard
# Returns comprehensive user analytics and insights
```

#### Text-to-Speech
```bash
POST /tts/synthesize
{
  "text": "Hello! How are you feeling today?",
  "emotion": "joy",
  "voice": "maple_default"
}
```

### Full API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Deployment

### Production Deployment with Docker

```bash
# 1. Clone and configure
git clone https://github.com/mapleaiorg/AIC.git
cd AIC
cp .env.example .env
# Edit .env with production settings

# 2. Deploy
./deploy.sh

# 3. Verify deployment
curl http://localhost:8000/health
```

### Cloud Deployment Options

#### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/maple-aic
gcloud run deploy --image gcr.io/PROJECT-ID/maple-aic --platform managed
```

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin
docker build -t maple-aic .
docker tag maple-aic:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/maple-aic:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/maple-aic:latest
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maple-aic
spec:
  replicas: 3
  selector:
    matchLabels:
      app: maple-aic
  template:
    metadata:
      labels:
        app: maple-aic
    spec:
      containers:
      - name: maple-aic
        image: maple-aic:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: maple-secrets
              key: database-url
```

## 🛠️ Development

### Development Setup

```bash
# Setup development environment
./dev.sh

# This will:
# - Install dev dependencies (pytest, black, flake8, mypy)
# - Run code quality checks
# - Run tests
# - Start development server with hot reload
```

### Code Quality

```bash
# Format code
black . --line-length 100

# Lint code
flake8 . --max-line-length=100

# Type checking
mypy . --ignore-missing-imports

# Run tests
pytest tests/ -v --cov=app
```

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Add Your Feature**
   - Add models to `app/models.py`
   - Add database models to `app/database.py`
   - Add business logic to `app/services/`
   - Add API endpoints to `main.py`

3. **Add Tests**
   ```bash
   # Add tests to tests/
   pytest tests/test_your_feature.py -v
   ```

4. **Submit Pull Request**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

### Database Migrations

```python
# Add new models to app/database.py
# Then run:
python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
"
```

## 📊 Monitoring

### Prometheus Metrics

Available at `http://localhost:9090` when using Docker deployment:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `active_users` - Currently active users
- `ai_response_time` - AI response generation time
- `memory_usage` - Memory service usage
- `companion_interactions` - Companion interaction counts

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (admin/admin123):

- **System Overview** - Overall system health and performance
- **User Analytics** - User engagement and growth metrics
- **AI Performance** - LLM response times and quality metrics
- **Companion Metrics** - Companion interaction and growth data

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed service status
curl http://localhost:8000/health | jq
{
  "status": "healthy",
  "services": {
    "llm": true,
    "tts": true,
    "database": true,
    "analytics": true,
    "memory": true
  },
  "uptime": "2h 34m",
  "version": "2.0.0"
}
```

### Logging

Structured JSON logging with multiple levels:

```python
# app/logging_config.py
import logging
import structlog

# Logs are automatically structured and include:
# - Request ID
# - User ID (when authenticated)
# - Timestamp
# - Service context
# - Performance metrics
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_chat.py -v

# Run integration tests
pytest tests/integration/ -v
```

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_companion.py
│   └── test_memory.py
├── integration/             # Integration tests
│   ├── test_api_flows.py
│   └── test_database.py
├── performance/             # Performance tests
│   └── test_load.py
└── fixtures/               # Test fixtures
    └── sample_data.py
```

### Performance Testing

```bash
# Load testing with locust
pip install locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## 🔒 Security

### Security Features

- **JWT Authentication** with secure token generation
- **Rate Limiting** to prevent abuse
- **Input Validation** using Pydantic models
- **SQL Injection Protection** via SQLAlchemy ORM
- **XSS Protection** with proper header configuration
- **CORS Configuration** for cross-origin security
- **Password Hashing** with bcrypt
- **Account Lockout** after failed login attempts

### Security Best Practices

1. **Environment Variables**: Never commit API keys or secrets
2. **HTTPS Only**: Always use HTTPS in production
3. **Regular Updates**: Keep dependencies updated
4. **Access Logs**: Monitor access patterns for anomalies
5. **Data Encryption**: Encrypt sensitive data at rest
6. **Backup Security**: Secure and encrypt backups

### Compliance

- **GDPR**: User data export and deletion capabilities
- **CCPA**: Privacy controls and data transparency
- **SOC 2**: Security and availability controls
- **HIPAA**: Healthcare data protection (enterprise)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Process

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/AmazingFeature`
3. **Make Changes**: Follow our coding standards
4. **Add Tests**: Ensure good test coverage
5. **Run Quality Checks**: `./dev.sh` to run all checks
6. **Commit Changes**: `git commit -m 'Add AmazingFeature'`
7. **Push to Branch**: `git push origin feature/AmazingFeature`
8. **Open Pull Request**: Describe your changes thoroughly

### Coding Standards

- **Python**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for all functions
- **Documentation**: Add docstrings for all public functions
- **Tests**: Maintain >90% test coverage
- **Commit Messages**: Use conventional commit format

### Areas for Contribution

- 🤖 **AI Improvements**: Better personality models, emotion recognition
- 🎵 **Voice Features**: New TTS providers, voice cloning improvements
- 📊 **Analytics**: Advanced insights and visualization
- 🔒 **Security**: Security audits and improvements
- 📚 **Documentation**: Tutorials, examples, API documentation
- 🧪 **Testing**: More comprehensive test coverage
- 🌐 **Internationalization**: Multi-language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Community Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/mapleaiorg/AIC/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/mapleaiorg/AIC/discussions)
- **Discord**: [Join our community Discord](https://discord.gg/mapleai)

### Commercial Support

- **Priority Support**: Available for production deployments
- **Custom Development**: Tailored features for enterprise needs
- **Consulting**: Architecture and deployment consultation
- **Training**: Team training and onboarding

Contact: [support@mapleai.org](mailto:support@mapleai.org)

## 🎯 Roadmap

### Version 2.1 (Q2 2024)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Advanced voice cloning with fewer samples
- [ ] Real-time voice conversations
- [ ] Group conversations with multiple AI personalities

### Version 2.2 (Q3 2024)
- [ ] Video call support with avatar animation
- [ ] Integration with popular services (Calendar, Spotify, etc.)
- [ ] Advanced emotion recognition from images
- [ ] Custom AI model training for enterprises

### Version 3.0 (Q4 2024)
- [ ] Multi-modal AI with vision and audio understanding
- [ ] Advanced reasoning and problem-solving capabilities
- [ ] Autonomous task execution
- [ ] Enterprise SSO and compliance features

## 🏆 Acknowledgments

- **OpenAI** for GPT models and Whisper
- **Anthropic** for Claude models
- **Google** for Gemini AI
- **FastAPI** team for the amazing framework
- **SQLAlchemy** for excellent ORM
- **Edge-TTS** for free text-to-speech
- **The open-source community** for countless libraries and tools

---

<div align="center">

**Built with ❤️ by the Maple AI Team**

[Website](https://mapleai.org) • [Documentation](https://docs.mapleai.org) • [Discord](https://discord.gg/mapleai) • [Twitter](https://twitter.com/mapleai)

</div>