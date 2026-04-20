# React Frontend Architecture - Todo App

## Overview

This document outlines a comprehensive, production-ready frontend architecture for a modern Todo application, built with React 18+, TypeScript, and industry best practices.

---

## 1. Component Architecture

### Project Structure

```
src/
├── components/
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── checkbox.tsx
│   │   └── card.tsx
│   ├── todo/
│   │   ├── TodoItem.tsx       # Individual todo item
│   │   ├── TodoList.tsx       # List container
│   │   ├── TodoForm.tsx       # Add/edit form
│   │   ├── TodoFilter.tsx     # Filter controls
│   │   └── TodoStats.tsx      # Statistics display
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── MainContent.tsx
├── hooks/
│   ├── useTodos.ts            # Todo CRUD operations
│   ├── useFilter.ts           # Filter state management
│   └── useLocalStorage.ts     # Persistence hook
├── stores/
│   └── todoStore.ts           # Zustand store
├── types/
│   └── todo.ts                # TypeScript interfaces
├── lib/
│   ├── utils.ts               # Utility functions
│   └── api.ts                 # API client
├── pages/
│   ├── HomePage.tsx
│   ├── TodoPage.tsx
│   └── SettingsPage.tsx
└── App.tsx
```

### TypeScript Interfaces

```typescript
// src/types/todo.ts

export enum TodoPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export enum TodoStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: TodoStatus;
  priority: TodoPriority;
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
}

export interface TodoFilter {
  status?: TodoStatus | 'all';
  priority?: TodoPriority | 'all';
  searchQuery?: string;
  tags?: string[];
}

export interface TodoFormData {
  title: string;
  description?: string;
  priority: TodoPriority;
  dueDate?: Date;
  tags: string[];
}
```

### Component Examples

```tsx
// src/components/todo/TodoItem.tsx
import { useState } from 'react';
import { Todo, TodoStatus } from '@/types/todo';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Card } from '@/components/ui/card';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: Todo) => void;
}

export function TodoItem({ todo, onToggle, onDelete, onEdit }: TodoItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  const priorityColors = {
    low: 'border-l-green-500',
    medium: 'border-l-yellow-500',
    high: 'border-l-red-500',
  };

  return (
    <Card
      className={cn(
        'flex items-center gap-3 p-4 border-l-4 transition-all',
        priorityColors[todo.priority],
        todo.status === TodoStatus.COMPLETED && 'opacity-60'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Checkbox
        checked={todo.status === TodoStatus.COMPLETED}
        onCheckedChange={() => onToggle(todo.id)}
      />
      
      <div className="flex-1 min-w-0">
        <p className={cn(
          'font-medium truncate',
          todo.status === TodoStatus.COMPLETED && 'line-through text-muted-foreground'
        )}>
          {todo.title}
        </p>
        {todo.description && (
          <p className="text-sm text-muted-foreground truncate">
            {todo.description}
          </p>
        )}
      </div>

      {isHovered && (
        <div className="flex gap-2 animate-in fade-in slide-in-from-right-2">
          <Button variant="ghost" size="sm" onClick={() => onEdit(todo)}>
            Edit
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-destructive"
            onClick={() => onDelete(todo.id)}
          >
            Delete
          </Button>
        </div>
      )}
    </Card>
  );
}
```

```tsx
// src/components/todo/TodoList.tsx
import { useMemo } from 'react';
import { useTodoStore } from '@/stores/todoStore';
import { useFilter } from '@/hooks/useFilter';
import { TodoItem } from './TodoItem';
import { EmptyState } from './EmptyState';

export function TodoList() {
  const { todos, toggleTodo, deleteTodo, updateTodo } = useTodoStore();
  const { filter } = useFilter();

  const filteredTodos = useMemo(() => {
    return todos.filter((todo) => {
      if (filter.status && filter.status !== 'all' && todo.status !== filter.status) {
        return false;
      }
      if (filter.priority && filter.priority !== 'all' && todo.priority !== filter.priority) {
        return false;
      }
      if (filter.searchQuery) {
        const query = filter.searchQuery.toLowerCase();
        const matchesSearch = 
          todo.title.toLowerCase().includes(query) ||
          todo.description?.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }
      return true;
    });
  }, [todos, filter]);

  const handleToggle = (id: string) => {
    const todo = todos.find((t) => t.id === id);
    if (todo) {
      updateTodo(id, {
        status: todo.status === 'completed' ? 'pending' : 'completed',
      });
    }
  };

  if (filteredTodos.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-3">
      {filteredTodos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
          onDelete={deleteTodo}
          onEdit={(todo) => {/* Open edit modal */}}
        />
      ))}
    </div>
  );
}
```

---

## 2. State Management Comparison

### Zustand (Recommended)

**Rationale:** Zustand is the preferred choice for this application due to its simplicity, TypeScript support, and minimal boilerplate while providing all necessary features.

```typescript
// src/stores/todoStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { Todo, TodoFormData, TodoFilter } from '@/types/todo';

interface TodoState {
  // State
  todos: Todo[];
  filter: TodoFilter;
  isLoading: boolean;
  error: string | null;

  // Actions
  addTodo: (data: TodoFormData) => void;
  updateTodo: (id: string, updates: Partial<Todo>) => void;
  deleteTodo: (id: string) => void;
  toggleTodo: (id: string) => void;
  setFilter: (filter: TodoFilter) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reorderTodos: (startIndex: number, endIndex: number) => void;
}

export const useTodoStore = create<TodoState>()(
  immer(
    persist(
      (set) => ({
        todos: [],
        filter: { status: 'all', priority: 'all' },
        isLoading: false,
        error: null,

        addTodo: (data) =>
          set((state) => {
            const newTodo: Todo = {
              id: crypto.randomUUID(),
              ...data,
              status: 'pending',
              createdAt: new Date(),
              updatedAt: new Date(),
            };
            state.todos.unshift(newTodo);
          }),

        updateTodo: (id, updates) =>
          set((state) => {
            const todo = state.todos.find((t) => t.id === id);
            if (todo) {
              Object.assign(todo, updates, { updatedAt: new Date() });
            }
          }),

        deleteTodo: (id) =>
          set((state) => {
            state.todos = state.todos.filter((t) => t.id !== id);
          }),

        toggleTodo: (id) =>
          set((state) => {
            const todo = state.todos.find((t) => t.id === id);
            if (todo) {
              todo.status = todo.status === 'completed' ? 'pending' : 'completed';
              todo.updatedAt = new Date();
            }
          }),

        setFilter: (filter) =>
          set((state) => {
            state.filter = { ...state.filter, ...filter };
          }),

        setLoading: (loading) =>
          set((state) => {
            state.isLoading = loading;
          }),

        setError: (error) =>
          set((state) => {
            state.error = error;
          }),

        reorderTodos: (startIndex, endIndex) =>
          set((state) => {
            const [removed] = state.todos.splice(startIndex, 1);
            state.todos.splice(endIndex, 0, removed);
          }),
      }),
      {
        name: 'todo-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({ todos: state.todos }), // Only persist todos
      }
    )
  )
);
```

### Redux Toolkit (Alternative)

```typescript
// src/redux/todoSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Todo, TodoFormData, TodoFilter } from '@/types/todo';

interface TodoState {
  todos: Todo[];
  filter: TodoFilter;
  isLoading: boolean;
  error: string | null;
}

const initialState: TodoState = {
  todos: [],
  filter: { status: 'all', priority: 'all' },
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/todos');
      return await response.json();
    } catch (error) {
      return rejectWithValue('Failed to fetch todos');
    }
  }
);

const todoSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {
    addTodo: (state, action: PayloadAction<TodoFormData>) => {
      const newTodo: Todo = {
        id: crypto.randomUUID(),
        ...action.payload,
        status: 'pending',
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      state.todos.unshift(newTodo);
    },
    updateTodo: (state, action: PayloadAction<{ id: string; updates: Partial<Todo> }>) => {
      const { id, updates } = action.payload;
      const todo = state.todos.find((t) => t.id === id);
      if (todo) {
        Object.assign(todo, updates, { updatedAt: new Date() });
      }
    },
    deleteTodo: (state, action: PayloadAction<string>) => {
      state.todos = state.todos.filter((t) => t.id !== action.payload);
    },
    setFilter: (state, action: PayloadAction<TodoFilter>) => {
      state.filter = { ...state.filter, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.isLoading = false;
        state.todos = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { addTodo, updateTodo, deleteTodo, setFilter } = todoSlice.actions;
export default todoSlice.reducer;
```

### Comparison Matrix

| Feature | Zustand | Redux Toolkit |
|---------|---------|---------------|
| **Bundle Size** | ~1KB | ~11KB |
| **Boilerplate** | Minimal | Moderate |
| **DevTools** | Built-in | Excellent |
| **Async Handling** | Manual / Libraries | createAsyncThunk |
| **TypeScript** | Excellent | Good |
| **Learning Curve** | Low | Medium |
| **Middleware** | Limited but extensible | Rich ecosystem |
| **Recommended For** | Small-Medium apps | Large, complex apps |

**Decision:** Use **Zustand** for this todo app due to its simplicity and adequate feature set. Consider Redux Toolkit if the app grows significantly or requires complex side-effect management.

---

## 3. UI Library Selection

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Styling | Tailwind CSS | ^3.4 |
| Components | shadcn/ui | Latest |
| Icons | Lucide React | ^0.400 |
| Animations | Framer Motion | ^11 |

### Tailwind CSS Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'slide-in': {
          from: { transform: 'translateX(-100%)', opacity: '0' },
          to: { transform: 'translateX(0)', opacity: '1' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

### Component Example with Tailwind + shadcn/ui

```tsx
// src/components/todo/TodoForm.tsx
import { useState } from 'react';
import { useTodoStore } from '@/stores/todoStore';
import { TodoFormData, TodoPriority } from '@/types/todo';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus } from 'lucide-react';

export function TodoForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TodoPriority>('medium');
  const addTodo = useTodoStore((state) => state.addTodo);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    addTodo({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      tags: [],
    });

    // Reset form
    setTitle('');
    setDescription('');
    setPriority('medium');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-6 bg-card rounded-lg border">
      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="title">
          Task Title
        </label>
        <Input
          id="title"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="h-11"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="description">
          Description (optional)
        </label>
        <Textarea
          id="description"
          placeholder="Add more details..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />
      </div>

      <div className="flex gap-4 items-end">
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium">Priority</label>
          <Select value={priority} onValueChange={(v) => setPriority(v as TodoPriority)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low Priority</SelectItem>
              <SelectItem value="medium">Medium Priority</SelectItem>
              <SelectItem value="high">High Priority</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button type="submit" size="lg" className="gap-2">
          <Plus className="w-4 h-4" />
          Add Task
        </Button>
      </div>
    </form>
  );
}
```

### Global Styles

```css
/* src/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}
```

---

## 4. Routing Architecture

### React Router v6 Setup

```tsx
// src/App.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { RootLayout } from '@/components/layout/RootLayout';
import { HomePage } from '@/pages/HomePage';
import { TodoPage } from '@/pages/TodoPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'todos',
        children: [
          {
            index: true,
            element: <TodoPage />,
          },
          {
            path: ':id',
            element: <TodoDetailPage />,
            loader: todoLoader,
          },
        ],
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
```

### Route Components

```tsx
// src/pages/TodoPage.tsx
import { Suspense } from 'react';
import { useSearchParams } from 'react-router-dom';
import { TodoList } from '@/components/todo/TodoList';
import { TodoForm } from '@/components/todo/TodoForm';
import { TodoFilter } from '@/components/todo/TodoFilter';
import { TodoStats } from '@/components/todo/TodoStats';
import { Skeleton } from '@/components/ui/skeleton';

export function TodoPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Sync URL params with filter state
  const statusFilter = searchParams.get('status') || 'all';
  const priorityFilter = searchParams.get('priority') || 'all';

  return (
    <div className="container mx-auto max-w-4xl py-8 px-4 space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">My Tasks</h1>
        <p className="text-muted-foreground">
          Manage your todos and stay organized
        </p>
      </header>

      <TodoStats />
      
      <TodoForm />
      
      <TodoFilter 
        status={statusFilter}
        priority={priorityFilter}
        onFilterChange={(filters) => {
          const params = new URLSearchParams();
          if (filters.status !== 'all') params.set('status', filters.status);
          if (filters.priority !== 'all') params.set('priority', filters.priority);
          setSearchParams(params);
        }}
      />

      <Suspense fallback={<TodoListSkeleton />}>
        <TodoList />
      </Suspense>
    </div>
  );
}

function TodoListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-20 w-full" />
      ))}
    </div>
  );
}
```

```tsx
// src/components/layout/RootLayout.tsx
import { Outlet, NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Layout, ListTodo, Settings } from 'lucide-react';

export function RootLayout() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto max-w-4xl px-4">
          <div className="flex h-14 items-center gap-6">
            <NavLink
              to="/"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors',
                  isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
                )
              }
            >
              <Layout className="w-4 h-4" />
              Dashboard
            </NavLink>
            <NavLink
              to="/todos"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors',
                  isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
                )
              }
            >
              <ListTodo className="w-4 h-4" />
              Tasks
            </NavLink>
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors',
                  isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
                )
              }
            >
              <Settings className="w-4 h-4" />
              Settings
            </NavLink>
          </div>
        </div>
      </nav>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

### Data Loaders

```tsx
// src/loaders/todoLoader.ts
import { LoaderFunctionArgs } from 'react-router-dom';

export async function todoLoader({ params }: LoaderFunctionArgs) {
  const { id } = params;
  
  if (!id) {
    throw new Response('Todo ID is required', { status: 400 });
  }

  const response = await fetch(`/api/todos/${id}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Response('Todo not found', { status: 404 });
    }
    throw new Response('Failed to load todo', { status: 500 });
  }

  return response.json();
}
```

### Protected Routes Pattern

```tsx
// src/components/auth/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
```

---

## 5. Package Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.23.0",
    "zustand": "^4.5.0",
    "immer": "^10.1.0",
    "@radix-ui/react-checkbox": "^1.0.0",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-dialog": "^1.0.0",
    "lucide-react": "^0.400.0",
    "framer-motion": "^11.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "tailwindcss-animate": "^1.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "eslint": "^8.57.0",
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "@typescript-eslint/parser": "^7.0.0"
  }
}
```

---

## 6. Key Decisions Summary

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **State Management** | Zustand + Immer | Minimal boilerplate, excellent TypeScript support, built-in persistence |
| **Styling** | Tailwind CSS | Utility-first, rapid development, consistent design system |
| **Components** | shadcn/ui | Accessible, customizable, Radix UI primitives |
| **Routing** | React Router v6 | Industry standard, data loaders, nested routes |
| **Icons** | Lucide React | Clean, consistent, tree-shakeable |
| **Animation** | Framer Motion | Declarative, performant, excellent React integration |
| **Persistence** | Zustand persist | Simple localStorage sync, selective state persistence |

---

## 7. Performance Considerations

1. **Memoization**: Use `useMemo` for filtered todos, `useCallback` for event handlers
2. **Code Splitting**: Lazy load route components with `React.lazy()`
3. **Virtualization**: For large lists (>100 items), use `react-window` or `react-virtualized`
4. **State Selectors**: Use Zustand's selector pattern to prevent unnecessary re-renders
5. **Bundle Optimization**: Configure tree-shaking and code splitting in Vite config

---

*Document generated for Todo App Frontend Architecture following Swarm Solver standards.*
