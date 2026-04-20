# Todo App Backend Architecture

## Executive Summary

This document provides a complete backend architecture design for a production-ready Todo application, including REST API design, database schema comparison, JWT authentication with refresh tokens, and deployment strategies.

---

## 1. REST API Endpoints

### 1.1 Framework Comparison: Express vs Fastify

| Feature | Express.js | Fastify |
|---------|-----------|---------|
| **Performance** | Good (30k+ req/s) | Excellent (70k+ req/s) |
| **Startup Time** | ~50ms | ~5ms |
| **Schema Validation** | Manual (Joi/Yup) | Built-in |
| **TypeScript Support** | Requires setup | Native |
| **Ecosystem** | Massive | Growing |
| **Learning Curve** | Low | Low-Medium |

**Recommendation:** Use Fastify for new projects requiring high performance; Express for rapid prototyping with extensive middleware needs.

### 1.2 API Endpoints Design

#### Authentication Endpoints

```
POST   /api/v1/auth/register      # User registration
POST   /api/v1/auth/login         # User login
POST   /api/v1/auth/refresh       # Refresh access token
POST   /api/v1/auth/logout        # User logout
POST   /api/v1/auth/forgot-password  # Request password reset
POST   /api/v1/auth/reset-password   # Confirm password reset
```

#### Todo Endpoints

```
GET    /api/v1/todos              # List all todos (with pagination)
POST   /api/v1/todos              # Create new todo
GET    /api/v1/todos/:id          # Get specific todo
PUT    /api/v1/todos/:id          # Update todo
DELETE /api/v1/todos/:id          # Delete todo
PATCH  /api/v1/todos/:id/complete # Mark as complete/incomplete
GET    /api/v1/todos/search       # Search todos
```

#### User Endpoints

```
GET    /api/v1/users/me           # Get current user profile
PUT    /api/v1/users/me           # Update user profile
DELETE /api/v1/users/me           # Delete account
```

### 1.3 Fastify Implementation

```typescript
// src/server.ts
import Fastify from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import cookie from '@fastify/cookie';
import { todoRoutes } from './routes/todos';
import { authRoutes } from './routes/auth';
import { userRoutes } from './routes/users';

const app = Fastify({
  logger: true,
  pluginTimeout: 10000,
});

// Plugins
await app.register(cors, {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
});

await app.register(cookie);

await app.register(jwt, {
  secret: process.env.JWT_SECRET!,
  cookie: {
    cookieName: 'refreshToken',
    signed: false,
  },
});

// Decorators
app.decorate('authenticate', async (request: FastifyRequest, reply: FastifyReply) => {
  try {
    await request.jwtVerify();
  } catch (err) {
    reply.send(err);
  }
});

// Routes
await app.register(authRoutes, { prefix: '/api/v1/auth' });
await app.register(todoRoutes, { prefix: '/api/v1/todos' });
await app.register(userRoutes, { prefix: '/api/v1/users' });

// Health check
app.get('/health', async () => ({ status: 'ok', timestamp: new Date().toISOString() }));

// Start server
const start = async () => {
  try {
    await app.listen({ port: parseInt(process.env.PORT || '3000'), host: '0.0.0.0' });
    app.log.info(`Server listening on ${app.server.address()}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
```

```typescript
// src/routes/todos.ts
import { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { z } from 'zod';

const createTodoSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  dueDate: z.string().datetime().optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  tags: z.array(z.string()).optional(),
});

const updateTodoSchema = createTodoSchema.partial();

const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  status: z.enum(['all', 'active', 'completed']).default('all'),
  priority: z.enum(['low', 'medium', 'high']).optional(),
  search: z.string().optional(),
  sortBy: z.enum(['createdAt', 'dueDate', 'priority']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

export async function todoRoutes(app: FastifyInstance, options: FastifyPluginOptions) {
  // List todos with pagination and filtering
  app.get('/', {
    preHandler: [app.authenticate],
    schema: {
      querystring: querySchema,
    },
  }, async (request, reply) => {
    const userId = request.user.id;
    const { page, limit, status, priority, search, sortBy, sortOrder } = request.query;
    
    // Implementation with repository pattern
    const todos = await app.todoRepository.findMany({
      userId,
      page,
      limit,
      status,
      priority,
      search,
      sortBy,
      sortOrder,
    });
    
    return { todos, pagination: { page, limit, total: todos.total } };
  });

  // Create todo
  app.post('/', {
    preHandler: [app.authenticate],
    schema: {
      body: createTodoSchema,
    },
  }, async (request, reply) => {
    const userId = request.user.id;
    const todo = await app.todoRepository.create({
      ...request.body,
      userId,
    });
    reply.code(201).send(todo);
  });

  // Get specific todo
  app.get('/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const userId = request.user.id;
    
    const todo = await app.todoRepository.findById(id, userId);
    if (!todo) {
      return reply.code(404).send({ error: 'Todo not found' });
    }
    return todo;
  });

  // Update todo
  app.put('/:id', {
    preHandler: [app.authenticate],
    schema: {
      body: updateTodoSchema,
    },
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const userId = request.user.id;
    
    const todo = await app.todoRepository.update(id, userId, request.body);
    if (!todo) {
      return reply.code(404).send({ error: 'Todo not found' });
    }
    return todo;
  });

  // Delete todo
  app.delete('/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const userId = request.user.id;
    
    await app.todoRepository.delete(id, userId);
    reply.code(204).send();
  });

  // Toggle completion status
  app.patch('/:id/complete', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const userId = request.user.id;
    
    const todo = await app.todoRepository.toggleComplete(id, userId);
    if (!todo) {
      return reply.code(404).send({ error: 'Todo not found' });
    }
    return todo;
  });
}
```

---

## 2. Database Schema Design

### 2.1 PostgreSQL vs MongoDB Comparison

| Aspect | PostgreSQL | MongoDB |
|--------|-----------|---------|
| **Data Model** | Relational (tables, rows) | Document (JSON-like) |
| **Schema** | Strict, enforced | Flexible, optional |
| **ACID** | Full ACID compliance | Multi-document ACID (v4.0+) |
| **Joins** | Native support | Limited ($lookup) |
| **Scaling** | Vertical + read replicas | Horizontal sharding |
| **Use Case** | Complex queries, transactions | Rapid iteration, unstructured data |
| **Todo App Fit** | Excellent | Good |

### 2.2 PostgreSQL Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    replaced_by_token UUID REFERENCES refresh_tokens(id),
    device_info VARCHAR(500),
    ip_address INET
);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Todo-Tag junction table
CREATE TABLE todo_tags (
    todo_id UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (todo_id, tag_id)
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_user_status ON todos(user_id, status);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);

-- Full-text search index
CREATE INDEX idx_todos_search ON todos 
    USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')));

-- Trigger for updated_at
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

### 2.3 MongoDB Schema

```javascript
// models/User.js
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
    index: true
  },
  passwordHash: {
    type: String,
    required: true
  },
  profile: {
    firstName: String,
    lastName: String,
    avatarUrl: String
  },
  emailVerified: {
    type: Boolean,
    default: false
  },
  isActive: {
    type: Boolean,
    default: true
  },
  settings: {
    theme: { type: String, default: 'light' },
    timezone: { type: String, default: 'UTC' },
    defaultView: { type: String, default: 'list' },
    notifications: {
      email: { type: Boolean, default: true },
      push: { type: Boolean, default: false },
      dueDateReminder: { type: Number, default: 24 } // hours before
    }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Compound index for queries
userSchema.index({ email: 1, isActive: 1 });

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.profile.firstName || ''} ${this.profile.lastName || ''}`.trim();
});

// models/RefreshToken.js
const refreshTokenSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  tokenHash: {
    type: String,
    required: true,
    index: true
  },
  expiresAt: {
    type: Date,
    required: true
  },
  revokedAt: Date,
  replacedByToken: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RefreshToken'
  },
  metadata: {
    deviceInfo: String,
    ipAddress: String,
    userAgent: String
  }
}, {
  timestamps: true
});

// TTL index for automatic cleanup
refreshTokenSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// models/Todo.js
const todoSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  title: {
    type: String,
    required: true,
    trim: true,
    maxlength: 200
  },
  description: {
    type: String,
    trim: true,
    maxlength: 5000
  },
  status: {
    type: String,
    enum: ['active', 'completed', 'archived'],
    default: 'active',
    index: true
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high'],
    default: 'medium'
  },
  dueDate: Date,
  completedAt: Date,
  tags: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Tag'
  }],
  subtasks: [{
    title: { type: String, required: true },
    completed: { type: Boolean, default: false },
    completedAt: Date
  }],
  attachments: [{
    filename: String,
    url: String,
    mimeType: String,
    size: Number,
    uploadedAt: { type: Date, default: Date.now }
  }],
  order: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// Compound indexes for common queries
todoSchema.index({ userId: 1, status: 1, createdAt: -1 });
todoSchema.index({ userId: 1, dueDate: 1 });
todoSchema.index({ userId: 1, priority: 1 });

// Text index for search
todoSchema.index({ title: 'text', description: 'text' });

// models/Tag.js
const tagSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  color: {
    type: String,
    default: '#3B82F6',
    match: /^#[0-9A-Fa-f]{6}$/
  }
}, {
  timestamps: true
});

tagSchema.index({ userId: 1, name: 1 }, { unique: true });
```

---

## 3. JWT Authentication with Refresh Tokens

### 3.1 Token Strategy

| Token Type | Duration | Storage | Purpose |
|------------|----------|---------|---------|
| **Access Token** | 15 minutes | Memory only | API authorization |
| **Refresh Token** | 7 days | HttpOnly cookie | Token renewal |

### 3.2 Authentication Flow

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │                    │  DB      │
└────┬─────┘                    └────┬─────┘                    └────┬─────┘
     │                               │                               │
     │ POST /auth/login              │                               │
     │ { email, password }          │                               │
     ├──────────────────────────────►│                               │
     │                               │ Verify credentials            │
     │                               ├──────────────────────────────►│
     │                               │◄──────────────────────────────┤
     │                               │                               │
     │                               │ Generate tokens               │
     │                               │ - Access Token (15min)        │
     │                               │ - Refresh Token (7days)       │
     │                               │                               │
     │                               │ Store refresh token hash      │
     │                               ├──────────────────────────────►│
     │                               │                               │
     │ Set-Cookie: refreshToken=...  │                               │
     │ { accessToken }               │                               │
     │◄──────────────────────────────┤                               │
     │                               │                               │
     │ [API Call with accessToken]   │                               │
     ├──────────────────────────────►│                               │
     │                               │ Validate access token         │
     │ Response                      │                               │
     │◄──────────────────────────────┤                               │
     │                               │                               │
     │ [Access Token Expired]        │                               │
     ├──────────────────────────────►│                               │
     │ 401 Unauthorized              │                               │
     │◄──────────────────────────────┤                               │
     │                               │                               │
     │ POST /auth/refresh            │                               │
     │ Cookie: refreshToken=...     │                               │
     ├──────────────────────────────►│                               │
     │                               │ Verify refresh token          │
     │                               ├──────────────────────────────►│
     │                               │◄──────────────────────────────┤
     │                               │                               │
     │ Set-Cookie: new refreshToken │                               │
     │ { newAccessToken }            │                               │
     │◄──────────────────────────────┤                               │
     │                               │                               │
```

### 3.3 Implementation

```typescript
// src/services/auth.ts
import crypto from 'crypto';
import bcrypt from 'bcrypt';
import { FastifyInstance, FastifyRequest } from 'fastify';

const SALT_ROUNDS = 12;
const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY_DAYS = 7;

// Types
interface TokenPayload {
  id: string;
  email: string;
  type: 'access' | 'refresh';
}

interface RefreshTokenData {
  userId: string;
  tokenHash: string;
  expiresAt: Date;
  deviceInfo?: string;
  ipAddress?: string;
}

// Hash token for storage (prevent DB leak from being usable)
function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}

// Generate cryptographically secure random token
function generateSecureToken(): string {
  return crypto.randomBytes(64).toString('base64url');
}

export class AuthService {
  constructor(
    private app: FastifyInstance,
    private db: any // Database repository
  ) {}

  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, SALT_ROUNDS);
  }

  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  generateAccessToken(userId: string, email: string): string {
    return this.app.jwt.sign(
      { id: userId, email, type: 'access' },
      { expiresIn: ACCESS_TOKEN_EXPIRY }
    );
  }

  async createRefreshToken(
    userId: string,
    deviceInfo?: string,
    ipAddress?: string
  ): Promise<{ token: string; expiresAt: Date }> {
    const token = generateSecureToken();
    const tokenHash = hashToken(token);
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + REFRESH_TOKEN_EXPIRY_DAYS);

    await this.db.refreshTokens.create({
      userId,
      tokenHash,
      expiresAt,
      deviceInfo,
      ipAddress,
    });

    return { token, expiresAt };
  }

  async rotateRefreshToken(
    oldToken: string,
    deviceInfo?: string,
    ipAddress?: string
  ): Promise<{ userId: string; accessToken: string; refreshToken: string } | null> {
    const oldTokenHash = hashToken(oldToken);
    
    // Find and validate the old refresh token
    const storedToken = await this.db.refreshTokens.findByHash(oldTokenHash);
    
    if (!storedToken) {
      return null;
    }

    // Check if token is expired or revoked
    if (storedToken.expiresAt < new Date() || storedToken.revokedAt) {
      // Potential token reuse detected - revoke all user tokens
      if (storedToken.revokedAt) {
        await this.revokeAllUserTokens(storedToken.userId);
        throw new Error('Token reuse detected. All sessions terminated.');
      }
      return null;
    }

    // Revoke the old token
    await this.db.refreshTokens.revoke(oldTokenHash);

    // Generate new tokens
    const user = await this.db.users.findById(storedToken.userId);
    if (!user || !user.isActive) {
      return null;
    }

    const accessToken = this.generateAccessToken(user.id, user.email);
    const { token: newRefreshToken, expiresAt } = await this.createRefreshToken(
      user.id,
      deviceInfo,
      ipAddress
    );

    // Link new token to old one for audit trail
    await this.db.refreshTokens.linkToPrevious(
      hashToken(newRefreshToken),
      storedToken.id
    );

    return {
      userId: user.id,
      accessToken,
      refreshToken: newRefreshToken,
    };
  }

  async revokeToken(tokenHash: string): Promise<void> {
    await this.db.refreshTokens.revoke(tokenHash);
  }

  async revokeAllUserTokens(userId: string): Promise<void> {
    await this.db.refreshTokens.revokeAllForUser(userId);
  }

  async logout(userId: string, tokenHash: string): Promise<void> {
    await this.revokeToken(tokenHash);
    // Optional: Log the logout event for security audit
  }
}
```

```typescript
// src/routes/auth.ts
import { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { z } from 'zod';
import { AuthService } from '../services/auth';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export async function authRoutes(app: FastifyInstance, options: FastifyPluginOptions) {
  const authService = new AuthService(app, app.db);

  // Register
  app.post('/register', {
    schema: { body: registerSchema },
  }, async (request, reply) => {
    const { email, password, firstName, lastName } = request.body;

    // Check if user exists
    const existingUser = await app.db.users.findByEmail(email);
    if (existingUser) {
      return reply.code(409).send({ error: 'Email already registered' });
    }

    // Create user
    const passwordHash = await authService.hashPassword(password);
    const user = await app.db.users.create({
      email: email.toLowerCase(),
      passwordHash,
      profile: { firstName, lastName },
    });

    // Generate tokens
    const accessToken = authService.generateAccessToken(user.id, user.email);
    const { token: refreshToken, expiresAt } = await authService.createRefreshToken(
      user.id,
      request.headers['user-agent'],
      request.ip
    );

    // Set refresh token cookie
    reply.setCookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      expires: expiresAt,
      path: '/api/v1/auth',
    });

    reply.code(201).send({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.profile.firstName,
        lastName: user.profile.lastName,
      },
      accessToken,
    });
  });

  // Login
  app.post('/login', {
    schema: { body: loginSchema },
  }, async (request, reply) => {
    const { email, password } = request.body;

    const user = await app.db.users.findByEmail(email.toLowerCase());
    if (!user) {
      return reply.code(401).send({ error: 'Invalid credentials' });
    }

    const isValidPassword = await authService.verifyPassword(password, user.passwordHash);
    if (!isValidPassword) {
      return reply.code(401).send({ error: 'Invalid credentials' });
    }

    if (!user.isActive) {
      return reply.code(401).send({ error: 'Account deactivated' });
    }

    // Generate tokens
    const accessToken = authService.generateAccessToken(user.id, user.email);
    const { token: refreshToken, expiresAt } = await authService.createRefreshToken(
      user.id,
      request.headers['user-agent'],
      request.ip
    );

    reply.setCookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      expires: expiresAt,
      path: '/api/v1/auth',
    });

    reply.send({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.profile.firstName,
        lastName: user.profile.lastName,
      },
      accessToken,
    });
  });

  // Refresh token
  app.post('/refresh', async (request, reply) => {
    const oldRefreshToken = request.cookies.refreshToken;
    
    if (!oldRefreshToken) {
      return reply.code(401).send({ error: 'No refresh token' });
    }

    try {
      const result = await authService.rotateRefreshToken(
        oldRefreshToken,
        request.headers['user-agent'],
        request.ip
      );

      if (!result) {
        return reply.code(401).send({ error: 'Invalid refresh token' });
      }

      const { accessToken, refreshToken: newRefreshToken } = result;
      
      reply.setCookie('refreshToken', newRefreshToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        path: '/api/v1/auth',
      });

      reply.send({ accessToken });
    } catch (err) {
      // Token reuse detected
      reply.clearCookie('refreshToken', { path: '/api/v1/auth' });
      return reply.code(401).send({ error: 'Session terminated for security' });
    }
  });

  // Logout
  app.post('/logout', { preHandler: [app.authenticate] }, async (request, reply) => {
    const refreshToken = request.cookies.refreshToken;
    
    if (refreshToken) {
      await authService.logout(request.user.id, refreshToken);
    }

    reply.clearCookie('refreshToken', { path: '/api/v1/auth' });
    reply.send({ message: 'Logged out successfully' });
  });

  // Logout all sessions
  app.post('/logout-all', { preHandler: [app.authenticate] }, async (request, reply) => {
    await authService.revokeAllUserTokens(request.user.id);
    reply.clearCookie('refreshToken', { path: '/api/v1/auth' });
    reply.send({ message: 'All sessions terminated' });
  });
}
```

### 3.4 Security Considerations

| Threat | Mitigation |
|--------|------------|
| Token theft | Short-lived access tokens, HttpOnly refresh cookies |
| Token replay | Token rotation with family detection |
| XSS | HttpOnly cookies, CSP headers |
| CSRF | SameSite=Strict cookies |
| Brute force | Rate limiting on auth endpoints |
| Database leak | Token hashes stored, not raw tokens |

---

## 4. Deployment Strategy

### 4.1 Docker Configuration

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Production image
FROM node:20-alpine AS production

# Install security updates and dumb-init
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy built application
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# Set environment
ENV NODE_ENV=production
ENV PORT=3000

USER nodejs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

CMD ["dumb-init", "node", "dist/server.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: todo-api
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/todoapp
      - JWT_SECRET=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - todo-network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  db:
    image: postgres:16-alpine
    container_name: todo-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=todoapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - todo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: todo-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - todo-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: todo-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - todo-network

volumes:
  postgres_data:
  redis_data:

networks:
  todo-network:
    driver: bridge
```

```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    upstream api {
        server app:3000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_buffering off;
        }

        # Auth endpoints - stricter rate limiting
        location /api/v1/auth/ {
            limit_req zone=auth burst=3 nodelay;
            
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://api;
            access_log off;
        }
    }
}
```

### 4.2 Kubernetes Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    name: todo-app
```

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
  namespace: todo-app
data:
  NODE_ENV: "production"
  PORT: "3000"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
  namespace: todo-app
type: Opaque
stringData:
  DATABASE_URL: "postgresql://postgres:password@postgres:5432/todoapp"
  JWT_SECRET: "your-super-secret-jwt-key-change-in-production"
  REDIS_URL: "redis://redis:6379"
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
  namespace: todo-app
  labels:
    app: todo-api
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
        image: todo-api:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        envFrom:
        - configMapRef:
            name: todo-config
        - secretRef:
            name: todo-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1001
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - todo-api
              topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: todo-api
  namespace: todo-app
spec:
  type: ClusterIP
  selector:
    app: todo-api
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
```

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: todo-app
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: todoapp
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: todo-app
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.todoapp.com
    secretName: todo-tls
  rules:
  - host: api.todoapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-api
            port:
              number: 80
---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-api-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command:
        - redis-server
        - --appendonly
        - "yes"
        - --maxmemory
        - "256mb"
        - --maxmemory-policy
        - "allkeys-lru"
        resources:
          requests:
            memory: "128Mi"
            cpu: "50m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        volumeMounts:
        - name: redis-data
          mountPath: /data
      volumes:
      - name: redis-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: todo-app
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

### 4.3 Deployment Commands

```bash
# Docker deployment
docker-compose up -d

# Kubernetes deployment
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get all -n todo-app
kubectl logs -n todo-app deployment/todo-api -f
```

---

## 5. Environment Configuration

```bash
# .env.example
# Application
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug

# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todoapp
# Or MongoDB
# DATABASE_URL=mongodb://localhost:27017/todoapp

# Redis (for sessions/cache)
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-super-secret-jwt-key-min-32-characters
JWT_EXPIRES_IN=15m

# Security
BCRYPT_ROUNDS=12
REFRESH_TOKEN_DAYS=7

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

---

## 6. Project Structure

```
todo-backend/
├── src/
│   ├── config/
│   │   ├── database.ts
│   │   ├── redis.ts
│   │   └── env.ts
│   ├── models/
│   │   ├── user.ts
│   │   ├── todo.ts
│   │   ├── tag.ts
│   │   └── refreshToken.ts
│   ├── repositories/
│   │   ├── user.repository.ts
│   │   ├── todo.repository.ts
│   │   └── refreshToken.repository.ts
│   ├── services/
│   │   ├── auth.service.ts
│   │   ├── todo.service.ts
│   │   └── email.service.ts
│   ├── routes/
│   │   ├── auth.ts
│   │   ├── todos.ts
│   │   └── users.ts
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── errorHandler.ts
│   │   └── rateLimiter.ts
│   ├── utils/
│   │   ├── logger.ts
│   │   ├── validators.ts
│   │   └── crypto.ts
│   └── server.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── k8s/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── package.json
└── tsconfig.json
```

---

## 7. Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **API Framework** | Fastify | High performance, built-in validation, native TypeScript |
| **Database** | PostgreSQL | ACID compliance, relational data, complex queries |
| **Alternative DB** | MongoDB | Flexible schema, rapid iteration, horizontal scaling |
| **Authentication** | JWT + Refresh Tokens | Stateless, secure, token rotation |
| **Caching** | Redis | Session storage, rate limiting, performance |
| **Container** | Docker | Consistent environments, easy deployment |
| **Orchestration** | Kubernetes | Auto-scaling, high availability, production-ready |

---

*Document generated following Swarm Solver standards. Model: k2p5 | Agent: backend-architect*
