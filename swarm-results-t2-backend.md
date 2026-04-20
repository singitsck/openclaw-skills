# Todo App Backend Architecture

## Overview

This document outlines a production-ready backend architecture for a modern todo application, designed with scalability, security, and maintainability in mind.

---

## 1. API Endpoints

### REST API Design

Base URL: `https://api.todoapp.com/v1`

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | User login | No |
| POST | `/auth/logout` | User logout | Yes |
| POST | `/auth/refresh` | Refresh access token | Yes (refresh token) |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| GET | `/auth/oauth/:provider` | OAuth login (google, github) | No |
| GET | `/auth/oauth/:provider/callback` | OAuth callback | No |

#### Todo Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/todos` | List all todos (with pagination) | Yes |
| GET | `/todos/:id` | Get single todo | Yes |
| POST | `/todos` | Create new todo | Yes |
| PUT | `/todos/:id` | Update todo (full) | Yes |
| PATCH | `/todos/:id` | Partial update todo | Yes |
| DELETE | `/todos/:id` | Delete todo | Yes |
| PUT | `/todos/:id/complete` | Mark todo as complete | Yes |
| PUT | `/todos/:id/uncomplete` | Mark todo as incomplete | Yes |

#### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/me` | Get current user profile | Yes |
| PUT | `/users/me` | Update user profile | Yes |
| DELETE | `/users/me` | Delete account | Yes |
| GET | `/users/me/stats` | Get todo statistics | Yes |

### GraphQL Schema (Alternative)

```graphql
# Types
type User {
  id: ID!
  email: String!
  name: String!
  avatar: String
  createdAt: DateTime!
  updatedAt: DateTime!
  todos: [Todo!]!
  stats: UserStats!
}

type Todo {
  id: ID!
  title: String!
  description: String
  completed: Boolean!
  priority: Priority!
  dueDate: DateTime
  tags: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  user: User!
}

type UserStats {
  totalTodos: Int!
  completedTodos: Int!
  pendingTodos: Int!
  completionRate: Float!
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  URGENT
}

# Inputs
input CreateTodoInput {
  title: String!
  description: String
  priority: Priority = MEDIUM
  dueDate: DateTime
  tags: [String!]
}

input UpdateTodoInput {
  title: String
  description: String
  priority: Priority
  dueDate: DateTime
  tags: [String!]
  completed: Boolean
}

input PaginationInput {
  page: Int = 1
  limit: Int = 20
}

# Queries
type Query {
  me: User!
  todo(id: ID!): Todo
  todos(
    filter: TodoFilterInput
    sort: TodoSortInput
    pagination: PaginationInput
  ): TodoConnection!
}

input TodoFilterInput {
  completed: Boolean
  priority: Priority
  tags: [String!]
  dueBefore: DateTime
  dueAfter: DateTime
}

input TodoSortInput {
  field: TodoSortField = CREATED_AT
  direction: SortDirection = DESC
}

enum TodoSortField {
  CREATED_AT
  UPDATED_AT
  DUE_DATE
  PRIORITY
  TITLE
}

enum SortDirection {
  ASC
  DESC
}

type TodoConnection {
  edges: [TodoEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type TodoEdge {
  node: Todo!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Mutations
type Mutation {
  # Auth
  register(input: RegisterInput!): AuthPayload!
  login(input: LoginInput!): AuthPayload!
  logout: Boolean!
  refreshToken: AuthPayload!
  
  # Todos
  createTodo(input: CreateTodoInput!): Todo!
  updateTodo(id: ID!, input: UpdateTodoInput!): Todo!
  deleteTodo(id: ID!): Boolean!
  completeTodo(id: ID!): Todo!
  uncompleteTodo(id: ID!): Todo!
  
  # User
  updateProfile(input: UpdateProfileInput!): User!
  deleteAccount: Boolean!
}

input RegisterInput {
  email: String!
  password: String!
  name: String!
}

input LoginInput {
  email: String!
  password: String!
}

input UpdateProfileInput {
  name: String
  avatar: Upload
}

type AuthPayload {
  user: User!
  accessToken: String!
  refreshToken: String!
}

# Subscriptions
type Subscription {
  todoCreated: Todo!
  todoUpdated: Todo!
  todoDeleted: ID!
}
```

---

## 2. Database Schema

### PostgreSQL Schema (Recommended for Relational Data)

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
    priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    due_date TIMESTAMP WITH TIME ZONE,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh tokens table (for JWT rotation)
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

### MongoDB Schema (Alternative for Flexible Document Storage)

```javascript
// User Schema
const userSchema = new Schema({
  email: { type: String, required: true, unique: true },
  passwordHash: { type: String, required: true },
  name: { type: String, required: true },
  avatarUrl: String,
  emailVerified: { type: Boolean, default: false },
  oauthProvider: String,
  oauthId: String,
  settings: {
    theme: { type: String, default: 'light' },
    defaultPriority: { type: String, default: 'MEDIUM' },
    notifications: { type: Boolean, default: true }
  }
}, { timestamps: true });

// Todo Schema
const todoSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  title: { type: String, required: true },
  description: String,
  completed: { type: Boolean, default: false },
  priority: { 
    type: String, 
    enum: ['LOW', 'MEDIUM', 'HIGH', 'URGENT'],
    default: 'MEDIUM'
  },
  dueDate: Date,
  tags: [{ type: String }],
  subtasks: [{
    title: String,
    completed: Boolean
  }],
  attachments: [{
    filename: String,
    url: String,
    size: Number
  }]
}, { 
  timestamps: true,
  toJSON: { virtuals: true }
});

// Compound indexes for MongoDB
todoSchema.index({ userId: 1, completed: 1 });
todoSchema.index({ userId: 1, priority: 1 });
todoSchema.index({ userId: 1, dueDate: 1 });
todoSchema.index({ userId: 1, createdAt: -1 });
todoSchema.index({ tags: 1 });

// Refresh Token Schema
const refreshTokenSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  tokenHash: { type: String, required: true },
  expiresAt: { type: Date, required: true },
  revokedAt: Date
}, { timestamps: true });

refreshTokenSchema.index({ tokenHash: 1 });
refreshTokenSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
```

### Database Choice Recommendation

| Criteria | PostgreSQL | MongoDB |
|----------|------------|---------|
| **Best for** | Structured data, complex queries, ACID transactions | Flexible schema, rapid iteration, unstructured data |
| **Query complexity** | Excellent (JOINs, CTEs, window functions) | Good (aggregation pipeline) |
| **Relationships** | Native support | Manual references |
| **Scaling** | Vertical + read replicas | Horizontal sharding |
| **Todo App Fit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recommendation**: PostgreSQL for production todo apps due to better data integrity and query capabilities.

---

## 3. Authentication Architecture

### JWT-Based Authentication Flow

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

### Token Configuration

```javascript
// Token settings
const AUTH_CONFIG = {
  accessToken: {
    secret: process.env.JWT_ACCESS_SECRET,
    expiresIn: '15m',        // Short-lived
    algorithm: 'HS256'
  },
  refreshToken: {
    secret: process.env.JWT_REFRESH_SECRET,
    expiresIn: '7d',         // Longer-lived
    algorithm: 'HS256'
  }
};

// Token payload structure
interface AccessTokenPayload {
  sub: string;        // user id
  email: string;
  iat: number;        // issued at
  exp: number;        // expiration
  type: 'access';
}

interface RefreshTokenPayload {
  sub: string;        // user id
  jti: string;        // token id for rotation
  iat: number;
  exp: number;
  type: 'refresh';
}
```

### OAuth Integration

```javascript
// Supported OAuth providers
const OAUTH_PROVIDERS = {
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    redirectUri: '/auth/google/callback',
    scope: ['email', 'profile'],
    authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo'
  },
  github: {
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    redirectUri: '/auth/github/callback',
    scope: ['user:email'],
    authorizationUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    userInfoUrl: 'https://api.github.com/user'
  }
};

// OAuth flow handler
async function handleOAuthCallback(provider, code) {
  // 1. Exchange code for access token
  const tokenResponse = await fetch(provider.tokenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: provider.clientId,
      client_secret: provider.clientSecret,
      code,
      grant_type: 'authorization_code',
      redirect_uri: provider.redirectUri
    })
  });
  
  // 2. Fetch user info
  const { access_token } = await tokenResponse.json();
  const userResponse = await fetch(provider.userInfoUrl, {
    headers: { Authorization: `Bearer ${access_token}` }
  });
  const oauthUser = await userResponse.json();
  
  // 3. Find or create user
  let user = await db.users.findByOAuth(provider.name, oauthUser.id);
  if (!user) {
    user = await db.users.create({
      email: oauthUser.email,
      name: oauthUser.name,
      oauthProvider: provider.name,
      oauthId: oauthUser.id,
      avatarUrl: oauthUser.picture || oauthUser.avatar_url
    });
  }
  
  // 4. Generate JWT tokens
  return generateTokens(user);
}
```

### Security Best Practices

```javascript
// Middleware for authentication
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  try {
    const decoded = jwt.verify(token, AUTH_CONFIG.accessToken.secret);
    
    // Additional checks
    if (decoded.type !== 'access') {
      return res.status(401).json({ error: 'Invalid token type' });
    }
    
    req.userId = decoded.sub;
    req.userEmail = decoded.email;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired', code: 'TOKEN_EXPIRED' });
    }
    return res.status(403).json({ error: 'Invalid token' });
  }
}

// Rate limiting for auth endpoints
const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many authentication attempts, please try again later',
  skipSuccessfulRequests: true
});

// Password security
const PASSWORD_CONFIG = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSymbols: true,
  bcryptRounds: 12
};

async function hashPassword(password) {
  return bcrypt.hash(password, PASSWORD_CONFIG.bcryptRounds);
}
```

---

## 4. Deployment Strategy

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

### Containerization (Docker)

```dockerfile
# Dockerfile
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

```yaml
# docker-compose.yml (Development)
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
      - JWT_ACCESS_SECRET=dev-access-secret
      - JWT_REFRESH_SECRET=dev-refresh-secret
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
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
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
        image: todoapp/api:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
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
        - name: JWT_REFRESH_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-refresh-secret
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

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| ECS Fargate / EKS | Container orchestration | $30-100/mo |
| RDS PostgreSQL | Managed database | $15-50/mo |
| ElastiCache Redis | Managed cache | $15-30/mo |
| Application Load Balancer | Traffic distribution | $20-30/mo |
| CloudFront | CDN + SSL | $5-20/mo |
| Secrets Manager | Secure secrets | $0.40/secret/mo |
| **Total** | | **$85-230/mo** |

#### Option 2: Google Cloud Platform

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| Cloud Run | Serverless containers | Pay-per-use |
| Cloud SQL | Managed PostgreSQL | $15-50/mo |
| Memorystore | Managed Redis | $15-30/mo |
| Cloud Load Balancing | Traffic distribution | $18/mo |
| Cloud CDN | CDN + SSL | $5-20/mo |

#### Option 3: Railway / Render / Fly.io (Simple)

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
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - run: npm run lint
    - run: npm run test:coverage
    - run: npm run test:e2e

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker image
      run: |
        docker build -t todoapp/api:${{ github.sha }} .
        docker tag todoapp/api:${{ github.sha }} todoapp/api:latest
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push todoapp/api:${{ github.sha }}
        docker push todoapp/api:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        # Update Kubernetes deployment
        kubectl set image deployment/todo-api api=todoapp/api:${{ github.sha }}
        kubectl rollout status deployment/todo-api
```

### Environment Configuration

```javascript
// config/environments.js
const environments = {
  development: {
    port: 3000,
    database: {
      url: process.env.DATABASE_URL || 'postgresql://localhost:5432/todoapp_dev'
    },
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    },
    jwt: {
      accessSecret: 'dev-access-secret-change-in-production',
      refreshSecret: 'dev-refresh-secret-change-in-production'
    },
    cors: {
      origin: ['http://localhost:3000', 'http://localhost:5173']
    },
    logging: 'debug'
  },
  
  production: {
    port: process.env.PORT || 3000,
    database: {
      url: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false }
    },
    redis: {
      url: process.env.REDIS_URL,
      tls: process.env.REDIS_TLS === 'true'
    },
    jwt: {
      accessSecret: process.env.JWT_ACCESS_SECRET,
      refreshSecret: process.env.JWT_REFRESH_SECRET
    },
    cors: {
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['https://todoapp.com']
    },
    logging: 'error',
    sentry: {
      dsn: process.env.SENTRY_DSN
    }
  }
};

module.exports = environments[process.env.NODE_ENV || 'development'];
```

### Monitoring & Observability

```javascript
// monitoring setup
const monitoring = {
  // Application metrics
  metrics: {
    requestDuration: new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code']
    }),
    requestCount: new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code']
    }),
    activeConnections: new Gauge({
      name: 'active_connections',
      help: 'Number of active connections'
    })
  },
  
  // Health checks
  healthChecks: {
    database: async () => {
      await db.query('SELECT 1');
      return 'healthy';
    },
    redis: async () => {
      await redis.ping();
      return 'healthy';
    },
    disk: async () => {
      const stats = await checkDiskSpace('/');
      return stats.free > 1024 * 1024 * 1024 ? 'healthy' : 'warning';
    }
  },
  
  // Alerting rules
  alerts: {
    highErrorRate: {
      condition: 'rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05',
      severity: 'critical'
    },
    highLatency: {
      condition: 'histogram_quantile(0.95, http_request_duration_seconds) > 1',
      severity: 'warning'
    },
    databaseConnections: {
      condition: 'pg_stat_activity_count > 80',
      severity: 'warning'
    }
  }
};
```

---

## 5. Technology Stack Recommendations

| Layer | Technology | Alternative |
|-------|------------|-------------|
| **Runtime** | Node.js 20+ | Deno, Bun |
| **Framework** | Express.js / Fastify | NestJS, Hono |
| **Database** | PostgreSQL 16 | MySQL, MongoDB |
| **Cache** | Redis 7 | Memcached |
| **ORM** | Prisma | Drizzle, TypeORM |
| **Auth** | JWT + bcrypt | Auth0, Clerk |
| **Validation** | Zod | Joi, Yup |
| **Testing** | Vitest + Supertest | Jest, Mocha |
| **Documentation** | OpenAPI (Swagger) | Postman |

---

## 6. API Response Standards

### Success Response Format

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

### Error Response Format

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

---

## Summary

This architecture provides:

- **Scalable API**: RESTful + GraphQL options with clear endpoint design
- **Robust Data Layer**: PostgreSQL schema with proper indexing and relations
- **Secure Authentication**: JWT with refresh token rotation and OAuth support
- **Production-Ready Deployment**: Containerized with Kubernetes and cloud-native options
- **Observability**: Health checks, metrics, and structured logging

The design prioritizes security, scalability, and developer experience while remaining simple enough for an MVP and robust enough for production workloads.
