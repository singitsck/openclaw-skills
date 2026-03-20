# Todo Application Research — Requirements Summary

**Research Date:** 2026-03-20  
**Task:** Research online todo applications for feature, tech stack, architecture, and security requirements

---

## 1. Common Features (CRUD, Filtering, Sorting)

### Core CRUD Operations
- **Create** — Add new tasks with title, description, due date, priority, tags
- **Read** — List all tasks, view single task details
- **Update** — Edit task title/content, toggle completion status, change priority/dates
- **Delete** — Remove individual tasks or bulk delete completed tasks

### Filtering Capabilities
- **By status** — All / Active / Completed (most common)
- **By priority** — High, Medium, Low
- **By tags/categories** — User-defined labels with colors
- **By due date** — Overdue, Today, This Week, Custom range
- **Search** — Full-text search on title + details

### Sorting Options
- Created date (asc/desc)
- Due date (with nulls last handling)
- Priority level
- Alphabetical order
- Updated timestamp

### Additional Features (Production Apps)
- Drag-and-drop / Kanban board (columns: To Do / In Progress / Done)
- Recurring tasks / reminders
- Sub-tasks / check-list items
- Assign tasks to projects/lists
- File attachments
- Collaboration / shared lists
- Activity/history log
- Pagination for large datasets

---

## 2. Popular Tech Stacks

### MERN Stack (MongoDB, Express, React, Node.js)
- Most popular for learning and prototyping
- JSON everywhere, unified JavaScript/TypeScript
- Example: Next.js + Express.js + MySQL (TypeScript full-stack)

### FARM Stack (FastAPI, React, MongoDB)
- FastAPI for high-performance async Python backend
- Popular for Python shops

### FastAPI + SQLAlchemy + SQLite/PostgreSQL
- Production-ready REST APIs
- Built-in Swagger/OpenAPI documentation
- JWT auth with access + refresh tokens
- Per-user data isolation

### Laravel + Inertia.js + Vue 3
- Server-side routing with SPA-like UX
- Kanban board, tags, filters, sorting
- Eloquent ORM

### Next.js Full-Stack (SSR + API Routes)
- Single framework covers frontend + backend
- SQLite3 for data persistence
- Server-Side Rendering + WebSockets support

### Django REST Framework + React
- Enterprise-grade with comprehensive auth
- Email verification support
- 336+ test scenarios in one example project

### Frontend-Only (localStorage)
- React + Hooks + localStorage persistence
- Filter: All / Active / Completed
- Toggle completion, inline edit, delete

### Mobile-First
- React Native + Expo for cross-platform mobile
- Supabase for backend-as-a-service

---

## 3. Architecture Patterns

### Clean Architecture / Layered Architecture
- **Presentation Layer** — React/Vue UI components
- **Business Logic Layer** — Services / Use Cases
- **Data Access Layer** — Repositories / ORM
- **Database** — SQLite / PostgreSQL / MongoDB

### RESTful API Design
Standard endpoints per resource:
```
POST   /todos          — Create task
GET    /todos          — List tasks (with query params for filter/sort/paginate)
GET    /todos/{id}     — Get single task
PUT    /todos/{id}     — Update task
DELETE /todos/{id}     — Delete task
POST   /auth/register  — User registration
POST   /auth/login     — User login
POST   /auth/refresh   — Refresh token
```

### Authentication Patterns
- **JWT Access Tokens** (short-lived, 15-30 min)
- **JWT Refresh Tokens** (long-lived, stored in httpOnly cookie)
- **Per-user data isolation** — Users can only access their own tasks
- Role-Based Access Control (RBAC) for multi-user features

### State Management
- **React Context + useReducer** for simple apps
- **Redux / Redux Toolkit** for complex state
- **TanStack Query (React Query)** for server state + caching

### Real-Time Features
- WebSockets for live updates (collaborative todo lists)
- Server-Sent Events for notifications

---

## 4. Security Considerations

### Authentication & Authorization
- **JWT tokens** with short-lived access tokens + rotating refresh tokens
- **Password hashing** — bcrypt / Argon2 (never plain text)
- **httpOnly cookies** for refresh tokens (XSS protection)
- **CORS** configuration restricting allowed origins
- **Rate limiting** on auth endpoints (brute-force protection)
- Per-user task isolation at API layer (always filter by authenticated user ID)

### Input Validation
- **Request validation** — Pydantic (FastAPI), Zod (React), express-validator
- **SQL injection prevention** — Parameterized queries / ORM
- **XSS prevention** — Sanitize user input, Content-Security-Policy headers
- **CSRF protection** — SameSite cookies, CSRF tokens

### Data Protection
- **HTTPS everywhere** — TLS 1.2+ required
- **Database encryption** at rest (especially for cloud deployments)
- **Environment variables** for secrets (never hardcode API keys / DB credentials)
- **Secure file uploads** if attachments supported (type validation, size limits, virus scan)

### API Security
- **Pagination** to prevent large response DoS
- **Request size limits** to prevent payload overflow
- **Graceful error handling** — Never leak stack traces in production
- **Logging + monitoring** — Detect anomalous access patterns

### Specific OWASP Considerations
- Broken Access Control — Users must not read/write other users' tasks
- Broken Authentication — Enforce strong passwords, token expiration
- Sensitive Data Exposure — Encrypt PII, use HTTPS
- Security Misconfiguration — Disable debug mode in production, secure headers

---

## Summary Table

| Category | Common Choices |
|----------|---------------|
| Frontend | React, Vue 3, Next.js, React Native |
| Backend | Node.js/Express, FastAPI, Laravel, Django REST |
| Database | MongoDB, PostgreSQL, SQLite, MySQL |
| Auth | JWT (access + refresh), bcrypt, httpOnly cookies |
| ORM | SQLAlchemy, Mongoose, Prisma, Eloquent |
| State (Frontend) | React Context, Redux Toolkit, TanStack Query |
| API Style | RESTful JSON, OpenAPI/Swagger docs |
| Deployment | Docker, Vercel, Railway, cloud VMs |

---

*Research compiled from analysis of 20+ open-source todo projects and production-ready tutorials (2024-2026).*
