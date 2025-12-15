/**
 * Triboka Agro - Mobile Responsive Utilities
 * Utilidades JavaScript para optimización móvil
 */

class MobileOptimizer {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupViewportHeight();
        this.setupTouchHandlers();
        this.setupResizeHandlers();
        this.optimizeScrolling();
        this.setupFormOptimizations();
    }
    
    /**
     * Configura la altura del viewport para móviles
     */
    setupViewportHeight() {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 100);
        });
    }
    
    /**
     * Configura manejadores de eventos táctiles
     */
    setupTouchHandlers() {
        // Prevenir zoom en double-tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Mejorar experiencia táctil en botones
        document.addEventListener('touchstart', function(e) {
            if (e.target.classList.contains('btn') || 
                e.target.closest('.btn') || 
                e.target.classList.contains('card') ||
                e.target.closest('.card')) {
                e.target.style.transform = 'scale(0.98)';
            }
        });
        
        document.addEventListener('touchend', function(e) {
            if (e.target.classList.contains('btn') || 
                e.target.closest('.btn') || 
                e.target.classList.contains('card') ||
                e.target.closest('.card')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 100);
            }
        });
    }
    
    /**
     * Configura manejadores de redimensionamiento
     */
    setupResizeHandlers() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.adjustLayoutForViewport();
            }, 250);
        });
        
        // Ajuste inicial
        this.adjustLayoutForViewport();
    }
    
    /**
     * Ajusta el layout según el viewport
     */
    adjustLayoutForViewport() {
        const isMobile = window.innerWidth < 768;
        const isSmallMobile = window.innerWidth < 576;
        
        document.body.classList.toggle('mobile-view', isMobile);
        document.body.classList.toggle('small-mobile-view', isSmallMobile);
        
        // Ajustar tablas para móvil
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            if (isMobile) {
                if (!table.closest('.table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'table-responsive';
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
            }
        });
        
        // Ajustar modales para móvil
        const modals = document.querySelectorAll('.modal-dialog');
        modals.forEach(modal => {
            if (isMobile) {
                modal.classList.add('modal-fullscreen-sm-down');
            } else {
                modal.classList.remove('modal-fullscreen-sm-down');
            }
        });
    }
    
    /**
     * Optimiza el scrolling en dispositivos móviles
     */
    optimizeScrolling() {
        // Scroll suave en iOS
        document.documentElement.style.webkitOverflowScrolling = 'touch';
        
        // Prevenir scroll horizontal accidental
        document.addEventListener('touchmove', function(e) {
            const target = e.target;
            const isScrollable = target.scrollWidth > target.clientWidth ||
                                target.scrollHeight > target.clientHeight ||
                                target.closest('.table-responsive') ||
                                target.closest('.overflow-auto');
            
            if (!isScrollable) {
                // Solo prevenir si no es un elemento que debe hacer scroll
                if (Math.abs(e.touches[0].clientY - this.startY) < 
                    Math.abs(e.touches[0].clientX - this.startX)) {
                    e.preventDefault();
                }
            }
        });
        
        document.addEventListener('touchstart', function(e) {
            this.startX = e.touches[0].clientX;
            this.startY = e.touches[0].clientY;
        });
    }
    
    /**
     * Optimiza formularios para dispositivos móviles
     */
    setupFormOptimizations() {
        // Auto-focus en inputs cuando se abren modales
        document.addEventListener('shown.bs.modal', function(e) {
            const firstInput = e.target.querySelector('input, textarea, select');
            if (firstInput && window.innerWidth >= 768) {
                // Solo auto-focus en desktop
                setTimeout(() => firstInput.focus(), 100);
            }
        });
        
        // Mejorar UX de selects en móvil
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            if (window.innerWidth < 768) {
                select.setAttribute('size', '1');
            }
        });
        
        // Optimizar inputs numéricos
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (window.innerWidth < 768) {
                    this.setAttribute('inputmode', 'numeric');
                }
            });
        });
    }
    
    /**
     * Detecta si es un dispositivo táctil
     */
    static isTouchDevice() {
        return (('ontouchstart' in window) ||
                (navigator.maxTouchPoints > 0) ||
                (navigator.msMaxTouchPoints > 0));
    }
    
    /**
     * Obtiene información del dispositivo
     */
    static getDeviceInfo() {
        return {
            isMobile: window.innerWidth < 768,
            isSmallMobile: window.innerWidth < 576,
            isTouch: this.isTouchDevice(),
            orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape',
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
    }
}

/**
 * Utilidades específicas para componentes móviles
 */
class MobileComponentUtils {
    
    /**
     * Convierte tablas normales en tablas apiladas para móvil
     */
    static stackTable(tableSelector) {
        const tables = document.querySelectorAll(tableSelector);
        
        tables.forEach(table => {
            if (window.innerWidth < 768) {
                const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            cell.setAttribute('data-label', headers[index]);
                        }
                    });
                });
                
                table.classList.add('mobile-stacked');
            }
        });
    }
    
    /**
     * Crea un swiper horizontal para cards en móvil
     */
    static enableCardSwiper(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container || window.innerWidth >= 768) return;
        
        let startX = 0;
        let scrollLeft = 0;
        let isDown = false;
        
        container.addEventListener('touchstart', (e) => {
            isDown = true;
            startX = e.touches[0].pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });
        
        container.addEventListener('touchmove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.touches[0].pageX - container.offsetLeft;
            const walk = (x - startX) * 2;
            container.scrollLeft = scrollLeft - walk;
        });
        
        container.addEventListener('touchend', () => {
            isDown = false;
        });
    }
    
    /**
     * Optimiza dropdowns para móvil
     */
    static optimizeDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('click', function(e) {
                if (window.innerWidth < 768) {
                    e.preventDefault();
                    const menu = this.nextElementSibling;
                    if (menu && menu.classList.contains('dropdown-menu')) {
                        menu.classList.toggle('show');
                        
                        // Cerrar otros dropdowns
                        document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
                            if (otherMenu !== menu) {
                                otherMenu.classList.remove('show');
                            }
                        });
                    }
                }
            });
        });
        
        // Cerrar dropdowns al hacer click fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }
}

// CSS para tablas apiladas en móvil
const mobileStyles = `
    <style id="mobile-responsive-styles">
        @media (max-width: 767px) {
            .mobile-stacked {
                border: 0;
            }
            
            .mobile-stacked thead {
                display: none;
            }
            
            .mobile-stacked tbody tr {
                display: block;
                border: 1px solid #ccc;
                margin-bottom: 10px;
                border-radius: 8px;
                padding: 10px;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .mobile-stacked tbody td {
                display: block;
                text-align: left;
                border: none;
                padding: 5px 0;
                position: relative;
                padding-left: 35%;
            }
            
            .mobile-stacked tbody td:before {
                content: attr(data-label) ": ";
                position: absolute;
                left: 0;
                width: 30%;
                font-weight: bold;
                color: #666;
            }
            
            /* Estilos específicos para cards en móvil */
            .mobile-view .card-columns {
                column-count: 1;
            }
            
            .mobile-view .btn-group {
                display: flex;
                flex-direction: column;
            }
            
            .mobile-view .btn-group .btn {
                border-radius: 0.375rem !important;
                margin-bottom: 0.25rem;
            }
            
            /* Ajustes para notificaciones */
            .mobile-view #notification-panel {
                width: 100% !important;
                left: 0 !important;
            }
            
            /* Ajustes para formularios */
            .mobile-view .form-row {
                flex-direction: column;
            }
            
            .mobile-view .form-row .col {
                margin-bottom: 1rem;
            }
        }
        
        @media (max-width: 575px) {
            .small-mobile-view .container-fluid {
                padding-left: 10px;
                padding-right: 10px;
            }
            
            .small-mobile-view .card-body {
                padding: 1rem 0.75rem;
            }
            
            .small-mobile-view .btn {
                font-size: 0.8rem;
                padding: 0.4rem 0.8rem;
            }
        }
    </style>
`;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Agregar estilos móviles
    document.head.insertAdjacentHTML('beforeend', mobileStyles);
    
    // Inicializar optimizador móvil
    window.mobileOptimizer = new MobileOptimizer();
    
    // Aplicar optimizaciones específicas
    MobileComponentUtils.stackTable('.table:not(.no-mobile-stack)');
    MobileComponentUtils.optimizeDropdowns();
    
    // Habilitar swiper en containers de cards si es necesario
    MobileComponentUtils.enableCardSwiper('.card-deck');
    
    console.log('📱 Optimización móvil inicializada');
});

// Exportar para uso global
window.MobileOptimizer = MobileOptimizer;
window.MobileComponentUtils = MobileComponentUtils;