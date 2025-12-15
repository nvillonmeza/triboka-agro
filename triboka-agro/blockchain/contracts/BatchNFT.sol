// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title BatchNFT
 * @dev NFT contract para agregación y división de lotes con trazabilidad completa
 * @author Triboka Team
 */
contract BatchNFT is ERC721, ERC721URIStorage, ERC721Enumerable, AccessControl, Pausable {
    using Counters for Counters.Counter;

    // Roles
    bytes32 public constant BATCH_CREATOR_ROLE = keccak256("BATCH_CREATOR_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    // Contador de tokens
    Counters.Counter private _tokenIdCounter;

    // Estados del batch
    enum BatchStatus { Created, InTransit, Delivered, Split, Consumed }

    // Estructura del batch
    struct Batch {
        uint256 batchId;
        uint256[] sourceLotIds;        // IDs de lotes originales
        uint256[] sourceLotWeights;    // Peso de cada lote original
        uint256 totalWeight;           // Peso total del batch
        address creator;               // Quien creó el batch
        address currentOwner;          // Propietario actual
        string batchType;              // Tipo: "export", "retail", "wholesale"
        string location;               // Ubicación actual
        uint256 creationDate;          // Fecha de creación
        BatchStatus status;            // Estado del batch
        bytes32 contractId;            // ID del contrato asociado (si aplica)
        bytes32 shipmentId;            // ID del envío (si aplica)
        string metadataURI;            // URI de metadatos IPFS
        bool exists;                   // Flag de existencia
    }

    // Estructura para sub-batches (cuando se divide un batch)
    struct SubBatch {
        uint256 parentBatchId;         // ID del batch padre
        uint256 weight;                // Peso del sub-batch
        address assignedTo;            // A quien se asignó
        uint256 creationDate;          // Fecha de creación
        bool consumed;                 // Si ya fue consumido/entregado
    }

    // Mappings
    mapping(uint256 => Batch) public batches;
    mapping(uint256 => SubBatch) public subBatches;
    mapping(uint256 => uint256[]) public batchToSubBatches; // batch -> sub-batches
    mapping(uint256 => uint256[]) public lotToBatches;      // lote -> batches que lo contienen
    mapping(address => uint256[]) public batchesByCreator;
    mapping(address => uint256[]) public batchesByOwner;
    mapping(bytes32 => uint256[]) public batchesByContract;
    mapping(BatchStatus => uint256) public batchesByStatus;

    // Events
    event BatchCreated(
        uint256 indexed batchId,
        address indexed creator,
        uint256[] sourceLotIds,
        uint256 totalWeight,
        string batchType
    );

    event BatchSplit(
        uint256 indexed parentBatchId,
        uint256[] subBatchIds,
        uint256[] weights,
        address[] assignees
    );

    event BatchMerged(
        uint256[] sourceBatchIds,
        uint256 indexed newBatchId,
        uint256 totalWeight
    );

    event BatchTransferred(
        uint256 indexed batchId,
        address indexed from,
        address indexed to
    );

    event BatchStatusChanged(
        uint256 indexed batchId,
        BatchStatus oldStatus,
        BatchStatus newStatus
    );

    constructor() ERC721("BatchNFT", "BATCH") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(BATCH_CREATOR_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    /**
     * @dev Crear nuevo batch desde múltiples lotes
     */
    function createBatch(
        uint256[] memory _sourceLotIds,
        uint256[] memory _sourceLotWeights,
        string memory _batchType,
        string memory _location,
        string memory _metadataURI
    ) external onlyRole(BATCH_CREATOR_ROLE) whenNotPaused returns (uint256) {
        require(_sourceLotIds.length > 0, "Must include at least one lot");
        require(_sourceLotIds.length == _sourceLotWeights.length, "Arrays length mismatch");
        
        // Calcular peso total
        uint256 totalWeight = 0;
        for (uint256 i = 0; i < _sourceLotWeights.length; i++) {
            require(_sourceLotWeights[i] > 0, "Weight must be greater than 0");
            totalWeight += _sourceLotWeights[i];
        }

        _tokenIdCounter.increment();
        uint256 batchId = _tokenIdCounter.current();

        // Crear el batch
        batches[batchId] = Batch({
            batchId: batchId,
            sourceLotIds: _sourceLotIds,
            sourceLotWeights: _sourceLotWeights,
            totalWeight: totalWeight,
            creator: msg.sender,
            currentOwner: msg.sender,
            batchType: _batchType,
            location: _location,
            creationDate: block.timestamp,
            status: BatchStatus.Created,
            contractId: bytes32(0),
            shipmentId: bytes32(0),
            metadataURI: _metadataURI,
            exists: true
        });

        // Actualizar índices
        batchesByCreator[msg.sender].push(batchId);
        batchesByOwner[msg.sender].push(batchId);
        batchesByStatus[BatchStatus.Created]++;

        // Vincular lotes con el batch
        for (uint256 i = 0; i < _sourceLotIds.length; i++) {
            lotToBatches[_sourceLotIds[i]].push(batchId);
        }

        // Mint NFT
        _mint(msg.sender, batchId);
        if (bytes(_metadataURI).length > 0) {
            _setTokenURI(batchId, _metadataURI);
        }

        emit BatchCreated(batchId, msg.sender, _sourceLotIds, totalWeight, _batchType);
        return batchId;
    }

    /**
     * @dev Dividir batch en sub-batches para diferentes destinatarios
     */
    function splitBatch(
        uint256 _batchId,
        uint256[] memory _weights,
        address[] memory _assignees,
        string[] memory _metadataURIs
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused returns (uint256[] memory) {
        require(batches[_batchId].exists, "Batch does not exist");
        require(_weights.length == _assignees.length, "Arrays length mismatch");
        require(_weights.length == _metadataURIs.length, "Metadata array length mismatch");
        require(_isApprovedOrOwner(msg.sender, _batchId), "Not authorized");

        Batch storage batch = batches[_batchId];
        require(batch.status == BatchStatus.Created || batch.status == BatchStatus.InTransit, "Cannot split batch in current status");

        // Verificar que la suma de pesos no exceda el batch original
        uint256 totalSplitWeight = 0;
        for (uint256 i = 0; i < _weights.length; i++) {
            require(_weights[i] > 0, "Weight must be greater than 0");
            totalSplitWeight += _weights[i];
        }
        require(totalSplitWeight <= batch.totalWeight, "Total split weight exceeds batch weight");

        uint256[] memory subBatchIds = new uint256[](_weights.length);

        // Crear sub-batches
        for (uint256 i = 0; i < _weights.length; i++) {
            _tokenIdCounter.increment();
            uint256 subBatchId = _tokenIdCounter.current();
            subBatchIds[i] = subBatchId;

            // Crear sub-batch
            subBatches[subBatchId] = SubBatch({
                parentBatchId: _batchId,
                weight: _weights[i],
                assignedTo: _assignees[i],
                creationDate: block.timestamp,
                consumed: false
            });

            // Crear batch NFT para el sub-batch (hereda información del padre)
            batches[subBatchId] = Batch({
                batchId: subBatchId,
                sourceLotIds: batch.sourceLotIds, // Hereda lotes originales
                sourceLotWeights: _calculateProportionalWeights(batch.sourceLotWeights, _weights[i], batch.totalWeight),
                totalWeight: _weights[i],
                creator: batch.creator,
                currentOwner: _assignees[i],
                batchType: string(abi.encodePacked(batch.batchType, "-split")),
                location: batch.location,
                creationDate: block.timestamp,
                status: BatchStatus.Created,
                contractId: batch.contractId,
                shipmentId: batch.shipmentId,
                metadataURI: _metadataURIs[i],
                exists: true
            });

            // Actualizar índices
            batchToSubBatches[_batchId].push(subBatchId);
            batchesByOwner[_assignees[i]].push(subBatchId);
            batchesByStatus[BatchStatus.Created]++;

            // Mint NFT para el destinatario
            _mint(_assignees[i], subBatchId);
            if (bytes(_metadataURIs[i]).length > 0) {
                _setTokenURI(subBatchId, _metadataURIs[i]);
            }
        }

        // Cambiar estado del batch original
        _changeBatchStatus(_batchId, BatchStatus.Split);

        emit BatchSplit(_batchId, subBatchIds, _weights, _assignees);
        return subBatchIds;
    }

    /**
     * @dev Obtener trazabilidad completa de un batch
     */
    function getFullTraceability(uint256 _batchId) external view returns (
        uint256[] memory sourceLotIds,
        uint256[] memory sourceLotWeights,
        uint256 totalWeight,
        address creator,
        address currentOwner,
        string memory batchType,
        uint256 creationDate,
        BatchStatus status,
        uint256[] memory subBatchIds,
        uint256 parentBatchId
    ) {
        require(batches[_batchId].exists, "Batch does not exist");
        
        Batch memory batch = batches[_batchId];
        
        return (
            batch.sourceLotIds,
            batch.sourceLotWeights,
            batch.totalWeight,
            batch.creator,
            batch.currentOwner,
            batch.batchType,
            batch.creationDate,
            batch.status,
            batchToSubBatches[_batchId],
            subBatches[_batchId].parentBatchId // 0 si no es sub-batch
        );
    }

    /**
     * @dev Obtener información básica del batch
     */
    function getBatch(uint256 _batchId) external view returns (
        uint256[] memory sourceLotIds,
        uint256[] memory sourceLotWeights,
        uint256 totalWeight,
        address creator,
        address currentOwner,
        string memory batchType,
        BatchStatus status
    ) {
        require(batches[_batchId].exists, "Batch does not exist");
        
        Batch memory batch = batches[_batchId];
        
        return (
            batch.sourceLotIds,
            batch.sourceLotWeights,
            batch.totalWeight,
            batch.creator,
            batch.currentOwner,
            batch.batchType,
            batch.status
        );
    }

    /**
     * @dev Obtener batches que contienen un lote específico
     */
    function getBatchesByLot(uint256 _lotId) external view returns (uint256[] memory) {
        return lotToBatches[_lotId];
    }

    /**
     * @dev Obtener batches creados por una dirección
     */
    function getBatchesByCreator(address _creator) external view returns (uint256[] memory) {
        return batchesByCreator[_creator];
    }

    /**
     * @dev Obtener batches propiedad de una dirección
     */
    function getBatchesByOwner(address _owner) external view returns (uint256[] memory) {
        return batchesByOwner[_owner];
    }

    /**
     * @dev Cambiar estado del batch
     */
    function changeBatchStatus(uint256 _batchId, BatchStatus _newStatus) 
        external onlyRole(OPERATOR_ROLE) whenNotPaused 
    {
        _changeBatchStatus(_batchId, _newStatus);
    }

    /**
     * @dev Función interna para cambiar estado
     */
    function _changeBatchStatus(uint256 _batchId, BatchStatus _newStatus) internal {
        require(batches[_batchId].exists, "Batch does not exist");
        
        Batch storage batch = batches[_batchId];
        BatchStatus oldStatus = batch.status;
        
        // Actualizar contadores
        batchesByStatus[oldStatus]--;
        batchesByStatus[_newStatus]++;
        
        batch.status = _newStatus;
        
        emit BatchStatusChanged(_batchId, oldStatus, _newStatus);
    }

    /**
     * @dev Calcular pesos proporcionales para sub-batches
     */
    function _calculateProportionalWeights(
        uint256[] memory _originalWeights,
        uint256 _subBatchWeight,
        uint256 _totalWeight
    ) internal pure returns (uint256[] memory) {
        uint256[] memory proportionalWeights = new uint256[](_originalWeights.length);
        
        for (uint256 i = 0; i < _originalWeights.length; i++) {
            proportionalWeights[i] = (_originalWeights[i] * _subBatchWeight) / _totalWeight;
        }
        
        return proportionalWeights;
    }

    /**
     * @dev Override transfer para actualizar índices
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) whenNotPaused {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
        
        if (from != address(0) && to != address(0)) {
            // Actualizar índices de propietario
            _removeFromOwnerList(from, tokenId);
            batchesByOwner[to].push(tokenId);
            
            // Actualizar owner en el batch
            batches[tokenId].currentOwner = to;
            
            emit BatchTransferred(tokenId, from, to);
        }
    }

    /**
     * @dev Remover batch de la lista del propietario
     */
    function _removeFromOwnerList(address _owner, uint256 _batchId) internal {
        uint256[] storage ownerBatches = batchesByOwner[_owner];
        for (uint256 i = 0; i < ownerBatches.length; i++) {
            if (ownerBatches[i] == _batchId) {
                ownerBatches[i] = ownerBatches[ownerBatches.length - 1];
                ownerBatches.pop();
                break;
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
     * @dev Override funciones requeridas por herencia múltiple
     */
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721Enumerable, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}