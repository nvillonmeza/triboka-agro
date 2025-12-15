// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title AgroExportContract
 * @dev Smart contract para gestión de contratos de exportación agrícola
 * @author Triboka Team
 */
contract AgroExportContract is AccessControl, ReentrancyGuard, Pausable {
    // Roles
    bytes32 public constant EXPORTER_ROLE = keccak256("EXPORTER_ROLE");
    bytes32 public constant BUYER_ROLE = keccak256("BUYER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    // Estados del contrato
    enum ContractStatus { Active, Completed, Cancelled, Expired }

    // Estructura del contrato de exportación
    struct ExportContract {
        bytes32 contractId;
        address buyer;              // Dirección del comprador
        address exporter;           // Dirección de la exportadora
        string contractCode;        // Código único del contrato
        string productType;         // Tipo de producto (cacao, café, etc.)
        string productGrade;        // Grado de calidad
        uint256 totalVolumeMT;      // Volumen total en toneladas métricas
        int256 differentialUSD;     // Diferencial vs precio spot (puede ser negativo)
        uint256 contractDate;       // Fecha de creación del contrato
        uint256 startDate;          // Fecha de inicio
        uint256 endDate;            // Fecha de fin
        uint256 deliveryDate;       // Fecha de entrega
        uint256 fixedVolumeMT;      // Volumen ya fijado
        ContractStatus status;      // Estado del contrato
        bool exists;                // Flag de existencia
    }

    // Estructura de fijación
    struct Fixation {
        bytes32 fixationId;
        bytes32 contractId;
        uint256 fixedQuantityMT;    // Cantidad fijada en TM
        uint256 spotPriceUSD;       // Precio spot en USD/TM (con 2 decimales)
        uint256 finalPriceUSD;      // Precio final (spot + diferencial)
        uint256 fixationDate;       // Fecha de la fijación
        uint256[] lotIds;           // IDs de lotes asociados
        string notes;               // Observaciones
        address registeredBy;       // Quién registró la fijación
        bool exists;                // Flag de existencia
    }

    // Mappings
    mapping(bytes32 => ExportContract) public contracts;
    mapping(bytes32 => Fixation) public fixations;
    mapping(address => bytes32[]) public contractsByExporter;
    mapping(address => bytes32[]) public contractsByBuyer;
    mapping(bytes32 => bytes32[]) public fixationsByContract;

    // Contadores
    uint256 public totalContracts;
    uint256 public totalFixations;

    // Events
    event ContractCreated(
        bytes32 indexed contractId,
        address indexed buyer,
        address indexed exporter,
        string contractCode,
        uint256 totalVolumeMT
    );

    event FixationRegistered(
        bytes32 indexed fixationId,
        bytes32 indexed contractId,
        uint256 fixedQuantityMT,
        uint256 spotPriceUSD,
        uint256 finalPriceUSD,
        uint256[] lotIds
    );

    event ContractStatusChanged(
        bytes32 indexed contractId,
        ContractStatus oldStatus,
        ContractStatus newStatus
    );

    event ContractCompleted(
        bytes32 indexed contractId,
        uint256 totalFixedVolume,
        uint256 totalFixations
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    /**
     * @dev Crear nuevo contrato de exportación
     */
    function createContract(
        address _buyer,
        address _exporter,
        string memory _contractCode,
        string memory _productType,
        string memory _productGrade,
        uint256 _totalVolumeMT,
        int256 _differentialUSD,
        uint256 _startDate,
        uint256 _endDate,
        uint256 _deliveryDate
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused returns (bytes32) {
        require(_buyer != address(0), "Invalid buyer address");
        require(_exporter != address(0), "Invalid exporter address");
        require(_totalVolumeMT > 0, "Volume must be greater than 0");
        require(_startDate < _endDate, "Invalid date range");
        require(_deliveryDate >= _endDate, "Delivery date must be after end date");

        bytes32 contractId = keccak256(abi.encodePacked(
            _contractCode,
            _buyer,
            _exporter,
            block.timestamp,
            totalContracts
        ));

        require(!contracts[contractId].exists, "Contract already exists");

        contracts[contractId] = ExportContract({
            contractId: contractId,
            buyer: _buyer,
            exporter: _exporter,
            contractCode: _contractCode,
            productType: _productType,
            productGrade: _productGrade,
            totalVolumeMT: _totalVolumeMT,
            differentialUSD: _differentialUSD,
            contractDate: block.timestamp,
            startDate: _startDate,
            endDate: _endDate,
            deliveryDate: _deliveryDate,
            fixedVolumeMT: 0,
            status: ContractStatus.Active,
            exists: true
        });

        // Agregar a índices
        contractsByExporter[_exporter].push(contractId);
        contractsByBuyer[_buyer].push(contractId);
        totalContracts++;

        // Otorgar roles si no los tienen
        if (!hasRole(BUYER_ROLE, _buyer)) {
            _grantRole(BUYER_ROLE, _buyer);
        }
        if (!hasRole(EXPORTER_ROLE, _exporter)) {
            _grantRole(EXPORTER_ROLE, _exporter);
        }

        emit ContractCreated(contractId, _buyer, _exporter, _contractCode, _totalVolumeMT);
        return contractId;
    }

    /**
     * @dev Registrar nueva fijación
     */
    function registerFixation(
        bytes32 _contractId,
        uint256 _fixedQuantityMT,
        uint256 _spotPriceUSD,
        uint256[] memory _lotIds,
        string memory _notes
    ) external whenNotPaused returns (bytes32) {
        ExportContract storage contractData = contracts[_contractId];
        require(contractData.exists, "Contract does not exist");
        require(contractData.status == ContractStatus.Active, "Contract not active");
        require(
            hasRole(EXPORTER_ROLE, msg.sender) || hasRole(OPERATOR_ROLE, msg.sender),
            "Not authorized to register fixations"
        );

        // Validar que el exportador sea correcto
        if (hasRole(EXPORTER_ROLE, msg.sender)) {
            require(contractData.exporter == msg.sender, "Not the contract exporter");
        }

        // Validaciones de negocio
        require(_fixedQuantityMT > 0, "Fixed quantity must be greater than 0");
        require(_spotPriceUSD > 0, "Spot price must be greater than 0");
        
        uint256 pendingVolume = contractData.totalVolumeMT - contractData.fixedVolumeMT;
        require(_fixedQuantityMT <= pendingVolume, "Fixed quantity exceeds pending volume");

        // Verificar fechas
        require(block.timestamp >= contractData.startDate, "Contract period not started");
        require(block.timestamp <= contractData.endDate, "Contract period expired");

        // Calcular precio final
        uint256 finalPriceUSD;
        if (contractData.differentialUSD >= 0) {
            finalPriceUSD = _spotPriceUSD + uint256(contractData.differentialUSD);
        } else {
            uint256 absDifferential = uint256(-contractData.differentialUSD);
            require(_spotPriceUSD >= absDifferential, "Spot price too low for differential");
            finalPriceUSD = _spotPriceUSD - absDifferential;
        }

        // Crear ID de fijación
        bytes32 fixationId = keccak256(abi.encodePacked(
            _contractId,
            _fixedQuantityMT,
            _spotPriceUSD,
            block.timestamp,
            totalFixations
        ));

        require(!fixations[fixationId].exists, "Fixation already exists");

        // Registrar fijación
        fixations[fixationId] = Fixation({
            fixationId: fixationId,
            contractId: _contractId,
            fixedQuantityMT: _fixedQuantityMT,
            spotPriceUSD: _spotPriceUSD,
            finalPriceUSD: finalPriceUSD,
            fixationDate: block.timestamp,
            lotIds: _lotIds,
            notes: _notes,
            registeredBy: msg.sender,
            exists: true
        });

        // Actualizar contrato
        contractData.fixedVolumeMT += _fixedQuantityMT;
        fixationsByContract[_contractId].push(fixationId);
        totalFixations++;

        // Verificar si el contrato se completó
        if (contractData.fixedVolumeMT >= contractData.totalVolumeMT) {
            _changeContractStatus(_contractId, ContractStatus.Completed);
            emit ContractCompleted(_contractId, contractData.fixedVolumeMT, fixationsByContract[_contractId].length);
        }

        emit FixationRegistered(fixationId, _contractId, _fixedQuantityMT, _spotPriceUSD, finalPriceUSD, _lotIds);
        return fixationId;
    }

    /**
     * @dev Cambiar estado del contrato
     */
    function changeContractStatus(bytes32 _contractId, ContractStatus _newStatus) 
        external onlyRole(OPERATOR_ROLE) {
        _changeContractStatus(_contractId, _newStatus);
    }

    function _changeContractStatus(bytes32 _contractId, ContractStatus _newStatus) internal {
        ExportContract storage contractData = contracts[_contractId];
        require(contractData.exists, "Contract does not exist");
        
        ContractStatus oldStatus = contractData.status;
        contractData.status = _newStatus;
        
        emit ContractStatusChanged(_contractId, oldStatus, _newStatus);
    }

    /**
     * @dev Obtener información del contrato
     */
    function getContract(bytes32 _contractId) external view returns (
        address buyer,
        address exporter,
        string memory contractCode,
        string memory productType,
        string memory productGrade,
        uint256 totalVolumeMT,
        int256 differentialUSD,
        uint256 contractDate,
        uint256 startDate,
        uint256 endDate,
        uint256 deliveryDate,
        uint256 fixedVolumeMT,
        ContractStatus status
    ) {
        ExportContract storage contractData = contracts[_contractId];
        require(contractData.exists, "Contract does not exist");

        return (
            contractData.buyer,
            contractData.exporter,
            contractData.contractCode,
            contractData.productType,
            contractData.productGrade,
            contractData.totalVolumeMT,
            contractData.differentialUSD,
            contractData.contractDate,
            contractData.startDate,
            contractData.endDate,
            contractData.deliveryDate,
            contractData.fixedVolumeMT,
            contractData.status
        );
    }

    /**
     * @dev Obtener información de fijación
     */
    function getFixation(bytes32 _fixationId) external view returns (
        bytes32 contractId,
        uint256 fixedQuantityMT,
        uint256 spotPriceUSD,
        uint256 finalPriceUSD,
        uint256 fixationDate,
        uint256[] memory lotIds,
        string memory notes,
        address registeredBy
    ) {
        Fixation storage fixation = fixations[_fixationId];
        require(fixation.exists, "Fixation does not exist");

        return (
            fixation.contractId,
            fixation.fixedQuantityMT,
            fixation.spotPriceUSD,
            fixation.finalPriceUSD,
            fixation.fixationDate,
            fixation.lotIds,
            fixation.notes,
            fixation.registeredBy
        );
    }

    /**
     * @dev Obtener contratos por exportadora
     */
    function getContractsByExporter(address _exporter) external view returns (bytes32[] memory) {
        return contractsByExporter[_exporter];
    }

    /**
     * @dev Obtener contratos por comprador
     */
    function getContractsByBuyer(address _buyer) external view returns (bytes32[] memory) {
        return contractsByBuyer[_buyer];
    }

    /**
     * @dev Obtener fijaciones por contrato
     */
    function getFixationsByContract(bytes32 _contractId) external view returns (bytes32[] memory) {
        return fixationsByContract[_contractId];
    }

    /**
     * @dev Obtener volumen pendiente del contrato
     */
    function getPendingVolume(bytes32 _contractId) external view returns (uint256) {
        ExportContract storage contractData = contracts[_contractId];
        require(contractData.exists, "Contract does not exist");
        return contractData.totalVolumeMT - contractData.fixedVolumeMT;
    }

    /**
     * @dev Verificar si el contrato está vencido
     */
    function isContractExpired(bytes32 _contractId) external view returns (bool) {
        ExportContract storage contractData = contracts[_contractId];
        require(contractData.exists, "Contract does not exist");
        return block.timestamp > contractData.endDate && contractData.status == ContractStatus.Active;
    }

    /**
     * @dev Marcar contratos vencidos (función administrativa)
     */
    function markExpiredContracts(bytes32[] memory _contractIds) external onlyRole(OPERATOR_ROLE) {
        for (uint256 i = 0; i < _contractIds.length; i++) {
            if (this.isContractExpired(_contractIds[i])) {
                _changeContractStatus(_contractIds[i], ContractStatus.Expired);
            }
        }
    }

    /**
     * @dev Funciones de pausa para emergencias
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Obtener estadísticas generales
     */
    function getStats() external view returns (
        uint256 _totalContracts,
        uint256 _totalFixations,
        uint256 activeContracts,
        uint256 completedContracts
    ) {
        // Esta función requeriría iterar sobre todos los contratos para contar activos/completados
        // En una implementación de producción, se mantendrían contadores separados
        return (totalContracts, totalFixations, 0, 0);
    }
}