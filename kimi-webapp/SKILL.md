---
name: kimi-webapp
description: "Modern React webapp building with TypeScript, Tailwind CSS and shadcn/ui. Complete project scaffolding with 40+ pre-installed components. Best for complex UI and state management."
---

# Kimi Webapp Building Skill

**React + TypeScript + Vite + Tailwind CSS + shadcn/ui**

## Tech Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite 5+
- **Styling**: Tailwind CSS 3.4+
- **Components**: shadcn/ui (40+ components)
- **Icons**: Lucide React

## Project Structure

```
project/
├── src/
│   ├── components/     # Reusable components
│   │   └── ui/         # shadcn/ui components
│   ├── pages/           # Page components
│   ├── hooks/          # Custom React hooks
│   ├── lib/             # Utilities
│   ├── types/           # TypeScript definitions
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Quick Start

### 1. Initialize Project
```bash
# Create new project
npx create-vite@latest my-app --template react-ts
cd my-app

# Install dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn@latest init
```

### 2. Add Components
```bash
# Add common shadcn/ui components
npx shadcn@latest add button card input table dialog tabs
```

### 3. Run Development
```bash
npm run dev
```

## shadcn/ui Components (40+ available)

| Category | Components |
|----------|-----------|
| **Forms** | button, input, label, textarea, select, checkbox, radio, switch |
| **Layout** | card, sheet, dialog, alert-dialog, popover, tooltip |
| **Navigation** | tabs, navigation-menu, breadcrumb, sidebar |
| **Data** | table, data-table, avatar, badge, skeleton |
| **Feedback** | alert, toast, progress, spinner, empty-state |
| **Overlay** | modal, drawer, sheet, popover |
| **Typography** | heading, text, paragraph, code, kbd |

## Component Usage

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

function App() {
  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Welcome</CardTitle>
        </CardHeader>
        <CardContent>
          <Button variant="default">Get Started</Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

## Styling with Tailwind

### Color Palette
```tsx
// Use Tailwind's built-in colors
<div className="bg-slate-900 text-white" />
<div className="bg-blue-500 hover:bg-blue-600" />
<div className="text-gray-500 dark:text-gray-400" />
```

### Typography
```tsx
<h1 className="text-4xl font-bold">Title</h1>
<p className="text-lg text-muted-foreground">Description</p>
<code className="font-mono text-sm bg-muted p-1">Code</code>
```

### Spacing & Layout
```tsx
<div className="flex items-center justify-between p-4 gap-4">
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
```

## Custom Hooks

### useLocalStorage
```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const item = window.localStorage.getItem(key)
    return item ? JSON.parse(item) : initialValue
  })
  
  useEffect(() => {
    window.localStorage.setItem(key, JSON.stringify(value))
  }, [key, value])
  
  return [value, setValue] as const
}
```

### useDebounce
```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  
  return debouncedValue
}
```

## Build & Deploy

### Production Build
```bash
npm run build
# Output in dist/
```

### Deploy Options
- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy --prod`
- **GitHub Pages**: Use `gh-pages` package
- **Docker**: Multi-stage Dockerfile for SSR

## Performance Tips

1. **Code Splitting**
```tsx
const HeavyComponent = lazy(() => import("./HeavyComponent"))
```

2. **Memoization**
```tsx
const memoizedValue = useMemo(() => expensiveCalculation(a, b), [a, b])
const memoizedCallback = useCallback(() => doSomething(a, b), [a, b])
```

3. **Image Optimization**
```tsx
<img src={placeholder} loading="lazy" alt="..." />
```

## TypeScript Patterns

### Generic Components
```tsx
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <div>{items.map(renderItem)}</div>
}
```

### API Response Types
```tsx
interface ApiResponse<T> {
  data: T
  status: number
  message: string
}

interface User {
  id: string
  name: string
  email: string
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tailwind not working | Check `content` in tailwind.config.js |
| shadcn/ui not importing | Run `npx shadcn@latest init` |
| Type errors | Check `tsconfig.json` paths |
| Build slow | Enable `swcMinify` in vite.config.ts |

## Design Principles

1. **Consistency** - Use shadcn/ui design system
2. **Accessibility** - Use semantic HTML and ARIA
3. **Performance** - Lazy load, memoize, optimize
4. **Responsive** - Mobile-first design
5. **Dark mode** - Support `dark:` variants
