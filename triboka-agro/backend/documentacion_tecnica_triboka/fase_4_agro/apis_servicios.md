# 🔌 APIs y Servicios - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de API](#arquitectura-de-api)
3. [Cliente HTTP](#cliente-http)
4. [Servicios de Datos](#servicios-de-datos)
5. [Autenticación y Autorización](#autenticación-y-autorización)
6. [Gestión de Estado API](#gestión-de-estado-api)
7. [Manejo de Errores](#manejo-de-errores)
8. [Caching y Optimización](#caching-y-optimización)
9. [APIs Externas](#apis-externas)
10. [Testing de APIs](#testing-de-apis)
11. [Monitoreo y Logging](#monitoreo-y-logging)

---

## 🎯 Visión General

El sistema de APIs y servicios de Triboka Agro está diseñado para proporcionar una comunicación eficiente y segura entre el frontend y los servicios backend. La arquitectura sigue principios de separación de responsabilidades, con capas claramente definidas para diferentes tipos de operaciones.

---

## 🏗️ Arquitectura de API

### Capas de la Arquitectura

```
┌─────────────────────────────────────┐
│         Frontend Components         │
├─────────────────────────────────────┤
│         Custom Hooks Layer          │
├─────────────────────────────────────┤
│         Services Layer              │
│  ┌─────────────┬─────────────┐      │
│  │ API Client  │  External   │      │
│  │             │  Services   │      │
│  └─────────────┴─────────────┘      │
├─────────────────────────────────────┤
│         HTTP Client Layer           │
├─────────────────────────────────────┤
│         Backend APIs                │
└─────────────────────────────────────┘
```

### Principios de Diseño

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad clara
2. **Abstracción**: Los componentes no conocen los detalles de implementación de las APIs
3. **Reutilización**: Servicios compartidos para operaciones comunes
4. **Manejo de Errores**: Estrategia consistente de manejo de errores
5. **Type Safety**: Interfaces TypeScript para todas las operaciones

---

## 🌐 Cliente HTTP

### API Client Base

```typescript
// lib/api/client.ts
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
}

export interface ApiError {
  message: string;
  code: string;
  status: number;
  details?: any;
}

export interface RequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

export class ApiClient {
  private baseURL: string;
  private token: string | null = null;
  private refreshPromise: Promise<string> | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string): void {
    this.token = token;
  }

  clearToken(): void {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      timeout = 30000,
      retries = 3,
      retryDelay = 1000,
      ...requestConfig
    } = config;

    const url = `${this.baseURL}${endpoint}`;
    const headers = new Headers(requestConfig.headers);

    // Agregar token de autenticación
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    // Headers por defecto
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const requestConfigWithHeaders = {
      ...requestConfig,
      headers,
    };

    let lastError: Error;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...requestConfigWithHeaders,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Manejar respuesta
        if (response.ok) {
          const data = await response.json();
          return {
            data,
            success: true,
            timestamp: new Date().toISOString(),
          };
        }

        // Token expirado - intentar refresh
        if (response.status === 401 && this.token) {
          await this.refreshToken();
          if (attempt < retries) continue; // Reintentar con nuevo token
        }

        // Error de la API
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.message || `HTTP ${response.status}`,
          errorData.code || 'API_ERROR',
          response.status,
          errorData.details
        );

      } catch (error) {
        lastError = error as Error;

        // No reintentar para errores de cliente
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          break;
        }

        // Esperar antes de reintentar
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, attempt)));
        }
      }
    }

    throw lastError!;
  }

  private async refreshToken(): Promise<void> {
    if (this.refreshPromise) {
      await this.refreshPromise;
      return;
    }

    this.refreshPromise = this.request<{ token: string }>('/auth/refresh', {
      method: 'POST',
      retries: 0, // No reintentar refresh
    }).then(response => {
      this.setToken(response.data.token);
      return response.data.token;
    }).finally(() => {
      this.refreshPromise = null;
    });

    await this.refreshPromise;
  }

  // Métodos HTTP
  async get<T>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }
}

// Instancia global
export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api'
);
```

### Configuración del Cliente

```typescript
// lib/api/config.ts
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  endpoints: {
    auth: {
      login: '/auth/login',
      logout: '/auth/logout',
      refresh: '/auth/refresh',
      profile: '/auth/profile',
    },
    lots: {
      list: '/lots',
      create: '/lots',
      update: '/lots/:id',
      delete: '/lots/:id',
      share: '/lots/:id/share',
    },
    contracts: {
      list: '/contracts',
      create: '/contracts',
      negotiate: '/contracts/:id/negotiate',
    },
    blockchain: {
      events: '/blockchain/events',
      verify: '/blockchain/verify',
    },
  },
};
```

---

## 📊 Servicios de Datos

### Servicio de Lotes

```typescript
// services/lots.ts
import { apiClient } from '@/lib/api/client';
import { API_CONFIG } from '@/lib/api/config';

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

export interface CreateLotData {
  name: string;
  description?: string;
  weight: number;
  unit: 'kg' | 'ton' | 'lb';
  quality: 'premium' | 'standard' | 'basic';
  location: string;
  harvestDate: string;
  certifications?: string[];
}

export interface UpdateLotData extends Partial<CreateLotData> {
  status?: 'available' | 'sold' | 'reserved';
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

export interface LotListResponse {
  lots: Lot[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export class LotsService {
  async getLots(filters?: LotFilters, page = 1, limit = 20): Promise<LotListResponse> {
    try {
      const queryParams = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...this.buildFiltersQuery(filters),
      });

      const response = await apiClient.get<LotListResponse>(
        `${API_CONFIG.endpoints.lots.list}?${queryParams}`
      );

      return {
        ...response.data,
        lots: response.data.lots.map(lot => ({
          ...lot,
          createdAt: new Date(lot.createdAt),
          updatedAt: new Date(lot.updatedAt),
          harvestDate: new Date(lot.harvestDate),
        })),
      };
    } catch (error) {
      console.error('Error fetching lots:', error);
      throw this.handleError(error);
    }
  }

  async getLotById(id: string): Promise<Lot> {
    try {
      const response = await apiClient.get<Lot>(
        API_CONFIG.endpoints.lots.update.replace(':id', id)
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
        harvestDate: new Date(response.data.harvestDate),
      };
    } catch (error) {
      console.error('Error fetching lot:', error);
      throw this.handleError(error);
    }
  }

  async createLot(data: CreateLotData): Promise<Lot> {
    try {
      // Validación de datos
      this.validateLotData(data);

      const response = await apiClient.post<Lot>(
        API_CONFIG.endpoints.lots.create,
        data
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
        harvestDate: new Date(response.data.harvestDate),
      };
    } catch (error) {
      console.error('Error creating lot:', error);
      throw this.handleError(error);
    }
  }

  async updateLot(id: string, data: UpdateLotData): Promise<Lot> {
    try {
      const response = await apiClient.put<Lot>(
        API_CONFIG.endpoints.lots.update.replace(':id', id),
        data
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
        harvestDate: new Date(response.data.harvestDate),
      };
    } catch (error) {
      console.error('Error updating lot:', error);
      throw this.handleError(error);
    }
  }

  async deleteLot(id: string): Promise<void> {
    try {
      await apiClient.delete(
        API_CONFIG.endpoints.lots.update.replace(':id', id)
      );
    } catch (error) {
      console.error('Error deleting lot:', error);
      throw this.handleError(error);
    }
  }

  async shareLot(id: string, userId: string, permissions: string[]): Promise<void> {
    try {
      await apiClient.post(
        API_CONFIG.endpoints.lots.share.replace(':id', id),
        { userId, permissions }
      );
    } catch (error) {
      console.error('Error sharing lot:', error);
      throw this.handleError(error);
    }
  }

  private buildFiltersQuery(filters?: LotFilters): Record<string, string> {
    if (!filters) return {};

    const query: Record<string, string> = {};

    if (filters.status) query.status = filters.status;
    if (filters.quality) query.quality = filters.quality;
    if (filters.location) query.location = filters.location;
    if (filters.minWeight) query.minWeight = filters.minWeight.toString();
    if (filters.maxWeight) query.maxWeight = filters.maxWeight.toString();
    if (filters.harvestDateFrom) query.harvestDateFrom = filters.harvestDateFrom;
    if (filters.harvestDateTo) query.harvestDateTo = filters.harvestDateTo;
    if (filters.producerId) query.producerId = filters.producerId;
    if (filters.certifications?.length) {
      query.certifications = filters.certifications.join(',');
    }

    return query;
  }

  private validateLotData(data: CreateLotData): void {
    if (!data.name || data.name.trim().length === 0) {
      throw new Error('El nombre del lote es requerido');
    }
    if (!data.weight || data.weight <= 0) {
      throw new Error('El peso debe ser mayor a 0');
    }
    if (!data.location || data.location.trim().length === 0) {
      throw new Error('La ubicación es requerida');
    }
    if (!data.harvestDate) {
      throw new Error('La fecha de cosecha es requerida');
    }

    const harvestDate = new Date(data.harvestDate);
    if (harvestDate > new Date()) {
      throw new Error('La fecha de cosecha no puede ser futura');
    }
  }

  private handleError(error: any): Error {
    if (error instanceof ApiError) {
      switch (error.status) {
        case 400:
          return new Error('Datos inválidos: ' + error.message);
        case 401:
          return new Error('No autorizado. Por favor, inicia sesión nuevamente.');
        case 403:
          return new Error('No tienes permisos para realizar esta acción.');
        case 404:
          return new Error('El recurso solicitado no existe.');
        case 409:
          return new Error('Conflicto: ' + error.message);
        case 422:
          return new Error('Datos inválidos: ' + error.message);
        default:
          return new Error('Error del servidor: ' + error.message);
      }
    }

    if (error.name === 'NetworkError') {
      return new Error('Error de conexión. Verifica tu conexión a internet.');
    }

    return new Error('Ha ocurrido un error inesperado. Por favor, intenta nuevamente.');
  }
}

export const lotsService = new LotsService();
```

### Servicio de Contratos

```typescript
// services/contracts.ts
import { apiClient } from '@/lib/api/client';
import { API_CONFIG } from '@/lib/api/config';

export interface Contract {
  id: string;
  lotId: string;
  buyerId: string;
  sellerId: string;
  price: number;
  currency: string;
  quantity: number;
  unit: string;
  terms: string;
  status: 'draft' | 'negotiating' | 'agreed' | 'signed' | 'completed' | 'cancelled';
  blockchainTxHash?: string;
  createdAt: string;
  updatedAt: string;
  signedAt?: string;
}

export interface ContractNegotiation {
  id: string;
  contractId: string;
  proposerId: string;
  proposedPrice: number;
  proposedTerms: string;
  status: 'pending' | 'accepted' | 'rejected';
  createdAt: string;
}

export class ContractsService {
  async getContracts(filters?: {
    status?: string;
    buyerId?: string;
    sellerId?: string;
    lotId?: string;
  }): Promise<Contract[]> {
    try {
      const queryParams = new URLSearchParams(filters as any);
      const response = await apiClient.get<Contract[]>(
        `${API_CONFIG.endpoints.contracts.list}?${queryParams}`
      );

      return response.data.map(contract => ({
        ...contract,
        createdAt: new Date(contract.createdAt),
        updatedAt: new Date(contract.updatedAt),
        signedAt: contract.signedAt ? new Date(contract.signedAt) : undefined,
      }));
    } catch (error) {
      console.error('Error fetching contracts:', error);
      throw error;
    }
  }

  async createContract(data: {
    lotId: string;
    buyerId: string;
    price: number;
    currency: string;
    quantity: number;
    unit: string;
    terms: string;
  }): Promise<Contract> {
    try {
      const response = await apiClient.post<Contract>(
        API_CONFIG.endpoints.contracts.create,
        data
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
        signedAt: response.data.signedAt ? new Date(response.data.signedAt) : undefined,
      };
    } catch (error) {
      console.error('Error creating contract:', error);
      throw error;
    }
  }

  async negotiateContract(
    contractId: string,
    negotiation: {
      proposedPrice: number;
      proposedTerms: string;
    }
  ): Promise<ContractNegotiation> {
    try {
      const response = await apiClient.post<ContractNegotiation>(
        API_CONFIG.endpoints.contracts.negotiate.replace(':id', contractId),
        negotiation
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
      };
    } catch (error) {
      console.error('Error negotiating contract:', error);
      throw error;
    }
  }

  async signContract(contractId: string): Promise<Contract> {
    try {
      const response = await apiClient.post<Contract>(
        `${API_CONFIG.endpoints.contracts.list}/${contractId}/sign`
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
        signedAt: response.data.signedAt ? new Date(response.data.signedAt) : undefined,
      };
    } catch (error) {
      console.error('Error signing contract:', error);
      throw error;
    }
  }
}

export const contractsService = new ContractsService();
```

### Servicio de Blockchain

```typescript
// services/blockchain.ts
import { apiClient } from '@/lib/api/client';
import { API_CONFIG } from '@/lib/api/config';

export interface BlockchainEvent {
  id: string;
  type: 'created' | 'transported' | 'certified' | 'sold' | 'delivered';
  lotId: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'pending' | 'confirmed' | 'failed';
  transactionHash?: string;
  blockNumber?: number;
  gasUsed?: number;
  gasPrice?: number;
  metadata?: Record<string, any>;
}

export interface BlockchainVerification {
  isValid: boolean;
  lotId: string;
  events: BlockchainEvent[];
  lastVerified: string;
  certificateHash?: string;
}

export class BlockchainService {
  async getLotEvents(lotId: string): Promise<BlockchainEvent[]> {
    try {
      const response = await apiClient.get<BlockchainEvent[]>(
        `${API_CONFIG.endpoints.blockchain.events}/${lotId}`
      );

      return response.data.map(event => ({
        ...event,
        timestamp: new Date(event.timestamp),
      }));
    } catch (error) {
      console.error('Error fetching blockchain events:', error);
      throw error;
    }
  }

  async verifyLot(lotId: string): Promise<BlockchainVerification> {
    try {
      const response = await apiClient.get<BlockchainVerification>(
        `${API_CONFIG.endpoints.blockchain.verify}/${lotId}`
      );

      return {
        ...response.data,
        events: response.data.events.map(event => ({
          ...event,
          timestamp: new Date(event.timestamp),
        })),
        lastVerified: new Date(response.data.lastVerified),
      };
    } catch (error) {
      console.error('Error verifying lot on blockchain:', error);
      throw error;
    }
  }

  async createEvent(data: {
    lotId: string;
    type: BlockchainEvent['type'];
    title: string;
    description: string;
    metadata?: Record<string, any>;
  }): Promise<BlockchainEvent> {
    try {
      const response = await apiClient.post<BlockchainEvent>(
        API_CONFIG.endpoints.blockchain.events,
        data
      );

      return {
        ...response.data,
        timestamp: new Date(response.data.timestamp),
      };
    } catch (error) {
      console.error('Error creating blockchain event:', error);
      throw error;
    }
  }

  async getTransactionStatus(txHash: string): Promise<{
    status: 'pending' | 'confirmed' | 'failed';
    blockNumber?: number;
    gasUsed?: number;
    confirmations?: number;
  }> {
    try {
      const response = await apiClient.get(
        `${API_CONFIG.endpoints.blockchain.events}/transaction/${txHash}`
      );

      return response.data;
    } catch (error) {
      console.error('Error getting transaction status:', error);
      throw error;
    }
  }
}

export const blockchainService = new BlockchainService();
```

---

## 🔐 Autenticación y Autorización

### Servicio de Autenticación

```typescript
// services/auth.ts
import { apiClient } from '@/lib/api/client';
import { API_CONFIG } from '@/lib/api/config';

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

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role: User['role'];
  company?: string;
  location?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export class AuthService {
  private tokenStorage = {
    getToken: () => {
      if (typeof window === 'undefined') return null;
      return localStorage.getItem('triboka_token');
    },
    setToken: (token: string) => {
      if (typeof window === 'undefined') return;
      localStorage.setItem('triboka_token', token);
    },
    removeToken: () => {
      if (typeof window === 'undefined') return;
      localStorage.removeItem('triboka_token');
      localStorage.removeItem('triboka_refresh_token');
    },
    getRefreshToken: () => {
      if (typeof window === 'undefined') return null;
      return localStorage.getItem('triboka_refresh_token');
    },
    setRefreshToken: (token: string) => {
      if (typeof window === 'undefined') return;
      localStorage.setItem('triboka_refresh_token', token);
    },
  };

  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    try {
      const response = await apiClient.post<{
        user: User;
        tokens: AuthTokens;
      }>(API_CONFIG.endpoints.auth.login, credentials);

      const { user, tokens } = response.data;

      // Guardar tokens
      this.tokenStorage.setToken(tokens.accessToken);
      this.tokenStorage.setRefreshToken(tokens.refreshToken);
      apiClient.setToken(tokens.accessToken);

      return {
        user: {
          ...user,
          createdAt: new Date(user.createdAt),
          updatedAt: new Date(user.updatedAt),
        },
        tokens,
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(data: RegisterData): Promise<{ user: User; tokens: AuthTokens }> {
    try {
      const response = await apiClient.post<{
        user: User;
        tokens: AuthTokens;
      }>(API_CONFIG.endpoints.auth.register || '/auth/register', data);

      const { user, tokens } = response.data;

      // Guardar tokens
      this.tokenStorage.setToken(tokens.accessToken);
      this.tokenStorage.setRefreshToken(tokens.refreshToken);
      apiClient.setToken(tokens.accessToken);

      return {
        user: {
          ...user,
          createdAt: new Date(user.createdAt),
          updatedAt: new Date(user.updatedAt),
        },
        tokens,
      };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post(API_CONFIG.endpoints.auth.logout);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Limpiar tokens independientemente del resultado
      this.tokenStorage.removeToken();
      apiClient.clearToken();
    }
  }

  async refreshToken(): Promise<string> {
    try {
      const refreshToken = this.tokenStorage.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<{ token: string }>(
        API_CONFIG.endpoints.auth.refresh,
        { refreshToken }
      );

      const newToken = response.data.token;
      this.tokenStorage.setToken(newToken);
      apiClient.setToken(newToken);

      return newToken;
    } catch (error) {
      console.error('Token refresh error:', error);
      // Limpiar tokens si el refresh falla
      this.tokenStorage.removeToken();
      apiClient.clearToken();
      throw error;
    }
  }

  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get<User>(API_CONFIG.endpoints.auth.profile);

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
      };
    } catch (error) {
      console.error('Get profile error:', error);
      throw error;
    }
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put<User>(
        API_CONFIG.endpoints.auth.profile,
        data
      );

      return {
        ...response.data,
        createdAt: new Date(response.data.createdAt),
        updatedAt: new Date(response.data.updatedAt),
      };
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  }

  isAuthenticated(): boolean {
    const token = this.tokenStorage.getToken();
    if (!token) return false;

    try {
      // Verificar si el token no ha expirado
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  getCurrentUser(): User | null {
    const token = this.tokenStorage.getToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user || null;
    } catch {
      return null;
    }
  }
}

export const authService = new AuthService();
```

### Autorización y Roles

```typescript
// lib/auth/permissions.ts
export type Permission =
  | 'lots:read'
  | 'lots:create'
  | 'lots:update'
  | 'lots:delete'
  | 'lots:share'
  | 'contracts:read'
  | 'contracts:create'
  | 'contracts:negotiate'
  | 'contracts:sign'
  | 'users:read'
  | 'users:create'
  | 'users:update'
  | 'admin:full';

export const ROLE_PERMISSIONS: Record<User['role'], Permission[]> = {
  producer: [
    'lots:read',
    'lots:create',
    'lots:update',
    'lots:delete',
    'lots:share',
    'contracts:read',
    'contracts:create',
    'contracts:negotiate',
  ],
  exporter: [
    'lots:read',
    'contracts:read',
    'contracts:create',
    'contracts:negotiate',
    'contracts:sign',
  ],
  admin: [
    'lots:read',
    'lots:create',
    'lots:update',
    'lots:delete',
    'lots:share',
    'contracts:read',
    'contracts:create',
    'contracts:negotiate',
    'contracts:sign',
    'users:read',
    'users:create',
    'users:update',
    'admin:full',
  ],
};

export function hasPermission(user: User | null, permission: Permission): boolean {
  if (!user) return false;
  return ROLE_PERMISSIONS[user.role]?.includes(permission) || false;
}

export function hasAnyPermission(user: User | null, permissions: Permission[]): boolean {
  if (!user) return false;
  return permissions.some(permission => hasPermission(user, permission));
}

export function hasAllPermissions(user: User | null, permissions: Permission[]): boolean {
  if (!user) return false;
  return permissions.every(permission => hasPermission(user, permission));
}
```

---

## 🗂️ Gestión de Estado API

### Zustand Store para API State

```typescript
// stores/api.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface ApiState {
  loading: Record<string, boolean>;
  errors: Record<string, string | null>;
  cache: Record<string, { data: any; timestamp: number }>;
}

export interface ApiActions {
  setLoading: (key: string, loading: boolean) => void;
  setError: (key: string, error: string | null) => void;
  clearError: (key: string) => void;
  setCache: (key: string, data: any, ttl?: number) => void;
  getCache: (key: string, maxAge?: number) => any | null;
  clearCache: (key?: string) => void;
  invalidateCache: (pattern: string) => void;
}

export const useApiStore = create<ApiState & ApiActions>()(
  devtools(
    (set, get) => ({
      loading: {},
      errors: {},
      cache: {},

      setLoading: (key: string, loading: boolean) =>
        set(state => ({
          loading: { ...state.loading, [key]: loading }
        }), false, 'api/setLoading'),

      setError: (key: string, error: string | null) =>
        set(state => ({
          errors: { ...state.errors, [key]: error }
        }), false, 'api/setError'),

      clearError: (key: string) =>
        set(state => ({
          errors: { ...state.errors, [key]: null }
        }), false, 'api/clearError'),

      setCache: (key: string, data: any, ttl = 5 * 60 * 1000) => // 5 minutos por defecto
        set(state => ({
          cache: {
            ...state.cache,
            [key]: {
              data,
              timestamp: Date.now() + ttl,
            }
          }
        }), false, 'api/setCache'),

      getCache: (key: string, maxAge?: number) => {
        const cached = get().cache[key];
        if (!cached) return null;

        const now = Date.now();
        if (now > cached.timestamp) {
          // Cache expirado, limpiar
          set(state => {
            const newCache = { ...state.cache };
            delete newCache[key];
            return { cache: newCache };
          });
          return null;
        }

        return cached.data;
      },

      clearCache: (key?: string) =>
        set(state => {
          if (key) {
            const newCache = { ...state.cache };
            delete newCache[key];
            return { cache: newCache };
          }
          return { cache: {} };
        }, false, 'api/clearCache'),

      invalidateCache: (pattern: string) =>
        set(state => {
          const newCache = { ...state.cache };
          Object.keys(newCache).forEach(key => {
            if (key.includes(pattern)) {
              delete newCache[key];
            }
          });
          return { cache: newCache };
        }, false, 'api/invalidateCache'),
    }),
    { name: 'api-store' }
  )
);
```

### Custom Hook para API Calls

```typescript
// hooks/useApi.ts
import { useState, useEffect, useCallback } from 'react';
import { useApiStore } from '@/stores/api';
import { apiClient } from '@/lib/api/client';

export interface UseApiOptions {
  cacheKey?: string;
  cacheTime?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  enabled?: boolean;
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
) {
  const {
    cacheKey,
    cacheTime = 5 * 60 * 1000, // 5 minutos
    onSuccess,
    onError,
    enabled = true,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { setLoading: setGlobalLoading, setError: setGlobalError, getCache, setCache } = useApiStore();

  const execute = useCallback(async () => {
    if (!enabled) return;

    // Verificar cache primero
    if (cacheKey) {
      const cachedData = getCache(cacheKey, cacheTime);
      if (cachedData) {
        setData(cachedData);
        onSuccess?.(cachedData);
        return;
      }
    }

    setLoading(true);
    setError(null);
    setGlobalLoading(cacheKey || 'api', true);
    setGlobalError(cacheKey || 'api', null);

    try {
      const result = await apiCall();
      setData(result);

      // Guardar en cache si aplica
      if (cacheKey) {
        setCache(cacheKey, result, cacheTime);
      }

      onSuccess?.(result);
    } catch (err) {
      const error = err as Error;
      setError(error);
      setGlobalError(cacheKey || 'api', error.message);
      onError?.(error);
    } finally {
      setLoading(false);
      setGlobalLoading(cacheKey || 'api', false);
    }
  }, [apiCall, cacheKey, cacheTime, enabled, getCache, setCache, setGlobalLoading, setGlobalError, onSuccess, onError]);

  useEffect(() => {
    execute();
  }, [execute]);

  const refetch = useCallback(() => {
    execute();
  }, [execute]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

// Hook específico para mutations
export function useApiMutation<T, P>(
  apiCall: (params: P) => Promise<T>,
  options: {
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
    invalidateCache?: string[];
  } = {}
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { setLoading: setGlobalLoading, setError: setGlobalError, invalidateCache } = useApiStore();

  const mutate = useCallback(async (params: P) => {
    setLoading(true);
    setError(null);
    setGlobalLoading('mutation', true);
    setGlobalError('mutation', null);

    try {
      const result = await apiCall(params);

      // Invalidar cache relacionado
      options.invalidateCache?.forEach(pattern => {
        invalidateCache(pattern);
      });

      options.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      setGlobalError('mutation', error.message);
      options.onError?.(error);
      throw error;
    } finally {
      setLoading(false);
      setGlobalLoading('mutation', false);
    }
  }, [apiCall, options, setGlobalLoading, setGlobalError, invalidateCache]);

  return {
    mutate,
    loading,
    error,
  };
}
```

---

## 🚨 Manejo de Errores

### Error Boundary

```typescript
// components/ErrorBoundary.tsx
import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });

    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo);

    // Aquí podrías enviar el error a un servicio de monitoreo
    // logError(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error!} retry={this.handleRetry} />;
      }

      return <DefaultErrorFallback error={this.state.error!} retry={this.handleRetry} />;
    }

    return this.props.children;
  }
}

function DefaultErrorFallback({ error, retry }: { error: Error; retry: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            <span>Ha ocurrido un error</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Lo sentimos, ha ocurrido un error inesperado. Por favor, intenta nuevamente.
          </p>

          {process.env.NODE_ENV === 'development' && (
            <details className="text-xs">
              <summary className="cursor-pointer font-medium">Detalles del error</summary>
              <pre className="mt-2 whitespace-pre-wrap bg-gray-100 p-2 rounded">
                {error.message}
                {error.stack}
              </pre>
            </details>
          )}

          <Button onClick={retry} className="w-full">
            <RefreshCw className="h-4 w-4 mr-2" />
            Intentar nuevamente
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Toast Notifications

```typescript
// components/Toast.tsx
import { useEffect } from 'react';
import { CheckCircle, AlertCircle, XCircle, Info, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

interface ToastProps extends Toast {
  onClose: (id: string) => void;
}

export function Toast({ id, type, title, description, duration = 5000, onClose }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onClose(id), duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className={`p-4 rounded-md border ${getStyles()} shadow-md`}>
      <div className="flex items-start space-x-3">
        {getIcon()}
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{title}</h4>
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onClose(id)}
          className="h-6 w-6 p-0"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

// Toast Container
interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onRemove} />
      ))}
    </div>
  );
}
```

---

## 💾 Caching y Optimización

### React Query para Server State

```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      gcTime: 10 * 60 * 1000, // 10 minutos
      retry: (failureCount, error) => {
        // No reintentar en errores de autenticación
        if (error instanceof ApiError && error.status === 401) {
          return false;
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: false,
    },
  },
});
```

### Custom Hooks con React Query

```typescript
// hooks/useLots.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lotsService } from '@/services/lots';
import { Lot, CreateLotData, UpdateLotData, LotFilters } from '@/types/lots';

export function useLots(filters?: LotFilters, page = 1, limit = 20) {
  return useQuery({
    queryKey: ['lots', filters, page, limit],
    queryFn: () => lotsService.getLots(filters, page, limit),
    keepPreviousData: true,
  });
}

export function useLot(id: string) {
  return useQuery({
    queryKey: ['lot', id],
    queryFn: () => lotsService.getLotById(id),
    enabled: !!id,
  });
}

export function useCreateLot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateLotData) => lotsService.createLot(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['lots']);
    },
  });
}

export function useUpdateLot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateLotData }) =>
      lotsService.updateLot(id, data),
    onSuccess: (updatedLot) => {
      queryClient.invalidateQueries(['lots']);
      queryClient.setQueryData(['lot', updatedLot.id], updatedLot);
    },
  });
}

export function useDeleteLot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => lotsService.deleteLot(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['lots']);
    },
  });
}
```

### Service Worker para Offline

```typescript
// public/sw.js
const CACHE_NAME = 'triboka-v1';
const STATIC_CACHE = 'triboka-static-v1';
const API_CACHE = 'triboka-api-v1';

const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  // Agregar otros assets estáticos
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Cache API responses
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE).then((cache) => {
        return fetch(request).then((response) => {
          // Cache successful GET requests
          if (request.method === 'GET' && response.status === 200) {
            cache.put(request, response.clone());
          }
          return response;
        }).catch(() => {
          // Return cached version if available
          return cache.match(request);
        });
      })
    );
  } else {
    // Cache static assets
    event.respondWith(
      caches.match(request).then((response) => {
        return response || fetch(request);
      })
    );
  }
});
```

---

## 🌐 APIs Externas

### Servicio de Geocodificación

```typescript
// services/geocoding.ts
import { apiClient } from '@/lib/api/client';

export interface GeocodeResult {
  lat: number;
  lng: number;
  address: string;
  city?: string;
  country?: string;
}

export class GeocodingService {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async geocode(address: string): Promise<GeocodeResult[]> {
    try {
      // Usar OpenStreetMap Nominatim (gratuito)
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=5`,
        {
          headers: {
            'User-Agent': 'Triboka Agro App',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Geocoding service error');
      }

      const data = await response.json();

      return data.map((item: any) => ({
        lat: parseFloat(item.lat),
        lng: parseFloat(item.lon),
        address: item.display_name,
        city: item.address?.city || item.address?.town,
        country: item.address?.country,
      }));
    } catch (error) {
      console.error('Geocoding error:', error);
      throw error;
    }
  }

  async reverseGeocode(lat: number, lng: number): Promise<GeocodeResult> {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
        {
          headers: {
            'User-Agent': 'Triboka Agro App',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Reverse geocoding service error');
      }

      const data = await response.json();

      return {
        lat,
        lng,
        address: data.display_name,
        city: data.address?.city || data.address?.town,
        country: data.address?.country,
      };
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      throw error;
    }
  }
}

export const geocodingService = new GeocodingService(process.env.NEXT_PUBLIC_MAPS_API_KEY || '');
```

### Servicio de Clima

```typescript
// services/weather.ts
export interface WeatherData {
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  description: string;
  icon: string;
}

export class WeatherService {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async getCurrentWeather(lat: number, lng: number): Promise<WeatherData> {
    try {
      // Usar OpenWeatherMap API
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${this.apiKey}&units=metric&lang=es`
      );

      if (!response.ok) {
        throw new Error('Weather service error');
      }

      const data = await response.json();

      return {
        temperature: data.main.temp,
        humidity: data.main.humidity,
        precipitation: data.rain?.['1h'] || 0,
        windSpeed: data.wind.speed,
        description: data.weather[0].description,
        icon: data.weather[0].icon,
      };
    } catch (error) {
      console.error('Weather API error:', error);
      throw error;
    }
  }

  async getForecast(lat: number, lng: number, days = 7): Promise<WeatherData[]> {
    try {
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lng}&appid=${this.apiKey}&units=metric&lang=es`
      );

      if (!response.ok) {
        throw new Error('Weather forecast service error');
      }

      const data = await response.json();

      // Procesar datos cada 24 horas
      const dailyData: { [key: string]: any } = {};

      data.list.forEach((item: any) => {
        const date = new Date(item.dt * 1000).toDateString();

        if (!dailyData[date]) {
          dailyData[date] = {
            temperature: item.main.temp,
            humidity: item.main.humidity,
            precipitation: item.rain?.['3h'] || 0,
            windSpeed: item.wind.speed,
            description: item.weather[0].description,
            icon: item.weather[0].icon,
            count: 1,
          };
        } else {
          // Promediar valores
          const current = dailyData[date];
          current.temperature = (current.temperature + item.main.temp) / 2;
          current.humidity = Math.max(current.humidity, item.main.humidity);
          current.precipitation += item.rain?.['3h'] || 0;
          current.windSpeed = Math.max(current.windSpeed, item.wind.speed);
          current.count += 1;
        }
      });

      return Object.values(dailyData).slice(0, days);
    } catch (error) {
      console.error('Weather forecast API error:', error);
      throw error;
    }
  }
}

export const weatherService = new WeatherService(process.env.NEXT_PUBLIC_WEATHER_API_KEY || '');
```

---

## 🧪 Testing de APIs

### Testing del API Client

```typescript
// tests/lib/api/client.test.ts
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/client';

// Mock fetch
global.fetch = jest.fn();

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('request', () => {
    it('should make successful GET request', async () => {
      const mockResponse = { data: 'test', success: true };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await apiClient.get('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.data).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ message: 'Bad Request', code: 'VALIDATION_ERROR' }),
      });

      await expect(apiClient.get('/test')).rejects.toThrow(ApiError);
    });

    it('should retry on network errors', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ data: 'success' }),
        });

      const result = await apiClient.get('/test');

      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(result.data).toEqual({ data: 'success' });
    });
  });

  describe('token handling', () => {
    it('should include authorization header when token is set', async () => {
      apiClient.setToken('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: 'success' }),
      });

      await apiClient.get('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });
  });
});
```

### Testing de Servicios

```typescript
// tests/services/lots.test.ts
import { lotsService } from '@/services/lots';
import { apiClient } from '@/lib/api/client';

// Mock apiClient
jest.mock('@/lib/api/client');

describe('LotsService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLots', () => {
    it('should fetch lots with filters', async () => {
      const mockLots = [
        { id: '1', name: 'Lot 1', weight: 100 },
        { id: '2', name: 'Lot 2', weight: 200 },
      ];

      (apiClient.get as jest.Mock).mockResolvedValueOnce({
        data: { lots: mockLots, total: 2, page: 1, limit: 20, hasMore: false },
      });

      const filters = { status: 'available' };
      const result = await lotsService.getLots(filters);

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('status=available')
      );
      expect(result.lots).toHaveLength(2);
      expect(result.lots[0].createdAt).toBeInstanceOf(Date);
    });

    it('should handle API errors', async () => {
      (apiClient.get as jest.Mock).mockRejectedValueOnce(
        new Error('API Error')
      );

      await expect(lotsService.getLots()).rejects.toThrow('API Error');
    });
  });

  describe('createLot', () => {
    it('should create lot with valid data', async () => {
      const lotData = {
        name: 'Test Lot',
        weight: 100,
        unit: 'kg' as const,
        quality: 'premium' as const,
        location: 'Test Location',
        harvestDate: '2025-01-01',
      };

      const mockResponse = { ...lotData, id: '1', createdAt: '2025-01-01T00:00:00Z' };

      (apiClient.post as jest.Mock).mockResolvedValueOnce({
        data: mockResponse,
      });

      const result = await lotsService.createLot(lotData);

      expect(apiClient.post).toHaveBeenCalledWith('/lots', lotData);
      expect(result.id).toBe('1');
      expect(result.createdAt).toBeInstanceOf(Date);
    });

    it('should validate lot data', async () => {
      const invalidData = {
        name: '',
        weight: 100,
        unit: 'kg' as const,
        quality: 'premium' as const,
        location: 'Test Location',
        harvestDate: '2025-01-01',
      };

      await expect(lotsService.createLot(invalidData)).rejects.toThrow(
        'El nombre del lote es requerido'
      );
    });
  });
});
```

---

## 📊 Monitoreo y Logging

### Logger Service

```typescript
// lib/logger.ts
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  userId?: string;
  sessionId?: string;
  metadata?: Record<string, any>;
}

class Logger {
  private logLevel: LogLevel = 'info';
  private userId?: string;
  private sessionId?: string;

  setUser(userId: string) {
    this.userId = userId;
  }

  setSession(sessionId: string) {
    this.sessionId = sessionId;
  }

  setLogLevel(level: LogLevel) {
    this.logLevel = level;
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private createLogEntry(level: LogLevel, message: string, metadata?: Record<string, any>): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId,
      metadata,
    };
  }

  private log(entry: LogEntry) {
    const logMessage = `[${entry.timestamp}] ${entry.level.toUpperCase()}: ${entry.message}`;

    // Console logging
    switch (entry.level) {
      case 'debug':
        console.debug(logMessage, entry.metadata);
        break;
      case 'info':
        console.info(logMessage, entry.metadata);
        break;
      case 'warn':
        console.warn(logMessage, entry.metadata);
        break;
      case 'error':
        console.error(logMessage, entry.metadata);
        break;
    }

    // Send to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToMonitoring(entry);
    }
  }

  private async sendToMonitoring(entry: LogEntry) {
    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log to monitoring:', error);
    }
  }

  debug(message: string, metadata?: Record<string, any>) {
    if (this.shouldLog('debug')) {
      this.log(this.createLogEntry('debug', message, metadata));
    }
  }

  info(message: string, metadata?: Record<string, any>) {
    if (this.shouldLog('info')) {
      this.log(this.createLogEntry('info', message, metadata));
    }
  }

  warn(message: string, metadata?: Record<string, any>) {
    if (this.shouldLog('warn')) {
      this.log(this.createLogEntry('warn', message, metadata));
    }
  }

  error(message: string, metadata?: Record<string, any>) {
    if (this.shouldLog('error')) {
      this.log(this.createLogEntry('error', message, metadata));
    }
  }
}

export const logger = new Logger();
```

### API Monitoring

```typescript
// lib/api/monitoring.ts
import { apiClient } from './client';
import { logger } from '../logger';

interface ApiMetrics {
  endpoint: string;
  method: string;
  duration: number;
  status: number;
  success: boolean;
  timestamp: string;
}

class ApiMonitor {
  private metrics: ApiMetrics[] = [];
  private maxMetrics = 1000;

  recordRequest(endpoint: string, method: string, startTime: number, status: number, success: boolean) {
    const duration = Date.now() - startTime;
    const metric: ApiMetrics = {
      endpoint,
      method,
      duration,
      status,
      success,
      timestamp: new Date().toISOString(),
    };

    this.metrics.push(metric);

    // Mantener solo las últimas métricas
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    // Log métricas importantes
    if (!success || duration > 5000) {
      logger.warn('API Request Alert', {
        endpoint,
        method,
        duration,
        status,
        success,
      });
    }

    // Enviar métricas a servicio de monitoreo
    this.sendMetrics(metric);
  }

  getMetrics(timeRange?: number): ApiMetrics[] {
    if (!timeRange) return this.metrics;

    const cutoff = Date.now() - timeRange;
    return this.metrics.filter(m => new Date(m.timestamp).getTime() > cutoff);
  }

  getAverageResponseTime(): number {
    if (this.metrics.length === 0) return 0;

    const total = this.metrics.reduce((sum, m) => sum + m.duration, 0);
    return total / this.metrics.length;
  }

  getErrorRate(): number {
    if (this.metrics.length === 0) return 0;

    const errors = this.metrics.filter(m => !m.success).length;
    return errors / this.metrics.length;
  }

  private async sendMetrics(metric: ApiMetrics) {
    try {
      // Enviar a servicio de métricas (ej: DataDog, New Relic, etc.)
      if (process.env.NODE_ENV === 'production') {
        await fetch('/api/metrics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(metric),
        });
      }
    } catch (error) {
      logger.error('Failed to send API metrics', { error: error.message });
    }
  }
}

export const apiMonitor = new ApiMonitor();

// Middleware para monitorear requests
const originalRequest = apiClient.request;
apiClient.request = async function(endpoint: string, config: any = {}) {
  const startTime = Date.now();

  try {
    const result = await originalRequest.call(this, endpoint, config);
    apiMonitor.recordRequest(endpoint, config.method || 'GET', startTime, 200, true);
    return result;
  } catch (error: any) {
    const status = error.status || 0;
    apiMonitor.recordRequest(endpoint, config.method || 'GET', startTime, status, false);
    throw error;
  }
};
```

---

## 📚 Conclusión

El sistema de APIs y servicios de Triboka Agro proporciona:

- **Cliente HTTP Robusto**: Manejo de errores, reintentos, timeouts y autenticación
- **Servicios Modulares**: Separación clara de responsabilidades por dominio
- **Gestión de Estado**: Caching inteligente y sincronización de estado
- **Manejo de Errores**: Estrategias consistentes y user-friendly
- **Optimización**: Caching, React Query y Service Workers
- **Integraciones Externas**: Geocodificación, clima y otros servicios
- **Testing Completo**: Cobertura de unit tests e integración
- **Monitoreo**: Logging y métricas para observabilidad

Esta arquitectura proporciona una base sólida y escalable para la comunicación entre el frontend y los servicios backend, asegurando una experiencia de usuario fluida y confiable.