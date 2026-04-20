# React Todo App - Frontend Architecture Design

## 1. Component Structure

### Directory Organization

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Shared UI primitives
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Checkbox/
│   │   └── Modal/
│   ├── todo/            # Todo-specific components
│   │   ├── TodoItem/
│   │   ├── TodoList/
│   │   ├── TodoForm/
│   │   ├── TodoFilter/
│   │   └── TodoStats/
│   └── layout/          # Layout components
│       ├── Header/
│       ├── Sidebar/
│       └── Footer/
├── pages/               # Page-level components
│   ├── Home/
│   ├── Today/
│   ├── Upcoming/
│   ├── Completed/
│   └── Settings/
├── hooks/               # Custom React hooks
│   ├── useTodos.ts
│   ├── useLocalStorage.ts
│   └── useFilter.ts
├── services/            # API and external services
│   └── todoApi.ts
├── types/               # TypeScript interfaces
│   └── index.ts
├── utils/               # Utility functions
│   └── helpers.ts
├── store/               # State management
│   └── (see State Management section)
└── styles/              # Global styles
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

### Component Interfaces

```typescript
// types/index.ts

export interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
}

export interface TodoFilter {
  status: 'all' | 'active' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  searchQuery?: string;
  tags?: string[];
}

export interface TodoFormData {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tags: string[];
}
```

---

## 2. State Management

### Recommendation: Zustand + React Query

For a modern todo app, we recommend a hybrid approach:
- **Zustand** for client-side UI state
- **React Query (TanStack Query)** for server state

### Why Zustand over Redux?

| Feature | Zustand | Redux |
|---------|---------|-------|
| Bundle Size | ~1KB | ~10KB+ |
| Boilerplate | Minimal | Significant |
| Learning Curve | Low | High |
| DevTools | Built-in | Requires setup |
| TypeScript | Excellent | Good |
| Middleware | Simple | Complex |

### Zustand Store Structure

```typescript
// store/todoStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

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

export const useTodoStore = create<TodoState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        todos: [],
        filter: { status: 'all' },
        isLoading: false,
        error: null,

        // Actions
        addTodo: (todoData) => {
          set((state) => {
            const newTodo: Todo = {
              id: crypto.randomUUID(),
              ...todoData,
              completed: false,
              createdAt: new Date(),
              updatedAt: new Date(),
            };
            state.todos.unshift(newTodo);
          });
        },

        updateTodo: (id, updates) => {
          set((state) => {
            const todo = state.todos.find((t) => t.id === id);
            if (todo) {
              Object.assign(todo, { ...updates, updatedAt: new Date() });
            }
          });
        },

        deleteTodo: (id) => {
          set((state) => {
            state.todos = state.todos.filter((t) => t.id !== id);
          });
        },

        toggleTodo: (id) => {
          set((state) => {
            const todo = state.todos.find((t) => t.id === id);
            if (todo) {
              todo.completed = !todo.completed;
              todo.updatedAt = new Date();
            }
          });
        },

        setFilter: (filter) => {
          set((state) => {
            state.filter = { ...state.filter, ...filter };
          });
        },

        clearCompleted: () => {
          set((state) => {
            state.todos = state.todos.filter((t) => !t.completed);
          });
        },

        reorderTodos: (startIndex, endIndex) => {
          set((state) => {
            const [removed] = state.todos.splice(startIndex, 1);
            state.todos.splice(endIndex, 0, removed);
          });
        },
      })),
      {
        name: 'todo-storage',
        partialize: (state) => ({ todos: state.todos }),
      }
    ),
    { name: 'TodoStore' }
  )
);
```

### Derived State with Selectors

```typescript
// store/selectors.ts
import { useTodoStore } from './todoStore';

// Computed/filtered todos
export const useFilteredTodos = () => {
  return useTodoStore((state) => {
    const { todos, filter } = state;
    
    return todos.filter((todo) => {
      // Status filter
      if (filter.status === 'active' && todo.completed) return false;
      if (filter.status === 'completed' && !todo.completed) return false;
      
      // Priority filter
      if (filter.priority && todo.priority !== filter.priority) return false;
      
      // Search filter
      if (filter.searchQuery) {
        const query = filter.searchQuery.toLowerCase();
        const matchesSearch = 
          todo.title.toLowerCase().includes(query) ||
          todo.description?.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }
      
      // Tags filter
      if (filter.tags?.length) {
        const hasTag = filter.tags.some((tag) => todo.tags.includes(tag));
        if (!hasTag) return false;
      }
      
      return true;
    });
  });
};

// Stats
export const useTodoStats = () => {
  return useTodoStore((state) => {
    const { todos } = state;
    return {
      total: todos.length,
      active: todos.filter((t) => !t.completed).length,
      completed: todos.filter((t) => t.completed).length,
      highPriority: todos.filter((t) => t.priority === 'high' && !t.completed).length,
    };
  });
};
```

### React Query for Server Sync (Optional)

```typescript
// hooks/useTodosQuery.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const TODOS_KEY = 'todos';

export const useTodosQuery = () => {
  return useQuery({
    queryKey: [TODOS_KEY],
    queryFn: fetchTodos, // Your API call
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useCreateTodoMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createTodo, // Your API call
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TODOS_KEY] });
    },
  });
};
```

---

## 3. UI Library Selection

### Recommended Stack: Tailwind CSS + shadcn/ui + Radix UI

### Component Library Comparison

| Library | Bundle Size | Customization | Accessibility | Best For |
|---------|-------------|---------------|---------------|----------|
| **shadcn/ui** | Tree-shakeable | Excellent | Built-in | Modern, consistent apps |
| Material-UI | ~300KB | Good | Good | Google Material Design |
| Chakra UI | ~250KB | Good | Excellent | Rapid prototyping |
| Ant Design | ~500KB | Moderate | Good | Enterprise dashboards |
| Radix (primitives) | ~20KB | Unlimited | Excellent | Custom design systems |

### Why shadcn/ui?

1. **Copy-paste components** - Not a dependency, own your code
2. **Built on Radix** - Unstyled, accessible primitives
3. **Tailwind-first** - Easy customization
4. **TypeScript-native** - Full type safety
5. **Active community** - Regular updates

### Core Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.8.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-select": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "date-fns": "^2.30.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.2"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@types/react": "^18.2.0"
  }
}
```

### Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      animation: {
        'slide-in': 'slideIn 0.2s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

---

## 4. Routing

### Router: React Router v6

### Route Structure

```typescript
// router/index.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { Home } from '@/pages/Home';
import { Today } from '@/pages/Today';
import { Upcoming } from '@/pages/Upcoming';
import { Completed } from '@/pages/Completed';
import { Settings } from '@/pages/Settings';
import { NotFound } from '@/pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Navigate to="/all" replace />,
      },
      {
        path: 'all',
        element: <Home />,
      },
      {
        path: 'today',
        element: <Today />,
      },
      {
        path: 'upcoming',
        element: <Upcoming />,
      },
      {
        path: 'completed',
        element: <Completed />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);
```

### Route-based Data Loading

```typescript
// pages/Today.tsx
import { useLoaderData } from 'react-router-dom';
import { isToday, parseISO } from 'date-fns';

export const todayLoader = () => {
  // Pre-load today's todos
  const todos = useTodoStore.getState().todos;
  return todos.filter(
    (todo) => todo.dueDate && isToday(parseISO(todo.dueDate.toString()))
  );
};

export const Today = () => {
  const todaysTodos = useLoaderData<typeof todayLoader>();
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Today</h1>
      <TodoList todos={todaysTodos} />
    </div>
  );
};
```

### Protected Routes (Future-proofing)

```typescript
// components/auth/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiresAuth?: boolean;
}

export const ProtectedRoute = ({ 
  children, 
  requiresAuth = false 
}: ProtectedRouteProps) => {
  const location = useLocation();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (requiresAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

---

## 5. Additional Architecture Considerations

### Performance Optimizations

1. **Code Splitting**
   ```typescript
   const Settings = lazy(() => import('./pages/Settings'));
   ```

2. **Memoization**
   ```typescript
   export const TodoItem = memo(({ todo, onToggle }: TodoItemProps) => {
     // Component logic
   });
   ```

3. **Virtualization** (for large lists)
   ```typescript
   import { useVirtualizer } from '@tanstack/react-virtual';
   ```

### Error Handling

```typescript
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <DefaultErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Testing Strategy

```typescript
// Tests: Vitest + React Testing Library + MSW

// Unit tests for store
// Integration tests for components
// E2E tests with Playwright
```

---

## Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **State Management** | Zustand + Immer | Minimal boilerplate, TypeScript-first, easy to learn |
| **UI Library** | shadcn/ui + Tailwind | Customizable, accessible, no runtime dependency |
| **Routing** | React Router v6 | Industry standard, excellent data loading |
| **Server State** | React Query | Caching, synchronization, background updates |
| **Forms** | React Hook Form + Zod | Performance, validation, TypeScript |
| **Build Tool** | Vite | Fast HMR, modern bundling |

---

*Document generated for Todo App Frontend Architecture Design*
