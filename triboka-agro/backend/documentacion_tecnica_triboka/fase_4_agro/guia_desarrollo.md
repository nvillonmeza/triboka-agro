# 🛠️ Guía de Desarrollo - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Estándares de Código](#estándares-de-código)
5. [Desarrollo de Funcionalidades](#desarrollo-de-funcionalidades)
6. [Testing](#testing)
7. [CI/CD y Despliegue](#cicd-y-despliegue)
8. [Debugging y Troubleshooting](#debugging-y-troubleshooting)
9. [Contribución al Proyecto](#contribución-al-proyecto)

---

## 🌟 Introducción

Esta guía proporciona las mejores prácticas y estándares para el desarrollo del frontend de Triboka Agro. Está diseñada para asegurar consistencia, calidad y mantenibilidad del código.

### Tecnologías Principales

- **Framework**: Next.js 16.0.3 con TypeScript
- **Estado**: Zustand con persistencia
- **UI**: Tailwind CSS + Lucide Icons
- **Testing**: Jest, React Testing Library, Playwright
- **Control de calidad**: ESLint, Prettier, Husky

### Principios de Desarrollo

- **Type Safety**: Uso obligatorio de TypeScript
- **Componentización**: Componentes reutilizables y modulares
- **Performance**: Optimización y lazy loading
- **Accesibilidad**: Cumplimiento WCAG 2.1
- **Responsive Design**: Mobile-first approach
- **SEO**: Optimización para motores de búsqueda

---

## ⚙️ Configuración del Entorno

### Requisitos del Sistema

```bash
# Node.js versión recomendada
Node.js: 18.17.0+
npm: 9.0.0+
Yarn: 1.22.0+ (opcional)

# Sistema operativo
Linux/macOS/Windows (WSL2 recomendado para Windows)
```

### Instalación del Proyecto

```bash
# Clonar el repositorio
git clone https://github.com/triboka/triboka-agro-frontend.git
cd triboka-agro-frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Iniciar servidor de desarrollo
npm run dev
```

### Variables de Entorno

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_VERSION=1.0.0-dev

# Base de datos (desarrollo)
DATABASE_URL=postgresql://user:pass@localhost:5432/triboka_dev

# Autenticación
JWT_SECRET=your-development-jwt-secret
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

### Extensiones de VS Code Recomendadas

```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-jest",
    "formulahendry.auto-rename-tag",
    "ms-vscode.vscode-css-peek"
  ]
}
```

---

## 📁 Estructura del Proyecto

### Arquitectura General

```
triboka-agro-frontend/
├── .github/                 # GitHub Actions y plantillas
├── .husky/                  # Git hooks
├── .next/                   # Build de Next.js (generado)
├── public/                  # Assets estáticos
├── src/
│   ├── app/                 # App Router de Next.js
│   │   ├── (auth)/         # Rutas de autenticación
│   │   ├── (dashboard)/    # Rutas del dashboard
│   │   ├── api/            # API Routes
│   │   ├── globals.css     # Estilos globales
│   │   ├── layout.tsx      # Layout raíz
│   │   └── page.tsx        # Página de inicio
│   ├── components/         # Componentes reutilizables
│   │   ├── ui/            # Componentes base de UI
│   │   ├── forms/         # Componentes de formularios
│   │   ├── layout/        # Componentes de layout
│   │   └── charts/        # Componentes de gráficos
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utilidades y configuraciones
│   │   ├── config/        # Configuraciones
│   │   ├── utils/         # Funciones utilitarias
│   │   ├── validations/   # Esquemas de validación
│   │   └── constants/     # Constantes
│   ├── stores/            # Estado global (Zustand)
│   ├── styles/            # Estilos adicionales
│   └── types/             # Definiciones TypeScript
├── tests/                  # Tests
│   ├── unit/              # Tests unitarios
│   ├── integration/       # Tests de integración
│   └── e2e/               # Tests end-to-end
├── docs/                   # Documentación
├── .env.example           # Variables de entorno ejemplo
├── .eslintrc.js           # Configuración ESLint
├── .prettierrc            # Configuración Prettier
├── jest.config.js         # Configuración Jest
├── next.config.js         # Configuración Next.js
├── package.json           # Dependencias y scripts
├── tailwind.config.js     # Configuración Tailwind
└── tsconfig.json          # Configuración TypeScript
```

### Convenciones de Nombres

#### Archivos y Directorios

```typescript
// ✅ Correcto
components/
├── Button.tsx
├── InputField.tsx
├── UserProfile/
│   ├── index.ts
│   ├── UserProfile.tsx
│   └── UserProfile.test.tsx

// ❌ Incorrecto
components/
├── button.tsx
├── input_field.tsx
├── user-profile.tsx
```

#### Componentes

```typescript
// ✅ PascalCase para componentes
export function UserDashboard() { ... }
export function ProductCard() { ... }

// ✅ camelCase para hooks
export function useAuth() { ... }
export function useLocalStorage() { ... }

// ✅ UPPER_SNAKE_CASE para constantes
export const API_BASE_URL = 'https://api.triboka.com';
export const MAX_FILE_SIZE = 10 * 1024 * 1024;
```

---

## 🎯 Estándares de Código

### TypeScript

#### Configuración Estricta

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

#### Tipos Comunes

```typescript
// types/common.ts
export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type UserRole = 'producer' | 'exporter' | 'buyer' | 'admin';
```

#### Generic Components

```typescript
// components/DataTable.tsx
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  onRowClick,
}: DataTableProps<T>) {
  // Implementation
}
```

### ESLint y Prettier

#### Configuración ESLint

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
    'prettier',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'off',
    'react-hooks/exhaustive-deps': 'warn',
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
  },
};
```

#### Configuración Prettier

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### Git Hooks con Husky

```json
// .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,css,md}": [
      "prettier --write"
    ]
  }
}
```

---

## 🏗️ Desarrollo de Funcionalidades

### Creación de Componentes

#### Patrón de Componente

```typescript
// components/ProductCard.tsx
import { memo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Product } from '@/types/product';

interface ProductCardProps {
  product: Product;
  onViewDetails: (productId: string) => void;
  onAddToCart: (productId: string) => void;
}

export const ProductCard = memo<ProductCardProps>(({
  product,
  onViewDetails,
  onAddToCart,
}) => {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="flex justify-between items-start">
          {product.name}
          <Badge variant={product.inStock ? 'default' : 'secondary'}>
            {product.inStock ? 'En Stock' : 'Agotado'}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-gray-600">{product.description}</p>

          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold">
              ${product.price.toFixed(2)}
            </span>

            <div className="space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onViewDetails(product.id)}
              >
                Ver Detalles
              </Button>

              <Button
                size="sm"
                disabled={!product.inStock}
                onClick={() => onAddToCart(product.id)}
              >
                Agregar al Carrito
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

ProductCard.displayName = 'ProductCard';
```

#### Custom Hooks

```typescript
// hooks/useProducts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Product, CreateProductData } from '@/types/product';

export function useProducts(filters?: ProductFilters) {
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['products', filters, page],
    queryFn: () => apiClient.getProducts({ ...filters, page }),
    keepPreviousData: true,
  });

  const createProductMutation = useMutation({
    mutationFn: (data: CreateProductData) => apiClient.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['products']);
    },
  });

  return {
    products: data?.products ?? [],
    totalCount: data?.totalCount ?? 0,
    isLoading,
    error,
    page,
    setPage,
    createProduct: createProductMutation.mutate,
    isCreating: createProductMutation.isLoading,
  };
}
```

### Gestión de Estado

#### Zustand Store

```typescript
// stores/auth.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserRole } from '@/types/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  hasRole: (role: UserRole) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) => set({
        user,
        token,
        isAuthenticated: true,
      }),

      logout: () => set({
        user: null,
        token: null,
        isAuthenticated: false,
      }),

      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null,
      })),

      hasRole: (role) => get().user?.role === role,
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### API Integration

#### API Client

```typescript
// lib/api-client.ts
import { ApiResponse } from '@/types/common';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Products
  async getProducts(filters?: ProductFilters) {
    return this.request<Product[]>('/products', {
      method: 'GET',
      body: filters ? JSON.stringify(filters) : undefined,
    });
  }

  async createProduct(data: CreateProductData) {
    return this.request<Product>('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
);
```

### Formularios con Validación

#### Schema de Validación

```typescript
// lib/validations/product.ts
import { z } from 'zod';

export const createProductSchema = z.object({
  name: z.string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .max(100, 'El nombre no puede exceder 100 caracteres'),

  description: z.string()
    .min(10, 'La descripción debe tener al menos 10 caracteres')
    .max(1000, 'La descripción no puede exceder 1000 caracteres'),

  price: z.number()
    .min(0.01, 'El precio debe ser mayor a 0')
    .max(999999.99, 'El precio no puede exceder 999,999.99'),

  category: z.enum(['coffee', 'cocoa', 'fruits'], {
    errorMap: () => ({ message: 'Selecciona una categoría válida' }),
  }),

  inStock: z.boolean(),

  tags: z.array(z.string())
    .min(1, 'Debes seleccionar al menos una etiqueta')
    .max(5, 'No puedes seleccionar más de 5 etiquetas'),
});

export type CreateProductForm = z.infer<typeof createProductSchema>;
```

#### Componente de Formulario

```typescript
// components/forms/CreateProductForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { createProductSchema, CreateProductForm } from '@/lib/validations/product';
import { useProducts } from '@/hooks/useProducts';

export function CreateProductForm() {
  const { createProduct, isCreating } = useProducts();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<CreateProductForm>({
    resolver: zodResolver(createProductSchema),
    defaultValues: {
      inStock: true,
      tags: [],
    },
  });

  const onSubmit = (data: CreateProductForm) => {
    createProduct(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Nombre del Producto
        </label>
        <Input
          id="name"
          {...register('name')}
          className={errors.name ? 'border-red-500' : ''}
        />
        {errors.name && (
          <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium">
          Descripción
        </label>
        <Textarea
          id="description"
          {...register('description')}
          rows={4}
          className={errors.description ? 'border-red-500' : ''}
        />
        {errors.description && (
          <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="price" className="block text-sm font-medium">
            Precio
          </label>
          <Input
            id="price"
            type="number"
            step="0.01"
            {...register('price', { valueAsNumber: true })}
            className={errors.price ? 'border-red-500' : ''}
          />
          {errors.price && (
            <p className="text-red-500 text-sm mt-1">{errors.price.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-medium">
            Categoría
          </label>
          <Select {...register('category')}>
            <option value="coffee">Café</option>
            <option value="cocoa">Cacao</option>
            <option value="fruits">Frutas</option>
          </Select>
          {errors.category && (
            <p className="text-red-500 text-sm mt-1">{errors.category.message}</p>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="inStock"
          checked={watch('inStock')}
          onCheckedChange={(checked) => setValue('inStock', !!checked)}
        />
        <label htmlFor="inStock" className="text-sm">
          Producto disponible
        </label>
      </div>

      <Button type="submit" disabled={isCreating} className="w-full">
        {isCreating ? 'Creando...' : 'Crear Producto'}
      </Button>
    </form>
  );
}
```

---

## 🧪 Testing

### Configuración de Jest

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/pages/_app.tsx',
    '!src/pages/_document.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### Test Unitario

```typescript
// components/ProductCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from './ProductCard';

const mockProduct = {
  id: '1',
  name: 'Café Orgánico',
  description: 'Café de alta calidad',
  price: 25.99,
  inStock: true,
};

const mockOnViewDetails = jest.fn();
const mockOnAddToCart = jest.fn();

describe('ProductCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onViewDetails={mockOnViewDetails}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Café Orgánico')).toBeInTheDocument();
    expect(screen.getByText('Café de alta calidad')).toBeInTheDocument();
    expect(screen.getByText('$25.99')).toBeInTheDocument();
    expect(screen.getByText('En Stock')).toBeInTheDocument();
  });

  it('calls onViewDetails when view details button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onViewDetails={mockOnViewDetails}
        onAddToCart={mockOnAddToCart}
      />
    );

    const viewDetailsButton = screen.getByText('Ver Detalles');
    fireEvent.click(viewDetailsButton);

    expect(mockOnViewDetails).toHaveBeenCalledWith('1');
  });

  it('shows out of stock badge when product is not in stock', () => {
    const outOfStockProduct = { ...mockProduct, inStock: false };

    render(
      <ProductCard
        product={outOfStockProduct}
        onViewDetails={mockOnViewDetails}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Agotado')).toBeInTheDocument();
  });
});
```

### Test de Integración

```typescript
// tests/integration/ProductManagement.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProductManagement } from '@/components/ProductManagement';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('ProductManagement Integration', () => {
  it('creates a new product successfully', async () => {
    const user = userEvent.setup();
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <ProductManagement />
      </QueryClientProvider>
    );

    // Fill out the form
    await user.type(screen.getByLabelText(/nombre/i), 'Nuevo Producto');
    await user.type(screen.getByLabelText(/descripción/i), 'Descripción del producto');
    await user.type(screen.getByLabelText(/precio/i), '29.99');

    // Submit the form
    await user.click(screen.getByRole('button', { name: /crear producto/i }));

    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText(/producto creado exitosamente/i)).toBeInTheDocument();
    });

    // Verify the product appears in the list
    expect(screen.getByText('Nuevo Producto')).toBeInTheDocument();
  });
});
```

### Test E2E con Playwright

```typescript
// tests/e2e/product-creation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Product Creation Flow', () => {
  test('user can create a new product', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');

    // Login
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');

    // Navigate to products page
    await page.click('[data-testid="products-nav-link"]');

    // Click create product button
    await page.click('[data-testid="create-product-button"]');

    // Fill out the form
    await page.fill('[data-testid="product-name-input"]', 'Café Especial');
    await page.fill('[data-testid="product-description-input"]', 'Café de especialidad premium');
    await page.fill('[data-testid="product-price-input"]', '45.00');
    await page.selectOption('[data-testid="product-category-select"]', 'coffee');

    // Submit the form
    await page.click('[data-testid="submit-product-button"]');

    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="product-list"]')).toContainText('Café Especial');
  });
});
```

---

## 🔄 CI/CD y Despliegue

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run type-check

      - name: Run tests
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-files
          path: .next/
```

### Scripts de Package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "prepare": "husky install"
  }
}
```

---

## 🐛 Debugging y Troubleshooting

### Herramientas de Debugging

#### React Developer Tools

```typescript
// lib/debug.ts
import { useEffect } from 'react';

export function useDebugInfo(componentName: string, props: any) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[${componentName}] Props:`, props);
    }
  }, [componentName, props]);
}

// Uso en componentes
export function MyComponent({ data, loading }) {
  useDebugInfo('MyComponent', { data, loading });

  // ... resto del componente
}
```

#### Logging Estructurado

```typescript
// lib/logger.ts
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  userId?: string;
  sessionId?: string;
  metadata?: Record<string, any>;
}

class Logger {
  private logLevel: LogLevel = 'info';

  setLogLevel(level: LogLevel) {
    this.logLevel = level;
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private log(level: LogLevel, message: string, metadata?: Record<string, any>) {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      metadata,
    };

    // In development, log to console
    if (process.env.NODE_ENV === 'development') {
      console[level](`[${level.toUpperCase()}] ${message}`, metadata || '');
    }

    // Send to logging service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToService(entry);
    }
  }

  debug(message: string, metadata?: Record<string, any>) {
    this.log('debug', message, metadata);
  }

  info(message: string, metadata?: Record<string, any>) {
    this.log('info', message, metadata);
  }

  warn(message: string, metadata?: Record<string, any>) {
    this.log('warn', message, metadata);
  }

  error(message: string, metadata?: Record<string, any>) {
    this.log('error', message, metadata);
  }

  private async sendToService(entry: LogEntry) {
    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log to service:', error);
    }
  }
}

export const logger = new Logger();
```

### Problemas Comunes y Soluciones

#### Problema: Componente no se re-renderiza

```typescript
// ❌ Incorrecto - mutación directa
function MyComponent() {
  const [items, setItems] = useState([1, 2, 3]);

  const addItem = (item) => {
    items.push(item); // Mutación directa
    setItems(items); // No trigger re-render
  };

  return <div>...</div>;
}

// ✅ Correcto - nuevo array
function MyComponent() {
  const [items, setItems] = useState([1, 2, 3]);

  const addItem = (item) => {
    setItems([...items, item]); // Nuevo array
  };

  return <div>...</div>;
}
```

#### Problema: Memory Leaks

```typescript
// ❌ Incorrecto - no cleanup
function MyComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData().then(setData);
  }, []); // Se ejecuta solo una vez

  return <div>{data?.name}</div>;
}

// ✅ Correcto - cleanup
function MyComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    fetchData().then((result) => {
      if (isMounted) {
        setData(result);
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <div>Loading...</div>;

  return <div>{data?.name}</div>;
}
```

#### Problema: Infinite Re-renders

```typescript
// ❌ Incorrecto - objeto nuevo en cada render
function MyComponent({ user }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log('User changed');
  }, [user]); // user es un objeto nuevo cada vez

  return <div>...</div>;
}

// ✅ Correcto - usar ID o memoización
function MyComponent({ user }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log('User changed');
  }, [user.id]); // Usar propiedad específica

  return <div>...</div>;
}
```

---

## 🤝 Contribución al Proyecto

### Proceso de Contribución

1. **Fork** el repositorio
2. **Crea una branch** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Realiza tus cambios** siguiendo los estándares del proyecto
4. **Escribe tests** para tu funcionalidad
5. **Ejecuta los tests** y linting: `npm run lint && npm run test`
6. **Commit** tus cambios: `git commit -m "feat: add nueva funcionalidad"`
7. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
8. **Crea un Pull Request** con descripción detallada

### Convenciones de Commit

```bash
# Formato: type(scope): description
git commit -m "feat(auth): add login with Google OAuth"
git commit -m "fix(dashboard): resolve memory leak in chart component"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(api): simplify error handling logic"
git commit -m "test(products): add unit tests for product validation"
```

#### Tipos de Commit

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **style**: Cambios de estilo (formateo, etc.)
- **refactor**: Refactorización de código
- **test**: Añadir o modificar tests
- **chore**: Cambios en herramientas, configuración

### Code Review

#### Checklist para Reviewers

- [ ] **Funcionalidad**: ¿Funciona como se espera?
- [ ] **Código**: ¿Sigue los estándares del proyecto?
- [ ] **Tests**: ¿Tiene cobertura adecuada?
- [ ] **Performance**: ¿No degrada el rendimiento?
- [ ] **Seguridad**: ¿No introduce vulnerabilidades?
- [ ] **Documentación**: ¿Está documentado apropiadamente?

#### Checklist para Contributors

- [ ] Ejecuté todos los tests localmente
- [ ] El código pasa linting
- [ ] Añadí tests para nueva funcionalidad
- [ ] Actualicé la documentación si es necesario
- [ ] Probé la funcionalidad en diferentes navegadores
- [ ] Verifiqué que no hay console.logs en producción

### Gestión de Releases

#### Versionado Semántico

- **MAJOR**: Cambios incompatibles
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de bugs

#### Proceso de Release

1. **Crear branch de release**: `git checkout -b release/v1.2.0`
2. **Actualizar versión**: En `package.json` y otros archivos relevantes
3. **Actualizar CHANGELOG.md**: Documentar cambios
4. **Merge a main**: Después de testing y aprobación
5. **Crear tag**: `git tag v1.2.0`
6. **Deploy**: Automático via CI/CD

---

*Esta guía de desarrollo asegura que el código de Triboka Agro sea mantenible, escalable y de alta calidad. Sigue estos estándares para contribuir efectivamente al proyecto.*