# Todo Application - Web Architecture Document

**Version:** 1.0  
**Date:** 2026-03-20  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Database Design](#database-design)
6. [Security Considerations](#security-considerations)
7. [Deployment Guide](#deployment-guide)
8. [Technology Stack Summary](#technology-stack-summary)

---

## Executive Summary

This document presents a comprehensive web architecture for a modern Todo Application designed with scalability, security, and maintainability in mind. The architecture follows industry best practices and leverages proven technologies to deliver a production-ready solution.

### Key Highlights

| Aspect | Approach |
|--------|----------|
| **Architecture Pattern** | Clean Architecture / Layered Architecture |
| **Frontend Stack** | React 18 + TypeScript + Vite |
| **State Management** | Zustand (client) + React Query (server) |
| **UI Framework** | Tailwind CSS + shadcn/ui |
| **Backend Framework** | Express.js / Fastify (Node.js) |
| **Database** | PostgreSQL 16 (primary) |
| **Authentication** | JWT with refresh token rotation |
| **Deployment** | Containerized (Docker + Kubernetes) |

### Architecture Goals

1. **Scalability** - Horizontal scaling support via containerization
2. **Security** - Defense-in-depth with JWT auth, input validation, and OWASP compliance
3. **Performance** - Optimized database queries, caching layer, and CDN integration
4. **Maintainability** - Clean code structure, comprehensive documentation, and automated testing
5. **Developer Experience** - Fast HMR, TypeScript throughout, and clear API contracts

---

## System Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   Web App    │  │  Mobile App  │  │   PWA        │                    │
│  │  (React)     │  │ (React Native)│  │  (Future)   │                    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                    │
└─────────┼─────────────────┼─────────────────┼───────────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │ HTTPS / HTTP/2
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CDN / EDGE LAYER                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  CloudFront / Cloudflare - Static Assets + DDoS Protection      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOAD BALANCER LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  AWS ALB / NGINX - SSL Termination + Health Checks              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  API Server 1 │   │  API Server 2 │   │  API Server N │
│  (Node.js)    │   │  (Node.js)    │   │  (Node.js)    │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    Cache      │   │    Message    │   │     File      │
│   (Redis)     │   │    Queue      │   │   Storage     │
│               │   │   (Future)    │   │   (Future)    │
└───────────────┘   └───────────────┘   └───────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL (Primary + Read Replicas)               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### System Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + TypeScript | Single Page Application |
| **State Management** | Zustand + React Query | Client & Server State |
| **API Gateway** | Express.js / Fastify | RESTful API |
| **Authentication** | JWT + bcrypt | User Auth & Authorization |
| **Database** | PostgreSQL 16 | Primary Data Store |
| **Cache** | Redis 7 | Session & Rate Limiting |
| **Container** | Docker | Application Packaging |
| **Orchestration** | Kubernetes | Container Management |

### Data Flow

```
User Action → React Component → Zustand Store → API Service
                                                ↓
                    UI Update ← React Query ← Backend API
                                                ↓
                    PostgreSQL ← Prisma ORM ← Business Logic
```

---

## Frontend Architecture

### Directory Structure

```
src/
├── components/              # Reusable UI components
│   ├── common/             # Shared UI primitives
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Checkbox/
│   │   └── Modal/
│   ├── todo/               # Todo-specific components
│   │   ├── TodoItem/
│   │   ├── TodoList/
│   │   ├── TodoForm/
│   │   ├── TodoFilter/
│   │   └── TodoStats/
│   └── layout/             # Layout components
│       ├── Header/
│       ├── Sidebar/
│       └── Footer/
├── pages/                  # Page-level components
│   ├── Home/
│   ├── Today/
│   ├── Upcoming/
│   ├── Completed/
│   └── Settings/
├── hooks/                  # Custom React hooks
│   ├── useTodos.ts
│   ├── useLocalStorage.ts
│   └── useFilter.ts
├── services/               # API and external services
│   └── todoApi.ts
├── types/                  # TypeScript interfaces
│   └── index.ts
├── utils/                  # Utility functions
│   └── helpers.ts
├── store/                  # State management
│   ├── todoStore.ts
│   └── selectors.ts
└── styles/                 # Global styles
    └── global.css
```

### Component Hierarchy

```
App
├── Router
│   ├── Layout
│   │   ├── Header
│   │   │   └── Navigation
│   │   ├── Sidebar
│   │   │   └── FilterMenu
│   │   └── Main Content
│   │       └── Routes
│   │           ├── Home
│   │           │   ├── TodoStats
│   │           │   ├── TodoForm
│   │           │   ├── TodoFilter
│   │           │   └── TodoList
│   │           │       └── TodoItem[]
│   │           ├── Today
│   │           ├── Upcoming
│   │           ├── Completed
│   │           └── Settings
│   └── Footer
└── Modals (Portal)
    └── ConfirmDialog
```

### State Management Architecture

#### Zustand Store Structure

```typescript
// Store Architecture
interface TodoState {
  // State
  todos: Todo[];
  filter: TodoFilter;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  addTodo: (todo: TodoFormData) => void;
  updateTodo: (id: string, updates: Partial<Todo>) => void;
  deleteTodo: (id: string) => void;
  toggleTodo: (id: string) => void;
  setFilter: (filter: Partial<TodoFilter>) => void;
  clearCompleted: () => void;
  reorderTodos: (startIndex: number, endIndex: number) => void;
}
```

#### State Management Flow

```
┌─────────────────────────────────────────────────────────┐
│                    STATE ARCHITECTURE                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │   CLIENT STATE  │      │   SERVER STATE  │          │
│  │   (Zustand)     │      │  (React Query)  │          │
│  │                 │      │                 │          │
│  │  • UI State     │      │  • API Cache    │          │
│  │  • Form State   │      │  • Background   │          │
│  │  • Local Todos  │      │    Sync         │          │
│  │  • Filters      │      │  • Optimistic   │          │
│  │                 │      │    Updates      │          │
│  └────────┬────────┘      └────────┬────────┘          │
│           │                        │                    │
│           │   ┌──────────────┐    │                    │
│           └──▶│  Persistence │◀───┘                    │
│               │  (Optional)  │                         │
│               └──────────────┘                         │
│                        │                               │
│                        ▼                               │
│               ┌──────────────┐                         │
│               │ localStorage │                         │
│               │  / Backend   │                         │
│               └──────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

### Routing Architecture

#### Route Structure

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Home | Redirect to `/all` |
| `/all` | Home | All todos view |
| `/today` | Today | Today's todos |
| `/upcoming` | Upcoming | Upcoming todos |
| `/completed` | Completed | Completed todos |
| `/settings` | Settings | User settings |
| `*` | NotFound | 404 page |

#### Route Guards

```typescript
// Protected Route Pattern
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiresAuth?: boolean;
}

// Authentication flow for protected routes
Unauthenticated User → Redirect to /login → Authenticate → Redirect back
```

### UI Component Strategy

#### shadcn/ui + Tailwind CSS

| Feature | Implementation |
|---------|----------------|
| **Component Library** | shadcn/ui (built on Radix UI) |
| **Styling** | Tailwind CSS |
| **Icons** | Lucide React |
| **Animations** | Tailwind Animations |
| **Forms** | React Hook Form + Zod |

#### Component Example: TodoItem

```typescript
interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onEdit: (id: string, data: Partial<Todo>) => void;
  onDelete: (id: string) => void;
}

// Optimized with React.memo for performance
export const TodoItem = memo(({ todo, onToggle, onEdit, onDelete }: TodoItemProps) => {
  // Component implementation
});
```

### Performance Optimizations

| Technique | Implementation |
|-----------|----------------|
| **Code Splitting** | `React.lazy()` for route-level splitting |
| **Memoization** | `React.memo()` for list items |
| **Virtualization** | `@tanstack/react-virtual` for large lists |
| **Image Optimization** | Lazy loading + WebP format |
| **Bundle Analysis** | `rollup-plugin-visualizer` |

---

## Backend Architecture

### API Architecture

#### REST API Endpoints

Base URL: `https://api.todoapp.com/v1`

**Authentication Endpoints**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | User login |
| POST | `/auth/logout` | Yes | User logout |
| POST | `/auth/refresh` | Yes (refresh) | Refresh access token |
| POST | `/auth/forgot-password` | No | Request password reset |
| POST | `/auth/reset-password` | No | Reset password |
| GET | `/auth/oauth/:provider` | No | OAuth login |

**Todo Endpoints**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/todos` | Yes | List all todos (paginated) |
| GET | `/todos/:id` | Yes | Get single todo |
| POST | `/todos` | Yes | Create new todo |
| PUT | `/todos/:id` | Yes | Update todo (full) |
| PATCH | `/todos/:id` | Yes | Partial update todo |
| DELETE | `/todos/:id` | Yes | Delete todo |
| PUT | `/todos/:id/complete` | Yes | Mark as complete |
| PUT | `/todos/:id/uncomplete` | Yes | Mark as incomplete |

**User Endpoints**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/users/me` | Yes | Get current user |
| PUT | `/users/me` | Yes | Update user profile |
| DELETE | `/users/me` | Yes | Delete account |
| GET | `/users/me/stats` | Yes | Get todo statistics |

### Request/Response Format

#### Success Response

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete backend architecture",
    "completed": false
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-abc123"
  }
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "title", "message": "Title is required" }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-abc123"
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | OK - Successful GET, PUT, PATCH |
| 201 | Created - Successful POST |
| 204 | No Content - Successful DELETE |
| 400 | Bad Request - Validation errors |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Business logic error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Unexpected error |

### Middleware Stack

```
Request → CORS → Rate Limiter → Helmet (Security) → Body Parser → 
          Auth Middleware → Validation → Route Handler → Response
```

| Middleware | Purpose |
|------------|---------|
| **CORS** | Cross-origin resource sharing |
| **Rate Limiter** | Prevent brute force attacks |
| **Helmet** | Security headers |
| **Body Parser** | Parse JSON/form data |
| **Auth Middleware** | JWT verification |
| **Validation** | Request validation (Zod) |
| **Error Handler** | Global error handling |

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────────────┐         ┌─────────────────────┐
│       users         │         │       todos         │
├─────────────────────┤         ├─────────────────────┤
│ id (PK) UUID        │◄───────│ user_id (FK) UUID   │
│ email VARCHAR(255)  │    1:M  │ id (PK) UUID        │
│ password_hash       │         │ title VARCHAR(255)  │
│   VARCHAR(255)      │         │ description TEXT    │
│ name VARCHAR(100)   │         │ completed BOOLEAN   │
│ avatar_url          │         │ priority VARCHAR(20)│
│   VARCHAR(500)      │         │ due_date TIMESTAMP  │
│ email_verified      │         │ tags TEXT[]         │
│   BOOLEAN           │         │ created_at          │
│ oauth_provider      │         │ updated_at          │
│   VARCHAR(50)       │         └─────────────────────┘
│ oauth_id            │                   │
│   VARCHAR(255)      │                   │
│ created_at          │                   │
│ updated_at          │                   │
└─────────────────────┘                   │
                                          │
                                          ▼
                           ┌─────────────────────────────┐
                           │     refresh_tokens          │
                           ├─────────────────────────────┤
                           │ id (PK) UUID                │
                           │ user_id (FK) UUID           │
                           │ token_hash VARCHAR(255)     │
                           │ expires_at TIMESTAMP        │
                           │ created_at TIMESTAMP        │
                           │ revoked_at TIMESTAMP        │
                           └─────────────────────────────┘
```

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'MEDIUM' 
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    due_date TIMESTAMP WITH TIME ZONE,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_user_completed ON todos(user_id, completed);
CREATE INDEX idx_todos_due_date ON todos(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
CREATE INDEX idx_todos_tags ON todos USING GIN(tags);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token_hash);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todos_updated_at BEFORE UPDATE ON todos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Data Types

| Entity | Field | Type | Constraints |
|--------|-------|------|-------------|
| **User** | id | UUID | PRIMARY KEY |
| | email | VARCHAR(255) | UNIQUE, NOT NULL |
| | password_hash | VARCHAR(255) | NOT NULL |
| | name | VARCHAR(100) | NOT NULL |
| | created_at | TIMESTAMP | DEFAULT NOW() |
| **Todo** | id | UUID | PRIMARY KEY |
| | user_id | UUID | FK → users(id) |
| | title | VARCHAR(255) | NOT NULL |
| | priority | VARCHAR(20) | CHECK IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT') |
| | completed | BOOLEAN | DEFAULT FALSE |
| | tags | TEXT[] | Array of tags |

---

## Security Considerations

### Authentication Architecture

#### JWT Token Flow

```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ Client  │────▶│ Auth Server │────▶│ Database│
└─────────┘     └─────────────┘     └─────────┘
     │                  │                  │
     │  1. POST /login  │                  │
     │─────────────────▶│                  │
     │                  │  2. Validate     │
     │                  │─────────────────▶│
     │                  │◀─────────────────│
     │                  │  3. Generate     │
     │                  │     Tokens       │
     │  4. Return       │                  │
     │     {access,     │                  │
     │      refresh}    │                  │
     │◀─────────────────│                  │
     │                  │                  │
     │  5. Use access   │                  │
     │     token in     │                  │
     │     API calls    │                  │
     │                  │                  │
     │  6. Token expired│                  │
     │     401 response │                  │
     │◀─────────────────│                  │
     │                  │                  │
     │  7. POST /refresh│                  │
     │     with refresh │                  │
     │     token        │                  │
     │─────────────────▶│                  │
     │                  │  8. Validate &   │
     │                  │     rotate       │
     │  9. New tokens   │                  │
     │◀─────────────────│                  │
```

#### Token Configuration

| Token Type | Expiration | Storage | Usage |
|------------|------------|---------|-------|
| **Access Token** | 15 minutes | Memory | API authentication |
| **Refresh Token** | 7 days | httpOnly cookie | Token rotation |

### Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                       │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Transport Security                             │
│  ├── HTTPS everywhere (TLS 1.2+)                        │
│  ├── HSTS headers                                       │
│  └── Secure cookie flags                                │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Application Security                           │
│  ├── JWT authentication                                 │
│  ├── Input validation (Zod)                             │
│  ├── Rate limiting                                      │
│  └── CORS configuration                                 │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Data Security                                  │
│  ├── Password hashing (bcrypt, 12 rounds)               │
│  ├── SQL injection prevention (parameterized queries)   │
│  ├── XSS prevention (input sanitization)                │
│  └── Per-user data isolation                            │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Infrastructure Security                        │
│  ├── Container security (non-root user)                 │
│  ├── Secrets management                                 │
│  ├── Network policies                                   │
│  └── Security headers (Helmet)                          │
└─────────────────────────────────────────────────────────┘
```

### OWASP Top 10 Mitigations

| Risk | Mitigation |
|------|------------|
| **Broken Access Control** | JWT validation, per-user data filtering, role-based access |
| **Cryptographic Failures** | bcrypt password hashing, JWT secrets in env vars, HTTPS only |
| **Injection** | Parameterized queries via ORM, input validation |
| **Insecure Design** | Rate limiting, request size limits, pagination |
| **Security Misconfiguration** | Secure headers, minimal container permissions, no debug in prod |
| **Vulnerable Components** | Dependency scanning, regular updates |
| **Auth Failures** | Strong password policy, token expiration, brute-force protection |
| **Data Integrity** | CSRF tokens, SameSite cookies |
| **Logging Failures** | Structured logging, no sensitive data in logs |
| **SSRF** | URL validation, network segmentation |

### Security Headers

```javascript
// Helmet.js configuration
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

---

## Deployment Guide

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          CDN (CloudFront/Cloudflare)            │
│                    Static Assets + DDoS Protection              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer (ALB/NLB)                  │
│                    SSL Termination + Health Checks              │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   API Server 1  │ │   API Server 2  │ │   API Server N  │
│   (Node.js)     │ │   (Node.js)     │ │   (Node.js)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cache Layer (Redis Cluster)                    │
│              Sessions + Rate Limiting + Real-time                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Primary Database (PostgreSQL RDS/Aurora)            │
│              ┌─────────────────────────────────┐                 │
│              │     Read Replicas (2-3x)        │                 │
│              └─────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

### Containerization

#### Dockerfile

```dockerfile
# Multi-stage build for production
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app
ENV NODE_ENV=production

# Security: Run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

USER nodejs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

CMD ["node", "dist/main.js"]
```

#### Docker Compose (Development)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/todoapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=todoapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
      - name: api
        image: todoapp/api:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: JWT_ACCESS_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-access-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: todo-api-service
spec:
  selector:
    app: todo-api
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-api-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.todoapp.com
    secretName: todo-api-tls
  rules:
  - host: api.todoapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-api-service
            port:
              number: 80
```

### Cloud Deployment Options

#### Option 1: AWS (Recommended)

| Service | Purpose | Est. Cost |
|---------|---------|-----------|
| ECS Fargate / EKS | Container orchestration | $30-100/mo |
| RDS PostgreSQL | Managed database | $15-50/mo |
| ElastiCache Redis | Managed cache | $15-30/mo |
| Application Load Balancer | Traffic distribution | $20-30/mo |
| CloudFront | CDN + SSL | $5-20/mo |
| Secrets Manager | Secure secrets | $0.40/secret/mo |
| **Total** | | **$85-230/mo** |

#### Option 2: Google Cloud Platform

| Service | Purpose | Est. Cost |
|---------|---------|-----------|
| Cloud Run | Serverless containers | Pay-per-use |
| Cloud SQL | Managed PostgreSQL | $15-50/mo |
| Memorystore | Managed Redis | $15-30/mo |
| Cloud Load Balancing | Traffic distribution | $18/mo |
| Cloud CDN | CDN + SSL | $5-20/mo |

#### Option 3: Simple PaaS (Railway/Render/Fly.io)

Best for MVP and quick deployment:

```yaml
# railway.yaml
build:
  builder: NIXPACKS

deploy:
  startCommand: npm start
  healthcheckPath: /health
  healthcheckTimeout: 100
  restartPolicyType: ON_FAILURE
  restartPolicyMaxRetries: 3
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - run: npm run lint
    - run: npm run test:coverage

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker image
      run: |
        docker build -t todoapp/api:${{ github.sha }} .
        docker push todoapp/api:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/todo-api api=todoapp/api:${{ github.sha }}
        kubectl rollout status deployment/todo-api
```

### Environment Configuration

| Environment | Database | Redis | Auth Secrets | CORS Origins |
|-------------|----------|-------|--------------|--------------|
| **Development** | localhost:5432 | localhost:6379 | dev secrets | localhost:5173 |
| **Staging** | Staging RDS | ElastiCache | staging secrets | *.staging.todoapp.com |
| **Production** | Production RDS | ElastiCache | production secrets | todoapp.com |

### Health Checks & Monitoring

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /health` | Liveness probe | `200 OK` |
| `GET /ready` | Readiness probe | `200 OK` (checks DB/Redis) |
| `GET /metrics` | Prometheus metrics | Metrics data |

---

## Technology Stack Summary

### Complete Stack Overview

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | | | |
| Framework | React | 18.x | UI Library |
| Language | TypeScript | 5.x | Type Safety |
| Build Tool | Vite | 5.x | Development & Bundling |
| State (Client) | Zustand | 4.x | Client State |
| State (Server) | TanStack Query | 5.x | Server State |
| Styling | Tailwind CSS | 3.x | CSS Framework |
| Components | shadcn/ui | latest | UI Components |
| Forms | React Hook Form + Zod | latest | Form Handling |
| Routing | React Router | 6.x | Client Routing |
| Icons | Lucide React | latest | Icon Library |
| **Backend** | | | |
| Runtime | Node.js | 20.x | JavaScript Runtime |
| Framework | Express.js / Fastify | 4.x / 4.x | Web Framework |
| ORM | Prisma | 5.x | Database ORM |
| Validation | Zod | 3.x | Schema Validation |
| Authentication | JWT + bcrypt | latest | Auth & Security |
| **Database** | | | |
| Primary DB | PostgreSQL | 16.x | Relational Database |
| Cache | Redis | 7.x | In-Memory Cache |
| **DevOps** | | | |
| Container | Docker | latest | Containerization |
| Orchestration | Kubernetes | 1.28+ | Container Management |
| CI/CD | GitHub Actions | latest | Automation |
| Monitoring | Prometheus + Grafana | latest | Observability |

### Dependencies Summary

#### Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.8.0",
    "tailwindcss": "^3.3.6",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.2",
    "date-fns": "^2.30.0",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@types/react": "^18.2.0",
    "vitest": "latest",
    "@testing-library/react": "latest"
  }
}
```

#### Backend Dependencies

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "@prisma/client": "^5.0.0",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0",
    "zod": "^3.22.0",
    "helmet": "^7.0.0",
    "cors": "^2.8.5",
    "express-rate-limit": "^7.0.0",
    "redis": "^4.6.0",
    "dotenv": "^16.3.0"
  },
  "devDependencies": {
    "prisma": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "@types/jsonwebtoken": "^9.0.0",
    "@types/bcrypt": "^5.0.0",
    "typescript": "^5.3.0",
    "vitest": "latest",
    "supertest": "latest"
  }
}
```

### Architecture Decision Records

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **React over Vue/Angular** | React | Larger ecosystem, better job market, excellent TypeScript support |
| **Zustand over Redux** | Zustand | Less boilerplate, smaller bundle, easier to learn |
| **PostgreSQL over MongoDB** | PostgreSQL | Better data integrity, ACID compliance, powerful queries |
| **Express over Fastify** | Express/Fastify | Express for familiarity, Fastify for performance |
| **Docker + K8s over Serverless** | Containers | Better control, predictable costs, easier local development |
| **REST over GraphQL** | REST | Simpler caching, better tooling, sufficient for todo app |

---

## Appendix

### A. API Endpoint Summary

| Resource | Endpoint | Methods |
|----------|----------|---------|
| **Authentication** | `/auth/*` | POST |
| **Todos** | `/todos` | GET, POST |
| **Todo** | `/todos/:id` | GET, PUT, PATCH, DELETE |
| **User** | `/users/me` | GET, PUT, DELETE |
| **Stats** | `/users/me/stats` | GET |

### B. Database Schema Summary

| Table | Records | Primary Key | Foreign Keys |
|-------|---------|-------------|--------------|
| `users` | ~100K | `id` (UUID) | - |
| `todos` | ~1M | `id` (UUID) | `user_id` → users |
| `refresh_tokens` | ~200K | `id` (UUID) | `user_id` → users |
| `password_reset_tokens` | ~10K | `id` (UUID) | `user_id` → users |

### C. Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200ms |
| Page Load Time | < 2s |
| Time to Interactive | < 3s |
| Lighthouse Score | > 90 |
| Uptime SLA | 99.9% |

---

*Document generated for Todo App Web Architecture*  
*Last updated: 2026-03-20*
