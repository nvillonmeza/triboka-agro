/**
 * ESG Analytics Charts Generator
 * Genera gráficos dinámicos para el dashboard de analytics ESG
 */

class ESGChartsManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#2E8B57',
            secondary: '#4CAF50',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            light: '#f8f9fa',
            dark: '#343a40'
        };
    }

    /**
     * Inicializar todos los gráficos ESG
     */
    initializeAllCharts(esgData) {
        this.createCarbonTrendChart(esgData);
        this.createCertificationsChart(esgData);
        this.createESGDistributionChart(esgData);
        this.createSocialImpactChart(esgData);
    }

    /**
     * Crear gráfico de tendencia de carbono
     */
    createCarbonTrendChart(esgData) {
        const ctx = document.getElementById('carbonTrendChart');
        if (!ctx) return;

        // Datos simulados de tendencia (último año)
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        const baseValue = esgData.environmental.carbon_footprint.co2_per_ton;
        const carbonData = months.map((_, index) => {
            return baseValue + (Math.random() - 0.5) * 0.4; // Variación realista
        });

        this.charts.carbonTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'CO₂ por TM',
                    data: carbonData,
                    borderColor: this.colors.success,
                    backgroundColor: this.colors.success + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Tendencia de Huella de Carbono',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'tCO₂/TM'
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    }
                }
            }
        });
    }

    /**
     * Crear gráfico de certificaciones
     */
    createCertificationsChart(esgData) {
        const ctx = document.getElementById('certificationsChart');
        if (!ctx) return;

        const certData = esgData.governance.certifications;
        
        this.charts.certifications = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Orgánico', 'Fair Trade', 'Rainforest Alliance', 'Sin Certificar'],
                datasets: [{
                    data: [
                        certData.organic_pct,
                        certData.fair_trade_pct,
                        certData.rainforest_alliance_pct,
                        100 - Math.max(certData.organic_pct, certData.fair_trade_pct, certData.rainforest_alliance_pct)
                    ],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.primary,
                        this.colors.info,
                        this.colors.light
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    title: {
                        display: true,
                        text: 'Distribución de Certificaciones',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            }
        });
    }

    /**
     * Crear gráfico de distribución ESG
     */
    createESGDistributionChart(esgData) {
        const ctx = document.getElementById('esgDistributionChart');
        if (!ctx) return;

        // Calcular scores parciales basados en los datos
        const environmentalScore = this.calculateEnvironmentalScore(esgData);
        const socialScore = this.calculateSocialScore(esgData);
        const governanceScore = this.calculateGovernanceScore(esgData);

        this.charts.esgDistribution = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Ambiental',
                    'Social', 
                    'Gobernanza',
                    'Transparencia',
                    'Cumplimiento',
                    'Sostenibilidad'
                ],
                datasets: [{
                    label: 'Score ESG',
                    data: [
                        environmentalScore,
                        socialScore,
                        governanceScore,
                        esgData.governance.transparency.blockchain_traced_pct,
                        esgData.governance.transparency.audit_compliance,
                        esgData.overall.esg_score
                    ],
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '30',
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Distribución ESG',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
    }

    /**
     * Crear gráfico de impacto social
     */
    createSocialImpactChart(esgData) {
        const ctx = document.getElementById('socialImpactChart');
        if (!ctx) return;

        const social = esgData.social;
        
        this.charts.socialImpact = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Productores Certificados', 'Cobertura Salud', 'Escuelas Apoyadas', 'Mujeres Líderes'],
                datasets: [{
                    label: 'Impacto Social',
                    data: [
                        social.fair_trade.certified_producers,
                        social.worker_welfare.healthcare_coverage,
                        social.community_impact.schools_supported,
                        social.gender_equality.women_leadership
                    ],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.info,
                        this.colors.warning,
                        this.colors.primary
                    ],
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Indicadores de Impacto Social',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad / Porcentaje'
                        }
                    }
                }
            }
        });
    }

    /**
     * Calcular score ambiental
     */
    calculateEnvironmentalScore(esgData) {
        const env = esgData.environmental;
        return Math.round((
            env.water_usage.efficiency_score + 
            env.waste_management.waste_recycled_pct + 
            env.carbon_footprint.renewable_energy
        ) / 3);
    }

    /**
     * Calcular score social
     */
    calculateSocialScore(esgData) {
        const social = esgData.social;
        return Math.round((
            social.worker_welfare.safety_score + 
            social.worker_welfare.healthcare_coverage + 
            social.gender_equality.equal_pay_score
        ) / 3);
    }

    /**
     * Calcular score de gobernanza
     */
    calculateGovernanceScore(esgData) {
        const gov = esgData.governance;
        return Math.round((
            gov.transparency.blockchain_traced_pct + 
            gov.transparency.audit_compliance + 
            gov.supply_chain.traceability_score
        ) / 3);
    }

    /**
     * Destruir todos los gráficos
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Redimensionar todos los gráficos
     */
    resizeAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
}

// Instancia global
window.esgChartsManager = new ESGChartsManager();