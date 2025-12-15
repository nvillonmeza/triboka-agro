// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ProducerLotNFT
 * @dev NFT contract para lotes de productores agrícolas con trazabilidad completa
 * @author Triboka Team
 */
contract ProducerLotNFT is ERC721, ERC721URIStorage, ERC721Enumerable, AccessControl, Pausable {
    using Counters for Counters.Counter;

    // Roles
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant PRODUCER_ROLE = keccak256("PRODUCER_ROLE");

    // Contador de tokens
    Counters.Counter private _tokenIdCounter;

    // Estados del lote
    enum LotStatus { Created, Purchased, Fixed, Shipped, Delivered }

    // Estructura del lote de productor
    struct ProducerLot {
        uint256 lotId;
        address producer;           // Dirección del productor
        string producerName;        // Nombre del productor
        string farmName;            // Nombre de la finca
        string location;            // Ubicación GPS (lat,lng)
        string productType;         // Tipo de producto (cacao, café, etc.)
        uint256 weightKg;           // Peso neto en kilogramos
        string qualityGrade;        // Grado de calidad
        uint256 harvestDate;        // Fecha de cosecha (timestamp)
        uint256 purchaseDate;       // Fecha de compra (timestamp)
        uint256 purchasePriceUSD;   // Precio de compra en USD (con 2 decimales)
        string[] certifications;   // Certificaciones (orgánico, fair trade, etc.)
        LotStatus status;           // Estado actual del lote
        bytes32 contractId;         // ID del contrato al que fue asignado (si aplica)
        bytes32 shipmentId;         // ID del embarque (si aplica)
        string metadataURI;         // URI de metadatos IPFS
        bool exists;                // Flag de existencia
    }

    // Mappings
    mapping(uint256 => ProducerLot) public lots;
    mapping(address => uint256[]) public lotsByProducer;
    mapping(bytes32 => uint256[]) public lotsByContract;
    mapping(bytes32 => uint256[]) public lotsByShipment;
    mapping(string => uint256) public lotsByCode;

    // Contadores por estado
    mapping(LotStatus => uint256) public lotsByStatus;

    // Events
    event LotCreated(
        uint256 indexed lotId,
        address indexed producer,
        string lotCode,
        uint256 weightKg,
        string productType
    );

    event LotPurchased(
        uint256 indexed lotId,
        address indexed buyer,
        uint256 purchasePriceUSD,
        uint256 purchaseDate
    );

    event LotFixed(
        uint256 indexed lotId,
        bytes32 indexed contractId,
        string contractCode
    );

    event LotShipped(
        uint256 indexed lotId,
        bytes32 indexed shipmentId,
        string containerNumber
    );

    event LotStatusChanged(
        uint256 indexed lotId,
        LotStatus oldStatus,
        LotStatus newStatus
    );

    event CertificationAdded(
        uint256 indexed lotId,
        string certification,
        address addedBy
    );

    constructor() ERC721("ProducerLotNFT", "PLNFT") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    /**
     * @dev Crear nuevo lote de productor y mint NFT
     */
    function createLot(
        address _producer,
        string memory _producerName,
        string memory _farmName,
        string memory _location,
        string memory _productType,
        uint256 _weightKg,
        string memory _qualityGrade,
        uint256 _harvestDate,
        string[] memory _certifications,
        string memory _metadataURI
    ) external onlyRole(MINTER_ROLE) whenNotPaused returns (uint256) {
        require(_producer != address(0), "Invalid producer address");
        require(_weightKg > 0, "Weight must be greater than 0");
        require(_harvestDate <= block.timestamp, "Harvest date cannot be in the future");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        // Mint NFT al productor
        _safeMint(_producer, tokenId);

        // Generar código único del lote
        string memory lotCode = string(abi.encodePacked(
            "LOT-",
            _productType,
            "-",
            _toString(block.timestamp),
            "-",
            _toString(tokenId)
        ));

        // Crear estructura del lote
        lots[tokenId] = ProducerLot({
            lotId: tokenId,
            producer: _producer,
            producerName: _producerName,
            farmName: _farmName,
            location: _location,
            productType: _productType,
            weightKg: _weightKg,
            qualityGrade: _qualityGrade,
            harvestDate: _harvestDate,
            purchaseDate: 0,
            purchasePriceUSD: 0,
            certifications: _certifications,
            status: LotStatus.Created,
            contractId: bytes32(0),
            shipmentId: bytes32(0),
            metadataURI: _metadataURI,
            exists: true
        });

        // Actualizar índices
        lotsByProducer[_producer].push(tokenId);
        lotsByCode[lotCode] = tokenId;
        lotsByStatus[LotStatus.Created]++;

        // Otorgar role de productor si no lo tiene
        if (!hasRole(PRODUCER_ROLE, _producer)) {
            _grantRole(PRODUCER_ROLE, _producer);
        }

        // Establecer URI de metadatos
        if (bytes(_metadataURI).length > 0) {
            _setTokenURI(tokenId, _metadataURI);
        }

        emit LotCreated(tokenId, _producer, lotCode, _weightKg, _productType);
        return tokenId;
    }

    /**
     * @dev Registrar compra del lote
     */
    function purchaseLot(
        uint256 _lotId,
        address _buyer,
        uint256 _purchasePriceUSD
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");
        require(lot.status == LotStatus.Created, "Lot already purchased");
        require(_buyer != address(0), "Invalid buyer address");
        require(_purchasePriceUSD > 0, "Purchase price must be greater than 0");

        // Actualizar información de compra
        lot.purchaseDate = block.timestamp;
        lot.purchasePriceUSD = _purchasePriceUSD;

        // Cambiar estado
        _changeLotStatus(_lotId, LotStatus.Purchased);

        // Transferir NFT al comprador (exportadora)
        address currentOwner = ownerOf(_lotId);
        _transfer(currentOwner, _buyer, _lotId);

        emit LotPurchased(_lotId, _buyer, _purchasePriceUSD, block.timestamp);
    }

    /**
     * @dev Asignar lote a un contrato (fijación)
     */
    function fixLotToContract(
        uint256 _lotId,
        bytes32 _contractId,
        string memory _contractCode
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");
        require(lot.status == LotStatus.Purchased, "Lot must be purchased first");
        require(_contractId != bytes32(0), "Invalid contract ID");

        // Asignar al contrato
        lot.contractId = _contractId;
        lotsByContract[_contractId].push(_lotId);

        // Cambiar estado
        _changeLotStatus(_lotId, LotStatus.Fixed);

        emit LotFixed(_lotId, _contractId, _contractCode);
    }

    /**
     * @dev Asignar lote a un embarque
     */
    function shipLot(
        uint256 _lotId,
        bytes32 _shipmentId,
        string memory _containerNumber
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");
        require(lot.status == LotStatus.Fixed, "Lot must be fixed to contract first");
        require(_shipmentId != bytes32(0), "Invalid shipment ID");

        // Asignar al embarque
        lot.shipmentId = _shipmentId;
        lotsByShipment[_shipmentId].push(_lotId);

        // Cambiar estado
        _changeLotStatus(_lotId, LotStatus.Shipped);

        emit LotShipped(_lotId, _shipmentId, _containerNumber);
    }

    /**
     * @dev Marcar lote como entregado
     */
    function deliverLot(uint256 _lotId) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");
        require(lot.status == LotStatus.Shipped, "Lot must be shipped first");

        // Cambiar estado
        _changeLotStatus(_lotId, LotStatus.Delivered);
    }

    /**
     * @dev Cambiar estado del lote
     */
    function _changeLotStatus(uint256 _lotId, LotStatus _newStatus) internal {
        ProducerLot storage lot = lots[_lotId];
        LotStatus oldStatus = lot.status;
        
        // Actualizar contadores
        lotsByStatus[oldStatus]--;
        lotsByStatus[_newStatus]++;
        
        // Cambiar estado
        lot.status = _newStatus;

        emit LotStatusChanged(_lotId, oldStatus, _newStatus);
    }

    /**
     * @dev Agregar certificación a un lote
     */
    function addCertification(
        uint256 _lotId,
        string memory _certification
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");
        require(bytes(_certification).length > 0, "Certification cannot be empty");

        // Verificar que no exista ya la certificación
        for (uint256 i = 0; i < lot.certifications.length; i++) {
            require(
                keccak256(abi.encodePacked(lot.certifications[i])) != 
                keccak256(abi.encodePacked(_certification)),
                "Certification already exists"
            );
        }

        lot.certifications.push(_certification);
        emit CertificationAdded(_lotId, _certification, msg.sender);
    }

    /**
     * @dev Actualizar URI de metadatos
     */
    function updateMetadataURI(
        uint256 _lotId,
        string memory _newURI
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        require(_exists(_lotId), "Lot does not exist");
        lots[_lotId].metadataURI = _newURI;
        _setTokenURI(_lotId, _newURI);
    }

    /**
     * @dev Obtener información completa del lote
     */
    function getLot(uint256 _lotId) external view returns (
        address producer,
        string memory producerName,
        string memory farmName,
        string memory location,
        string memory productType,
        uint256 weightKg,
        string memory qualityGrade,
        uint256 harvestDate,
        uint256 purchaseDate,
        uint256 purchasePriceUSD,
        string[] memory certifications,
        LotStatus status,
        bytes32 contractId,
        bytes32 shipmentId
    ) {
        ProducerLot storage lot = lots[_lotId];
        require(lot.exists, "Lot does not exist");

        return (
            lot.producer,
            lot.producerName,
            lot.farmName,
            lot.location,
            lot.productType,
            lot.weightKg,
            lot.qualityGrade,
            lot.harvestDate,
            lot.purchaseDate,
            lot.purchasePriceUSD,
            lot.certifications,
            lot.status,
            lot.contractId,
            lot.shipmentId
        );
    }

    /**
     * @dev Obtener lotes por productor
     */
    function getLotsByProducer(address _producer) external view returns (uint256[] memory) {
        return lotsByProducer[_producer];
    }

    /**
     * @dev Obtener lotes por contrato
     */
    function getLotsByContract(bytes32 _contractId) external view returns (uint256[] memory) {
        return lotsByContract[_contractId];
    }

    /**
     * @dev Obtener lotes por embarque
     */
    function getLotsByShipment(bytes32 _shipmentId) external view returns (uint256[] memory) {
        return lotsByShipment[_shipmentId];
    }

    /**
     * @dev Obtener estadísticas de lotes
     */
    function getLotStats() external view returns (
        uint256 totalLots,
        uint256 createdLots,
        uint256 purchasedLots,
        uint256 fixedLots,
        uint256 shippedLots,
        uint256 deliveredLots
    ) {
        return (
            totalSupply(),
            lotsByStatus[LotStatus.Created],
            lotsByStatus[LotStatus.Purchased],
            lotsByStatus[LotStatus.Fixed],
            lotsByStatus[LotStatus.Shipped],
            lotsByStatus[LotStatus.Delivered]
        );
    }

    /**
     * @dev Verificar si un lote está disponible para fijación
     */
    function isLotAvailableForFixation(uint256 _lotId) external view returns (bool) {
        ProducerLot storage lot = lots[_lotId];
        return lot.exists && lot.status == LotStatus.Purchased;
    }

    /**
     * @dev Obtener peso total de lotes por contrato
     */
    function getTotalWeightByContract(bytes32 _contractId) external view returns (uint256) {
        uint256[] memory contractLots = lotsByContract[_contractId];
        uint256 totalWeight = 0;
        
        for (uint256 i = 0; i < contractLots.length; i++) {
            totalWeight += lots[contractLots[i]].weightKg;
        }
        
        return totalWeight;
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
     * @dev Funciones override requeridas por herencia múltiple
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) whenNotPaused {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    /**
     * @dev Convertir uint256 a string
     */
    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}