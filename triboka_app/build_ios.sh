#!/bin/bash

# Script para compilar TRIBOKA App para iOS
# Autor: Sistema de desarrollo TRIBOKA
# Fecha: $(date)

set -e

echo "🍎 TRIBOKA iOS Build Script"
echo "================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "pubspec.yaml" ]; then
    print_error "Este script debe ejecutarse desde el directorio raíz del proyecto Flutter"
    exit 1
fi

# Verificar Flutter
print_message "Verificando instalación de Flutter..."
if ! command -v flutter &> /dev/null; then
    print_error "Flutter no está instalado o no está en el PATH"
    exit 1
fi

# Verificar Xcode
print_message "Verificando instalación de Xcode..."
if ! command -v xcodebuild &> /dev/null; then
    print_error "Xcode no está instalado o no está en el PATH"
    exit 1
fi

# Limpiar compilaciones anteriores
print_message "Limpiando compilaciones anteriores..."
flutter clean

# Obtener dependencias
print_message "Obteniendo dependencias de Flutter..."
flutter pub get

# Instalar pods de iOS
print_message "Instalando CocoaPods para iOS..."
cd ios
pod install
cd ..

# Verificar configuración
print_message "Verificando configuración de Flutter..."
flutter doctor

# Función para construir para simulador
build_for_simulator() {
    print_message "Construyendo para simulador iOS..."
    flutter build ios --simulator --no-codesign
    if [ $? -eq 0 ]; then
        print_success "Build para simulador completado exitosamente"
        print_message "La app está lista para ejecutar en el simulador con: flutter run"
    else
        print_error "Falló el build para simulador"
        return 1
    fi
}

# Función para construir para dispositivo
build_for_device() {
    print_message "Construyendo para dispositivo iOS..."
    flutter build ios --release --no-codesign
    if [ $? -eq 0 ]; then
        print_success "Build para dispositivo completado exitosamente"
        print_warning "Nota: Necesitarás firmar la app manualmente para instalar en dispositivo"
    else
        print_error "Falló el build para dispositivo"
        return 1
    fi
}

# Mostrar opciones
echo ""
echo "Selecciona el tipo de build:"
echo "1) Simulador iOS"
echo "2) Dispositivo iOS (sin firma)"
echo "3) Ambos"
echo "4) Solo verificar configuración"
read -p "Opción (1-4): " option

case $option in
    1)
        build_for_simulator
        ;;
    2)
        build_for_device
        ;;
    3)
        build_for_simulator
        if [ $? -eq 0 ]; then
            build_for_device
        fi
        ;;
    4)
        print_success "Configuración verificada"
        ;;
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
print_success "Script completado"
print_message "Para instalar simuladores iOS adicionales:"
print_message "1. Abre Xcode"
print_message "2. Ve a Xcode > Preferences > Components"
print_message "3. Descarga los simuladores iOS que necesites"