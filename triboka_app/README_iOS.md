# TRIBOKA iOS Setup & Build Guide

## 📱 Requisitos Previos

### Software Necesario
- **macOS** (para desarrollo iOS)
- **Xcode 16.4+** instalado desde App Store
- **Flutter 3.35.6+** 
- **CocoaPods** instalado

### Verificación de Requisitos
```bash
# Verificar Flutter
flutter doctor

# Verificar Xcode
xcodebuild -version

# Verificar CocoaPods
pod --version
```

## 🛠️ Configuración Inicial

### 1. Instalar Simuladores iOS
1. Abrir **Xcode**
2. Ir a **Xcode > Settings > Components**
3. Descargar e instalar **iOS 17.0+** o versiones disponibles
4. Esperar a que termine la descarga e instalación

### 2. Configurar Proyecto
```bash
# Navegar al directorio del proyecto
cd triboka_app

# Instalar dependencias Flutter
flutter pub get

# Instalar dependencias iOS (CocoaPods)
cd ios && pod install && cd ..
```

## 🚀 Compilación y Ejecución

### Método 1: Script Automatizado
```bash
# Hacer ejecutable el script (solo primera vez)
chmod +x build_ios.sh

# Ejecutar script interactivo
./build_ios.sh
```

### Método 2: Comandos Flutter
```bash
# Para simulador
flutter run -d "iPhone"

# Para compilar sin ejecutar
flutter build ios --simulator

# Para dispositivo (requiere configuración de firma)
flutter build ios --release --no-codesign
```

### Método 3: Usando Xcode
```bash
# Abrir el workspace en Xcode
open ios/Runner.xcworkspace

# Compilar desde Xcode:
# 1. Seleccionar dispositivo/simulador
# 2. Product > Build (⌘+B)
# 3. Product > Run (⌘+R)
```

## 📦 Generación de IPA

### Para Distribución Ad-Hoc
```bash
flutter build ios --release --no-codesign
```

### Usando Fastlane (Recomendado)
```bash
# Instalar Fastlane
sudo gem install fastlane

# Ejecutar build
fastlane ios build_release
```

## 🔧 Configuración del Proyecto

### Bundle Identifier
- **ID:** `com.triboka.tribokaApp`
- **Nombre:** TRIBOKA
- **Versión:** 1.0.0

### Características Habilitadas
- ✅ Firebase Cloud Messaging
- ✅ Push Notifications  
- ✅ Background App Refresh
- ✅ Network Requests
- ✅ Local Storage

### Orientaciones Soportadas
- ✅ Portrait
- ✅ Landscape Left
- ✅ Landscape Right

## 🐛 Solución de Problemas

### Error: "iOS X.X is not installed"
**Solución:**
1. Abrir Xcode
2. Ir a Xcode > Settings > Components
3. Descargar la versión de iOS requerida

### Error: "No provisioning profile"
**Solución:**
- Para pruebas: usar `--no-codesign`
- Para distribución: configurar Apple Developer Account

### Error: "CocoaPods not found"
**Solución:**
```bash
sudo gem install cocoapods
cd ios && pod install
```

### Error: "Unable to find destination"
**Solución:**
1. Verificar que el simulador esté instalado
2. Iniciar simulador: `open -a Simulator`
3. Verificar dispositivos: `flutter devices`

## 📋 Checklist Pre-Compilación

- [ ] Xcode instalado y actualizado
- [ ] Simuladores iOS descargados
- [ ] Flutter actualizado (`flutter upgrade`)
- [ ] Dependencias instaladas (`flutter pub get`)
- [ ] CocoaPods actualizado (`cd ios && pod install`)
- [ ] Bundle ID configurado correctamente
- [ ] Firebase configurado (si aplica)

## 🎯 Distribución

### TestFlight (App Store Connect)
1. Configurar Apple Developer Account
2. Crear certificados y provisioning profiles
3. Usar `flutter build ios --release`
4. Subir a App Store Connect

### Distribución Ad-Hoc
1. Generar IPA sin firma: `flutter build ios --no-codesign`
2. Firmar manualmente con herramientas de desarrollo
3. Distribuir via email/web

### Sideloading (Para Pruebas)
1. Usar Xcode para instalar directamente
2. Confiar certificado de desarrollador en dispositivo
3. Ejecutar desde Xcode

## 📞 Soporte

Para problemas específicos de iOS:
- Consultar [Flutter iOS Deployment](https://docs.flutter.dev/deployment/ios)
- Revisar [Xcode Documentation](https://developer.apple.com/documentation/xcode)
- Verificar [CocoaPods Guides](https://guides.cocoapods.org/)

---
**TRIBOKA Development Team**  
Versión: 1.0.0 | Fecha: Octubre 2025