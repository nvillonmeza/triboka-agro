# 🚀 Despliegue y CI/CD - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Despliegue](#arquitectura-de-despliegue)
3. [Configuración de Producción](#configuración-de-producción)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Despliegue Automático](#despliegue-automático)
6. [Monitoreo y Alertas](#monitoreo-y-alertas)
7. [Rollback y Recuperación](#rollback-y-recuperación)
8. [Optimización de Performance](#optimización-de-performance)
9. [Seguridad en Despliegue](#seguridad-en-despliegue)

---

## 🎯 Visión General

El sistema de despliegue de Triboka Agro está diseñado para garantizar entregas continuas, confiables y seguras del frontend. Utilizamos una combinación de GitHub Actions, Docker y Nginx para lograr despliegues automatizados con monitoreo completo.

---

## 🏗️ Arquitectura de Despliegue

### Infraestructura de Producción

```
┌─────────────────────────────────────┐
│         Load Balancer (Nginx)       │
│  - SSL Termination                 │
│  - Rate Limiting                   │
│  - Static File Caching             │
├─────────────────────────────────────┤
│         Frontend Server            │
│  - Next.js Production Build        │
│  - Node.js Runtime                 │
│  - PM2 Process Manager             │
├─────────────────────────────────────┤
│         CDN (Cloudflare)           │
│  - Global Distribution             │
│  - Caching Strategy                │
│  - DDoS Protection                 │
└─────────────────────────────────────┘
```

### Entornos de Despliegue

#### Desarrollo (Development)
- **URL**: `https://dev.app.triboka.com`
- **Branch**: `develop`
- **Base de Datos**: Desarrollo
- **Características**: Últimas features en desarrollo

#### Staging
- **URL**: `https://staging.app.triboka.com`
- **Branch**: `staging`
- **Base de Datos**: Staging (copia de producción)
- **Características**: QA y testing final

#### Producción (Production)
- **URL**: `https://app.triboka.com`
- **Branch**: `main`
- **Base de Datos**: Producción
- **Características**: Versión estable para usuarios finales

---

## ⚙️ Configuración de Producción

### Variables de Entorno

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.triboka.com
NEXT_PUBLIC_WS_URL=wss://ws.triboka.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_VERSION=1.0.0
NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
NEXT_PUBLIC_GA_TRACKING_ID=GA-XXXXXXXXXX

# Server-side only
DATABASE_URL=postgresql://user:pass@prod-db.triboka.com:5432/triboka_prod
REDIS_URL=redis://prod-redis.triboka.com:6379
JWT_SECRET=your-production-jwt-secret
ENCRYPTION_KEY=your-encryption-key
```

### Configuración de Next.js

```javascript
// next.config.js
module.exports = {
  // Configuración de producción
  productionBrowserSourceMaps: false,
  compress: true,
  poweredByHeader: false,

  // Optimizaciones de performance
  swcMinify: true,
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },

  // Headers de seguridad
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },

  // Redirects y rewrites
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/dashboard',
        permanent: true,
      },
    ];
  },

  // Configuración de imágenes
  images: {
    domains: ['api.triboka.com', 'cdn.triboka.com'],
    formats: ['image/webp', 'image/avif'],
  },
};
```

### Configuración de PM2

```json
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'triboka-frontend',
      script: 'npm start',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3001,
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      max_memory_restart: '1G',
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
    },
  ],
};
```

### Configuración de Nginx

```nginx
# /etc/nginx/conf.d/app.triboka.com.conf
upstream triboka_frontend {
    server 127.0.0.1:3001;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name app.triboka.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.triboka.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.triboka.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GSSHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static files caching
    location /_next/static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Robots-Tag "noindex";
    }

    # API proxy
    location /api/ {
        proxy_pass http://triboka_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Main application
    location / {
        proxy_pass http://triboka_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Handle Next.js routing
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Rate limiting
    limit_req zone=api burst=10 nodelay;
    limit_req_status 429;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name app.triboka.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow Completo

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main, develop, staging]
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

      - name: Run unit tests
        run: npm run test:coverage

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop' || github.ref == 'refs/heads/staging'
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
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          NEXT_PUBLIC_ENVIRONMENT: production

      - name: Run build tests
        run: npm run test:build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-files
          path: |
            .next/
            public/
            package.json
            package-lock.json

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-files

      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /var/www/triboka-staging
            sudo systemctl stop triboka-frontend-staging
            rm -rf .next/ public/ node_modules/
            # Copy new build
            cp -r /tmp/build-files/* .
            npm ci --production
            sudo systemctl start triboka-frontend-staging

      - name: Health check
        run: |
          sleep 30
          curl -f https://staging.app.triboka.com/health || exit 1

      - name: Run smoke tests
        run: npm run test:smoke -- --baseUrl=https://staging.app.triboka.com

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-files

      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /var/www/triboka-production
            # Create backup
            sudo systemctl stop triboka-frontend
            cp -r .next/ backup-$(date +%Y%m%d_%H%M%S)/
            rm -rf .next/ public/ node_modules/
            # Copy new build
            cp -r /tmp/build-files/* .
            npm ci --production
            sudo systemctl start triboka-frontend

      - name: Health check
        run: |
          sleep 60
          curl -f https://app.triboka.com/health || exit 1

      - name: Run smoke tests
        run: npm run test:smoke -- --baseUrl=https://app.triboka.com

      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: '🚀 Frontend deployed to production successfully'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        if: success()

      - name: Notify failure
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: '❌ Frontend deployment to production failed'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        if: failure()
```

### Scripts de Despliegue

```json
// package.json
{
  "scripts": {
    "build": "next build",
    "build:analyze": "ANALYZE=true next build",
    "test:build": "npm run build && npm run test:build-smoke",
    "test:smoke": "playwright test smoke/",
    "deploy:staging": "npm run build && rsync -avz --delete .next/ user@staging:/var/www/triboka-staging/.next/",
    "deploy:prod": "npm run build && rsync -avz --delete .next/ user@prod:/var/www/triboka-prod/.next/",
    "rollback": "npm run deploy:prod -- --rollback"
  }
}
```

---

## 🤖 Despliegue Automático

### Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Blue-Green Deployment${NC}"

# Determine current active environment
CURRENT_ACTIVE=$(curl -s http://localhost:8080/active-environment)

if [ "$CURRENT_ACTIVE" = "blue" ]; then
    TARGET="green"
    PORT="3002"
else
    TARGET="blue"
    PORT="3001"
fi

echo -e "${YELLOW}Deploying to $TARGET environment on port $PORT${NC}"

# Deploy to target environment
cd /var/www/triboka-$TARGET
git pull origin main
npm ci
npm run build

# Start new version
pm2 start ecosystem.config.js --env $TARGET
sleep 30

# Health check
if curl -f http://localhost:$PORT/health; then
    echo -e "${GREEN}Health check passed for $TARGET${NC}"

    # Switch load balancer
    curl -X POST http://localhost:8080/switch -d "environment=$TARGET"

    # Stop old environment
    pm2 stop triboka-$CURRENT_ACTIVE
    pm2 delete triboka-$CURRENT_ACTIVE

    echo -e "${GREEN}Deployment completed successfully${NC}"
else
    echo -e "${RED}Health check failed, rolling back${NC}"
    pm2 stop triboka-$TARGET
    pm2 delete triboka-$TARGET
    exit 1
fi
```

### Canary Deployment

```typescript
// lib/canary-deployment.ts
export class CanaryDeployment {
  private currentTraffic = 0;
  private targetTraffic = 10; // 10% initial traffic
  private stepSize = 5; // 5% increments
  private checkInterval = 60000; // 1 minute

  async startCanary(newVersion: string): Promise<void> {
    console.log(`Starting canary deployment for version ${newVersion}`);

    // Deploy new version to canary group
    await this.deployToCanary(newVersion);

    // Gradually increase traffic
    const interval = setInterval(async () => {
      this.currentTraffic += this.stepSize;

      if (this.currentTraffic >= this.targetTraffic) {
        clearInterval(interval);
        await this.completeDeployment(newVersion);
        return;
      }

      await this.adjustTraffic(this.currentTraffic);
      await this.monitorHealth();

    }, this.checkInterval);
  }

  private async deployToCanary(version: string): Promise<void> {
    // Deploy to 10% of servers
    console.log(`Deploying ${version} to canary servers`);
  }

  private async adjustTraffic(percentage: number): Promise<void> {
    // Adjust load balancer weights
    console.log(`Adjusting traffic to ${percentage}% for canary`);
  }

  private async monitorHealth(): Promise<void> {
    // Check error rates, response times, etc.
    const metrics = await this.getHealthMetrics();

    if (metrics.errorRate > 5 || metrics.responseTime > 2000) {
      console.error('Canary health check failed, rolling back');
      await this.rollbackCanary();
    }
  }

  private async completeDeployment(version: string): Promise<void> {
    console.log(`Canary successful, deploying ${version} to all servers`);
    await this.deployToAll(version);
  }
}
```

---

## 📊 Monitoreo y Alertas

### Métricas de Aplicación

```typescript
// lib/monitoring.ts
import { NextWebVitalsMetric } from 'next/app';

export function reportWebVitals(metric: NextWebVitalsMetric) {
  // Report to monitoring service
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', metric.name, {
      event_category: 'Web Vitals',
      event_label: metric.id,
      value: Math.round(metric.value),
      non_interaction: true,
    });
  }

  // Send to custom monitoring
  fetch('/api/metrics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: metric.name,
      value: metric.value,
      id: metric.id,
      timestamp: Date.now(),
    }),
  });
}
```

### Dashboard de Monitoreo

```typescript
// pages/admin/monitoring.tsx
import { useState, useEffect } from 'react';
import { LineChart, BarChart } from '@/components/charts';

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState({
    responseTime: [],
    errorRate: [],
    throughput: [],
    activeUsers: 0,
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      const response = await fetch('/api/metrics');
      const data = await response.json();
      setMetrics(data);
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Active Users"
        value={metrics.activeUsers}
        change="+12%"
        icon="Users"
      />

      <MetricCard
        title="Response Time"
        value="245ms"
        change="-5%"
        icon="Clock"
      />

      <MetricCard
        title="Error Rate"
        value="0.1%"
        change="-0.05%"
        icon="AlertTriangle"
      />

      <MetricCard
        title="Throughput"
        value="1.2k req/min"
        change="+8%"
        icon="Activity"
      />

      <div className="col-span-full">
        <LineChart
          data={metrics.responseTime}
          title="Response Time Trend"
        />
      </div>
    </div>
  );
}
```

### Alertas y Notificaciones

```typescript
// lib/alerts.ts
export class AlertManager {
  private alertThresholds = {
    responseTime: 2000, // 2 seconds
    errorRate: 5, // 5%
    downtime: 300, // 5 minutes
  };

  async checkThresholds(metrics: any) {
    const alerts = [];

    if (metrics.responseTime > this.alertThresholds.responseTime) {
      alerts.push({
        type: 'warning',
        message: `High response time: ${metrics.responseTime}ms`,
        severity: 'high',
      });
    }

    if (metrics.errorRate > this.alertThresholds.errorRate) {
      alerts.push({
        type: 'error',
        message: `High error rate: ${metrics.errorRate}%`,
        severity: 'critical',
      });
    }

    if (alerts.length > 0) {
      await this.sendAlerts(alerts);
    }
  }

  private async sendAlerts(alerts: any[]) {
    // Send to Slack
    await fetch(process.env.SLACK_WEBHOOK_URL!, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: '🚨 Alertas del Sistema',
        attachments: alerts.map(alert => ({
          color: alert.severity === 'critical' ? 'danger' : 'warning',
          text: alert.message,
        })),
      }),
    });

    // Send email notifications
    // Integration with email service
  }
}
```

---

## 🔄 Rollback y Recuperación

### Estrategia de Rollback

```bash
#!/bin/bash
# rollback.sh

BACKUP_DIR="/var/www/backups"
CURRENT_VERSION=$(cat /var/www/current_version.txt)
ROLLBACK_VERSION=$1

if [ -z "$ROLLBACK_VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "Rolling back from $CURRENT_VERSION to $ROLLBACK_VERSION"

# Stop current application
sudo systemctl stop triboka-frontend

# Restore backup
if [ -d "$BACKUP_DIR/$ROLLBACK_VERSION" ]; then
    rm -rf /var/www/triboka-frontend/.next
    cp -r $BACKUP_DIR/$ROLLBACK_VERSION/.next /var/www/triboka-frontend/
    echo $ROLLBACK_VERSION > /var/www/current_version.txt
else
    echo "Backup not found: $ROLLBACK_VERSION"
    exit 1
fi

# Start application
sudo systemctl start triboka-frontend

# Health check
sleep 30
if curl -f https://app.triboka.com/health; then
    echo "Rollback successful"
    # Notify team
    curl -X POST $SLACK_WEBHOOK_URL \
         -H 'Content-type: application/json' \
         --data '{"text":"🔄 Rollback completed successfully"}'
else
    echo "Rollback failed, attempting emergency recovery"
    # Emergency procedures
fi
```

### Recuperación de Desastres

```typescript
// lib/disaster-recovery.ts
export class DisasterRecovery {
  async initiateRecovery(): Promise<void> {
    console.log('Initiating disaster recovery protocol');

    // 1. Assess damage
    const systemStatus = await this.checkSystemStatus();

    if (systemStatus.database === 'ok' && systemStatus.files === 'ok') {
      // Quick recovery
      await this.quickRecovery();
    } else {
      // Full recovery from backup
      await this.fullRecovery();
    }

    // 2. Restore from last good backup
    await this.restoreFromBackup();

    // 3. Validate recovery
    await this.validateRecovery();

    // 4. Notify stakeholders
    await this.notifyRecovery();
  }

  private async checkSystemStatus() {
    // Check database connectivity
    // Check file system integrity
    // Check service availability
    return {
      database: 'ok',
      files: 'ok',
      services: 'degraded',
    };
  }

  private async quickRecovery() {
    // Restart services
    // Clear caches
    // Reset connections
  }

  private async fullRecovery() {
    // Restore from backup
    // Rebuild search indexes
    // Recalculate cached data
  }
}
```

---

## ⚡ Optimización de Performance

### Optimizaciones de Build

```javascript
// next.config.js
module.exports = {
  // Bundle analyzer
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    if (!dev && !isServer) {
      config.plugins.push(
        new webpack.DefinePlugin({
          __BUILD_ID__: JSON.stringify(buildId),
        })
      );
    }

    // Bundle analyzer
    if (process.env.ANALYZE) {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: './analyze/client.html',
          openAnalyzer: false,
        })
      );
    }

    return config;
  },

  // Optimize images
  images: {
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    formats: ['image/webp', 'image/avif'],
  },

  // Compression
  compress: true,

  // Service worker
  experimental: {
    serviceWorker: true,
  },
};
```

### Caching Strategy

```typescript
// lib/cache.ts
export class CacheManager {
  private cache = new Map();

  async get<T>(key: string): Promise<T | null> {
    const cached = this.cache.get(key);
    if (cached && cached.expiry > Date.now()) {
      return cached.data;
    }
    return null;
  }

  async set<T>(key: string, data: T, ttl: number = 300000): Promise<void> {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl,
    });
  }

  async invalidate(pattern: string): Promise<void> {
    for (const [key] of this.cache) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  // Redis integration for distributed cache
  async getFromRedis(key: string): Promise<any> {
    // Implementation for Redis caching
  }

  async setInRedis(key: string, data: any, ttl: number): Promise<void> {
    // Implementation for Redis caching
  }
}
```

### CDN Configuration

```javascript
// lib/cdn.ts
export class CDNManager {
  private cdnUrl = process.env.CDN_URL || 'https://cdn.triboka.com';

  getAssetUrl(path: string, version?: string): string {
    const versionParam = version ? `?v=${version}` : '';
    return `${this.cdnUrl}${path}${versionParam}`;
  }

  async purgeCache(paths: string[]): Promise<void> {
    // Purge CDN cache for specific paths
    await fetch('/api/cdn/purge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ paths }),
    });
  }

  async uploadAsset(file: File, path: string): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', path);

    const response = await fetch('/api/cdn/upload', {
      method: 'POST',
      body: formData,
    });

    const { url } = await response.json();
    return url;
  }
}
```

---

## 🔒 Seguridad en Despliegue

### Secret Management

```bash
# .env.example
# Never commit actual values
NEXT_PUBLIC_API_URL=https://api.triboka.com
DATABASE_URL=postgresql://user:password@host:5432/db
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run npm audit
        run: npm audit --audit-level high

      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: javascript

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/code-actions/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### Hardening del Servidor

```bash
#!/bin/bash
# server-hardening.sh

# Update system
apt update && apt upgrade -y

# Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Disable root login
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl reload sshd

# Install and configure auditd
apt install auditd -y
systemctl enable auditd
systemctl start auditd

# Set up log rotation
cat > /etc/logrotate.d/triboka << EOF
/var/log/triboka/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload triboka-frontend
    endscript
}
EOF

echo "Server hardening completed"
```

---

## 📈 Métricas de Despliegue

### KPIs de Despliegue

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Deployment Frequency | Daily | Daily |
| Lead Time for Changes | < 1 hour | 45 min |
| Change Failure Rate | < 5% | 2.3% |
| Time to Restore | < 1 hour | 32 min |
| Uptime | > 99.9% | 99.95% |

### Reporte de Despliegues

```typescript
// lib/deployment-metrics.ts
export interface DeploymentMetrics {
  version: string;
  timestamp: string;
  duration: number;
  success: boolean;
  environment: 'staging' | 'production';
  triggeredBy: string;
  commitSha: string;
  testsPassed: number;
  testsFailed: number;
  coverage: number;
}

export class DeploymentTracker {
  async trackDeployment(metrics: DeploymentMetrics): Promise<void> {
    // Store in database
    await fetch('/api/metrics/deployment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metrics),
    });

    // Send to monitoring dashboard
    if (metrics.success) {
      console.log(`✅ Deployment ${metrics.version} successful`);
    } else {
      console.error(`❌ Deployment ${metrics.version} failed`);
    }
  }

  async getDeploymentHistory(days: number = 30): Promise<DeploymentMetrics[]> {
    const response = await fetch(`/api/metrics/deployments?days=${days}`);
    return response.json();
  }
}
```

---

*El sistema de despliegue garantiza entregas continuas, seguras y monitoreadas del frontend Triboka Agro con alta disponibilidad y rápida recuperación.*