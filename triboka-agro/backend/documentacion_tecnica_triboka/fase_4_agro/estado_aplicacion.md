# 🗂️ Estado de la Aplicación - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Estado](#arquitectura-de-estado)
3. [Zustand Stores](#zustand-stores)
4. [React Query para Server State](#react-query-para-server-state)
5. [Gestión de Estado Local](#gestión-de-estado-local)
6. [Sincronización de Estado](#sincronización-de-estado)
7. [Persistencia de Estado](#persistencia-de-estado)
8. [Optimización de Rendimiento](#optimización-de-rendimiento)
9. [Testing de Estado](#testing-de-estado)
10. [Debugging y DevTools](#debugging-y-devtools)

---

## 🎯 Visión General

El sistema de gestión de estado de Triboka Agro está diseñado para manejar eficientemente tanto el estado del cliente como el del servidor, utilizando una combinación de Zustand para estado global del cliente y React Query para estado del servidor. La arquitectura sigue principios de inmutabilidad, predictibilidad y separación de responsabilidades.

---

## 🏗️ Arquitectura de Estado

### Capas de Estado

```
┌─────────────────────────────────────┐
│         Component State              │
│  (useState, useReducer)             │
├─────────────────────────────────────┤
│         Global Client State          │
│  (Zustand Stores)                   │
├─────────────────────────────────────┤
│         Server State                │
│  (React Query)                      │
├─────────────────────────────────────┤
│         Persistent State             │
│  (localStorage, IndexedDB)          │
└─────────────────────────────────────┘
```

### Principios de Diseño

1. **Single Source of Truth**: Cada pieza de estado tiene una ubicación clara
2. **Inmutabilidad**: Los cambios de estado crean nuevos objetos
3. **Predictibilidad**: Los cambios siguen patrones claros y testeables
4. **Separación de Responsabilidades**: Estado del cliente vs estado del servidor
5. **Performance**: Optimizaciones para evitar re-renders innecesarios

---

## 🗄️ Zustand Stores

### Auth Store

```typescript
// stores/auth.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { authService } from '@/services/auth';
import { logger } from '@/lib/logger';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'producer' | 'exporter' | 'admin';
  avatar?: string;
  company?: string;
  location?: string;
  certifications?: string[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  devtools(
    persist(
      (set, get) => ({
        // Estado inicial
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: null,

        // Acciones
        login: async (email: string, password: string) => {
          set({ loading: true, error: null });

          try {
            const { user, tokens } = await authService.login({ email, password });

            set({
              user,
              token: tokens.accessToken,
              refreshToken: tokens.refreshToken,
              isAuthenticated: true,
              loading: false,
            });

            logger.info('User logged in', { userId: user.id, role: user.role });
          } catch (error: any) {
            const errorMessage = error.message || 'Error al iniciar sesión';
            set({ error: errorMessage, loading: false });
            logger.error('Login failed', { error: errorMessage, email });
            throw error;
          }
        },

        logout: async () => {
          set({ loading: true });

          try {
            await authService.logout();
          } catch (error) {
            logger.warn('Logout API call failed', { error: error.message });
          } finally {
            set({
              user: null,
              token: null,
              refreshToken: null,
              isAuthenticated: false,
              loading: false,
              error: null,
            });

            logger.info('User logged out');
          }
        },

        refreshToken: async () => {
          const { refreshToken } = get();
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          try {
            const newToken = await authService.refreshToken();
            set({ token: newToken });
            logger.debug('Token refreshed');
          } catch (error) {
            logger.error('Token refresh failed', { error: error.message });
            // Forzar logout si el refresh falla
            get().logout();
            throw error;
          }
        },

        updateProfile: async (data: Partial<User>) => {
          const { user } = get();
          if (!user) throw new Error('No user logged in');

          set({ loading: true, error: null });

          try {
            const updatedUser = await authService.updateProfile(data);

            set({
              user: updatedUser,
              loading: false,
            });

            logger.info('Profile updated', { userId: user.id, changes: Object.keys(data) });
          } catch (error: any) {
            const errorMessage = error.message || 'Error al actualizar perfil';
            set({ error: errorMessage, loading: false });
            logger.error('Profile update failed', { error: errorMessage, userId: user.id });
            throw error;
          }
        },

        clearError: () => set({ error: null }),
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          refreshToken: state.refreshToken,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'auth-store' }
  )
);
```

### Lots Store

```typescript
// stores/lots.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { lotsService } from '@/services/lots';
import { logger } from '@/lib/logger';

export interface Lot {
  id: string;
  name: string;
  description?: string;
  weight: number;
  unit: 'kg' | 'ton' | 'lb';
  quality: 'premium' | 'standard' | 'basic';
  location: string;
  harvestDate: string;
  certifications?: string[];
  status: 'available' | 'sold' | 'reserved';
  producerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface LotFilters {
  status?: string;
  quality?: string;
  location?: string;
  minWeight?: number;
  maxWeight?: number;
  harvestDateFrom?: string;
  harvestDateTo?: string;
  certifications?: string[];
  producerId?: string;
}

export interface LotsState {
  lots: Lot[];
  currentLot: Lot | null;
  filters: LotFilters;
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
  loading: boolean;
  error: string | null;
  selectedLots: string[];
}

export interface LotsActions {
  fetchLots: (filters?: LotFilters, page?: number) => Promise<void>;
  getLotById: (id: string) => Promise<void>;
  createLot: (data: Omit<Lot, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Lot>;
  updateLot: (id: string, data: Partial<Lot>) => Promise<void>;
  deleteLot: (id: string) => Promise<void>;
  shareLot: (id: string, userId: string, permissions: string[]) => Promise<void>;
  setFilters: (filters: LotFilters) => void;
  clearFilters: () => void;
  setSelectedLots: (lots: string[]) => void;
  toggleLotSelection: (lotId: string) => void;
  clearSelection: () => void;
  clearError: () => void;
}

export const useLotsStore = create<LotsState & LotsActions>()(
  devtools(
    (set, get) => ({
      // Estado inicial
      lots: [],
      currentLot: null,
      filters: {},
      pagination: {
        page: 1,
        limit: 20,
        total: 0,
        hasMore: false,
      },
      loading: false,
      error: null,
      selectedLots: [],

      // Acciones
      fetchLots: async (filters = {}, page = 1) => {
        set({ loading: true, error: null });

        try {
          const response = await lotsService.getLots(filters, page, get().pagination.limit);

          set({
            lots: page === 1 ? response.lots : [...get().lots, ...response.lots],
            pagination: {
              page,
              limit: get().pagination.limit,
              total: response.total,
              hasMore: response.hasMore,
            },
            filters,
            loading: false,
          });

          logger.debug('Lots fetched', {
            count: response.lots.length,
            total: response.total,
            filters,
            page
          });
        } catch (error: any) {
          const errorMessage = error.message || 'Error al cargar lotes';
          set({ error: errorMessage, loading: false });
          logger.error('Failed to fetch lots', { error: errorMessage, filters, page });
        }
      },

      getLotById: async (id: string) => {
        set({ loading: true, error: null });

        try {
          const lot = await lotsService.getLotById(id);

          set({
            currentLot: lot,
            loading: false,
          });

          logger.debug('Lot fetched', { lotId: id });
        } catch (error: any) {
          const errorMessage = error.message || 'Error al cargar lote';
          set({ error: errorMessage, loading: false });
          logger.error('Failed to fetch lot', { error: errorMessage, lotId: id });
        }
      },

      createLot: async (data) => {
        set({ loading: true, error: null });

        try {
          const newLot = await lotsService.createLot(data);

          set(state => ({
            lots: [newLot, ...state.lots],
            loading: false,
          }));

          logger.info('Lot created', { lotId: newLot.id, producerId: newLot.producerId });
          return newLot;
        } catch (error: any) {
          const errorMessage = error.message || 'Error al crear lote';
          set({ error: errorMessage, loading: false });
          logger.error('Failed to create lot', { error: errorMessage, data });
          throw error;
        }
      },

      updateLot: async (id: string, data) => {
        set({ loading: true, error: null });

        try {
          const updatedLot = await lotsService.updateLot(id, data);

          set(state => ({
            lots: state.lots.map(lot =>
              lot.id === id ? { ...lot, ...updatedLot } : lot
            ),
            currentLot: state.currentLot?.id === id ? { ...state.currentLot, ...updatedLot } : state.currentLot,
            loading: false,
          }));

          logger.info('Lot updated', { lotId: id, changes: Object.keys(data) });
        } catch (error: any) {
          const errorMessage = error.message || 'Error al actualizar lote';
          set({ error: errorMessage, loading: false });
          logger.error('Failed to update lot', { error: errorMessage, lotId: id, data });
        }
      },

      deleteLot: async (id: string) => {
        set({ loading: true, error: null });

        try {
          await lotsService.deleteLot(id);

          set(state => ({
            lots: state.lots.filter(lot => lot.id !== id),
            currentLot: state.currentLot?.id === id ? null : state.currentLot,
            selectedLots: state.selectedLots.filter(lotId => lotId !== id),
            loading: false,
          }));

          logger.info('Lot deleted', { lotId: id });
        } catch (error: any) {
          const errorMessage = error.message || 'Error al eliminar lote';
          set({ error: errorMessage, loading: false });
          logger.error('Failed to delete lot', { error: errorMessage, lotId: id });
        }
      },

      shareLot: async (id: string, userId: string, permissions: string[]) => {
        try {
          await lotsService.shareLot(id, userId, permissions);
          logger.info('Lot shared', { lotId: id, sharedWith: userId, permissions });
        } catch (error: any) {
          logger.error('Failed to share lot', {
            error: error.message,
            lotId: id,
            sharedWith: userId
          });
          throw error;
        }
      },

      setFilters: (filters: LotFilters) => {
        set({ filters });
        logger.debug('Filters updated', { filters });
      },

      clearFilters: () => {
        set({ filters: {} });
        logger.debug('Filters cleared');
      },

      setSelectedLots: (selectedLots: string[]) => {
        set({ selectedLots });
      },

      toggleLotSelection: (lotId: string) => {
        set(state => ({
          selectedLots: state.selectedLots.includes(lotId)
            ? state.selectedLots.filter(id => id !== lotId)
            : [...state.selectedLots, lotId]
        }));
      },

      clearSelection: () => {
        set({ selectedLots: [] });
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'lots-store' }
  )
);
```

### UI Store

```typescript
// stores/ui.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface UiState {
  theme: 'light' | 'dark' | 'system';
  sidebar: {
    collapsed: boolean;
    mobileOpen: boolean;
  };
  modals: {
    [key: string]: boolean;
  };
  notifications: {
    show: boolean;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  } | null;
  loading: {
    global: boolean;
    message?: string;
  };
}

export interface UiActions {
  setTheme: (theme: UiState['theme']) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setMobileSidebarOpen: (open: boolean) => void;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  closeAllModals: () => void;
  showNotification: (notification: Omit<UiState['notifications'], 'show'>) => void;
  hideNotification: () => void;
  setGlobalLoading: (loading: boolean, message?: string) => void;
}

export const useUiStore = create<UiState & UiActions>()(
  devtools(
    persist(
      (set, get) => ({
        // Estado inicial
        theme: 'system',
        sidebar: {
          collapsed: false,
          mobileOpen: false,
        },
        modals: {},
        notifications: null,
        loading: {
          global: false,
        },

        // Acciones
        setTheme: (theme: UiState['theme']) => {
          set({ theme });

          // Aplicar tema al documento
          const root = document.documentElement;
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
          const appliedTheme = theme === 'system' ? systemTheme : theme;

          root.classList.remove('light', 'dark');
          root.classList.add(appliedTheme);
        },

        toggleSidebar: () => {
          set(state => ({
            sidebar: {
              ...state.sidebar,
              collapsed: !state.sidebar.collapsed,
            },
          }));
        },

        setSidebarCollapsed: (collapsed: boolean) => {
          set(state => ({
            sidebar: {
              ...state.sidebar,
              collapsed,
            },
          }));
        },

        setMobileSidebarOpen: (open: boolean) => {
          set(state => ({
            sidebar: {
              ...state.sidebar,
              mobileOpen: open,
            },
          }));
        },

        openModal: (modalId: string) => {
          set(state => ({
            modals: {
              ...state.modals,
              [modalId]: true,
            },
          }));
        },

        closeModal: (modalId: string) => {
          set(state => ({
            modals: {
              ...state.modals,
              [modalId]: false,
            },
          }));
        },

        closeAllModals: () => {
          set({ modals: {} });
        },

        showNotification: (notification) => {
          set({
            notifications: {
              ...notification,
              show: true,
            },
          });
        },

        hideNotification: () => {
          set({ notifications: null });
        },

        setGlobalLoading: (global: boolean, message?: string) => {
          set({
            loading: {
              global,
              message,
            },
          });
        },
      }),
      {
        name: 'ui-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebar: {
            collapsed: state.sidebar.collapsed,
          },
        }),
      }
    ),
    { name: 'ui-store' }
  )
);
```

---

## 🔄 React Query para Server State

### Configuración de Query Client

```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';
import { logger } from './logger';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      gcTime: 10 * 60 * 1000, // 10 minutos (antes cacheTime)
      retry: (failureCount, error: any) => {
        // No reintentar en errores de autenticación
        if (error?.status === 401 || error?.status === 403) {
          return false;
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      onError: (error: any) => {
        logger.error('Query error', {
          message: error.message,
          status: error.status,
          endpoint: error.endpoint,
        });
      },
    },
    mutations: {
      retry: false,
      onError: (error: any) => {
        logger.error('Mutation error', {
          message: error.message,
          status: error.status,
        });
      },
    },
  },
});

// Query Client Provider
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
```

### Custom Hooks con React Query

```typescript
// hooks/useLots.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lotsService } from '@/services/lots';
import { useAuthStore } from '@/stores/auth';
import { logger } from '@/lib/logger';

export function useLots(filters?: any, page = 1, limit = 20) {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ['lots', filters, page, limit],
    queryFn: () => lotsService.getLots(filters, page, limit),
    enabled: isAuthenticated,
    keepPreviousData: true,
    select: (data) => ({
      ...data,
      lots: data.lots.map(lot => ({
        ...lot,
        createdAt: new Date(lot.createdAt),
        updatedAt: new Date(lot.updatedAt),
        harvestDate: new Date(lot.harvestDate),
      })),
    }),
    onSuccess: (data) => {
      logger.debug('Lots query successful', { count: data.lots.length });
    },
    onError: (error: any) => {
      logger.error('Lots query failed', { error: error.message });
    },
  });
}

export function useLot(id: string) {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ['lot', id],
    queryFn: () => lotsService.getLotById(id),
    enabled: isAuthenticated && !!id,
    select: (data) => ({
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      harvestDate: new Date(data.harvestDate),
    }),
    onSuccess: (data) => {
      logger.debug('Lot query successful', { lotId: data.id });
    },
    onError: (error: any) => {
      logger.error('Lot query failed', { error: error.message, lotId: id });
    },
  });
}

export function useCreateLot() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  return useMutation({
    mutationFn: lotsService.createLot,
    onSuccess: (newLot) => {
      // Invalidar y refetch de listas de lotes
      queryClient.invalidateQueries(['lots']);

      // Agregar el nuevo lote al cache
      queryClient.setQueryData(['lot', newLot.id], newLot);

      logger.info('Lot created successfully', {
        lotId: newLot.id,
        userId: user?.id
      });
    },
    onError: (error: any) => {
      logger.error('Lot creation failed', {
        error: error.message,
        userId: user?.id
      });
    },
  });
}

export function useUpdateLot() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      lotsService.updateLot(id, data),
    onSuccess: (updatedLot, { id }) => {
      // Actualizar el lote en todas las queries relevantes
      queryClient.setQueryData(['lot', id], updatedLot);

      // Actualizar en listas de lotes
      queryClient.setQueriesData(['lots'], (oldData: any) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          lots: oldData.lots.map((lot: any) =>
            lot.id === id ? { ...lot, ...updatedLot } : lot
          ),
        };
      });

      logger.info('Lot updated successfully', {
        lotId: id,
        userId: user?.id,
        changes: Object.keys(updatedLot)
      });
    },
    onError: (error: any, { id }) => {
      logger.error('Lot update failed', {
        error: error.message,
        lotId: id,
        userId: user?.id
      });
    },
  });
}

export function useDeleteLot() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  return useMutation({
    mutationFn: lotsService.deleteLot,
    onSuccess: (_, deletedId) => {
      // Remover de todas las queries
      queryClient.removeQueries(['lot', deletedId]);

      // Remover de listas de lotes
      queryClient.setQueriesData(['lots'], (oldData: any) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          lots: oldData.lots.filter((lot: any) => lot.id !== deletedId),
        };
      });

      logger.info('Lot deleted successfully', {
        lotId: deletedId,
        userId: user?.id
      });
    },
    onError: (error: any, deletedId) => {
      logger.error('Lot deletion failed', {
        error: error.message,
        lotId: deletedId,
        userId: user?.id
      });
    },
  });
}
```

---

## 🔧 Gestión de Estado Local

### Custom Hooks para Estado Local

```typescript
// hooks/useLocalState.ts
import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
}

export function useSessionStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
}

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
}
```

### Form State Management

```typescript
// hooks/useForm.ts
import { useState, useCallback } from 'react';

export interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

export interface FormActions<T> {
  setValue: <K extends keyof T>(field: K, value: T[K]) => void;
  setValues: (values: Partial<T>) => void;
  setError: <K extends keyof T>(field: K, error: string) => void;
  setErrors: (errors: Partial<Record<keyof T, string>>) => void;
  setTouched: <K extends keyof T>(field: K, touched?: boolean) => void;
  setSubmitting: (submitting: boolean) => void;
  reset: (initialValues?: T) => void;
  validate: () => boolean;
}

export function useForm<T extends Record<string, any>>(
  initialValues: T,
  validate?: (values: T) => Partial<Record<keyof T, string>>
) {
  const [state, setState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true,
  });

  const setValue = useCallback(<K extends keyof T>(field: K, value: T[K]) => {
    setState(prevState => {
      const newValues = { ...prevState.values, [field]: value };
      const errors = validate ? validate(newValues) : prevState.errors;
      const isValid = Object.keys(errors).length === 0;

      return {
        ...prevState,
        values: newValues,
        errors,
        isValid,
      };
    });
  }, [validate]);

  const setValues = useCallback((values: Partial<T>) => {
    setState(prevState => {
      const newValues = { ...prevState.values, ...values };
      const errors = validate ? validate(newValues) : prevState.errors;
      const isValid = Object.keys(errors).length === 0;

      return {
        ...prevState,
        values: newValues,
        errors,
        isValid,
      };
    });
  }, [validate]);

  const setError = useCallback(<K extends keyof T>(field: K, error: string) => {
    setState(prevState => ({
      ...prevState,
      errors: { ...prevState.errors, [field]: error },
      isValid: false,
    }));
  }, []);

  const setErrors = useCallback((errors: Partial<Record<keyof T, string>>) => {
    setState(prevState => ({
      ...prevState,
      errors,
      isValid: Object.keys(errors).length === 0,
    }));
  }, []);

  const setTouched = useCallback(<K extends keyof T>(field: K, touched = true) => {
    setState(prevState => ({
      ...prevState,
      touched: { ...prevState.touched, [field]: touched },
    }));
  }, []);

  const setSubmitting = useCallback((isSubmitting: boolean) => {
    setState(prevState => ({
      ...prevState,
      isSubmitting,
    }));
  }, []);

  const reset = useCallback((newInitialValues = initialValues) => {
    setState({
      values: newInitialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
      isValid: true,
    });
  }, [initialValues]);

  const validateForm = useCallback(() => {
    if (!validate) return true;

    const errors = validate(state.values);
    const isValid = Object.keys(errors).length === 0;

    setState(prevState => ({
      ...prevState,
      errors,
      isValid,
    }));

    return isValid;
  }, [validate, state.values]);

  return {
    ...state,
    setValue,
    setValues,
    setError,
    setErrors,
    setTouched,
    setSubmitting,
    reset,
    validate: validateForm,
  };
}
```

---

## 🔄 Sincronización de Estado

### Estado Sincronizado entre Pestañas

```typescript
// lib/stateSync.ts
import { useEffect, useRef } from 'react';

export function useBroadcastChannel<T>(
  channelName: string,
  onMessage: (data: T) => void
) {
  const channelRef = useRef<BroadcastChannel | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    channelRef.current = new BroadcastChannel(channelName);

    const handleMessage = (event: MessageEvent<T>) => {
      onMessage(event.data);
    };

    channelRef.current.addEventListener('message', handleMessage);

    return () => {
      channelRef.current?.removeEventListener('message', handleMessage);
      channelRef.current?.close();
    };
  }, [channelName, onMessage]);

  const postMessage = useCallback((data: T) => {
    channelRef.current?.postMessage(data);
  }, []);

  return { postMessage };
}

export function useCrossTabState<T>(
  key: string,
  initialValue: T,
  serialize: (value: T) => string = JSON.stringify,
  deserialize: (value: string) => T = JSON.parse
) {
  const [state, setState] = useLocalStorage(key, initialValue);
  const { postMessage } = useBroadcastChannel<T>(`state-${key}`, (data) => {
    setState(data);
  });

  const updateState = useCallback((newValue: T | ((prev: T) => T)) => {
    setState((prev) => {
      const value = typeof newValue === 'function' ? (newValue as Function)(prev) : newValue;
      postMessage(value);
      return value;
    });
  }, [setState, postMessage]);

  return [state, updateState] as const;
}
```

### Sincronización con Backend

```typescript
// hooks/useRealtimeSync.ts
import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { logger } from '@/lib/logger';

export function useRealtimeSync() {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001');

        ws.onopen = () => {
          logger.info('WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            switch (message.type) {
              case 'LOT_UPDATED':
                queryClient.invalidateQueries(['lot', message.data.id]);
                queryClient.invalidateQueries(['lots']);
                break;

              case 'LOT_CREATED':
                queryClient.invalidateQueries(['lots']);
                break;

              case 'LOT_DELETED':
                queryClient.removeQueries(['lot', message.data.id]);
                queryClient.invalidateQueries(['lots']);
                break;

              case 'CONTRACT_UPDATED':
                queryClient.invalidateQueries(['contracts']);
                break;

              default:
                logger.debug('Unknown WebSocket message type', { type: message.type });
            }
          } catch (error) {
            logger.error('Error processing WebSocket message', { error: error.message });
          }
        };

        ws.onclose = () => {
          logger.warn('WebSocket disconnected, attempting to reconnect...');
          setTimeout(connect, 5000);
        };

        ws.onerror = (error) => {
          logger.error('WebSocket error', { error });
        };

        wsRef.current = ws;
      } catch (error) {
        logger.error('Failed to connect to WebSocket', { error: error.message });
      }
    };

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, [queryClient]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  return { sendMessage };
}
```

---

## 💾 Persistencia de Estado

### IndexedDB para Grandes Datasets

```typescript
// lib/indexedDB.ts
export interface IDBConfig {
  name: string;
  version: number;
  stores: {
    [storeName: string]: {
      keyPath: string;
      indexes?: { name: string; keyPath: string; unique?: boolean }[];
    };
  };
}

export class IndexedDB {
  private db: IDBDatabase | null = null;
  private config: IDBConfig;

  constructor(config: IDBConfig) {
    this.config = config;
  }

  async open(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.config.name, this.config.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(request.result);
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Crear object stores
        Object.entries(this.config.stores).forEach(([storeName, storeConfig]) => {
          if (!db.objectStoreNames.contains(storeName)) {
            const store = db.createObjectStore(storeName, {
              keyPath: storeConfig.keyPath,
            });

            // Crear índices
            storeConfig.indexes?.forEach(index => {
              store.createIndex(index.name, index.keyPath, { unique: index.unique });
            });
          }
        });
      };
    });
  }

  async get<T>(storeName: string, key: string | number): Promise<T | null> {
    if (!this.db) await this.open();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result || null);
    });
  }

  async getAll<T>(storeName: string): Promise<T[]> {
    if (!this.db) await this.open();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async put<T>(storeName: string, value: T): Promise<void> {
    if (!this.db) await this.open();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(value);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async delete(storeName: string, key: string | number): Promise<void> {
    if (!this.db) await this.open();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async clear(storeName: string): Promise<void> {
    if (!this.db) await this.open();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
}

// Configuración para la app
export const dbConfig: IDBConfig = {
  name: 'triboka-db',
  version: 1,
  stores: {
    lots: {
      keyPath: 'id',
      indexes: [
        { name: 'producerId', keyPath: 'producerId' },
        { name: 'status', keyPath: 'status' },
        { name: 'createdAt', keyPath: 'createdAt' },
      ],
    },
    contracts: {
      keyPath: 'id',
      indexes: [
        { name: 'buyerId', keyPath: 'buyerId' },
        { name: 'sellerId', keyPath: 'sellerId' },
        { name: 'status', keyPath: 'status' },
      ],
    },
    cache: {
      keyPath: 'key',
      indexes: [
        { name: 'timestamp', keyPath: 'timestamp' },
      ],
    },
  },
};

export const db = new IndexedDB(dbConfig);
```

### Persistencia con Zustand

```typescript
// stores/persistedStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { db } from '@/lib/indexedDB';

interface PersistedData {
  userPreferences: {
    theme: 'light' | 'dark' | 'system';
    language: string;
    notifications: boolean;
  };
  recentSearches: string[];
  lastVisitedLots: string[];
}

interface PersistedState extends PersistedData {
  setUserPreferences: (preferences: Partial<PersistedData['userPreferences']>) => void;
  addRecentSearch: (search: string) => void;
  clearRecentSearches: () => void;
  addLastVisitedLot: (lotId: string) => void;
  clearLastVisitedLots: () => void;
}

const storage = {
  getItem: async (name: string) => {
    try {
      const data = await db.get('cache', name);
      return data?.value;
    } catch {
      return null;
    }
  },
  setItem: async (name: string, value: string) => {
    try {
      await db.put('cache', { key: name, value, timestamp: Date.now() });
    } catch (error) {
      console.warn('Failed to persist to IndexedDB:', error);
    }
  },
  removeItem: async (name: string) => {
    try {
      await db.delete('cache', name);
    } catch (error) {
      console.warn('Failed to remove from IndexedDB:', error);
    }
  },
};

export const usePersistedStore = create<PersistedState>()(
  persist(
    (set, get) => ({
      userPreferences: {
        theme: 'system',
        language: 'es',
        notifications: true,
      },
      recentSearches: [],
      lastVisitedLots: [],

      setUserPreferences: (preferences) =>
        set((state) => ({
          userPreferences: { ...state.userPreferences, ...preferences },
        })),

      addRecentSearch: (search) =>
        set((state) => ({
          recentSearches: [
            search,
            ...state.recentSearches.filter(s => s !== search).slice(0, 9),
          ],
        })),

      clearRecentSearches: () =>
        set({ recentSearches: [] }),

      addLastVisitedLot: (lotId) =>
        set((state) => ({
          lastVisitedLots: [
            lotId,
            ...state.lastVisitedLots.filter(id => id !== lotId).slice(0, 9),
          ],
        })),

      clearLastVisitedLots: () =>
        set({ lastVisitedLots: [] }),
    }),
    {
      name: 'persisted-store',
      storage: createJSONStorage(() => storage),
      partialize: (state) => ({
        userPreferences: state.userPreferences,
        recentSearches: state.recentSearches.slice(0, 10),
        lastVisitedLots: state.lastVisitedLots.slice(0, 10),
      }),
    }
  )
);
```

---

## ⚡ Optimización de Rendimiento

### Memoización Selectiva

```typescript
// hooks/useMemoizedState.ts
import { useMemo, useCallback } from 'react';
import { shallow } from 'zustand/shallow';

export function useShallowSelector<T, U>(
  store: any,
  selector: (state: T) => U
): U {
  return store(selector, shallow);
}

export function useMemoizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  return useCallback(callback, deps);
}

export function useMemoizedValue<T>(value: T, deps: React.DependencyList): T {
  return useMemo(() => value, deps);
}
```

### Lazy Loading de Stores

```typescript
// stores/lazyStore.ts
import { create } from 'zustand';

interface LazyState {
  loadedStores: Set<string>;
  loadStore: (storeName: string) => Promise<void>;
}

export const useLazyStore = create<LazyState>((set, get) => ({
  loadedStores: new Set(),

  loadStore: async (storeName: string) => {
    const { loadedStores } = get();

    if (loadedStores.has(storeName)) {
      return;
    }

    try {
      // Lazy load del store
      switch (storeName) {
        case 'blockchain':
          await import('../stores/blockchain');
          break;
        case 'reports':
          await import('../stores/reports');
          break;
        // Agregar más stores según sea necesario
      }

      set(state => ({
        loadedStores: new Set([...state.loadedStores, storeName]),
      }));
    } catch (error) {
      console.error(`Failed to load store ${storeName}:`, error);
    }
  },
}));
```

### Optimización de Re-renders

```typescript
// components/optimized/MemoizedLotCard.tsx
import { memo } from 'react';
import { LotCard } from '../dashboard/LotCard';

export const MemoizedLotCard = memo(LotCard, (prevProps, nextProps) => {
  // Comparación superficial de props
  return (
    prevProps.lot.id === nextProps.lot.id &&
    prevProps.lot.status === nextProps.lot.status &&
    prevProps.lot.updatedAt === nextProps.lot.updatedAt &&
    prevProps.onView === nextProps.onView &&
    prevProps.onShare === nextProps.onShare &&
    prevProps.onEdit === nextProps.onEdit
  );
});
```

---

## 🧪 Testing de Estado

### Testing de Zustand Stores

```typescript
// tests/stores/auth.test.ts
import { act, renderHook } from '@testing-library/react';
import { useAuthStore } from '@/stores/auth';

// Mock del servicio de auth
jest.mock('@/services/auth');

describe('Auth Store', () => {
  beforeEach(() => {
    // Limpiar el store antes de cada test
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

    // Mock del servicio
    const { authService } = require('@/services/auth');
    authService.login.mockResolvedValue({ user: mockUser, tokens: mockTokens });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe('token');
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.loading).toBe(false);
  });

  it('should handle login error', async () => {
    const { authService } = require('@/services/auth');
    authService.login.mockRejectedValue(new Error('Invalid credentials'));

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      try {
        await result.current.login('test@example.com', 'wrongpassword');
      } catch (error) {
        // Error esperado
      }
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBe('Invalid credentials');
    expect(result.current.loading).toBe(false);
  });

  it('should handle logout', async () => {
    // Setup: usuario logueado
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com' },
      token: 'token',
      isAuthenticated: true,
    });

    const { authService } = require('@/services/auth');
    authService.logout.mockResolvedValue();

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

### Testing de React Query

```typescript
// tests/hooks/useLots.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useLots } from '@/hooks/useLots';

// Mock del servicio
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
    const mockLots = [
      { id: '1', name: 'Lot 1', weight: 100 },
      { id: '2', name: 'Lot 2', weight: 200 },
    ];

    const { lotsService } = require('@/services/lots');
    lotsService.getLots.mockResolvedValue({
      lots: mockLots,
      total: 2,
      page: 1,
      limit: 20,
      hasMore: false,
    });

    const { result } = renderHook(() => useLots(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.lots).toEqual(mockLots);
    expect(lotsService.getLots).toHaveBeenCalledWith(undefined, 1, 20);
  });

  it('should handle error state', async () => {
    const { lotsService } = require('@/services/lots');
    lotsService.getLots.mockRejectedValue(new Error('API Error'));

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

## 🔍 Debugging y DevTools

### Zustand DevTools

```typescript
// stores/index.ts
import { devtools } from 'zustand/middleware';
import { create } from 'zustand';

// Store con devtools habilitados
export const useDebugStore = create(
  devtools(
    (set) => ({
      debugMode: false,
      actions: [],

      toggleDebugMode: () =>
        set((state) => ({ debugMode: !state.debugMode }), false, 'toggleDebugMode'),

      logAction: (action: string, data?: any) =>
        set(
          (state) => ({
            actions: [...state.actions.slice(-9), { action, data, timestamp: Date.now() }],
          }),
          false,
          'logAction'
        ),

      clearActions: () =>
        set({ actions: [] }, false, 'clearActions'),
    }),
    { name: 'debug-store' }
  )
);
```

### React Query DevTools

```typescript
// components/dev/ReactQueryDevTools.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

export function ReactQueryDevTools() {
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <ReactQueryDevtools
      initialIsOpen={false}
      position="bottom-right"
    />
  );
}
```

### Custom Debug Panel

```typescript
// components/dev/DebugPanel.tsx
import { useState } from 'react';
import { useAuthStore } from '@/stores/auth';
import { useLotsStore } from '@/stores/lots';
import { useUiStore } from '@/stores/ui';
import { useQueryClient } from '@tanstack/react-query';

export function DebugPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const auth = useAuthStore();
  const lots = useLotsStore();
  const ui = useUiStore();
  const queryClient = useQueryClient();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const queryCache = queryClient.getQueryCache().getAll();

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gray-900 text-white px-3 py-2 rounded-md text-sm"
      >
        🐛 Debug
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 bg-white border rounded-lg shadow-lg p-4 max-w-md max-h-96 overflow-auto">
          <h3 className="font-bold mb-3">Debug Panel</h3>

          <div className="space-y-4">
            {/* Auth State */}
            <div>
              <h4 className="font-semibold text-sm">Auth State</h4>
              <pre className="text-xs bg-gray-100 p-2 rounded">
                {JSON.stringify(
                  {
                    isAuthenticated: auth.isAuthenticated,
                    user: auth.user ? { id: auth.user.id, email: auth.user.email } : null,
                    loading: auth.loading,
                    error: auth.error,
                  },
                  null,
                  2
                )}
              </pre>
            </div>

            {/* Lots State */}
            <div>
              <h4 className="font-semibold text-sm">Lots State</h4>
              <pre className="text-xs bg-gray-100 p-2 rounded">
                {JSON.stringify(
                  {
                    lotsCount: lots.lots.length,
                    loading: lots.loading,
                    error: lots.error,
                    selectedCount: lots.selectedLots.length,
                  },
                  null,
                  2
                )}
              </pre>
            </div>

            {/* UI State */}
            <div>
              <h4 className="font-semibold text-sm">UI State</h4>
              <pre className="text-xs bg-gray-100 p-2 rounded">
                {JSON.stringify(
                  {
                    theme: ui.theme,
                    sidebarCollapsed: ui.sidebar.collapsed,
                    notifications: ui.notifications,
                  },
                  null,
                  2
                )}
              </pre>
            </div>

            {/* Query Cache */}
            <div>
              <h4 className="font-semibold text-sm">Query Cache ({queryCache.length})</h4>
              <div className="max-h-32 overflow-auto">
                {queryCache.slice(0, 5).map((query) => (
                  <div key={query.queryHash} className="text-xs">
                    <div className="font-medium">{query.queryHash}</div>
                    <div className="text-gray-600">
                      Status: {query.state.status}, Data: {query.state.data ? 'Yes' : 'No'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              <button
                onClick={() => queryClient.invalidateQueries()}
                className="bg-blue-500 text-white px-2 py-1 rounded text-xs"
              >
                Invalidate All
              </button>
              <button
                onClick={() => queryClient.clear()}
                className="bg-red-500 text-white px-2 py-1 rounded text-xs"
              >
                Clear Cache
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🔐 Configuración de Sesión por Rol

### Sidebar Dinámico

El sidebar de la aplicación se configura dinámicamente según el rol del usuario, mostrando únicamente las opciones relevantes para su perfil y responsabilidades.

#### Roles y Navegación

##### Admin
```typescript
const adminNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Gestión de Usuarios', href: '/admin/users', icon: Users },
  { name: 'Empresas', href: '/admin/companies', icon: Building },
  { name: 'Lotes', href: '/admin/lots', icon: Package },
  { name: 'Contratos', href: '/admin/contracts', icon: FileText },
  { name: 'Deal Room / Broker', href: '/admin/deal-room', icon: Handshake },
  { name: 'Licencias', href: '/admin/licenses', icon: Shield },
  { name: 'Soporte Técnico', href: '/admin/support', icon: HeadphonesIcon },
  { name: 'Tickets', href: '/admin/tickets', icon: Ticket },
  { name: 'API Management', href: '/admin/api', icon: Key },
  { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
  { name: 'Configuración', href: '/admin/settings', icon: Settings },
];
```

**Funcionalidades del Admin:**
- **Gestión de Usuarios**: Crear, editar, desactivar cuentas de usuario
- **Empresas**: Administrar perfiles de empresas registradas
- **Lotes**: Supervisar todos los lotes del sistema
- **Contratos**: Gestionar contratos entre todas las partes
- **Deal Room / Broker**: Facilitar negociaciones entre productores y exportadores
- **Licencias**: Gestionar licencias de uso del sistema
- **Soporte Técnico**: Atender consultas y problemas técnicos
- **Tickets**: Sistema de tickets para soporte al usuario
- **API Management**: Configurar y monitorear APIs del sistema
- **Analytics**: Métricas globales del sistema
- **Configuración**: Ajustes del sistema y preferencias administrativas

##### Producer (Productor)
```typescript
const producerNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Mis Lotes', href: '/producer/lots', icon: Package },
  { name: 'Contratos', href: '/producer/contracts', icon: FileText },
  { name: 'Certificaciones', href: '/producer/certifications', icon: FileCheck },
  { name: 'Pagos', href: '/producer/payments', icon: CreditCard },
  { name: 'Configuración', href: '/producer/settings', icon: Settings },
];
```

**Funcionalidades del Productor:**
- **Mis Lotes**: Gestionar lotes propios (crear, editar, publicar)
- **Contratos**: Ver contratos activos y negociaciones
- **Certificaciones**: Gestionar certificaciones agrícolas
- **Pagos**: Historial de pagos y facturación
- **Configuración**: Perfil personal y preferencias

##### Exporter (Exportador)
```typescript
const exporterNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Marketplace', href: '/exporter/marketplace', icon: ShoppingCart },
  { name: 'Mis Contratos', href: '/exporter/contracts', icon: FileText },
  { name: 'Lotes Comprados', href: '/exporter/lots', icon: Package },
  { name: 'Analytics', href: '/exporter/analytics', icon: BarChart3 },
  { name: 'Configuración', href: '/exporter/settings', icon: Settings },
];
```

**Funcionalidades del Exportador:**
- **Marketplace**: Explorar y comprar lotes disponibles
- **Mis Contratos**: Gestionar contratos de exportación
- **Lotes Comprados**: Seguimiento de lotes adquiridos
- **Analytics**: Métricas de compras y rendimiento
- **Configuración**: Perfil de empresa y preferencias comerciales

##### Buyer (Comprador)
```typescript
const buyerNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Buscar Lotes', href: '/buyer/search', icon: Search },
  { name: 'Mis Compras', href: '/buyer/purchases', icon: ShoppingCart },
  { name: 'Contratos', href: '/buyer/contracts', icon: FileText },
  { name: 'Favoritos', href: '/buyer/favorites', icon: Heart },
  { name: 'Configuración', href: '/buyer/settings', icon: Settings },
];
```

**Funcionalidades del Comprador:**
- **Buscar Lotes**: Buscador avanzado de lotes disponibles
- **Mis Compras**: Historial de compras realizadas
- **Contratos**: Gestionar contratos de compra
- **Favoritos**: Lotes marcados como favoritos
- **Configuración**: Perfil personal y preferencias de búsqueda

### Implementación del Sidebar

```typescript
// components/layout/sidebar.tsx
export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  if (!user) return null;

  // Obtener navegación según el rol
  const userNav = navigation[user.role as keyof typeof navigation] || [];

  return (
    <div className="flex h-full w-64 flex-col bg-white border-r">
      {/* Header */}
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold text-green-700">Triboka</h1>
      </div>

      <Separator />

      {/* Navegación */}
      <nav className="flex-1 space-y-1 p-4">
        {userNav.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start',
                  isActive && 'bg-green-50 text-green-700 hover:bg-green-100'
                )}
              >
                <item.icon className="mr-3 h-4 w-4" />
                {item.name}
              </Button>
            </Link>
          );
        })}
      </nav>

      <Separator />

      {/* Perfil de Usuario */}
      <div className="p-4">
        <div className="flex items-center space-x-3 mb-4">
          <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
            <User className="h-4 w-4 text-green-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user.email}
            </p>
            <p className="text-xs text-gray-400 capitalize">
              {user.role}
            </p>
          </div>
        </div>

        <Button
          variant="ghost"
          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
          onClick={logout}
        >
          <LogOut className="mr-3 h-4 w-4" />
          Cerrar Sesión
        </Button>
      </div>
    </div>
  );
}
```

### Configuración por Rol

Cada rol tiene su propia página de configuración con opciones específicas:

#### Configuración de Admin
- Configuración del sistema
- Gestión de permisos globales
- Configuración de APIs
- Parámetros de negocio
- Configuración de notificaciones del sistema

#### Configuración de Producer
- Perfil de productor
- Preferencias de certificaciones
- Configuración de pagos
- Notificaciones de mercado
- Configuración de ubicación

#### Configuración de Exporter
- Perfil de empresa
- Preferencias de compra
- Configuración de envíos
- Notificaciones comerciales
- Configuración de mercado

#### Configuración de Buyer
- Perfil personal
- Preferencias de búsqueda
- Configuración de alertas
- Notificaciones de lotes
- Configuración de favoritos

### Seguridad y Autorización

```typescript
// hooks/useRoleAccess.ts
export function useRoleAccess() {
  const { user } = useAuthStore();

  const hasAccess = useCallback((requiredRoles: string[]) => {
    if (!user) return false;
    return requiredRoles.includes(user.role);
  }, [user]);

  const isAdmin = user?.role === 'admin';
  const isProducer = user?.role === 'producer';
  const isExporter = user?.role === 'exporter';
  const isBuyer = user?.role === 'buyer';

  return {
    hasAccess,
    isAdmin,
    isProducer,
    isExporter,
    isBuyer,
    userRole: user?.role,
  };
}
```

### Gestión de Estado de Sesión

```typescript
// stores/session.ts
export interface SessionState {
  user: User | null;
  roleConfig: RoleConfig | null;
  permissions: string[];
  sessionStart: Date | null;
  lastActivity: Date | null;
}

export interface RoleConfig {
  role: string;
  navigation: NavigationItem[];
  permissions: string[];
  features: string[];
  limits: {
    maxLots?: number;
    maxContracts?: number;
    apiCallsPerHour?: number;
  };
}
```

---

## 📚 Conclusión