# 🎨 Componentes UI - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Sistema de Diseño](#sistema-de-diseño)
3. [Componentes Base](#componentes-base)
4. [Componentes del Dashboard](#componentes-del-dashboard)
5. [Componentes de Formularios](#componentes-de-formularios)
6. [Componentes de Datos](#componentes-de-datos)
7. [Componentes Especializados](#componentes-especializados)
8. [Patrones de Uso](#patrones-de-uso)
9. [Accesibilidad](#accesibilidad)
10. [Testing](#testing)

---

## 🎯 Visión General

El sistema de componentes UI de Triboka Agro está construido siguiendo principios de diseño atómico y composición, utilizando Tailwind CSS para estilos y Lucide Icons para iconografía. Los componentes están diseñados para ser:

- **Reutilizables**: Componentes modulares que se pueden combinar
- **Accesibles**: Cumplen estándares WCAG 2.1
- **Responsive**: Adaptables a diferentes tamaños de pantalla
- **Consistentes**: Siguen un sistema de diseño unificado
- **Performantes**: Optimizados para renderizado eficiente

---

## 🎨 Sistema de Diseño

### Paleta de Colores

```typescript
// lib/theme/colors.ts
export const colors = {
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    600: '#2563eb',
    900: '#1e3a8a',
  },
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    500: '#22c55e',
    600: '#16a34a',
    900: '#14532d',
  },
  accent: {
    50: '#fef3c7',
    100: '#fde68a',
    500: '#f59e0b',
    600: '#d97706',
    900: '#78350f',
  },
  neutral: {
    50: '#f9fafb',
    100: '#f3f4f6',
    500: '#6b7280',
    600: '#4b5563',
    900: '#111827',
  },
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
};
```

### Tipografía

```typescript
// lib/theme/typography.ts
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
};
```

### Espaciado

```typescript
// lib/theme/spacing.ts
export const spacing = {
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
  24: '6rem',
};
```

---

## 🧱 Componentes Base

### Button

```typescript
// components/ui/Button.tsx
import { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { LucideIcon } from 'lucide-react';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, icon: Icon, iconPosition = 'left', loading, children, ...props }, ref) => {
    return (
      <button
        className={buttonVariants({ variant, size, className })}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {Icon && iconPosition === 'left' && <Icon className="mr-2 h-4 w-4" />}
        {children}
        {Icon && iconPosition === 'right' && <Icon className="ml-2 h-4 w-4" />}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

**Uso:**
```tsx
<Button>Default Button</Button>
<Button variant="outline" size="sm">Outline Small</Button>
<Button variant="destructive" icon={Trash2} iconPosition="left">
  Delete
</Button>
<Button loading>Processing...</Button>
```

### Input

```typescript
// components/ui/Input.tsx
import { forwardRef } from 'react';
import { LucideIcon } from 'lucide-react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: LucideIcon;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, icon: Icon, error, helperText, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <div className="relative">
          {Icon && (
            <Icon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          )}
          <input
            type={type}
            className={cn(
              'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
              Icon && 'pl-10',
              error && 'border-destructive focus-visible:ring-destructive',
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {helperText && !error && <p className="text-sm text-muted-foreground">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

### Card

```typescript
// components/ui/Card.tsx
import { forwardRef } from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, padding = 'md', ...props }, ref) => {
    const paddingClasses = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border bg-card text-card-foreground shadow-sm',
          paddingClasses[padding],
          className
        )}
        {...props}
      />
    );
  }
);

Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
  )
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('text-2xl font-semibold leading-none tracking-tight', className)} {...props} />
  )
);

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-muted-foreground', className)} {...props} />
  )
);

CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
);

CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center p-6 pt-0', className)} {...props} />
  )
);

CardFooter.displayName = 'CardFooter';
```

---

## 📊 Componentes del Dashboard

### MetricCard

```typescript
// components/dashboard/MetricCard.tsx
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  color?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  loading?: boolean;
}

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  color = 'text-blue-600',
  trend,
  trendValue,
  loading = false,
}: MetricCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'stable':
        return <Minus className="h-4 w-4 text-gray-600" />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'stable':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <div className="h-4 w-4 bg-gray-200 rounded animate-pulse" />
        </CardHeader>
        <CardContent>
          <div className="h-8 w-20 bg-gray-200 rounded animate-pulse mb-1" />
          <div className="h-4 w-16 bg-gray-200 rounded animate-pulse" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
          {trend && trendValue && (
            <>
              {getTrendIcon()}
              <span className={getTrendColor()}>
                {trend === 'up' ? '+' : trend === 'down' ? '-' : ''}
                {trendValue}%
              </span>
            </>
          )}
          {description && <span>{description}</span>}
        </div>
      </CardContent>
    </Card>
  );
}
```

### DashboardHeader

```typescript
// components/dashboard/DashboardHeader.tsx
import { Button } from '@/components/ui/Button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/Avatar';
import { Bell, Search, Settings } from 'lucide-react';
import { useAuthStore } from '@/stores/auth';

export interface DashboardHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode[];
}

export function DashboardHeader({ title, subtitle, actions = [] }: DashboardHeaderProps) {
  const { user } = useAuthStore();

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar..."
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Actions */}
        {actions.map((action, index) => (
          <div key={index}>{action}</div>
        ))}

        {/* Notifications */}
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>

        {/* Settings */}
        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>

        {/* User Avatar */}
        <Avatar>
          <AvatarImage src={user?.avatar} alt={user?.name} />
          <AvatarFallback>
            {user?.name?.split(' ').map(n => n[0]).join('').toUpperCase()}
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
  );
}
```

### Sidebar

```typescript
// components/dashboard/Sidebar.tsx
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { ScrollArea } from '@/components/ui/ScrollArea';
import {
  Home,
  Package,
  FileText,
  Award,
  Users,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useAuthStore } from '@/stores/auth';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Lotes', href: '/dashboard/lots', icon: Package },
  { name: 'Contratos', href: '/dashboard/contracts', icon: FileText },
  { name: 'Certificaciones', href: '/dashboard/certifications', icon: Award },
  { name: 'Usuarios', href: '/dashboard/users', icon: Users, adminOnly: true },
  { name: 'Reportes', href: '/dashboard/reports', icon: BarChart3 },
  { name: 'Configuración', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const { user } = useAuthStore();

  const filteredNavigation = navigation.filter(
    item => !item.adminOnly || user?.role === 'admin'
  );

  return (
    <div className={cn(
      'flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TA</span>
            </div>
            <span className="font-semibold text-gray-900">Triboka Agro</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="ml-auto"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-1">
          {filteredNavigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.name} href={item.href}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn(
                    'w-full justify-start',
                    collapsed ? 'px-2' : 'px-3',
                    isActive && 'bg-green-50 text-green-700 hover:bg-green-100'
                  )}
                >
                  <item.icon className={cn('h-5 w-5', collapsed ? '' : 'mr-3')} />
                  {!collapsed && <span>{item.name}</span>}
                </Button>
              </Link>
            );
          })}
        </nav>
      </ScrollArea>
    </div>
  );
}
```

---

## 📝 Componentes de Formularios

### FormField

```typescript
// components/forms/FormField.tsx
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Checkbox } from '@/components/ui/Checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';

export type FieldType = 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select' | 'checkbox' | 'radio';

export interface FormFieldProps {
  name: string;
  label: string;
  type: FieldType;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  options?: { value: string; label: string }[];
  value?: any;
  onChange?: (value: any) => void;
  onBlur?: () => void;
}

export function FormField({
  name,
  label,
  type,
  placeholder,
  required,
  disabled,
  error,
  helperText,
  options = [],
  value,
  onChange,
  onBlur,
}: FormFieldProps) {
  const handleChange = (newValue: any) => {
    onChange?.(newValue);
  };

  const renderField = () => {
    switch (type) {
      case 'textarea':
        return (
          <Textarea
            id={name}
            name={name}
            placeholder={placeholder}
            value={value || ''}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={onBlur}
            disabled={disabled}
            error={error}
          />
        );

      case 'select':
        return (
          <Select
            value={value || ''}
            onValueChange={handleChange}
            disabled={disabled}
          >
            <SelectTrigger>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'checkbox':
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              id={name}
              name={name}
              checked={value || false}
              onCheckedChange={handleChange}
              disabled={disabled}
            />
            <Label htmlFor={name} className="text-sm font-normal">
              {label}
            </Label>
          </div>
        );

      case 'radio':
        return (
          <RadioGroup
            value={value || ''}
            onValueChange={handleChange}
            disabled={disabled}
          >
            {options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value} id={`${name}-${option.value}`} />
                <Label htmlFor={`${name}-${option.value}`} className="text-sm font-normal">
                  {option.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      default:
        return (
          <Input
            id={name}
            name={name}
            type={type}
            placeholder={placeholder}
            value={value || ''}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={onBlur}
            disabled={disabled}
            error={error}
          />
        );
    }
  };

  if (type === 'checkbox') {
    return (
      <div className="space-y-1">
        {renderField()}
        {error && <p className="text-sm text-destructive">{error}</p>}
        {helperText && !error && <p className="text-sm text-muted-foreground">{helperText}</p>}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <Label htmlFor={name}>
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </Label>
      {renderField()}
      {error && <p className="text-sm text-destructive">{error}</p>}
      {helperText && !error && <p className="text-sm text-muted-foreground">{helperText}</p>}
    </div>
  );
}
```

### LotForm

```typescript
// components/forms/LotForm.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { FormField } from './FormField';
import { useLotsStore } from '@/stores/lots';

const lotSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  description: z.string().optional(),
  weight: z.number().min(0.1, 'El peso debe ser mayor a 0'),
  unit: z.enum(['kg', 'ton', 'lb']),
  quality: z.enum(['premium', 'standard', 'basic']),
  location: z.string().min(1, 'La ubicación es requerida'),
  harvestDate: z.string().min(1, 'La fecha de cosecha es requerida'),
  certifications: z.array(z.string()).optional(),
});

type LotFormData = z.infer<typeof lotSchema>;

export interface LotFormProps {
  initialData?: Partial<LotFormData>;
  onSubmit: (data: LotFormData) => Promise<void>;
  onCancel?: () => void;
}

export function LotForm({ initialData, onSubmit, onCancel }: LotFormProps) {
  const [loading, setLoading] = useState(false);
  const { createLot, updateLot } = useLotsStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<LotFormData>({
    resolver: zodResolver(lotSchema),
    defaultValues: initialData,
  });

  const onFormSubmit = async (data: LotFormData) => {
    setLoading(true);
    try {
      await onSubmit(data);
    } finally {
      setLoading(false);
    }
  };

  const unitOptions = [
    { value: 'kg', label: 'Kilogramos' },
    { value: 'ton', label: 'Toneladas' },
    { value: 'lb', label: 'Libras' },
  ];

  const qualityOptions = [
    { value: 'premium', label: 'Premium' },
    { value: 'standard', label: 'Estándar' },
    { value: 'basic', label: 'Básico' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>{initialData?.id ? 'Editar Lote' : 'Crear Nuevo Lote'}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              name="name"
              label="Nombre del Lote"
              type="text"
              placeholder="Ej: Lote Cacao Premium 2025"
              required
              error={errors.name?.message}
              {...register('name')}
            />

            <FormField
              name="weight"
              label="Peso"
              type="number"
              placeholder="0.00"
              required
              error={errors.weight?.message}
              {...register('weight', { valueAsNumber: true })}
            />

            <FormField
              name="unit"
              label="Unidad"
              type="select"
              options={unitOptions}
              required
              error={errors.unit?.message}
              value={watch('unit')}
              onChange={(value) => setValue('unit', value)}
            />

            <FormField
              name="quality"
              label="Calidad"
              type="select"
              options={qualityOptions}
              required
              error={errors.quality?.message}
              value={watch('quality')}
              onChange={(value) => setValue('quality', value)}
            />

            <FormField
              name="location"
              label="Ubicación"
              type="text"
              placeholder="Ej: Finca San José, Ecuador"
              required
              error={errors.location?.message}
              {...register('location')}
            />

            <FormField
              name="harvestDate"
              label="Fecha de Cosecha"
              type="date"
              required
              error={errors.harvestDate?.message}
              {...register('harvestDate')}
            />
          </div>

          <FormField
            name="description"
            label="Descripción"
            type="textarea"
            placeholder="Describe las características del lote..."
            error={errors.description?.message}
            {...register('description')}
          />

          <div className="flex justify-end space-x-4">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancelar
              </Button>
            )}
            <Button type="submit" loading={loading}>
              {initialData?.id ? 'Actualizar Lote' : 'Crear Lote'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

---

## 📊 Componentes de Datos

### DataTable

```typescript
// components/ui/DataTable.tsx
import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { ChevronLeft, ChevronRight, Search, Filter } from 'lucide-react';

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: boolean;
  pageSize?: number;
  searchable?: boolean;
  filterable?: boolean;
  onRowClick?: (row: T) => void;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  onFilter?: (filters: Record<string, any>) => void;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  pagination = true,
  pageSize = 10,
  searchable = true,
  filterable = true,
  onRowClick,
  onSort,
  onFilter,
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [filters, setFilters] = useState<Record<string, any>>({});

  const filteredData = data.filter((row) =>
    Object.values(row).some((value) =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortKey) return 0;
    const aValue = a[sortKey];
    const bValue = b[sortKey];
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const paginatedData = pagination
    ? sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    : sortedData;

  const totalPages = Math.ceil(sortedData.length / pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
    onSort?.(key, sortDirection);
  };

  const handleFilter = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilter?.(newFilters);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-10 bg-gray-200 rounded animate-pulse" />
        <div className="space-y-2">
          {Array.from({ length: pageSize }).map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex items-center justify-between">
        {searchable && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Buscar..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-64"
            />
          </div>
        )}

        {filterable && (
          <div className="flex items-center space-x-2">
            {columns
              .filter((col) => col.filterable)
              .map((col) => (
                <Select
                  key={String(col.key)}
                  onValueChange={(value) => handleFilter(String(col.key), value)}
                >
                  <SelectTrigger className="w-32">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue placeholder={col.header} />
                  </SelectTrigger>
                  <SelectContent>
                    {/* Filter options would be dynamic based on data */}
                    <SelectItem value="all">Todos</SelectItem>
                  </SelectContent>
                </Select>
              ))}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead
                  key={String(column.key)}
                  className={column.sortable ? 'cursor-pointer hover:bg-gray-50' : ''}
                  onClick={() => column.sortable && handleSort(String(column.key))}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.header}</span>
                    {column.sortable && sortKey === column.key && (
                      <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center py-8 text-gray-500">
                  No se encontraron resultados
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => (
                <TableRow
                  key={index}
                  className={onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((column) => (
                    <TableCell key={String(column.key)}>
                      {column.render
                        ? column.render(row[column.key as keyof T], row)
                        : String(row[column.key as keyof T] || '')
                      }
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Mostrando {(currentPage - 1) * pageSize + 1} a{' '}
            {Math.min(currentPage * pageSize, sortedData.length)} de {sortedData.length} resultados
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Anterior
            </Button>
            <span className="text-sm">
              Página {currentPage} de {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
            >
              Siguiente
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
```

### LotCard

```typescript
// components/dashboard/LotCard.tsx
import { Package, MapPin, Calendar, Award, Share2, Edit, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export interface Lot {
  id: string;
  name: string;
  description?: string;
  weight: number;
  unit: string;
  quality: 'premium' | 'standard' | 'basic';
  location: string;
  harvestDate: string;
  certifications?: string[];
  status: 'available' | 'sold' | 'reserved';
  createdAt: string;
  updatedAt: string;
}

export interface LotCardProps {
  lot: Lot;
  onView?: (lot: Lot) => void;
  onShare?: (lot: Lot) => void;
  onEdit?: (lot: Lot) => void;
}

export function LotCard({ lot, onView, onShare, onEdit }: LotCardProps) {
  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'premium':
        return 'bg-green-100 text-green-800';
      case 'standard':
        return 'bg-blue-100 text-blue-800';
      case 'basic':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'sold':
        return 'bg-red-100 text-red-800';
      case 'reserved':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2">
            <Package className="h-5 w-5 text-gray-500" />
            <h3 className="font-semibold text-lg truncate">{lot.name}</h3>
          </div>
          <Badge className={getStatusColor(lot.status)}>
            {lot.status === 'available' ? 'Disponible' :
             lot.status === 'sold' ? 'Vendido' : 'Reservado'}
          </Badge>
        </div>
        {lot.description && (
          <p className="text-sm text-gray-600 line-clamp-2">{lot.description}</p>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Detalles principales */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-500">Peso:</span>
            <span className="font-semibold">{lot.weight} {lot.unit}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-500">Calidad:</span>
            <Badge variant="outline" className={getQualityColor(lot.quality)}>
              {lot.quality}
            </Badge>
          </div>
        </div>

        {/* Ubicación y fecha */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center space-x-2">
            <MapPin className="h-4 w-4 text-gray-400" />
            <span className="text-gray-600">{lot.location}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span className="text-gray-600">
              Cosechado {formatDistanceToNow(new Date(lot.harvestDate), {
                addSuffix: true,
                locale: es
              })}
            </span>
          </div>
        </div>

        {/* Certificaciones */}
        {lot.certifications && lot.certifications.length > 0 && (
          <div className="flex items-center space-x-2">
            <Award className="h-4 w-4 text-gray-400" />
            <div className="flex flex-wrap gap-1">
              {lot.certifications.slice(0, 3).map((cert) => (
                <Badge key={cert} variant="outline" className="text-xs">
                  {cert}
                </Badge>
              ))}
              {lot.certifications.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{lot.certifications.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Acciones */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="text-xs text-gray-500">
            Actualizado {formatDistanceToNow(new Date(lot.updatedAt), {
              addSuffix: true,
              locale: es
            })}
          </div>
          <div className="flex items-center space-x-2">
            {onView && (
              <Button variant="ghost" size="sm" onClick={() => onView(lot)}>
                <Eye className="h-4 w-4" />
              </Button>
            )}
            {onShare && (
              <Button variant="ghost" size="sm" onClick={() => onShare(lot)}>
                <Share2 className="h-4 w-4" />
              </Button>
            )}
            {onEdit && (
              <Button variant="ghost" size="sm" onClick={() => onEdit(lot)}>
                <Edit className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 🔧 Componentes Especializados

### BlockchainTimeline

```typescript
// components/blockchain/BlockchainTimeline.tsx
import { CheckCircle, Clock, AlertCircle, Package, Truck, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export interface BlockchainEvent {
  id: string;
  type: 'created' | 'transported' | 'certified' | 'sold' | 'delivered';
  title: string;
  description: string;
  timestamp: string;
  status: 'pending' | 'confirmed' | 'failed';
  transactionHash?: string;
  blockNumber?: number;
  metadata?: Record<string, any>;
}

export interface BlockchainTimelineProps {
  lotId: string;
  events: BlockchainEvent[];
  loading?: boolean;
}

export function BlockchainTimeline({ lotId, events, loading = false }: BlockchainTimelineProps) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'created':
        return Package;
      case 'transported':
        return Truck;
      case 'certified':
        return CheckCircle;
      case 'sold':
        return DollarSign;
      case 'delivered':
        return CheckCircle;
      default:
        return Clock;
    }
  };

  const getEventColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600 bg-green-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <Badge className="bg-green-100 text-green-800">Confirmado</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pendiente</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Fallido</Badge>;
      default:
        return <Badge variant="outline">Desconocido</Badge>;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Timeline Blockchain</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const sortedEvents = [...events].sort((a, b) =>
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Package className="h-5 w-5" />
          <span>Timeline Blockchain - Lote {lotId}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {sortedEvents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No hay eventos registrados en blockchain</p>
          </div>
        ) : (
          <div className="space-y-6">
            {sortedEvents.map((event, index) => {
              const Icon = getEventIcon(event.type);
              const isLast = index === sortedEvents.length - 1;

              return (
                <div key={event.id} className="flex items-start space-x-4">
                  {/* Timeline line */}
                  {!isLast && (
                    <div className="absolute left-4 top-8 w-px h-full bg-gray-200" />
                  )}

                  {/* Event icon */}
                  <div className={`relative flex items-center justify-center w-8 h-8 rounded-full ${getEventColor(event.status)}`}>
                    <Icon className="h-4 w-4" />
                  </div>

                  {/* Event content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">{event.title}</h4>
                      {getStatusBadge(event.status)}
                    </div>

                    <p className="text-sm text-gray-600 mt-1">{event.description}</p>

                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>
                        {formatDistanceToNow(new Date(event.timestamp), {
                          addSuffix: true,
                          locale: es
                        })}
                      </span>

                      {event.transactionHash && (
                        <span className="font-mono">
                          TX: {event.transactionHash.slice(0, 10)}...
                        </span>
                      )}

                      {event.blockNumber && (
                        <span>Bloque: {event.blockNumber}</span>
                      )}
                    </div>

                    {/* Additional metadata */}
                    {event.metadata && Object.keys(event.metadata).length > 0 && (
                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                        <details>
                          <summary className="cursor-pointer font-medium">Detalles técnicos</summary>
                          <pre className="mt-2 whitespace-pre-wrap">
                            {JSON.stringify(event.metadata, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

### DealRoom

```typescript
// components/dashboard/DealRoom.tsx
import { useState, useEffect } from 'react';
import { MessageCircle, Send, Users, DollarSign, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export interface Message {
  id: string;
  senderId: string;
  senderName: string;
  senderAvatar?: string;
  content: string;
  timestamp: string;
  type: 'text' | 'offer' | 'counter_offer' | 'accept' | 'reject';
  metadata?: {
    amount?: number;
    currency?: string;
    conditions?: string;
  };
}

export interface DealRoomProps {
  dealId: string;
  participants: Array<{
    id: string;
    name: string;
    avatar?: string;
    role: 'buyer' | 'seller' | 'mediator';
  }>;
  messages: Message[];
  currentUserId: string;
  onSendMessage: (content: string, type?: Message['type'], metadata?: any) => void;
  loading?: boolean;
}

export function DealRoom({
  dealId,
  participants,
  messages,
  currentUserId,
  onSendMessage,
  loading = false,
}: DealRoomProps) {
  const [newMessage, setNewMessage] = useState('');
  const [messageType, setMessageType] = useState<Message['type']>('text');

  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    onSendMessage(newMessage, messageType);
    setNewMessage('');
    setMessageType('text');
  };

  const getMessageTypeColor = (type: Message['type']) => {
    switch (type) {
      case 'offer':
        return 'bg-blue-100 text-blue-800';
      case 'counter_offer':
        return 'bg-yellow-100 text-yellow-800';
      case 'accept':
        return 'bg-green-100 text-green-800';
      case 'reject':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMessageTypeIcon = (type: Message['type']) => {
    switch (type) {
      case 'offer':
        return <DollarSign className="h-3 w-3" />;
      case 'counter_offer':
        return <DollarSign className="h-3 w-3" />;
      case 'accept':
        return <CheckCircle className="h-3 w-3" />;
      case 'reject':
        return <X className="h-3 w-3" />;
      default:
        return <MessageCircle className="h-3 w-3" />;
    }
  };

  const renderMessage = (message: Message) => {
    const isCurrentUser = message.senderId === currentUserId;
    const participant = participants.find(p => p.id === message.senderId);

    return (
      <div key={message.id} className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex ${isCurrentUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2 max-w-xs lg:max-w-md`}>
          <Avatar className="w-8 h-8">
            <AvatarImage src={participant?.avatar} alt={participant?.name} />
            <AvatarFallback>
              {participant?.name?.split(' ').map(n => n[0]).join('').toUpperCase()}
            </AvatarFallback>
          </Avatar>

          <div className={`rounded-lg p-3 ${isCurrentUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
            {!isCurrentUser && (
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-xs font-medium">{participant?.name}</span>
                <Badge variant="outline" className="text-xs">
                  {participant?.role}
                </Badge>
              </div>
            )}

            {message.type !== 'text' && (
              <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded text-xs mb-2 ${getMessageTypeColor(message.type)}`}>
                {getMessageTypeIcon(message.type)}
                <span className="capitalize">{message.type.replace('_', ' ')}</span>
              </div>
            )}

            <p className="text-sm">{message.content}</p>

            {message.metadata && (
              <div className="mt-2 p-2 bg-black/10 rounded text-xs">
                {message.metadata.amount && (
                  <div className="font-medium">
                    ${message.metadata.amount} {message.metadata.currency || 'USD'}
                  </div>
                )}
                {message.metadata.conditions && (
                  <div className="text-xs opacity-80 mt-1">
                    {message.metadata.conditions}
                  </div>
                )}
              </div>
            )}

            <div className={`text-xs mt-1 ${isCurrentUser ? 'text-blue-200' : 'text-gray-500'}`}>
              {formatDistanceToNow(new Date(message.timestamp), {
                addSuffix: true,
                locale: es
              })}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <MessageCircle className="h-5 w-5" />
            <span>Sala de Negociación - {dealId}</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Users className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">{participants.length} participantes</span>
          </div>
        </div>

        {/* Participants */}
        <div className="flex items-center space-x-2 mt-2">
          {participants.map((participant) => (
            <div key={participant.id} className="flex items-center space-x-1">
              <Avatar className="w-6 h-6">
                <AvatarImage src={participant.avatar} alt={participant.name} />
                <AvatarFallback className="text-xs">
                  {participant.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="text-xs text-gray-600">{participant.name}</span>
            </div>
          ))}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse" />
                    <div className="bg-gray-200 rounded-lg p-3 w-64 animate-pulse">
                      <div className="h-4 bg-gray-300 rounded mb-2" />
                      <div className="h-3 bg-gray-300 rounded w-3/4" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No hay mensajes aún. ¡Inicia la conversación!</p>
            </div>
          ) : (
            <div className="space-y-1">
              {messages.map(renderMessage)}
            </div>
          )}
        </ScrollArea>

        {/* Message Input */}
        <div className="border-t p-4">
          <div className="flex items-end space-x-2">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <select
                  value={messageType}
                  onChange={(e) => setMessageType(e.target.value as Message['type'])}
                  className="text-xs border rounded px-2 py-1"
                >
                  <option value="text">Mensaje</option>
                  <option value="offer">Oferta</option>
                  <option value="counter_offer">Contraoferta</option>
                  <option value="accept">Aceptar</option>
                  <option value="reject">Rechazar</option>
                </select>
              </div>
              <Input
                placeholder="Escribe tu mensaje..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={loading}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!newMessage.trim() || loading}
              size="icon"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 🎯 Patrones de Uso

### Composición de Componentes

```tsx
// Ejemplo de composición de componentes
function DashboardPage() {
  return (
    <MainLayout>
      <DashboardHeader
        title="Dashboard Triboka Agro"
        subtitle="Panel de control principal"
        actions={[
          <Button key="export" variant="outline" icon={Download}>
            Exportar
          </Button>,
          <Button key="create" icon={Plus}>
            Nuevo Lote
          </Button>
        ]}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Lotes Activos"
          value="24"
          description="+12% vs mes anterior"
          icon={Package}
          color="text-blue-600"
          trend="up"
          trendValue={12}
        />
        {/* Más métricas... */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DataTable
            data={lots}
            columns={lotColumns}
            pagination
            searchable
            onRowClick={handleLotClick}
          />
        </div>

        <div className="space-y-6">
          <BlockchainTimeline lotId="LOT-001" events={blockchainEvents} />
          <DealRoom
            dealId="DEAL-001"
            participants={dealParticipants}
            messages={dealMessages}
            currentUserId={currentUser.id}
            onSendMessage={handleSendMessage}
          />
        </div>
      </div>
    </MainLayout>
  );
}
```

### Custom Hooks para Lógica de Componentes

```tsx
// hooks/useDashboardData.ts
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/auth';
import { useLotsStore } from '@/stores/lots';
import { apiClient } from '@/services/api';

export function useDashboardData() {
  const { user } = useAuthStore();
  const { lots, loading: lotsLoading, fetchLots } = useLotsStore();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);

        // Cargar lotes
        await fetchLots();

        // Cargar métricas
        const dashboardMetrics = await apiClient.getDashboardMetrics();
        setMetrics(dashboardMetrics);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadDashboardData();
    }
  }, [user, fetchLots]);

  return {
    lots,
    metrics,
    loading: loading || lotsLoading,
  };
}
```

---

## ♿ Accesibilidad

### Principios de Accesibilidad

1. **Semántica HTML**: Uso correcto de elementos semánticos
2. **Navegación por teclado**: Todos los componentes son navegables con teclado
3. **Texto alternativo**: Imágenes y iconos tienen texto alternativo
4. **Contraste de color**: Cumple ratios de contraste WCAG 2.1 AA
5. **Screen readers**: Compatible con lectores de pantalla

### Implementación en Componentes

```tsx
// Ejemplo de componente accesible
export const AccessibleButton = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, icon: Icon, loading, ...props }, ref) => {
    return (
      <button
        ref={ref}
        {...props}
        aria-disabled={loading || props.disabled}
        aria-label={Icon ? `${children} (con icono)` : children}
      >
        {loading && (
          <span className="sr-only">Cargando...</span>
        )}
        {Icon && <Icon aria-hidden="true" />}
        <span>{children}</span>
      </button>
    );
  }
);
```

### Testing de Accesibilidad

```typescript
// tests/components/Button.test.tsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard navigable', () => {
    const { getByRole } = render(<Button onClick={mockOnClick}>Click me</Button>);
    const button = getByRole('button');

    button.focus();
    expect(button).toHaveFocus();

    fireEvent.keyDown(button, { key: 'Enter' });
    expect(mockOnClick).toHaveBeenCalled();
  });
});
```

---

## 🧪 Testing

### Estrategia de Testing

1. **Unit Tests**: Componentes individuales
2. **Integration Tests**: Interacción entre componentes
3. **E2E Tests**: Flujos completos de usuario
4. **Accessibility Tests**: Cumplimiento WCAG
5. **Visual Regression Tests**: Cambios visuales

### Ejemplos de Tests

```tsx
// tests/components/MetricCard.test.tsx
import { render, screen } from '@testing-library/react';
import { MetricCard } from '@/components/dashboard/MetricCard';

describe('MetricCard', () => {
  const defaultProps = {
    title: 'Test Metric',
    value: '100',
    icon: Package,
    color: 'text-blue-600',
  };

  it('renders correctly', () => {
    render(<MetricCard {...defaultProps} />);

    expect(screen.getByText('Test Metric')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<MetricCard {...defaultProps} loading />);

    expect(screen.getByText('Test Metric')).toBeInTheDocument();
    // Verificar que los elementos de carga están presentes
  });

  it('displays trend correctly', () => {
    render(
      <MetricCard
        {...defaultProps}
        trend="up"
        trendValue={10}
        description="vs last month"
      />
    );

    expect(screen.getByText('↑')).toBeInTheDocument();
    expect(screen.getByText('+10%')).toBeInTheDocument();
    expect(screen.getByText('vs last month')).toBeInTheDocument();
  });
});
```

### Testing de Formularios

```tsx
// tests/components/LotForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LotForm } from '@/components/forms/LotForm';

describe('LotForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  it('renders all form fields', () => {
    render(<LotForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/nombre del lote/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/peso/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/unidad/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/calidad/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<LotForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /crear lote/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/el nombre es requerido/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits form with valid data', async () => {
    render(<LotForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText(/nombre del lote/i), {
      target: { value: 'Test Lot' },
    });
    fireEvent.change(screen.getByLabelText(/peso/i), {
      target: { value: '100' },
    });
    // ... más campos

    const submitButton = screen.getByRole('button', { name: /crear lote/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Lot',
          weight: 100,
        })
      );
    });
  });
});
```

---

## 📚 Conclusión

El sistema de componentes UI de Triboka Agro proporciona:

- **Consistencia Visual**: Sistema de diseño unificado con Tailwind CSS
- **Reutilización**: Componentes modulares y composables
- **Accesibilidad**: Cumplimiento de estándares WCAG 2.1
- **Performance**: Optimización para renderizado eficiente
- **Mantenibilidad**: Código bien estructurado y testeado
- **Escalabilidad**: Arquitectura preparada para crecimiento

Los componentes están organizados en capas claras (base, dashboard, formularios, datos, especializados) y siguen patrones de diseño consistentes que facilitan el desarrollo y mantenimiento del frontend.