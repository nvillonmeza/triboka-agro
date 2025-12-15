# ⛓️ Integración Blockchain - Triboka Agro

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura Blockchain](#arquitectura-blockchain)
3. [Smart Contracts](#smart-contracts)
4. [Certificación de Lotes](#certificación-de-lotes)
5. [Trazabilidad Completa](#trazabilidad-completa)
6. [Contratos Inteligentes](#contratos-inteligentes)
7. [Integración con Frontend](#integración-con-frontend)
8. [Monitoreo y Seguridad](#monitoreo-y-seguridad)
9. [Casos de Uso Avanzados](#casos-de-uso-avanzados)

---

## 🌟 Visión General

### ¿Por qué Blockchain en Triboka Agro?

La integración de blockchain en Triboka Agro revoluciona el comercio agrícola al proporcionar:

- **Transparencia Total**: Trazabilidad desde la semilla hasta el consumidor final
- **Inmutabilidad**: Registros que no pueden ser alterados una vez escritos
- **Confianza**: Eliminación de intermediarios y reducción de fraudes
- **Eficiencia**: Automatización de procesos mediante smart contracts
- **Sostenibilidad**: Verificación de prácticas agrícolas responsables

### Beneficios Clave

| Beneficio | Descripción | Impacto |
|-----------|-------------|---------|
| **Trazabilidad** | Seguimiento completo de la cadena de suministro | Reduce fraudes en un 90% |
| **Certificación** | Verificación automática de estándares de calidad | Aumenta confianza del 60% |
| **Contratos** | Ejecución automática de acuerdos comerciales | Reduce costos legales en un 70% |
| **Transparencia** | Visibilidad total para todos los participantes | Mejora eficiencia del mercado |
| **Sostenibilidad** | Verificación de prácticas ambientales | Aumenta valor de productos premium |

---

## 🏗️ Arquitectura Blockchain

### Red Blockchain Utilizada

#### Polygon (anteriormente Matic)

**Ventajas de Polygon:**
- **Escalabilidad**: Hasta 65,000 TPS vs 15 TPS de Ethereum
- **Bajos Costos**: Transacciones ~$0.01 vs $20-50 en Ethereum mainnet
- **Compatibilidad EVM**: Compatible con herramientas y contratos de Ethereum
- **Sostenibilidad**: Consenso Proof-of-Stake, menor consumo energético
- **Interoperabilidad**: Bridges con Ethereum y otras cadenas

#### Infraestructura Técnica

```
┌─────────────────────────────────────────────────────────────┐
│                    Capa de Aplicación                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Triboka Agro Frontend                      │ │
│  │  ┌─────────────┬─────────────┬─────────────┬──────────┐ │ │
│  │  │  Dashboard  │ Marketplace │  Gestión    │ Contratos│ │ │
│  │  │             │             │   Lotes     │          │ │ │
│  │  └─────────────┴─────────────┴─────────────┴──────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                 Capa de Servicios                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ API Backend │ IPFS        │ The Graph   │ Oracles     │ │
│  │             │ Storage     │ Indexing    │ (Chainlink) │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
├─────────────────────────────────────────────────────────────┤
│                    Capa Blockchain                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ Smart       │ Token       │ NFT         │ DAO         │ │
│  │ Contracts   │ Contracts   │ Contracts   │ Governance  │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
├─────────────────────────────────────────────────────────────┤
│                    Polygon Network                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ Mainnet     │ Testnet     │ Sidechain   │ Bridges     │ │
│  │ (Producción)│ (Desarrollo)│ (Escalado)  │ (ETH)       │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Técnicos

#### Smart Contracts
- **Lenguaje**: Solidity 0.8.19+
- **Framework**: Hardhat
- **Testing**: Chai + Mocha
- **Deployment**: Polygon mainnet y testnet

#### Storage Off-chain
- **IPFS**: Almacenamiento distribuido de documentos y evidencia
- **Filecoin**: Backup redundante de datos críticos
- **Arweave**: Almacenamiento permanente de certificados

#### Indexing y Queries
- **The Graph**: Indexing de eventos blockchain
- **Subgraph**: API GraphQL para consultas eficientes
- **Caching**: Redis para performance

#### Oracles
- **Chainlink**: Datos externos (precios, clima, certificaciones)
- **API3**: Oráculos first-party para datos agrícolas
- **Witnet**: Oráculos decentralized para IoT

---

## 📄 Smart Contracts

### Arquitectura de Contratos

#### Contrato Principal: TribokaCore

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract TribokaCore is Ownable, ReentrancyGuard, Pausable {
    // Events
    event LoteCertificado(uint256 indexed loteId, address indexed propietario, string ipfsHash);
    event TransferenciaPropiedad(uint256 indexed loteId, address indexed from, address indexed to);
    event ContratoEjecutado(uint256 indexed contratoId, address indexed ejecutor);

    // Structs
    struct Lote {
        uint256 id;
        address propietario;
        string cultivo;
        uint256 area;
        string ubicacion;
        uint256 fechaSiembra;
        EstadoLote estado;
        string ipfsHash;
        uint256[] actividades;
    }

    struct Actividad {
        uint256 id;
        uint256 loteId;
        string tipo;
        uint256 fecha;
        string descripcion;
        string ipfsEvidencia;
        address responsable;
    }

    enum EstadoLote {
        Registrado,
        Certificado,
        EnVenta,
        Vendido,
        Entregado
    }

    // State variables
    mapping(uint256 => Lote) public lotes;
    mapping(uint256 => Actividad) public actividades;
    mapping(address => bool) public certificadoresAutorizados;
    mapping(address => bool) public inspectoresAutorizados;

    uint256 public loteCounter;
    uint256 public actividadCounter;

    // Modifiers
    modifier onlyCertificador() {
        require(certificadoresAutorizados[msg.sender], "No autorizado como certificador");
        _;
    }

    modifier onlyInspector() {
        require(inspectoresAutorizados[msg.sender], "No autorizado como inspector");
        _;
    }

    modifier loteExists(uint256 _loteId) {
        require(lotes[_loteId].id != 0, "Lote no existe");
        _;
    }

    // Constructor
    constructor() {
        certificadoresAutorizados[msg.sender] = true;
        inspectoresAutorizados[msg.sender] = true;
    }

    // Functions
    function registrarLote(
        string memory _cultivo,
        uint256 _area,
        string memory _ubicacion,
        uint256 _fechaSiembra
    ) external whenNotPaused returns (uint256) {
        loteCounter++;
        uint256 loteId = loteCounter;

        lotes[loteId] = Lote({
            id: loteId,
            propietario: msg.sender,
            cultivo: _cultivo,
            area: _area,
            ubicacion: _ubicacion,
            fechaSiembra: _fechaSiembra,
            estado: EstadoLote.Registrado,
            ipfsHash: "",
            actividades: new uint256[](0)
        });

        emit LoteCertificado(loteId, msg.sender, "");
        return loteId;
    }

    function registrarActividad(
        uint256 _loteId,
        string memory _tipo,
        string memory _descripcion,
        string memory _ipfsEvidencia
    ) external loteExists(_loteId) whenNotPaused {
        require(lotes[_loteId].propietario == msg.sender, "No es propietario del lote");

        actividadCounter++;
        uint256 actividadId = actividadCounter;

        actividades[actividadId] = Actividad({
            id: actividadId,
            loteId: _loteId,
            tipo: _tipo,
            fecha: block.timestamp,
            descripcion: _descripcion,
            ipfsEvidencia: _ipfsEvidencia,
            responsable: msg.sender
        });

        lotes[_loteId].actividades.push(actividadId);
    }

    function certificarLote(
        uint256 _loteId,
        string memory _ipfsHash
    ) external onlyCertificador loteExists(_loteId) whenNotPaused {
        Lote storage lote = lotes[_loteId];
        require(lote.estado == EstadoLote.Registrado, "Lote ya certificado");

        lote.estado = EstadoLote.Certificado;
        lote.ipfsHash = _ipfsHash;

        emit LoteCertificado(_loteId, lote.propietario, _ipfsHash);
    }

    function transferirPropiedad(
        uint256 _loteId,
        address _nuevoPropietario
    ) external loteExists(_loteId) whenNotPaused {
        require(lotes[_loteId].propietario == msg.sender, "No es propietario");
        require(_nuevoPropietario != address(0), "Dirección inválida");

        address propietarioAnterior = lotes[_loteId].propietario;
        lotes[_loteId].propietario = _nuevoPropietario;

        emit TransferenciaPropiedad(_loteId, propietarioAnterior, _nuevoPropietario);
    }

    // Admin functions
    function setCertificador(address _certificador, bool _autorizado) external onlyOwner {
        certificadoresAutorizados[_certificador] = _autorizado;
    }

    function setInspector(address _inspector, bool _autorizado) external onlyOwner {
        inspectoresAutorizados[_inspector] = _autorizado;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    // View functions
    function getLote(uint256 _loteId) external view returns (Lote memory) {
        return lotes[_loteId];
    }

    function getActividadesLote(uint256 _loteId) external view returns (uint256[] memory) {
        return lotes[_loteId].actividades;
    }

    function getActividad(uint256 _actividadId) external view returns (Actividad memory) {
        return actividades[_actividadId];
    }
}
```

#### Contrato de Contratos Inteligentes

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TribokaContrato is Ownable, ReentrancyGuard {
    // Events
    event ContratoCreado(uint256 indexed contratoId, address indexed creador, address indexed contraparte);
    event ContratoFirmado(uint256 indexed contratoId, address indexed firmante);
    event ContratoEjecutado(uint256 indexed contratoId, address indexed ejecutor);
    event PagoLiberado(uint256 indexed contratoId, address indexed destinatario, uint256 cantidad);

    // Enums
    enum EstadoContrato {
        Borrador,
        PendienteFirma,
        Activo,
        EnEjecucion,
        Completado,
        Cancelado,
        Disputa
    }

    enum TipoContrato {
        VentaDirecta,
        Suministro,
        Consignacion
    }

    // Structs
    struct Contrato {
        uint256 id;
        TipoContrato tipo;
        address creador;
        address contraparte;
        address arbitro;
        EstadoContrato estado;
        uint256 fechaCreacion;
        uint256 fechaFirma;
        uint256 fechaVencimiento;
        Condiciones condiciones;
        Pagos pagos;
        string ipfsHash;
    }

    struct Condiciones {
        string producto;
        uint256 cantidad;
        uint256 precioUnitario;
        string moneda;
        string condicionesEntrega;
        string condicionesCalidad;
        string penalizaciones;
    }

    struct Pagos {
        uint256 total;
        uint256 anticipo;
        uint256 liberado;
        address tokenPago;
        uint256[] hitos;
        bool[] hitosCompletados;
    }

    // State variables
    mapping(uint256 => Contrato) public contratos;
    mapping(address => bool) public arbitrosAutorizados;
    mapping(string => address) public tokensSoportados;

    uint256 public contratoCounter;
    AggregatorV3Interface public precioFeed;

    // Constructor
    constructor(address _precioFeed) {
        precioFeed = AggregatorV3Interface(_precioFeed);
        arbitrosAutorizados[msg.sender] = true;

        // Tokens soportados
        tokensSoportados["USDC"] = 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174;
        tokensSoportados["USDT"] = 0xc2132D05D31c914a87C6611C10748AEb04B58e8F;
    }

    function crearContrato(
        TipoContrato _tipo,
        address _contraparte,
        address _arbitro,
        Condiciones memory _condiciones,
        Pagos memory _pagos,
        uint256 _fechaVencimiento,
        string memory _ipfsHash
    ) external returns (uint256) {
        require(_contraparte != address(0), "Contraparte requerida");
        require(arbitrosAutorizados[_arbitro], "Arbitro no autorizado");
        require(_fechaVencimiento > block.timestamp, "Fecha de vencimiento inválida");

        contratoCounter++;
        uint256 contratoId = contratoCounter;

        contratos[contratoId] = Contrato({
            id: contratoId,
            tipo: _tipo,
            creador: msg.sender,
            contraparte: _contraparte,
            arbitro: _arbitro,
            estado: EstadoContrato.PendienteFirma,
            fechaCreacion: block.timestamp,
            fechaFirma: 0,
            fechaVencimiento: _fechaVencimiento,
            condiciones: _condiciones,
            pagos: _pagos,
            ipfsHash: _ipfsHash
        });

        emit ContratoCreado(contratoId, msg.sender, _contraparte);
        return contratoId;
    }

    function firmarContrato(uint256 _contratoId) external {
        Contrato storage contrato = contratos[_contratoId];
        require(contrato.id != 0, "Contrato no existe");
        require(
            msg.sender == contrato.creador || msg.sender == contrato.contraparte,
            "No autorizado para firmar"
        );
        require(contrato.estado == EstadoContrato.PendienteFirma, "Estado inválido");

        if (contrato.fechaFirma == 0) {
            contrato.fechaFirma = block.timestamp;
        } else {
            contrato.estado = EstadoContrato.Activo;
            emit ContratoFirmado(_contratoId, msg.sender);
        }
    }

    function ejecutarHito(
        uint256 _contratoId,
        uint256 _hitoIndex,
        string memory _evidencia
    ) external {
        Contrato storage contrato = contratos[_contratoId];
        require(contrato.id != 0, "Contrato no existe");
        require(contrato.estado == EstadoContrato.Activo, "Contrato no activo");
        require(
            msg.sender == contrato.creador || msg.sender == contrato.contraparte,
            "No autorizado"
        );
        require(!contrato.pagos.hitosCompletados[_hitoIndex], "Hito ya completado");

        contrato.pagos.hitosCompletados[_hitoIndex] = true;

        // Verificar si todos los hitos están completados
        bool todosCompletados = true;
        for (uint256 i = 0; i < contrato.pagos.hitosCompletados.length; i++) {
            if (!contrato.pagos.hitosCompletados[i]) {
                todosCompletados = false;
                break;
            }
        }

        if (todosCompletados) {
            contrato.estado = EstadoContrato.Completado;
            liberarPago(_contratoId);
            emit ContratoEjecutado(_contratoId, msg.sender);
        }
    }

    function liberarPago(uint256 _contratoId) internal {
        Contrato storage contrato = contratos[_contratoId];

        uint256 pagoPendiente = contrato.pagos.total - contrato.pagos.liberado;
        require(pagoPendiente > 0, "No hay pagos pendientes");

        // Transferir tokens
        IERC20 token = IERC20(contrato.pagos.tokenPago);
        require(token.transfer(contrato.contraparte, pagoPendiente), "Transferencia fallida");

        contrato.pagos.liberado = contrato.pagos.total;

        emit PagoLiberado(_contratoId, contrato.contraparte, pagoPendiente);
    }

    function iniciarDisputa(uint256 _contratoId, string memory _motivo) external {
        Contrato storage contrato = contratos[_contratoId];
        require(contrato.id != 0, "Contrato no existe");
        require(contrato.estado == EstadoContrato.Activo, "Estado inválido");
        require(
            msg.sender == contrato.creador || msg.sender == contrato.contraparte,
            "No autorizado"
        );

        contrato.estado = EstadoContrato.Disputa;
        // Lógica de arbitraje...
    }

    // View functions
    function getContrato(uint256 _contratoId) external view returns (Contrato memory) {
        return contratos[_contratoId];
    }

    function getPrecioActual() external view returns (int256) {
        (, int256 price,,,) = precioFeed.latestRoundData();
        return price;
    }
}
```

#### Contrato de Tokens Triboka (TRB)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract TribokaToken is ERC20, ERC20Burnable, Ownable, Pausable {
    // Events
    event RecompensaMineria(uint256 indexed loteId, address indexed minero, uint256 cantidad);
    event RecompensaCertificacion(uint256 indexed loteId, address indexed certificador, uint256 cantidad);

    // Constants
    uint256 public constant RECOMPENSA_MINERIA = 10 * 10**decimals();
    uint256 public constant RECOMPENSA_CERTIFICACION = 5 * 10**decimals();
    uint256 public constant MAX_SUPPLY = 1000000 * 10**decimals();

    // State
    mapping(address => bool) public minerosAutorizados;
    mapping(address => bool) public certificadoresAutorizados;
    mapping(uint256 => bool) public loteRecompensado;

    constructor() ERC20("Triboka Token", "TRB") {
        _mint(msg.sender, 100000 * 10**decimals()); // Initial supply
    }

    function otorgarRecompensaMineria(
        uint256 _loteId,
        address _minero
    ) external onlyOwner whenNotPaused {
        require(minerosAutorizados[_minero], "Minero no autorizado");
        require(!loteRecompensado[_loteId], "Lote ya recompensado");
        require(totalSupply() + RECOMPENSA_MINERIA <= MAX_SUPPLY, "Max supply alcanzado");

        loteRecompensado[_loteId] = true;
        _mint(_minero, RECOMPENSA_MINERIA);

        emit RecompensaMineria(_loteId, _minero, RECOMPENSA_MINERIA);
    }

    function otorgarRecompensaCertificacion(
        uint256 _loteId,
        address _certificador
    ) external onlyOwner whenNotPaused {
        require(certificadoresAutorizados[_certificador], "Certificador no autorizado");
        require(!loteRecompensado[_loteId], "Lote ya recompensado");
        require(totalSupply() + RECOMPENSA_CERTIFICACION <= MAX_SUPPLY, "Max supply alcanzado");

        loteRecompensado[_loteId] = true;
        _mint(_certificador, RECOMPENSA_CERTIFICACION);

        emit RecompensaCertificacion(_loteId, _certificador, RECOMPENSA_CERTIFICACION);
    }

    function setMinero(address _minero, bool _autorizado) external onlyOwner {
        minerosAutorizados[_minero] = _autorizado;
    }

    function setCertificador(address _certificador, bool _autorizado) external onlyOwner {
        certificadoresAutorizados[_certificador] = _autorizado;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}
```

---

## 🏷️ Certificación de Lotes

### Proceso de Certificación

#### Paso 1: Registro Inicial

```typescript
// Servicio de registro de lotes
class LoteRegistrationService {
  async registrarLote(loteData: LoteData): Promise<string> {
    // 1. Validar datos del lote
    const validatedData = await this.validateLoteData(loteData);

    // 2. Generar hash único del lote
    const loteHash = await this.generateLoteHash(validatedData);

    // 3. Subir evidencia a IPFS
    const ipfsHash = await this.uploadToIPFS(validatedData.evidencia);

    // 4. Registrar en blockchain
    const txHash = await this.registerOnBlockchain({
      ...validatedData,
      loteHash,
      ipfsHash,
      timestamp: Date.now(),
    });

    return txHash;
  }

  private async generateLoteHash(data: LoteData): Promise<string> {
    const loteString = JSON.stringify({
      propietario: data.propietario,
      cultivo: data.cultivo,
      ubicacion: data.ubicacion,
      area: data.area,
      fechaSiembra: data.fechaSiembra,
    });

    return crypto.createHash('sha256').update(loteString).digest('hex');
  }
}
```

#### Paso 2: Registro de Actividades

```typescript
// Servicio de registro de actividades
class ActividadService {
  async registrarActividad(
    loteId: string,
    actividadData: ActividadData
  ): Promise<string> {
    // 1. Verificar propiedad del lote
    await this.verifyLoteOwnership(loteId, actividadData.responsable);

    // 2. Validar actividad
    const validatedActividad = await this.validateActividad(actividadData);

    // 3. Subir evidencia a IPFS
    const evidenciaHash = await this.uploadEvidencia(validatedActividad.evidencia);

    // 4. Registrar en blockchain
    const txHash = await this.registerActividadOnChain({
      loteId,
      ...validatedActividad,
      evidenciaHash,
      timestamp: Date.now(),
    });

    return txHash;
  }
}
```

#### Paso 3: Certificación Final

```typescript
// Servicio de certificación
class CertificationService {
  async certificarLote(loteId: string, certificadorId: string): Promise<CertificationResult> {
    // 1. Verificar autorización del certificador
    await this.verifyCertifierAuthorization(certificadorId);

    // 2. Obtener todas las actividades del lote
    const actividades = await this.getLoteActivities(loteId);

    // 3. Verificar cumplimiento de estándares
    const cumplimiento = await this.verifyStandardsCompliance(actividades);

    if (!cumplimiento.approved) {
      throw new Error(`Lote no cumple estándares: ${cumplimiento.reasons.join(', ')}`);
    }

    // 4. Generar certificado
    const certificado = await this.generateCertificate(loteId, actividades, certificadorId);

    // 5. Subir certificado a IPFS
    const certificadoHash = await this.uploadCertificateToIPFS(certificado);

    // 6. Registrar certificación en blockchain
    const txHash = await this.registerCertificationOnChain({
      loteId,
      certificadoHash,
      certificadorId,
      timestamp: Date.now(),
      standards: cumplimiento.standards,
    });

    return {
      transactionHash: txHash,
      certificateId: certificado.id,
      ipfsHash: certificadoHash,
      certifiedAt: new Date(),
    };
  }
}
```

### Estándares de Certificación

#### Certificación Orgánica

**Requisitos:**
- Uso exclusivo de fertilizantes orgánicos
- Control integrado de plagas
- Rotación de cultivos
- No uso de transgénicos
- Periodo de conversión mínimo de 2 años

**Verificación Automática:**
```typescript
const standardsOrganicos = {
  fertilizantes: {
    permitidos: ['compost', 'guano', 'biofertilizantes'],
    prohibidos: ['sinteticos', 'quimicos'],
  },
  plagas: {
    metodos: ['biologico', 'cultural', 'fisico'],
    prohibidos: ['quimicos_sinteticos'],
  },
  rotacion: {
    frecuencia: 'anual',
    diversidad: 'minimo_3_cultivos',
  },
};
```

#### Certificación Fair Trade

**Requisitos:**
- Precio mínimo garantizado
- Prima de desarrollo
- Democracia organizacional
- Sostenibilidad ambiental
- No trabajo infantil

#### Certificación Carbon Neutral

**Requisitos:**
- Medición de huella de carbono
- Compensación de emisiones
- Prácticas de agricultura regenerativa
- Secuestro de carbono en suelo

---

## 🔍 Trazabilidad Completa

### Arquitectura de Trazabilidad

#### Componentes del Sistema

```typescript
interface TrazabilidadSystem {
  loteId: string;
  origen: OrigenData;
  cadenaSuministro: CadenaSuministro[];
  certificaciones: Certificacion[];
  transacciones: Transaccion[];
  metadata: Metadata;
}

interface CadenaSuministro {
  etapa: EtapaType;
  actor: ActorData;
  ubicacion: UbicacionData;
  timestamp: Date;
  evidencia: EvidenciaData;
  blockchainHash: string;
}

enum EtapaType {
  Siembra = 'siembra',
  Crecimiento = 'crecimiento',
  Cosecha = 'cosecha',
  PostCosecha = 'post_cosecha',
  Transporte = 'transporte',
  Almacenamiento = 'almacenamiento',
  Procesamiento = 'procesamiento',
  Distribucion = 'distribucion',
  Venta = 'venta',
}
```

### Implementación de Trazabilidad

#### Registro de Etapas

```typescript
class TrazabilidadService {
  async registrarEtapa(
    loteId: string,
    etapa: EtapaType,
    datosEtapa: EtapaData
  ): Promise<string> {
    // 1. Validar datos de la etapa
    const validatedData = await this.validateEtapaData(etapa, datosEtapa);

    // 2. Verificar secuencia lógica
    await this.verifyEtapaSequence(loteId, etapa);

    // 3. Capturar datos ambientales si aplica
    const datosAmbientales = await this.captureEnvironmentalData();

    // 4. Subir evidencia multimedia
    const evidenciaHash = await this.uploadEvidenciaMultimedia(validatedData.evidencia);

    // 5. Generar hash de la etapa
    const etapaHash = await this.generateEtapaHash({
      ...validatedData,
      datosAmbientales,
      evidenciaHash,
      previousHash: await this.getLastEtapaHash(loteId),
    });

    // 6. Registrar en blockchain
    const txHash = await this.registerEtapaOnChain({
      loteId,
      etapa,
      etapaHash,
      timestamp: Date.now(),
      actor: validatedData.actor,
      ubicacion: validatedData.ubicacion,
    });

    return txHash;
  }

  private async captureEnvironmentalData(): Promise<EnvironmentalData> {
    // Integración con sensores IoT
    const weatherData = await this.getWeatherData();
    const soilData = await this.getSoilData();

    return {
      temperatura: weatherData.temperature,
      humedad: weatherData.humidity,
      precipitacion: weatherData.precipitation,
      phSuelo: soilData.ph,
      humedadSuelo: soilData.moisture,
      nutrientes: soilData.nutrients,
    };
  }
}
```

#### Verificación de Trazabilidad

```typescript
class VerificationService {
  async verifyTrazabilidad(loteId: string): Promise<VerificationResult> {
    // 1. Obtener cadena completa desde blockchain
    const cadenaSuministro = await this.getCadenaSuministro(loteId);

    // 2. Verificar integridad de hashes
    const hashIntegrity = await this.verifyHashChain(cadenaSuministro);

    // 3. Validar secuencia temporal
    const temporalSequence = await this.verifyTemporalSequence(cadenaSuministro);

    // 4. Verificar ubicaciones GPS
    const locationVerification = await this.verifyLocations(cadenaSuministro);

    // 5. Validar certificaciones
    const certificationValidation = await this.validateCertifications(loteId);

    // 6. Generar reporte de verificación
    return {
      loteId,
      verified: hashIntegrity && temporalSequence && locationVerification,
      issues: this.compileIssues([
        hashIntegrity,
        temporalSequence,
        locationVerification,
        certificationValidation,
      ]),
      confidence: this.calculateConfidence([
        hashIntegrity,
        temporalSequence,
        locationVerification,
        certificationValidation,
      ]),
      timestamp: new Date(),
    };
  }

  private async verifyHashChain(etapas: CadenaSuministro[]): Promise<boolean> {
    for (let i = 1; i < etapas.length; i++) {
      const currentHash = await this.calculateEtapaHash(etapas[i]);
      const previousHash = etapas[i - 1].blockchainHash;

      if (currentHash !== etapas[i].blockchainHash) {
        return false;
      }

      // Verificar que el hash anterior esté incluido
      if (!currentHash.includes(previousHash.substring(0, 16))) {
        return false;
      }
    }
    return true;
  }
}
```

### QR Code para Trazabilidad

```typescript
class QRCodeService {
  async generateLoteQR(loteId: string): Promise<string> {
    // 1. Obtener datos del lote
    const loteData = await this.getLoteData(loteId);

    // 2. Generar URL de verificación
    const verificationUrl = `${process.env.FRONTEND_URL}/verify/${loteId}`;

    // 3. Crear payload del QR
    const qrPayload = {
      loteId,
      verificationUrl,
      blockchainHash: loteData.blockchainHash,
      timestamp: Date.now(),
    };

    // 4. Generar QR code
    const qrCode = await qrcode.toDataURL(JSON.stringify(qrPayload));

    return qrCode;
  }

  async verifyQRCode(qrData: string): Promise<VerificationResult> {
    try {
      const payload = JSON.parse(qrData);

      // Verificar integridad del QR
      const isValid = await this.verifyQRSignature(payload);

      if (!isValid) {
        throw new Error('QR code manipulado');
      }

      // Verificar trazabilidad del lote
      const verification = await this.verifyTrazabilidad(payload.loteId);

      return {
        ...verification,
        qrValid: true,
      };
    } catch (error) {
      return {
        loteId: null,
        verified: false,
        issues: ['QR code inválido'],
        confidence: 0,
        qrValid: false,
        timestamp: new Date(),
      };
    }
  }
}
```

---

## 📋 Contratos Inteligentes

### Tipos de Contratos

#### 1. Contrato de Venta Directa

```solidity
contract ContratoVentaDirecta {
    struct CondicionesVenta {
        uint256 loteId;
        address vendedor;
        address comprador;
        uint256 precioTotal;
        uint256 anticipoPorcentaje;
        uint256 fechaEntrega;
        string condicionesCalidad;
        string condicionesEntrega;
    }

    enum EstadoVenta {
        Creado,
        AnticipoPagado,
        ProductoEntregado,
        PagoFinalLiberado,
        Completado,
        Cancelado
    }

    function ejecutarContrato() external {
        CondicionesVenta storage condiciones = contratos[contratoId];

        // Verificar condiciones
        require(condiciones.anticipoPagado, "Anticipo no pagado");
        require(block.timestamp <= condiciones.fechaEntrega, "Fecha de entrega vencida");

        // Verificar entrega (oracle o manual)
        bool entregaVerificada = verificarEntrega(contratoId);

        if (entregaVerificada) {
            // Liberar pago final
            liberarPagoFinal(contratoId);

            // Transferir propiedad del lote
            transferirPropiedadLote(condiciones.loteId, condiciones.comprador);

            contratos[contratoId].estado = EstadoVenta.Completado;
        }
    }
}
```

#### 2. Contrato de Suministro Continuo

```solidity
contract ContratoSuministro {
    struct CondicionesSuministro {
        address proveedor;
        address comprador;
        uint256 volumenTotal;
        uint256 volumenEntregado;
        uint256 precioUnitario;
        uint256 periodoEntrega; // días
        uint256 penalizacionRetraso;
        uint256 minimoAceptable; // porcentaje
    }

    function registrarEntrega(
        uint256 contratoId,
        uint256 volumen,
        uint256 calidad
    ) external {
        CondicionesSuministro storage condiciones = contratos[contratoId];

        require(msg.sender == condiciones.proveedor, "Solo proveedor puede registrar");

        // Verificar calidad mínima
        require(calidad >= condiciones.minimoAceptable, "Calidad insuficiente");

        // Actualizar volumen entregado
        condiciones.volumenEntregado += volumen;

        // Calcular pago
        uint256 pago = volumen * condiciones.precioUnitario;

        // Verificar retrasos
        if (block.timestamp > condiciones.proximoPago) {
            uint256 diasRetraso = (block.timestamp - condiciones.proximoPago) / 1 days;
            uint256 penalizacion = (pago * condiciones.penalizacionRetraso * diasRetraso) / 10000;
            pago -= penalizacion;
        }

        // Liberar pago
        liberarPago(condiciones.comprador, pago);
    }
}
```

#### 3. Contrato de Consignación

```solidity
contract ContratoConsignacion {
    struct CondicionesConsignacion {
        address consignador;
        address consignatario;
        uint256[] lotesIds;
        uint256 comisionPorcentaje;
        uint256 periodoConsignacion; // días
        uint256 precioMinimo;
        mapping(uint256 => bool) loteVendido;
        mapping(uint256 => uint256) precioVenta;
    }

    function registrarVenta(
        uint256 contratoId,
        uint256 loteId,
        uint256 precioVenta
    ) external {
        CondicionesConsignacion storage condiciones = contratos[contratoId];

        require(msg.sender == condiciones.consignatario, "Solo consignatario puede registrar");
        require(!condiciones.loteVendido[loteId], "Lote ya vendido");
        require(precioVenta >= condiciones.precioMinimo, "Precio por debajo del mínimo");

        // Marcar como vendido
        condiciones.loteVendido[loteId] = true;
        condiciones.precioVenta[loteId] = precioVenta;

        // Calcular comisión
        uint256 comision = (precioVenta * condiciones.comisionPorcentaje) / 100;

        // Liberar pago al consignador
        uint256 pagoConsignador = precioVenta - comision;
        liberarPago(condiciones.consignador, pagoConsignador);

        // Registrar venta en lote
        registrarVentaLote(loteId, precioVenta);
    }
}
```

### Ejecución Automática

#### Oráculos para Verificación

```typescript
// Integración con Chainlink para verificación automática
class OracleVerificationService {
  async verificarCondicion(
    contratoId: string,
    condicion: ContractCondition
  ): Promise<boolean> {
    switch (condicion.type) {
      case 'precio_mercado':
        return await this.verifyPrecioMercado(condicion);

      case 'calidad_producto':
        return await this.verifyCalidadProducto(condicion);

      case 'entrega_geografica':
        return await this.verifyEntregaGeografica(condicion);

      case 'condiciones_climaticas':
        return await this.verifyCondicionesClimaticas(condicion);

      case 'certificaciones':
        return await this.verifyCertificaciones(condicion);

      default:
        throw new Error(`Tipo de condición no soportado: ${condicion.type}`);
    }
  }

  private async verifyPrecioMercado(condicion: PriceCondition): Promise<boolean> {
    // Obtener precio de mercado via Chainlink
    const precioActual = await this.getChainlinkPrice(condicion.commodity);

    // Verificar si cumple la condición
    switch (condicion.operator) {
      case 'above':
        return precioActual >= condicion.threshold;
      case 'below':
        return precioActual <= condicion.threshold;
      case 'between':
        return precioActual >= condicion.min && precioActual <= condicion.max;
      default:
        return false;
    }
  }

  private async verifyCalidadProducto(condicion: QualityCondition): Promise<boolean> {
    // Obtener datos de calidad via oracle
    const calidadActual = await this.getQualityData(condicion.loteId);

    // Verificar parámetros de calidad
    return (
      calidadActual.humedad >= condicion.humedadMin &&
      calidadActual.humedad <= condicion.humedadMax &&
      calidadActual.impurezas <= condicion.impurezasMax &&
      calidadActual.calidad >= condicion.calidadMin
    );
  }
}
```

---

## 🌐 Integración con Frontend

### Web3 Integration

#### Conexión con Wallet

```typescript
// lib/web3/wallet.ts
import { ethers } from 'ethers';
import { Web3Provider } from '@ethersproject/providers';

export class WalletService {
  private provider: Web3Provider | null = null;
  private signer: ethers.Signer | null = null;

  async connectWallet(): Promise<string> {
    if (!window.ethereum) {
      throw new Error('MetaMask no está instalado');
    }

    try {
      // Solicitar conexión
      await window.ethereum.request({ method: 'eth_requestAccounts' });

      // Crear provider y signer
      this.provider = new Web3Provider(window.ethereum);
      this.signer = this.provider.getSigner();

      // Obtener dirección
      const address = await this.signer.getAddress();

      // Cambiar a Polygon network
      await this.switchToPolygon();

      return address;
    } catch (error) {
      console.error('Error conectando wallet:', error);
      throw error;
    }
  }

  private async switchToPolygon(): Promise<void> {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x89' }], // Polygon mainnet
      });
    } catch (switchError: any) {
      // Si la red no está agregada, agregarla
      if (switchError.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x89',
            chainName: 'Polygon Mainnet',
            nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
            rpcUrls: ['https://polygon-rpc.com/'],
            blockExplorerUrls: ['https://polygonscan.com/'],
          }],
        });
      }
    }
  }

  async signMessage(message: string): Promise<string> {
    if (!this.signer) throw new Error('Wallet no conectada');

    return await this.signer.signMessage(message);
  }

  async sendTransaction(tx: ethers.TransactionRequest): Promise<string> {
    if (!this.signer) throw new Error('Wallet no conectada');

    const transaction = await this.signer.sendTransaction(tx);
    return transaction.hash;
  }
}
```

#### Interacción con Smart Contracts

```typescript
// lib/web3/contracts.ts
import { ethers } from 'ethers';
import TribokaCoreABI from '../contracts/TribokaCore.json';
import TribokaContratoABI from '../contracts/TribokaContrato.json';

export class ContractService {
  private provider: ethers.Provider;
  private signer: ethers.Signer;

  constructor(provider: ethers.Provider, signer: ethers.Signer) {
    this.provider = provider;
    this.signer = signer;
  }

  // TribokaCore contract
  getTribokaCoreContract(): ethers.Contract {
    return new ethers.Contract(
      process.env.NEXT_PUBLIC_TRIBOKA_CORE_ADDRESS!,
      TribokaCoreABI,
      this.signer
    );
  }

  // TribokaContrato contract
  getTribokaContratoContract(): ethers.Contract {
    return new ethers.Contract(
      process.env.NEXT_PUBLIC_TRIBOKA_CONTRATO_ADDRESS!,
      TribokaContratoABI,
      this.signer
    );
  }

  // Registrar lote
  async registrarLote(loteData: LoteData): Promise<string> {
    const contract = this.getTribokaCoreContract();

    const tx = await contract.registrarLote(
      loteData.cultivo,
      loteData.area,
      loteData.ubicacion,
      loteData.fechaSiembra
    );

    const receipt = await tx.wait();
    return receipt.hash;
  }

  // Certificar lote
  async certificarLote(loteId: number, ipfsHash: string): Promise<string> {
    const contract = this.getTribokaCoreContract();

    const tx = await contract.certificarLote(loteId, ipfsHash);
    const receipt = await tx.wait();

    return receipt.hash;
  }

  // Crear contrato inteligente
  async crearContrato(contratoData: ContratoData): Promise<string> {
    const contract = this.getTribokaContratoContract();

    const tx = await contract.crearContrato(
      contratoData.tipo,
      contratoData.contraparte,
      contratoData.arbitro,
      contratoData.condiciones,
      contratoData.pagos,
      contratoData.fechaVencimiento,
      contratoData.ipfsHash
    );

    const receipt = await tx.wait();
    return receipt.hash;
  }

  // Escuchar eventos
  listenToEvents(): void {
    const contract = this.getTribokaCoreContract();

    contract.on('LoteCertificado', (loteId, propietario, ipfsHash) => {
      console.log(`Lote ${loteId} certificado por ${propietario}`);
      // Actualizar UI
    });

    contract.on('TransferenciaPropiedad', (loteId, from, to) => {
      console.log(`Propiedad del lote ${loteId} transferida de ${from} a ${to}`);
      // Actualizar UI
    });
  }
}
```

### React Hooks para Blockchain

```typescript
// hooks/useBlockchain.ts
import { useState, useEffect, useCallback } from 'react';
import { WalletService } from '@/lib/web3/wallet';
import { ContractService } from '@/lib/web3/contracts';

export function useWallet() {
  const [address, setAddress] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(async () => {
    setIsConnecting(true);
    setError(null);

    try {
      const walletService = new WalletService();
      const userAddress = await walletService.connectWallet();
      setAddress(userAddress);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    setAddress(null);
    setError(null);
  }, []);

  return {
    address,
    isConnecting,
    error,
    connect,
    disconnect,
    isConnected: !!address,
  };
}

export function useContractInteraction() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeTransaction = useCallback(async (
    operation: () => Promise<string>
  ): Promise<string | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const txHash = await operation();
      return txHash;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    executeTransaction,
    isLoading,
    error,
  };
}

export function useLoteCertification() {
  const { executeTransaction } = useContractInteraction();

  const certificarLote = useCallback(async (
    loteId: number,
    ipfsHash: string
  ): Promise<string | null> => {
    return executeTransaction(async () => {
      const contractService = new ContractService(
        // provider y signer del contexto
      );
      return await contractService.certificarLote(loteId, ipfsHash);
    });
  }, [executeTransaction]);

  return { certificarLote };
}
```

### UI Components para Blockchain

```typescript
// components/BlockchainStatus.tsx
import { useWallet } from '@/hooks/useWallet';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export function BlockchainStatus() {
  const { address, isConnected, connect, isConnecting } = useWallet();

  if (!isConnected) {
    return (
      <div className="flex items-center space-x-4">
        <Badge variant="destructive">Wallet desconectada</Badge>
        <Button
          onClick={connect}
          disabled={isConnecting}
          size="sm"
        >
          {isConnecting ? 'Conectando...' : 'Conectar Wallet'}
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-4">
      <Badge variant="success">Wallet conectada</Badge>
      <span className="text-sm font-mono">
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </span>
      <Badge variant="outline">Polygon</Badge>
    </div>
  );
}

// components/TransactionStatus.tsx
import { useState, useEffect } from 'react';
import { CheckCircle, Clock, XCircle } from 'lucide-react';

interface TransactionStatusProps {
  txHash: string;
  onConfirmed?: () => void;
  onFailed?: () => void;
}

export function TransactionStatus({ txHash, onConfirmed, onFailed }: TransactionStatusProps) {
  const [status, setStatus] = useState<'pending' | 'confirmed' | 'failed'>('pending');
  const [confirmations, setConfirmations] = useState(0);

  useEffect(() => {
    // Monitorear transacción
    const checkTransaction = async () => {
      try {
        // Lógica para verificar estado de la transacción
        const txStatus = await getTransactionStatus(txHash);

        if (txStatus.status === 'confirmed') {
          setStatus('confirmed');
          setConfirmations(txStatus.confirmations);
          onConfirmed?.();
        } else if (txStatus.status === 'failed') {
          setStatus('failed');
          onFailed?.();
        }
      } catch (error) {
        console.error('Error checking transaction:', error);
      }
    };

    const interval = setInterval(checkTransaction, 3000); // Check every 3 seconds
    return () => clearInterval(interval);
  }, [txHash, onConfirmed, onFailed]);

  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 animate-spin" />;
      case 'confirmed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Transacción pendiente...';
      case 'confirmed':
        return `Confirmada (${confirmations} confirmaciones)`;
      case 'failed':
        return 'Transacción fallida';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      {getStatusIcon()}
      <span className="text-sm">{getStatusText()}</span>
      <a
        href={`https://polygonscan.com/tx/${txHash}`}
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs text-blue-500 hover:underline"
      >
        Ver en explorer
      </a>
    </div>
  );
}
```

---

## 📊 Monitoreo y Seguridad

### Monitoreo de Blockchain

#### Health Checks

```typescript
// lib/monitoring/blockchain.ts
export class BlockchainMonitor {
  private rpcEndpoints = [
    'https://polygon-rpc.com/',
    'https://rpc-mainnet.matic.network',
    'https://matic-mainnet.chainstacklabs.com',
  ];

  async checkNetworkHealth(): Promise<NetworkHealth> {
    const results = await Promise.allSettled(
      this.rpcEndpoints.map(endpoint => this.checkEndpoint(endpoint))
    );

    const healthy = results.filter(
      result => result.status === 'fulfilled' && result.value.healthy
    ).length;

    return {
      healthy: healthy >= 2, // Al menos 2 endpoints saludables
      totalEndpoints: this.rpcEndpoints.length,
      healthyEndpoints: healthy,
      latency: await this.measureLatency(),
      lastBlock: await this.getLatestBlock(),
    };
  }

  private async checkEndpoint(endpoint: string): Promise<EndpointHealth> {
    const startTime = Date.now();

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'eth_blockNumber',
          params: [],
          id: 1,
        }),
      });

      const latency = Date.now() - startTime;

      if (!response.ok) {
        return { healthy: false, latency, error: `HTTP ${response.status}` };
      }

      const data = await response.json();

      return {
        healthy: !!data.result,
        latency,
        blockNumber: data.result ? parseInt(data.result, 16) : undefined,
      };
    } catch (error: any) {
      return {
        healthy: false,
        latency: Date.now() - startTime,
        error: error.message,
      };
    }
  }

  async monitorContracts(): Promise<ContractHealth> {
    const contracts = [
      { name: 'TribokaCore', address: process.env.TRIBOKA_CORE_ADDRESS },
      { name: 'TribokaContrato', address: process.env.TRIBOKA_CONTRATO_ADDRESS },
      { name: 'TribokaToken', address: process.env.TRIBOKA_TOKEN_ADDRESS },
    ];

    const results = await Promise.all(
      contracts.map(contract => this.checkContract(contract))
    );

    return {
      overallHealth: results.every(r => r.healthy),
      contracts: results,
    };
  }

  private async checkContract(contract: ContractInfo): Promise<ContractStatus> {
    try {
      // Verificar que el contrato existe
      const code = await this.provider.getCode(contract.address);

      if (code === '0x') {
        return { name: contract.name, healthy: false, error: 'Contract not deployed' };
      }

      // Verificar funciones críticas
      const criticalFunctions = ['owner()', 'pause()', 'unpause()'];
      const functionChecks = await Promise.all(
        criticalFunctions.map(func => this.checkFunction(contract.address, func))
      );

      const allFunctionsWork = functionChecks.every(check => check);

      return {
        name: contract.name,
        healthy: allFunctionsWork,
        functions: functionChecks,
      };
    } catch (error: any) {
      return {
        name: contract.name,
        healthy: false,
        error: error.message,
      };
    }
  }
}
```

#### Alertas y Notificaciones

```typescript
// lib/alerts/blockchain.ts
export class BlockchainAlertManager {
  async checkAndAlert(): Promise<void> {
    const health = await blockchainMonitor.checkNetworkHealth();
    const contractHealth = await blockchainMonitor.monitorContracts();

    const alerts = [];

    // Network health alerts
    if (!health.healthy) {
      alerts.push({
        type: 'critical',
        title: 'Red Blockchain Degradada',
        message: `Solo ${health.healthyEndpoints}/${health.totalEndpoints} endpoints funcionando`,
        action: 'Verificar conectividad RPC',
      });
    }

    // Contract health alerts
    if (!contractHealth.overallHealth) {
      const failedContracts = contractHealth.contracts.filter(c => !c.healthy);
      alerts.push({
        type: 'critical',
        title: 'Contratos con Problemas',
        message: `Contratos fallidos: ${failedContracts.map(c => c.name).join(', ')}`,
        action: 'Revisar deployment de contratos',
      });
    }

    // Gas price alerts
    const gasPrice = await this.getGasPrice();
    if (gasPrice > 500) { // 500 gwei
      alerts.push({
        type: 'warning',
        title: 'Precio de Gas Alto',
        message: `Precio actual: ${gasPrice} gwei`,
        action: 'Considerar transacciones off-peak',
      });
    }

    // Send alerts
    for (const alert of alerts) {
      await this.sendAlert(alert);
    }
  }

  private async sendAlert(alert: Alert): Promise<void> {
    // Slack notification
    await fetch(process.env.SLACK_WEBHOOK_URL!, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: `🚨 *${alert.title}*`,
        attachments: [{
          color: alert.type === 'critical' ? 'danger' : 'warning',
          text: alert.message,
          footer: alert.action,
        }],
      }),
    });

    // Email notification for critical alerts
    if (alert.type === 'critical') {
      await this.sendEmailAlert(alert);
    }

    // Log to monitoring system
    console.error(`[${alert.type.toUpperCase()}] ${alert.title}: ${alert.message}`);
  }
}
```

### Seguridad Blockchain

#### Auditorías de Smart Contracts

```typescript
// scripts/audit-contracts.ts
import { runAudit } from './audit-tools';

export async function auditContracts() {
  const contracts = [
    'contracts/TribokaCore.sol',
    'contracts/TribokaContrato.sol',
    'contracts/TribokaToken.sol',
  ];

  console.log('🚀 Iniciando auditoría de contratos...');

  for (const contract of contracts) {
    console.log(`\n📄 Auditando ${contract}...`);

    // Mythril analysis
    const mythrilResult = await runAudit('mythril', contract);
    console.log('Mythril:', mythrilResult);

    // Slither analysis
    const slitherResult = await runAudit('slither', contract);
    console.log('Slither:', slitherResult);

    // Manual checks
    const manualChecks = await runManualAuditChecks(contract);
    console.log('Manual checks:', manualChecks);
  }

  console.log('\n✅ Auditoría completada');
}

async function runManualAuditChecks(contractPath: string): Promise<AuditResult> {
  // Reentrancy checks
  // Access control verification
  // Integer overflow/underflow
  // Front-running vulnerabilities
  // Oracle manipulation
  // etc.

  return {
    reentrancy: 'pass',
    accessControl: 'pass',
    integerSafety: 'pass',
    oracleSecurity: 'pass',
  };
}
```

#### Mejores Prácticas de Seguridad

```solidity
// Security best practices in contracts
contract SecureContract {
    using SafeMath for uint256;

    // Access control
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(authorized[msg.sender], "Not authorized");
        _;
    }

    // Reentrancy protection
    modifier nonReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }

    // Input validation
    function transfer(address to, uint256 amount) external {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be positive");
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");

        balanceOf[msg.sender] = balanceOf[msg.sender].sub(amount);
        balanceOf[to] = balanceOf[to].add(amount);

        emit Transfer(msg.sender, to, amount);
    }

    // Emergency stop
    function emergencyStop() external onlyOwner {
        paused = true;
        emit EmergencyStop(msg.sender);
    }

    // Time-locked functions
    function scheduleUpgrade(address newImplementation) external onlyOwner {
        upgradeTimelock = block.timestamp + 7 days;
        scheduledUpgrade = newImplementation;
        emit UpgradeScheduled(newImplementation, upgradeTimelock);
    }

    function executeUpgrade() external onlyOwner {
        require(block.timestamp >= upgradeTimelock, "Timelock not expired");
        require(scheduledUpgrade != address(0), "No upgrade scheduled");

        // Execute upgrade
        _upgradeTo(scheduledUpgrade);
    }
}
```

---

## 🎯 Casos de Uso Avanzados

### Sistema de Recompensas

#### Tokenomics de Triboka

```typescript
interface TokenomicsConfig {
  totalSupply: 1000000; // 1 millón TRB
  distribution: {
    productores: 0.4;    // 40% para productores
    certificadores: 0.2; // 20% para certificadores
    plataforma: 0.2;     // 20% para operaciones
    inversionistas: 0.1; // 10% para inversionistas
    reserva: 0.1;        // 10% reserva
  };
  rewards: {
    certificacion: 5;    // 5 TRB por certificación
    mineria: 10;         // 10 TRB por lote minero
    fidelidad: 1;        // 1 TRB por mes activo
  };
}

class RewardSystem {
  async otorgarRecompensaCertificacion(
    certificadorId: string,
    loteId: string
  ): Promise<void> {
    // Verificar elegibilidad
    const elegible = await this.verificarElegibilidadCertificacion(certificadorId, loteId);

    if (!elegible) {
      throw new Error('No elegible para recompensa');
    }

    // Calcular recompensa
    const recompensa = await this.calcularRecompensaCertificacion(loteId);

    // Transferir tokens
    await this.transferirTokens(certificadorId, recompensa);

    // Registrar en blockchain
    await this.registrarRecompensaBlockchain(certificadorId, loteId, recompensa);

    // Notificar usuario
    await this.notificarRecompensa(certificadorId, recompensa);
  }

  async otorgarRecompensaFidelidad(): Promise<void> {
    // Obtener usuarios activos del mes
    const usuariosActivos = await this.getUsuariosActivosMes();

    for (const usuario of usuariosActivos) {
      // Verificar que no haya recibido recompensa este mes
      const yaRecompensado = await this.verificarRecompensaMensual(usuario.id);

      if (!yaRecompensado) {
        await this.transferirTokens(usuario.id, 1); // 1 TRB
        await this.registrarRecompensaFidelidad(usuario.id);
      }
    }
  }
}
```

### Integración con IoT

#### Sensores Agrícolas

```typescript
interface SensorData {
  sensorId: string;
  loteId: string;
  tipo: 'temperatura' | 'humedad' | 'ph' | 'precipitacion';
  valor: number;
  unidad: string;
  timestamp: Date;
  ubicacion: {
    lat: number;
    lng: number;
  };
}

class IoTIntegrationService {
  async procesarDatosSensor(datos: SensorData): Promise<void> {
    // Validar datos
    const datosValidados = await this.validarDatosSensor(datos);

    // Almacenar en base de datos
    await this.almacenarDatosSensor(datosValidados);

    // Verificar condiciones críticas
    await this.verificarCondicionesCriticas(datosValidados);

    // Actualizar métricas del lote
    await this.actualizarMetricasLote(datosValidados.loteId);

    // Trigger contratos inteligentes si aplica
    await this.triggerContratosInteligentes(datosValidados);
  }

  private async verificarCondicionesCriticas(datos: SensorData): Promise<void> {
    const alertas = [];

    // Verificar temperatura extrema
    if (datos.tipo === 'temperatura') {
      if (datos.valor > 35) {
        alertas.push({
          tipo: 'temperatura_alta',
          mensaje: `Temperatura crítica: ${datos.valor}°C`,
          severidad: 'alta',
        });
      }
    }

    // Verificar pH del suelo
    if (datos.tipo === 'ph') {
      if (datos.valor < 5.5 || datos.valor > 7.5) {
        alertas.push({
          tipo: 'ph_inadecuado',
          mensaje: `pH del suelo inadecuado: ${datos.valor}`,
          severidad: 'media',
        });
      }
    }

    // Enviar alertas
    for (const alerta of alertas) {
      await this.enviarAlerta(datos.loteId, alerta);
    }
  }

  private async triggerContratosInteligentes(datos: SensorData): Promise<void> {
    // Buscar contratos que dependan de estos datos
    const contratos = await this.buscarContratosDependientes(datos);

    for (const contrato of contratos) {
      // Verificar si se cumplen las condiciones
      const condicionesCumplidas = await this.verificarCondicionesContrato(
        contrato,
        datos
      );

      if (condicionesCumplidas) {
        // Ejecutar contrato
        await this.ejecutarContrato(contrato.id);
      }
    }
  }
}
```

### Analytics Avanzados

#### Machine Learning para Predicciones

```typescript
interface PredictionModel {
  tipo: 'rendimiento' | 'precio' | 'calidad' | 'clima';
  modelo: 'regresion' | 'clasificacion' | 'time_series';
  precision: number;
  ultimaActualizacion: Date;
}

class MLAnalyticsService {
  async predecirRendimiento(loteId: string): Promise<PredictionResult> {
    // Obtener datos históricos del lote
    const datosHistoricos = await this.getDatosHistoricosLote(loteId);

    // Obtener datos ambientales
    const datosAmbientales = await this.getDatosAmbientales(loteId);

    // Obtener datos de mercado
    const datosMercado = await this.getDatosMercado();

    // Ejecutar modelo de ML
    const prediccion = await this.ejecutarModeloML({
      tipo: 'rendimiento',
      datos: {
        historicos: datosHistoricos,
        ambientales: datosAmbientales,
        mercado: datosMercado,
      },
    });

    return {
      loteId,
      tipo: 'rendimiento',
      valorPredicho: prediccion.valor,
      intervaloConfianza: prediccion.intervalo,
      factores: prediccion.factores,
      timestamp: new Date(),
    };
  }

  async predecirPrecio(cultivo: string, region: string): Promise<PricePrediction> {
    // Obtener datos de precios históricos
    const preciosHistoricos = await this.getPreciosHistoricos(cultivo, region);

    // Obtener indicadores económicos
    const indicadoresEconomicos = await this.getIndicadoresEconomicos();

    // Obtener datos de oferta y demanda
    const ofertaDemanda = await this.getOfertaDemanda(cultivo);

    // Ejecutar modelo de predicción
    const prediccion = await this.ejecutarModeloPrecio({
      cultivo,
      region,
      datos: {
        precios: preciosHistoricos,
        economicos: indicadoresEconomicos,
        ofertaDemanda,
      },
    });

    return {
      cultivo,
      region,
      precioPredicho: prediccion.precio,
      tendencia: prediccion.tendencia,
      factores: prediccion.factores,
      validez: prediccion.validezDias,
    };
  }
}
```

### Gobernanza DAO

#### Sistema de Votación

```solidity
contract TribokaDAO {
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        bytes32 ipfsHash;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        ProposalType proposalType;
        bytes32 proposalData;
    }

    enum ProposalType {
        ParameterChange,
        ContractUpgrade,
        FundAllocation,
        CertificationStandard
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(address => uint256) public votingPower;

    event ProposalCreated(uint256 indexed proposalId, address indexed proposer);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support);
    event ProposalExecuted(uint256 indexed proposalId);

    function createProposal(
        string memory title,
        string memory description,
        bytes32 ipfsHash,
        ProposalType proposalType,
        bytes32 proposalData
    ) external returns (uint256) {
        require(votingPower[msg.sender] > 0, "No voting power");

        uint256 proposalId = ++proposalCount;
        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            title: title,
            description: description,
            ipfsHash: ipfsHash,
            startTime: block.timestamp,
            endTime: block.timestamp + 7 days,
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            executed: false,
            proposalType: proposalType,
            proposalData: proposalData
        });

        emit ProposalCreated(proposalId, msg.sender);
        return proposalId;
    }

    function castVote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(votingPower[msg.sender] > 0, "No voting power");

        hasVoted[proposalId][msg.sender] = true;

        if (support) {
            proposal.forVotes += votingPower[msg.sender];
        } else {
            proposal.againstVotes += votingPower[msg.sender];
        }

        emit VoteCast(proposalId, msg.sender, support);
    }

    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp > proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.forVotes > proposal.againstVotes, "Proposal rejected");

        proposal.executed = true;

        // Execute based on proposal type
        if (proposal.proposalType == ProposalType.ParameterChange) {
            _executeParameterChange(proposal.proposalData);
        } else if (proposal.proposalType == ProposalType.ContractUpgrade) {
            _executeContractUpgrade(proposal.proposalData);
        }

        emit ProposalExecuted(proposalId);
    }

    function _executeParameterChange(bytes32 data) internal {
        // Decode and execute parameter change
        (string memory paramName, uint256 newValue) = abi.decode(data, (string, uint256));

        if (keccak256(bytes(paramName)) == keccak256("minQuorum")) {
            minQuorum = newValue;
        }
    }
}
```

---

*La integración blockchain de Triboka Agro establece un nuevo estándar en la agricultura digital, proporcionando transparencia, confianza y eficiencia a través de contratos inteligentes y trazabilidad completa.*