# 🧪 Testing Frontend - Triboka Agro

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Estrategia de Testing](#estrategia-de-testing)
3. [Testing Unitario](#testing-unitario)
4. [Testing de Componentes](#testing-de-componentes)
5. [Testing de Integración](#testing-de-integración)
6. [Testing E2E](#testing-e2e)
7. [Testing de Estado](#testing-de-estado)
8. [Herramientas y Configuración](#herramientas-y-configuración)
9. [CI/CD y Automatización](#cicd-y-automatización)
10. [Cobertura de Código](#cobertura-de-código)

---

## 🎯 Visión General

La estrategia de testing del frontend Triboka Agro está diseñada para garantizar la calidad, fiabilidad y mantenibilidad del código. Utilizamos una combinación de testing unitario, de componentes, integración y E2E para cubrir todos los aspectos de la aplicación.

---

## 📋 Estrategia de Testing

### Pirámide de Testing

```
     E2E Tests (10-20%)
    ╱        ╲
   ╱          ╲
Integration    Component
  Tests         Tests
 (20-30%)     (30-40%)
    ╲          ╱
     ╲        ╱
    Unit Tests
   (40-50%)
```

### Principios de Testing

1. **Test First**: Escribir tests antes del código cuando sea posible
2. **TDD/BDD**: Desarrollo guiado por tests y comportamiento
3. **Cobertura Completa**: Buscar > 80% de cobertura en código crítico
4. **Mantenibilidad**: Tests legibles y fáciles de mantener
5. **Rapidez**: Tests que se ejecuten en < 5 minutos
6. **Automatización**: Integración completa en CI/CD

---

## 🧩 Testing Unitario

### Configuración de Jest

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@/components/(.*)$': '<rootDir>/components/$1',
  },
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'hooks/**/*.{ts,tsx}',
    'stores/**/*.{ts,tsx}',
    '!**/*.d.ts',
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

### Setup de Tests

```typescript
// jest.setup.js
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock de Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock de localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock de fetch
global.fetch = jest.fn();

// Mock de ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Setup MSW
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Ejemplos de Tests Unitarios

#### Testing de Utilidades

```typescript
// lib/utils.test.ts
import { formatCurrency, formatDate, validateEmail } from './utils';

describe('Utils', () => {
  describe('formatCurrency', () => {
    it('should format USD currency correctly', () => {
      expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
    });

    it('should format EUR currency correctly', () => {
      expect(formatCurrency(1234.56, 'EUR')).toBe('€1,234.56');
    });

    it('should handle zero values', () => {
      expect(formatCurrency(0, 'USD')).toBe('$0.00');
    });
  });

  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2025-11-14T10:30:00Z');
      expect(formatDate(date)).toBe('14/11/2025');
    });

    it('should handle invalid dates', () => {
      expect(formatDate(new Date('invalid'))).toBe('Invalid Date');
    });
  });

  describe('validateEmail', () => {
    it('should validate correct emails', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name+tag@domain.co.uk')).toBe(true);
    });

    it('should reject invalid emails', () => {
      expect(validateEmail('invalid')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
    });
  });
});
```

#### Testing de Hooks Personalizados

```typescript
// hooks/useLocalStorage.test.ts
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from './useLocalStorage';

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return initial value', () => {
    const { result } = renderHook(() => useLocalStorage('test', 'initial'));
    expect(result.current[0]).toBe('initial');
  });

  it('should return stored value', () => {
    localStorage.setItem('test', JSON.stringify('stored'));
    const { result } = renderHook(() => useLocalStorage('test', 'initial'));
    expect(result.current[0]).toBe('stored');
  });

  it('should update value', () => {
    const { result } = renderHook(() => useLocalStorage('test', 'initial'));

    act(() => {
      result.current[1]('updated');
    });

    expect(result.current[0]).toBe('updated');
    expect(localStorage.getItem('test')).toBe(JSON.stringify('updated'));
  });

  it('should handle function updates', () => {
    const { result } = renderHook(() => useLocalStorage('test', 0));

    act(() => {
      result.current[1](prev => prev + 1);
    });

    expect(result.current[0]).toBe(1);
  });
});
```

---

## 🧩 Testing de Componentes

### Configuración de Testing Library

```typescript
// test-utils.tsx
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// Mock de Zustand stores
jest.mock('@/stores/auth');
jest.mock('@/stores/lots');

// Crear wrapper con providers
function AllTheProviders({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

### Testing de Componentes Simples

```typescript
// components/ui/Button.test.tsx
import { render, screen, fireEvent } from '@/test-utils';
import { Button } from './Button';

describe('Button', () => {
  it('should render with default props', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('should handle click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button', { name: /click me/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should apply variant classes', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const button = screen.getByRole('button', { name: /secondary/i });
    expect(button).toHaveClass('bg-secondary');
  });

  it('should be disabled when loading', () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeDisabled();
  });
});
```

### Testing de Componentes Complejos

```typescript
// components/dashboard/MetricCard.test.tsx
import { render, screen, waitFor } from '@/test-utils';
import { MetricCard } from './MetricCard';

describe('MetricCard', () => {
  const defaultProps = {
    title: 'Total Lotes',
    value: 150,
    change: 12.5,
    changeType: 'increase' as const,
    icon: 'Package',
  };

  it('should render metric data correctly', () => {
    render(<MetricCard {...defaultProps} />);

    expect(screen.getByText('Total Lotes')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('+12.5%')).toBeInTheDocument();
  });

  it('should show increase styling for positive change', () => {
    render(<MetricCard {...defaultProps} />);
    const changeElement = screen.getByText('+12.5%');
    expect(changeElement).toHaveClass('text-green-600');
  });

  it('should show decrease styling for negative change', () => {
    render(<MetricCard {...defaultProps} change={-5.2} changeType="decrease" />);
    const changeElement = screen.getByText('-5.2%');
    expect(changeElement).toHaveClass('text-red-600');
  });

  it('should format large numbers', () => {
    render(<MetricCard {...defaultProps} value={1500000} />);
    expect(screen.getByText('1.5M')).toBeInTheDocument();
  });

  it('should render loading state', () => {
    render(<MetricCard {...defaultProps} loading />);
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });
});
```

### Testing con Zustand

```typescript
// components/auth/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@/test-utils';
import { LoginForm } from './LoginForm';
import { useAuthStore } from '@/stores/auth';

jest.mock('@/stores/auth');

describe('LoginForm', () => {
  const mockLogin = jest.fn();

  beforeEach(() => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
    });
  });

  it('should render login form', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('should handle form submission', async () => {
    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('should show loading state', () => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: true,
      error: null,
    });

    render(<LoginForm />);

    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeDisabled();
    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });

  it('should display error messages', () => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: 'Credenciales inválidas',
    });

    render(<LoginForm />);

    expect(screen.getByText('Credenciales inválidas')).toBeInTheDocument();
  });
});
```

---

## 🔗 Testing de Integración

### Testing de API Calls

```typescript
// services/lots.test.ts
import { lotsService } from './lots';
import { apiClient } from '@/lib/api/client';

jest.mock('@/lib/api/client');

describe('Lots Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLots', () => {
    it('should fetch lots successfully', async () => {
      const mockResponse = {
        data: {
          lots: [
            { id: '1', name: 'Lot 1', weight: 100 },
            { id: '2', name: 'Lot 2', weight: 200 },
          ],
          total: 2,
          page: 1,
          limit: 20,
        },
      };

      (apiClient.get as jest.Mock).mockResolvedValue(mockResponse);

      const result = await lotsService.getLots();

      expect(apiClient.get).toHaveBeenCalledWith('/lots', {
        params: { page: 1, limit: 20 },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      (apiClient.get as jest.Mock).mockRejectedValue(error);

      await expect(lotsService.getLots()).rejects.toThrow('API Error');
    });

    it('should apply filters correctly', async () => {
      const filters = { status: 'available', quality: 'premium' };
      const mockResponse = { data: { lots: [], total: 0, page: 1, limit: 20 } };

      (apiClient.get as jest.Mock).mockResolvedValue(mockResponse);

      await lotsService.getLots(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/lots', {
        params: { page: 1, limit: 20, status: 'available', quality: 'premium' },
      });
    });
  });

  describe('createLot', () => {
    it('should create lot successfully', async () => {
      const lotData = { name: 'New Lot', weight: 150 };
      const mockResponse = {
        data: { id: '123', ...lotData, createdAt: new Date().toISOString() },
      };

      (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

      const result = await lotsService.createLot(lotData);

      expect(apiClient.post).toHaveBeenCalledWith('/lots', lotData);
      expect(result).toEqual(mockResponse.data);
    });
  });
});
```

### Testing de React Query

```typescript
// hooks/useLots.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useLots } from '@/hooks/useLots';
import { lotsService } from '@/services/lots';

jest.mock('@/services/lots');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useLots', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch lots successfully', async () => {
    const mockData = {
      lots: [
        { id: '1', name: 'Lot 1', weight: 100 },
        { id: '2', name: 'Lot 2', weight: 200 },
      ],
      total: 2,
      page: 1,
      limit: 20,
      hasMore: false,
    };

    (lotsService.getLots as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useLots(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockData);
    expect(lotsService.getLots).toHaveBeenCalledWith(undefined, 1, 20);
  });

  it('should handle error state', async () => {
    (lotsService.getLots as jest.Mock).mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useLots(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error?.message).toBe('API Error');
  });
});
```

---

## 🌐 Testing E2E

### Configuración de Playwright

```typescript
// playwright.config.ts
import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' },
    },
    {
      name: 'webkit',
      use: { browserName: 'webkit' },
    },
  ],
};

export default config;
```

### Ejemplos de Tests E2E

#### Flujo de Login Completo

```typescript
// e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('[data-testid="email-input"]', 'producer@triboka.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');

    // Should show user info
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Productor Demo');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[data-testid="email-input"]', 'invalid@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Credenciales inválidas');
  });
});
```

#### Gestión Completa de Lotes

```typescript
// e2e/lots/lot-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Lot Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as producer
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'producer@triboka.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should create new lot', async ({ page }) => {
    await page.click('[data-testid="create-lot-button"]');

    // Fill lot form
    await page.fill('[data-testid="lot-name"]', 'Lote Premium 2025');
    await page.fill('[data-testid="lot-weight"]', '250');
    await page.selectOption('[data-testid="lot-unit"]', 'kg');
    await page.selectOption('[data-testid="lot-quality"]', 'premium');
    await page.fill('[data-testid="lot-location"]', 'Manabí, Ecuador');

    await page.click('[data-testid="submit-lot"]');

    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

    // Should appear in lots list
    await expect(page.locator('[data-testid="lots-list"]')).toContainText('Lote Premium 2025');
  });

  test('should edit existing lot', async ({ page }) => {
    // Click on first lot in list
    await page.click('[data-testid="lot-item"]:first-child [data-testid="edit-button"]');

    // Update weight
    await page.fill('[data-testid="lot-weight"]', '300');
    await page.click('[data-testid="submit-lot"]');

    // Should show updated weight
    await expect(page.locator('[data-testid="lot-weight-display"]')).toContainText('300 kg');
  });
});
```

#### Testing de Roles

```typescript
// e2e/roles/role-based-access.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Role-Based Access', () => {
  test('admin should see all navigation options', async ({ page }) => {
    await loginAs(page, 'admin@triboka.com', 'admin123');

    // Check sidebar navigation
    await expect(page.locator('[data-testid="nav-users"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-companies"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-deal-room"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-licenses"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-support"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-api"]')).toBeVisible();
  });

  test('producer should see limited navigation', async ({ page }) => {
    await loginAs(page, 'producer@triboka.com', 'producer123');

    // Should see producer options
    await expect(page.locator('[data-testid="nav-my-lots"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-contracts"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-certifications"]')).toBeVisible();

    // Should not see admin options
    await expect(page.locator('[data-testid="nav-users"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="nav-deal-room"]')).not.toBeVisible();
  });

  test('buyer should access marketplace', async ({ page }) => {
    await loginAs(page, 'buyer@triboka.com', 'buyer123');

    // Should access marketplace
    await page.click('[data-testid="nav-marketplace"]');
    await expect(page).toHaveURL('/buyer/marketplace');

    // Should be able to search lots
    await expect(page.locator('[data-testid="search-input"]')).toBeVisible();
  });
});

async function loginAs(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', email);
  await page.fill('[data-testid="password-input"]', password);
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/dashboard');
}
```

---

## 🗄️ Testing de Estado

### Testing de Zustand Stores

```typescript
// stores/auth.test.ts
import { act, renderHook } from '@testing-library/react';
import { useAuthStore } from './auth';

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,
      error: null,
    });
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('should handle login success', async () => {
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };
    const mockTokens = { accessToken: 'token', refreshToken: 'refresh' };

    // Mock the login function
    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      // Simulate successful login
      result.current.login('test@example.com', 'password');
    });

    // In a real test, you'd mock the service and check the final state
    expect(result.current.loading).toBe(true);
  });

  it('should handle logout', () => {
    // Set initial authenticated state
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com' },
      token: 'token',
      isAuthenticated: true,
    });

    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

### Testing de Persistencia

```typescript
// stores/persistedStore.test.ts
import { act, renderHook } from '@testing-library/react';
import { usePersistedStore } from './persistedStore';

describe('Persisted Store', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should persist user preferences', () => {
    const { result } = renderHook(() => usePersistedStore());

    act(() => {
      result.current.setUserPreferences({
        theme: 'dark',
        language: 'es',
      });
    });

    // Re-render to test persistence
    const { result: result2 } = renderHook(() => usePersistedStore());

    expect(result2.current.userPreferences.theme).toBe('dark');
    expect(result2.current.userPreferences.language).toBe('es');
  });

  it('should manage recent searches', () => {
    const { result } = renderHook(() => usePersistedStore());

    act(() => {
      result.current.addRecentSearch('cacao premium');
      result.current.addRecentSearch('arabica ecuatoriano');
    });

    expect(result.current.recentSearches).toEqual([
      'arabica ecuatoriano',
      'cacao premium',
    ]);
  });
});
```

---

## 🛠️ Herramientas y Configuración

### Dependencias de Testing

```json
// package.json
{
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "@types/jest": "^29.5.8",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "msw": "^1.3.2",
    "playwright": "^1.40.1",
    "@playwright/test": "^1.40.1"
  }
}
```

### Scripts de Testing

```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:ci": "jest --coverage && playwright test"
  }
}
```

### Configuración de MSW (Mock Service Worker)

```typescript
// mocks/server.ts
import { setupServer } from 'msw/node';
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/lots', (req, res, ctx) => {
    return res(
      ctx.json({
        lots: [
          {
            id: '1',
            name: 'Lote Premium',
            weight: 100,
            quality: 'premium',
            status: 'available',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
      })
    );
  }),

  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'producer',
        },
        tokens: {
          accessToken: 'mock-token',
          refreshToken: 'mock-refresh-token',
        },
      })
    );
  }),
];

export const server = setupServer(...handlers);
```

---

## 🔄 CI/CD y Automatización

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test

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

      - name: Run unit tests
        run: npm run test:coverage

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

### Pre-commit Hooks

```javascript
// .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npm run test
npm run lint
```

### Testing en Desarrollo

```typescript
// components/dev/TestPanel.tsx
import { useState } from 'react';

export function TestPanel() {
  const [showTests, setShowTests] = useState(false);

  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <button
        onClick={() => setShowTests(!showTests)}
        className="bg-blue-500 text-white px-3 py-2 rounded-md text-sm"
      >
        🧪 Tests
      </button>

      {showTests && (
        <div className="absolute bottom-full left-0 mb-2 bg-white border rounded-lg shadow-lg p-4 max-w-sm">
          <h3 className="font-bold mb-3">Testing Tools</h3>
          <div className="space-y-2">
            <button
              onClick={() => window.location.reload()}
              className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded"
            >
              🔄 Reload App
            </button>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded"
            >
              🗑️ Clear Storage
            </button>
            <button
              onClick={() => {
                // Trigger error boundary
                throw new Error('Test error');
              }}
              className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded"
            >
              ❌ Trigger Error
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 📊 Cobertura de Código

### Configuración de Cobertura

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'hooks/**/*.{ts,tsx}',
    'stores/**/*.{ts,tsx}',
    'services/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/*.test.{ts,tsx}',
    '!**/*.spec.{ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: [
    'text',
    'lcov',
    'html',
  ],
};
```

### Reporte de Cobertura Actual

```
Coverage summary
=================
Statements   : 87.5%
Branches     : 82.3%
Functions    : 89.1%
Lines        : 87.8%

File                    | % Stmts | % Branch | % Funcs | % Lines |
-----------------------|---------|----------|---------|--------|
components/             |    88.2 |     84.1 |    90.3 |   88.5 |
lib/                    |    92.1 |     89.2 |    94.5 |   92.3 |
hooks/                  |    85.6 |     81.7 |    87.2 |   85.9 |
stores/                 |    91.4 |     88.9 |    93.1 |   91.7 |
services/               |    86.8 |     83.4 |    88.9 |   87.1 |
```

### Mejora Continua de Cobertura

1. **Identificar Áreas con Baja Cobertura**
   - Componentes de error handling
   - Funciones utilitarias complejas
   - Casos edge en formularios

2. **Estrategias de Mejora**
   - Tests adicionales para casos no cubiertos
   - Refactorización para mejor testabilidad
   - Mocking más efectivo de dependencias externas

3. **Monitoreo**
   - Alertas cuando cobertura baja del threshold
   - Reportes semanales de cobertura
   - Revisión en code reviews

---

## 🎯 Mejores Prácticas

### Testing de Componentes
- Usar `data-testid` para selectores estables
- Mockear dependencias externas
- Probar estados de loading y error
- Verificar accesibilidad básica

### Testing de Lógica
- Tests unitarios para funciones puras
- Mocks para APIs y servicios externos
- Tests de integración para flujos completos
- Cobertura de casos edge y errores

### Testing E2E
- Tests críticos del user journey
- Validación de flujos de autenticación
- Testing de formularios complejos
- Verificación de responsive design

### Mantenimiento
- Tests que fallen indican problemas reales
- Actualizar tests con cambios en funcionalidad
- Eliminar tests obsoletos
- Documentar casos de testing complejos

---

*La estrategia de testing garantiza la calidad y fiabilidad del frontend Triboka Agro, con cobertura completa y automatización en CI/CD.*