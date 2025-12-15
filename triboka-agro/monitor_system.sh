#!/bin/bash
# Triboka System Monitoring Script
# Monitoreo automatizado y gestión de logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
MONITOR_LOG="$LOG_DIR/system_monitor.log"
HEALTH_LOG="$LOG_DIR/health_checks.log"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$MONITOR_LOG"
}

# Función para verificar servicios
check_services() {
    log "🔍 Iniciando verificación de servicios..."

    # Verificar servicios systemd
    services=("triboka-flask.service" "triboka-frontend.service" "triboka-notifications.service" "triboka-inventory.service")

    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            log "✅ $service: ACTIVE"
        else
            log "❌ $service: INACTIVE - Intentando reiniciar..."
            sudo systemctl restart "$service"
            sleep 5
            if systemctl is-active --quiet "$service"; then
                log "✅ $service: Reiniciado exitosamente"
            else
                log "❌ $service: Falló el reinicio"
            fi
        fi
    done
}

# Función para ejecutar health checks
run_health_checks() {
    log "🏥 Ejecutando health checks..."

    if python3 "$SCRIPT_DIR/health_monitor.py" >> "$HEALTH_LOG" 2>&1; then
        log "✅ Health checks completados exitosamente"
    else
        log "❌ Health checks fallaron - revisar $HEALTH_LOG"
    fi
}

# Función para verificar logs de errores
check_error_logs() {
    log "📋 Verificando logs de errores..."

    # Verificar logs de nginx
    if [ -f "/var/log/nginx/triboka_error.log" ]; then
        errors=$(tail -n 50 "/var/log/nginx/triboka_error.log" | grep -i error | wc -l)
        if [ "$errors" -gt 0 ]; then
            log "⚠️  Se encontraron $errors errores en nginx - revisar /var/log/nginx/triboka_error.log"
        else
            log "✅ No hay errores recientes en nginx"
        fi
    fi

    # Verificar logs de servicios
    for service in flask frontend notifications inventory; do
        log_file="$SCRIPT_DIR/logs/${service}.log"
        if [ -f "$log_file" ]; then
            errors=$(tail -n 100 "$log_file" | grep -i error | wc -l)
            if [ "$errors" -gt 0 ]; then
                log "⚠️  Se encontraron $errors errores en $service - revisar $log_file"
            fi
        fi
    done
}

# Función para limpiar logs antiguos
cleanup_logs() {
    log "🧹 Limpiando logs antiguos..."

    # Mantener solo últimos 7 días de logs de health
    find "$LOG_DIR" -name "health_checks.log.*" -mtime +7 -delete 2>/dev/null || true

    # Rotar log principal si es muy grande (>10MB)
    if [ -f "$MONITOR_LOG" ] && [ "$(stat -f%z "$MONITOR_LOG" 2>/dev/null || stat -c%s "$MONITOR_LOG")" -gt 10485760 ]; then
        mv "$MONITOR_LOG" "$MONITOR_LOG.$(date +%Y%m%d_%H%M%S)"
        log "📄 Log rotado por tamaño"
    fi
}

# Función para verificar uso de recursos
check_resources() {
    log "📊 Verificando uso de recursos..."

    # Memoria
    mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    log "💾 Memoria: ${mem_usage}% usada"

    # CPU
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    log "⚡ CPU: ${cpu_usage}% usada"

    # Disco
    disk_usage=$(df / | tail -1 | awk '{print $5}')
    log "💿 Disco: ${disk_usage} usado"
}

# Función principal
main() {
    log "🚀 Iniciando monitoreo del sistema Triboka"

    check_services
    echo "---" >> "$HEALTH_LOG"
    run_health_checks
    check_error_logs
    check_resources
    cleanup_logs

    log "✅ Monitoreo completado"
    echo "==================================================" >> "$MONITOR_LOG"
}

# Ejecutar según parámetros
case "${1:-}" in
    "health")
        run_health_checks
        ;;
    "services")
        check_services
        ;;
    "resources")
        check_resources
        ;;
    "logs")
        check_error_logs
        ;;
    "cleanup")
        cleanup_logs
        ;;
    *)
        main
        ;;
esac