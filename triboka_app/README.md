# TRIBOKA App 📱

Una aplicación Flutter multiplataforma diseñada específicamente para Android e iOS.

## 🚀 Características

- **Multiplataforma**: Funciona nativamente en Android e iOS
- **Diseño Adaptativo**: Utiliza Material Design en Android y Cupertino en iOS
- **Arquitectura Limpia**: Estructura organizada con servicios, modelos y widgets
- **Información del Dispositivo**: Detecta y muestra información específica de la plataforma
- **Temas Personalizados**: Soporte para modo claro y oscuro
- **Conectividad**: Detección del estado de la conexión a internet

## 📱 Plataformas Soportadas

- ✅ **Android** (API 21+)
- ✅ **iOS** (iOS 12.0+)

## 🛠️ Tecnologías Utilizadas

- **Flutter** 3.35.6
- **Dart** 3.9.2
- **Material Design 3**
- **Cupertino (iOS)**

### 📦 Dependencias Principales

- `device_info_plus`: Información del dispositivo
- `connectivity_plus`: Estado de conectividad
- `package_info_plus`: Información de la aplicación
- `shared_preferences`: Almacenamiento local
- `path_provider`: Acceso a directorios del sistema
- `http`: Peticiones HTTP

## 🏗️ Estructura del Proyecto

```
lib/
├── main.dart                 # Punto de entrada de la aplicación
├── screens/                  # Pantallas de la aplicación
│   └── home_screen.dart     # Pantalla principal
├── widgets/                  # Widgets reutilizables
│   └── platform_button.dart # Botón adaptativo
├── services/                 # Servicios y lógica de negocio
│   └── platform_service.dart # Servicio de plataforma
├── models/                   # Modelos de datos
│   └── user.dart            # Modelo de usuario
└── utils/                    # Utilidades y constantes
    └── constants.dart       # Constantes de la aplicación
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Flutter SDK (3.35.6 o superior)
- Dart SDK (3.9.2 o superior)
- Android Studio / Xcode (para desarrollo móvil)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd triboka_app
   ```

2. **Instalar dependencias**
   ```bash
   flutter pub get
   ```

3. **Verificar configuración**
   ```bash
   flutter doctor
   ```

4. **Ejecutar la aplicación**
   ```bash
   # Para Android
   flutter run -d android
   
   # Para iOS
   flutter run -d ios
   ```

## 📱 Compilación para Producción

### Android

```bash
# Generar APK
flutter build apk --release

# Generar App Bundle (recomendado para Google Play)
flutter build appbundle --release
```

### iOS

```bash
# Generar para dispositivos iOS
flutter build ios --release

# Generar archivo IPA
flutter build ipa --release
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
flutter test

# Ejecutar tests con cobertura
flutter test --coverage

# Analizar el código
flutter analyze
```

## 📋 Características Implementadas

- [x] Pantalla principal con información de la plataforma
- [x] Detección automática de Android/iOS
- [x] Widgets adaptativos según la plataforma
- [x] Información del dispositivo y conectividad
- [x] Temas claro y oscuro
- [x] Estructura de proyecto escalable
- [x] Tests básicos

## 📋 Roadmap

- [ ] Sistema de navegación completo
- [ ] Integración con APIs externas
- [ ] Sistema de autenticación
- [ ] Almacenamiento local avanzado
- [ ] Notificaciones push
- [ ] Internacionalización (i18n)
- [ ] Análisis y métricas

## 🤝 Contribución

1. Fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📧 Contacto

**TRIBOKA Team**
- Email: contact@triboka.com
- Website: https://triboka.com

---

⭐ ¡No olvides darle una estrella al proyecto si te ha sido útil!
