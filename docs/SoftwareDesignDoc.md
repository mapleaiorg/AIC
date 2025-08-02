# Maple AI Companion - Software Design Document

**Version:** 2.0.0  
**Date:** August 2, 2025  
**Status:** Active Development  

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture Design](#3-architecture-design)
4. [Component Design](#4-component-design)
5. [Data Model](#5-data-model)
6. [API Design](#6-api-design)
7. [Security Design](#7-security-design)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Quality Attributes](#9-quality-attributes)
10. [Development Guidelines](#10-development-guidelines)

---

## 1. Executive Summary

### 1.1 Project Overview

Maple AI Companion is a next-generation AI companion backend service that provides advanced conversational AI capabilities with personality, memory, and emotional intelligence. The system is designed to create meaningful, personalized interactions between users and their AI companion "Maple."

### 1.2 Key Features

- **Advanced AI Personality System**: Dynamic personality adaptation based on Big Five traits + custom characteristics
- **Long-term Memory Management**: Persistent conversation context and user preference retention
- **Emotion Recognition & Response**: Real-time emotional analysis and appropriate responses
- **Multi-modal Interactions**: Text, voice, and image-based communication
- **Real-time Analytics**: Comprehensive user engagement and growth tracking
- **Enterprise Security**: JWT authentication, rate limiting, and data encryption

### 1.3 Technology Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite/PostgreSQL with SQLAlchemy ORM
- **AI Providers**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Voice Synthesis**: Edge-TTS, Google Cloud TTS, Azure TTS, AWS Polly
- **Deployment**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana
- **Load Balancing**: Nginx

---

## 2. System Overview

### 2.1 System Purpose

The Maple AI Companion backend serves as the core intelligence layer for AI companion applications, providing:

- Contextually aware conversational AI
- Persistent user relationship management
- Emotional intelligence and empathy
- Personalized interaction experiences
- Scalable multi-tenant architecture

### 2.2 System Scope

#### In Scope:
- RESTful API for AI companion interactions
- User authentication and authorization
- Conversation memory and context management
- Multi-provider AI integration
- Voice synthesis capabilities
- Analytics and insights dashboard
- Premium subscription management

#### Out of Scope:
- Frontend client applications
- Real-time video processing
- IoT device integration
- Third-party social media integrations

### 2.3 Stakeholders

- **End Users**: Individuals seeking AI companion interactions
- **App Developers**: iOS/Android developers integrating the API
- **System Administrators**: DevOps and infrastructure teams
- **Data Scientists**: Teams analyzing user interaction patterns
- **Product Managers**: Feature and roadmap planning teams

---

## 3. Architecture Design

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ iOS App     │  │ Android App │  │ Web Dashboard        │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/REST API
┌─────────────────────┼───────────────────────────────────────┐
│                 Load Balancer (Nginx)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┼─────────────────────────────────────────┐
│                Application Layer                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                         │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │   Auth      │ │ Middleware  │ │    API Routes       │ │ │
│  │  │  Security   │ │Rate Limiter │ │   Controllers       │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────┼────────────────────────────────────────┐
│                Service Layer                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    LLM      │ │ Companion   │ │      Analytics          │ │
│  │  Service    │ │  Service    │ │      Service            │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    TTS      │ │   Memory    │ │       User              │ │
│  │  Service    │ │  Service    │ │      Service            │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────┼────────────────────────────────────────┐
│                 Data Layer                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ PostgreSQL  │ │    Redis    │ │    File Storage         │ │
│  │  Database   │ │   Cache     │ │   (Uploads/Media)       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────┼────────────────────────────────────────┐
│               External Services                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   OpenAI    │ │  Anthropic  │ │      Google AI          │ │
│  │    API      │ │    Claude   │ │       Gemini            │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   AWS TTS   │ │  Azure TTS  │ │    Google Cloud TTS     │ │
│  │   Polly     │ │  Cognitive  │ │                         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Architectural Patterns

#### 3.2.1 Layered Architecture
- **Presentation Layer**: FastAPI routes and middleware
- **Business Logic Layer**: Service classes with domain logic
- **Data Access Layer**: SQLAlchemy ORM and database models
- **External Integration Layer**: Third-party API clients

#### 3.2.2 Service-Oriented Architecture (SOA)
- Modular service design for scalability
- Clear service boundaries and responsibilities
- Dependency injection for loose coupling

#### 3.2.3 Repository Pattern
- Data access abstraction
- Testable data layer
- Database-agnostic business logic

### 3.3 Design Principles

- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Extensible without modification
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Clients depend only on methods they use
- **DRY (Don't Repeat Yourself)**: Code reusability and maintainability

---

## 4. Component Design

### 4.1 Core Services

#### 4.1.1 LLM Service (`app/services/llm_service.py`)

**Purpose**: Manages AI conversation generation and personality adaptation

**Key Responsibilities**:
- AI provider abstraction (OpenAI, Anthropic, Google)
- Context-aware response generation
- Personality trait analysis
- Emotion recognition and response
- Fallback handling for service unavailability

**Key Methods**:
```python
async def generate_response(
    message: str,
    user_id: Optional[int],
    companion_state: Optional[CompanionState],
    conversation_context: Optional[ConversationContext],
    user_emotion: Optional[EmotionType]
) -> ChatResponse

async def generate_chat_suggestions(
    user_id: int,
    context: ConversationContext,
    companion_state: CompanionState
) -> List[str]
```

#### 4.1.2 Companion Service (`app/services/companion_service.py`)

**Purpose**: Manages AI companion state, personality, and interaction dynamics

**Key Responsibilities**:
- Companion state management
- Personality trait evolution
- Interaction processing
- Bond level calculation
- Energy and mood dynamics

**Key Methods**:
```python
async def get_companion_state(db: Session, user_id: int) -> CompanionState
async def process_enhanced_interaction(
    db: Session, 
    user_id: int, 
    action: CompanionAction
) -> CompanionResponse
```

#### 4.1.3 Memory Service (`app/services/memory_service.py`)

**Purpose**: Handles conversation memory, context, and long-term relationship data

**Key Responsibilities**:
- Conversation context management
- Memory storage and retrieval
- Context-aware information filtering
- Memory importance weighting

**Key Methods**:
```python
async def store_interaction(
    user_id: int,
    user_message: str,
    ai_response: str,
    user_emotion: Optional[EmotionType],
    ai_emotion: Optional[EmotionType]
)

async def get_conversation_context(user_id: int) -> ConversationContext
```

#### 4.1.4 TTS Service (`app/services/tts_service.py`)

**Purpose**: Provides text-to-speech capabilities with personality-aware synthesis

**Key Responsibilities**:
- Multi-provider TTS integration
- Voice personality adaptation
- Audio stream generation
- Voice preference management

**Key Methods**:
```python
async def synthesize_with_personality(
    text: str,
    companion_state: CompanionState,
    preferences: UserPreferences,
    emotion: Optional[str]
) -> io.BytesIO
```

#### 4.1.5 User Service (`app/services/user_service.py`)

**Purpose**: Manages user accounts, authentication, and preferences

**Key Responsibilities**:
- User registration and authentication
- Preference management
- Chat history storage
- Premium subscription handling

#### 4.1.6 Analytics Service (`app/services/analytics_service.py`)

**Purpose**: Provides user analytics, insights, and system monitoring

**Key Responsibilities**:
- User interaction tracking
- Companion growth analytics
- System performance monitoring
- Dashboard data aggregation

### 4.2 Middleware Components

#### 4.2.1 Rate Limiter (`app/middleware/rate_limiter.py`)
- Request rate limiting per client
- Sliding window algorithm
- Configurable limits per endpoint

#### 4.2.2 Analytics Middleware (`app/middleware/analytics.py`)
- Request/response logging
- Performance metrics collection
- Error tracking

### 4.3 Utility Components

#### 4.3.1 Security Utils (`app/utils/security.py`)
- JWT token management
- Admin access verification
- Encryption utilities

#### 4.3.2 Validation Utils (`app/utils/validation.py`)
- Input validation helpers
- Data sanitization
- Format checking

---

## 5. Data Model

### 5.1 Database Schema

#### 5.1.1 Core Entities

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    avatar_name VARCHAR DEFAULT 'maple_avatar_1',
    avatar_url VARCHAR,
    join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    total_conversations INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    total_voice_minutes FLOAT DEFAULT 0.0
);
```

**Companion States Table**
```sql
CREATE TABLE companion_states (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    mood VARCHAR DEFAULT 'happy',
    energy INTEGER DEFAULT 85,
    bond_level INTEGER DEFAULT 50,
    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_interactions INTEGER DEFAULT 0,
    
    -- Big Five Personality Traits
    openness FLOAT DEFAULT 0.7,
    conscientiousness FLOAT DEFAULT 0.8,
    extraversion FLOAT DEFAULT 0.6,
    agreeableness FLOAT DEFAULT 0.9,
    neuroticism FLOAT DEFAULT 0.2,
    
    -- Custom AI Traits
    playfulness FLOAT DEFAULT 0.7,
    empathy FLOAT DEFAULT 0.95,
    humor FLOAT DEFAULT 0.7,
    supportiveness FLOAT DEFAULT 0.95,
    adaptability FLOAT DEFAULT 0.8,
    
    experience_points INTEGER DEFAULT 0,
    skill_data JSON DEFAULT '{}'
);
```

**Chat Messages Table**
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR DEFAULT 'text',
    emotion VARCHAR,
    sentiment_score FLOAT DEFAULT 0.0,
    confidence FLOAT DEFAULT 0.8
);
```

**User Preferences Table**
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    voice VARCHAR DEFAULT 'maple_default',
    voice_speed FLOAT DEFAULT 1.0,
    voice_pitch FLOAT DEFAULT 1.0,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    companion_updates BOOLEAN DEFAULT TRUE,
    theme VARCHAR DEFAULT 'maple_red',
    dark_mode BOOLEAN DEFAULT FALSE,
    companion_name VARCHAR DEFAULT 'Maple',
    auto_play_voice BOOLEAN DEFAULT FALSE
);
```

### 5.2 Data Models (Pydantic)

#### 5.2.1 Core Models

**CompanionState**
```python
class CompanionState(BaseModel):
    mood: CompanionMood = CompanionMood.HAPPY
    energy: int = Field(85, ge=0, le=100)
    bond_level: int = Field(50, ge=0, le=100)
    last_interaction: datetime
    personality: PersonalityDimension
    experience_points: int = 0
    skills: Dict[str, int] = {}
```

**PersonalityDimension**
```python
class PersonalityDimension(BaseModel):
    # Big Five Traits
    openness: float = Field(0.7, ge=0.0, le=1.0)
    conscientiousness: float = Field(0.8, ge=0.0, le=1.0)
    extraversion: float = Field(0.6, ge=0.0, le=1.0)
    agreeableness: float = Field(0.9, ge=0.0, le=1.0)
    neuroticism: float = Field(0.2, ge=0.0, le=1.0)
    
    # Custom AI Traits
    playfulness: float = Field(0.7, ge=0.0, le=1.0)
    empathy: float = Field(0.95, ge=0.0, le=1.0)
    humor: float = Field(0.7, ge=0.0, le=1.0)
    supportiveness: float = Field(0.95, ge=0.0, le=1.0)
    adaptability: float = Field(0.8, ge=0.0, le=1.0)
```

### 5.3 Data Flow

#### 5.3.1 User Registration Flow
```
User Input → Validation → Password Hashing → Database Storage → 
Default Preferences Creation → Companion Initialization → 
Welcome Sequence (Background)
```

#### 5.3.2 Chat Interaction Flow
```
User Message → Authentication → Rate Limiting → 
Context Retrieval → AI Processing → Response Generation → 
Memory Storage → Analytics Update → Response Delivery
```

---

## 6. API Design

### 6.1 API Architecture

- **REST-based API** following OpenAPI 3.0 specification
- **JSON request/response** format
- **JWT Bearer token** authentication
- **Semantic versioning** with prefix `/api/v1/`
- **Rate limiting** with HTTP 429 responses
- **Comprehensive error handling** with structured error responses

### 6.2 Core Endpoints

#### 6.2.1 Authentication Endpoints

```
POST /auth/register
POST /auth/login
GET  /auth/me
POST /auth/refresh
```

#### 6.2.2 Chat Endpoints

```
POST /chat/message
GET  /chat/history
DELETE /chat/history
GET  /chat/suggestions
POST /chat/voice
```

#### 6.2.3 Companion Endpoints

```
GET  /companion/state
POST /companion/interact
PUT  /companion/personality
GET  /companion/memories
POST /companion/memory
```

#### 6.2.4 TTS Endpoints

```
POST /tts/synthesize
GET  /tts/voices
POST /tts/clone-voice  # Premium
```

#### 6.2.5 Analytics Endpoints

```
GET  /analytics/dashboard
GET  /analytics/companion-growth
GET  /analytics/insights
```

### 6.3 Request/Response Examples

#### 6.3.1 Chat Message Example

**Request**:
```json
POST /chat/message
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "content": "How are you feeling today?",
  "message_type": "text",
  "metadata": {}
}
```

**Response**:
```json
{
  "content": "I'm feeling wonderful today! The energy between us always brightens my mood. How has your day been going so far?",
  "timestamp": "2025-08-02T17:35:42.720Z",
  "message_type": "text",
  "emotion": "joy",
  "confidence": 0.85,
  "personality_traits": {
    "empathy": 0.9,
    "playfulness": 0.7,
    "supportiveness": 0.95
  },
  "response_context": {
    "conversation_style": "friendly",
    "emotional_resonance": 0.8,
    "context_utilization": 3
  }
}
```

---

## 7. Security Design

### 7.1 Authentication & Authorization

#### 7.1.1 JWT Token-Based Authentication
- **Access tokens**: Short-lived (7 days default)
- **Refresh tokens**: Long-lived (30 days)
- **Token payload**: User ID, email, permissions, expiration
- **Token signing**: HMAC SHA-256 with configurable secret

#### 7.1.2 Password Security
- **Bcrypt hashing** with configurable rounds (default: 12)
- **Password complexity** requirements enforced
- **Account lockout** after failed attempts (5 attempts, 15-minute lockout)

### 7.2 Data Protection

#### 7.2.1 Data Encryption
- **Passwords**: Bcrypt hashing
- **Sensitive data**: AES-256 encryption for stored credentials
- **Transit encryption**: HTTPS/TLS 1.3 required

#### 7.2.2 Privacy Controls
- **Data retention policies**: Configurable retention periods
- **User data export**: GDPR-compliant data export
- **Right to deletion**: Complete user data removal
- **Conversation privacy**: Encrypted conversation storage

### 7.3 Input Validation & Sanitization

#### 7.3.1 Request Validation
- **Pydantic model validation** for all inputs
- **SQL injection prevention** via ORM parameterized queries
- **XSS protection** through output encoding
- **File upload restrictions** with type and size validation

#### 7.3.2 Rate Limiting
- **Per-endpoint limits**: Configurable request rates
- **IP-based limiting**: Protection against abuse
- **User-based limiting**: Per-user quotas
- **Sliding window algorithm**: Smooth rate enforcement

### 7.4 Content Moderation

#### 7.4.1 AI Content Filtering
- **OpenAI Moderation API**: Automatic content screening
- **Custom word filters**: Configurable blocked content
- **Context-aware filtering**: Intelligent content analysis

---

## 8. Deployment Architecture

### 8.1 Containerization

#### 8.1.1 Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc g++ libffi-dev libssl-dev

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .
RUN mkdir -p uploads logs static

# Configuration
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s CMD curl -f http://localhost:8000/health

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.1.2 Docker Compose Stack
- **API Service**: Main FastAPI application
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for session and response caching
- **Reverse Proxy**: Nginx for load balancing
- **Monitoring**: Prometheus and Grafana stack

### 8.2 Environment Configuration

#### 8.2.1 Development Environment
- **SQLite database** for local development
- **Edge-TTS** for free voice synthesis
- **Debug logging** enabled
- **Hot reload** for development

#### 8.2.2 Production Environment
- **PostgreSQL** with connection pooling
- **Redis cluster** for high availability
- **Production logging** with structured output
- **Health checks** and auto-restart policies

### 8.3 Scaling Strategy

#### 8.3.1 Horizontal Scaling
- **Stateless application design** for easy scaling
- **Load balancing** with Nginx or cloud load balancers
- **Database connection pooling** for efficient resource usage
- **Shared file storage** for uploads and media

#### 8.3.2 Performance Optimization
- **Response caching** for frequently accessed data
- **Database query optimization** with proper indexing
- **Asynchronous processing** for background tasks
- **CDN integration** for static assets

---

## 9. Quality Attributes

### 9.1 Performance

#### 9.1.1 Response Time Targets
- **API response time**: < 200ms for 95th percentile
- **AI response generation**: < 3 seconds average
- **Database queries**: < 50ms for simple queries
- **TTS synthesis**: < 5 seconds for 200 characters

#### 9.1.2 Throughput Targets
- **Concurrent users**: 1,000+ simultaneous users
- **Requests per second**: 500+ RPS sustained
- **Database connections**: Efficient pooling (10-20 connections)

### 9.2 Scalability

#### 9.2.1 Horizontal Scaling
- **Stateless design** for easy horizontal scaling
- **Database partitioning** for large datasets
- **Microservice architecture** for independent scaling
- **Cloud-native deployment** ready

#### 9.2.2 Data Growth
- **Archive old conversations** automatically
- **Compress historical data** for storage efficiency
- **Implement data retention policies**

### 9.3 Reliability

#### 9.3.1 Availability Targets
- **Uptime**: 99.9% (8.77 hours downtime/year)
- **Recovery time**: < 5 minutes for planned maintenance
- **Data backup**: Daily automated backups with 30-day retention

#### 9.3.2 Fault Tolerance
- **Graceful degradation** when AI services unavailable
- **Circuit breaker pattern** for external API calls
- **Retry logic** with exponential backoff
- **Health checks** for all services

### 9.4 Security

#### 9.4.1 Authentication
- **Multi-factor authentication** support
- **OAuth2/OpenID Connect** integration ready
- **Session management** with secure token handling

#### 9.4.2 Data Protection
- **Encryption at rest** for sensitive data
- **Encryption in transit** (HTTPS/TLS)
- **PII handling** with privacy controls
- **Audit logging** for security events

### 9.5 Maintainability

#### 9.5.1 Code Quality
- **Type hints** throughout codebase
- **Comprehensive testing** (unit, integration, E2E)
- **Code documentation** with docstrings
- **Linting and formatting** with Black, Flake8

#### 9.5.2 Monitoring & Observability
- **Structured logging** with correlation IDs
- **Metrics collection** with Prometheus
- **Distributed tracing** for request flows
- **Error tracking** with detailed stack traces

---

## 10. Development Guidelines

### 10.1 Code Standards

#### 10.1.1 Python Code Style
- **PEP 8** compliance with 100-character line limit
- **Type hints** for all function parameters and returns
- **Docstrings** in Google format for all public functions
- **Async/await** for I/O operations

```python
async def generate_response(
    message: str,
    user_id: Optional[int] = None,
    companion_state: Optional[CompanionState] = None
) -> ChatResponse:
    """Generate AI response with context awareness.
    
    Args:
        message: User input message
        user_id: Optional user identifier for personalization
        companion_state: Current companion state for context
        
    Returns:
        Generated AI response with metadata
        
    Raises:
        HTTPException: When AI service is unavailable
    """
```

#### 10.1.2 Error Handling
- **Structured exceptions** with appropriate HTTP status codes
- **Graceful degradation** for external service failures
- **Comprehensive logging** with context information

### 10.2 Testing Strategy

#### 10.2.1 Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_auth.py
│   ├── test_services/
│   └── test_models.py
├── integration/             # Integration tests for API endpoints
│   ├── test_chat_api.py
│   └── test_auth_flow.py
├── performance/             # Load and performance tests
│   └── test_load.py
└── fixtures/               # Test data and fixtures
    └── sample_data.py
```

#### 10.2.2 Test Coverage Requirements
- **Unit tests**: > 90% code coverage
- **Integration tests**: All API endpoints
- **Performance tests**: Key user flows
- **Security tests**: Authentication and authorization

### 10.3 Deployment Process

#### 10.3.1 CI/CD Pipeline
```yaml
stages:
  - lint          # Code quality checks
  - test          # Unit and integration tests
  - security      # Security vulnerability scanning
  - build         # Docker image building
  - deploy-dev    # Development environment deployment
  - deploy-prod   # Production deployment (manual approval)
```

#### 10.3.2 Environment Promotion
- **Development**: Automatic deployment on merge to main
- **Staging**: Manual promotion for testing
- **Production**: Manual promotion with approval process

### 10.4 Monitoring & Alerting

#### 10.4.1 Key Metrics
- **Response time**: 95th percentile API response times
- **Error rate**: 5xx error percentage
- **User engagement**: Daily/monthly active users
- **AI performance**: Response quality metrics

#### 10.4.2 Alert Thresholds
- **Critical**: > 5% error rate, > 99th percentile response time
- **Warning**: > 2% error rate, degraded AI service performance
- **Info**: User registration spikes, unusual usage patterns

---

## Appendices

### Appendix A: Configuration Reference

**Environment Variables**:
```bash
# Application
APP_NAME="Maple AI Companion"
VERSION="2.0.0"
DEBUG=false
SECRET_KEY=<secure-random-key>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/maple_ai

# AI Providers
LLM_PROVIDER=openai
OPENAI_API_KEY=<api-key>
OPENAI_MODEL=gpt-4

# TTS
TTS_PROVIDER=edge

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=10080
RATE_LIMIT_REQUESTS=100
```

### Appendix B: API Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| AUTH_001 | Invalid credentials | 401 |
| AUTH_002 | Token expired | 401 |
| AUTH_003 | Account locked | 423 |
| RATE_001 | Rate limit exceeded | 429 |
| COMP_001 | Companion not found | 404 |
| AI_001 | AI service unavailable | 503 |

### Appendix C: Database Indexes

**Performance-Critical Indexes**:
```sql
-- Chat message queries
CREATE INDEX idx_chat_messages_user_timestamp 
ON chat_messages(user_id, timestamp DESC);

-- User lookup
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Companion state
CREATE INDEX idx_companion_states_user 
ON companion_states(user_id);
```

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-08-02 | Development Team | Initial version |
| 2.0 | 2025-08-02 | Development Team | Production-ready version |

**Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | - | - | 2025-08-02 |
| Product Manager | - | - | 2025-08-02 |
| Security Engineer | - | - | 2025-08-02 |