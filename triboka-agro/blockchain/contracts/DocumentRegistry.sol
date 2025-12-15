// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title DocumentRegistry
 * @dev Registro de documentos con verificación blockchain para trazabilidad
 * @author Triboka Team
 */
contract DocumentRegistry is AccessControl, ReentrancyGuard, Pausable {
    // Roles
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    // Tipos de documentos
    enum DocumentType { 
        Invoice,           // Factura comercial
        Certificate,       // Certificado (fitosanitario, calidad, etc.)
        BillOfLading,      // Conocimiento de embarque
        PackingList,       // Lista de empaque
        Insurance,         // Póliza de seguro
        CustomsDeclaration,// Declaración aduanera
        QualityReport,     // Reporte de calidad
        Contract,          // Contrato
        Other              // Otros documentos
    }

    // Estados del documento
    enum DocumentStatus { 
        Issued,      // Emitido
        Verified,    // Verificado
        Rejected,    // Rechazado
        Revoked      // Revocado
    }

    // Estructura del documento
    struct Document {
        bytes32 documentId;
        bytes32 entityId;          // ID de entidad relacionada (contrato, embarque, etc.)
        DocumentType docType;
        string documentName;       // Nombre del documento
        bytes32 documentHash;      // Hash SHA-256 del documento
        string ipfsHash;           // Hash IPFS para almacenamiento descentralizado
        address issuer;            // Quien emitió el documento
        address verifier;          // Quien verificó (si aplica)
        uint256 issuedDate;        // Fecha de emisión
        uint256 verifiedDate;      // Fecha de verificación
        uint256 expiryDate;        // Fecha de vencimiento (0 si no vence)
        DocumentStatus status;     // Estado actual
        string metadata;           // Metadatos adicionales (JSON)
        bool exists;               // Flag de existencia
    }

    // Mappings
    mapping(bytes32 => Document) public documents;
    mapping(bytes32 => bytes32[]) public documentsByEntity;  // Por contrato/embarque
    mapping(address => bytes32[]) public documentsByIssuer;
    mapping(DocumentType => bytes32[]) public documentsByType;
    mapping(bytes32 => bytes32[]) public documentsByHash;    // Para detectar duplicados

    // Contadores
    uint256 public totalDocuments;
    mapping(DocumentType => uint256) public documentCountByType;
    mapping(DocumentStatus => uint256) public documentCountByStatus;

    // Events
    event DocumentIssued(
        bytes32 indexed documentId,
        bytes32 indexed entityId,
        DocumentType indexed docType,
        address issuer,
        bytes32 documentHash
    );

    event DocumentVerified(
        bytes32 indexed documentId,
        address indexed verifier,
        uint256 verifiedDate
    );

    event DocumentStatusChanged(
        bytes32 indexed documentId,
        DocumentStatus oldStatus,
        DocumentStatus newStatus,
        address changedBy
    );

    event DocumentRevoked(
        bytes32 indexed documentId,
        address revokedBy,
        string reason
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
        _grantRole(ISSUER_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
    }

    /**
     * @dev Emitir nuevo documento
     */
    function issueDocument(
        bytes32 _entityId,
        DocumentType _docType,
        string memory _documentName,
        bytes32 _documentHash,
        string memory _ipfsHash,
        uint256 _expiryDate,
        string memory _metadata
    ) external onlyRole(ISSUER_ROLE) whenNotPaused returns (bytes32) {
        require(_entityId != bytes32(0), "Invalid entity ID");
        require(_documentHash != bytes32(0), "Invalid document hash");
        require(bytes(_documentName).length > 0, "Document name required");

        // Verificar que el hash no exista ya para la misma entidad
        bytes32[] memory existingDocs = documentsByHash[_documentHash];
        for (uint256 i = 0; i < existingDocs.length; i++) {
            Document storage existingDoc = documents[existingDocs[i]];
            require(existingDoc.entityId != _entityId || existingDoc.status == DocumentStatus.Revoked, 
                   "Document with same hash already exists for this entity");
        }

        // Generar ID único del documento
        bytes32 documentId = keccak256(abi.encodePacked(
            _entityId,
            _documentHash,
            msg.sender,
            block.timestamp,
            totalDocuments
        ));

        require(!documents[documentId].exists, "Document ID collision");

        // Crear documento
        documents[documentId] = Document({
            documentId: documentId,
            entityId: _entityId,
            docType: _docType,
            documentName: _documentName,
            documentHash: _documentHash,
            ipfsHash: _ipfsHash,
            issuer: msg.sender,
            verifier: address(0),
            issuedDate: block.timestamp,
            verifiedDate: 0,
            expiryDate: _expiryDate,
            status: DocumentStatus.Issued,
            metadata: _metadata,
            exists: true
        });

        // Actualizar índices
        documentsByEntity[_entityId].push(documentId);
        documentsByIssuer[msg.sender].push(documentId);
        documentsByType[_docType].push(documentId);
        documentsByHash[_documentHash].push(documentId);

        // Actualizar contadores
        totalDocuments++;
        documentCountByType[_docType]++;
        documentCountByStatus[DocumentStatus.Issued]++;

        emit DocumentIssued(documentId, _entityId, _docType, msg.sender, _documentHash);
        return documentId;
    }

    /**
     * @dev Verificar documento
     */
    function verifyDocument(bytes32 _documentId) external onlyRole(VERIFIER_ROLE) whenNotPaused {
        Document storage doc = documents[_documentId];
        require(doc.exists, "Document does not exist");
        require(doc.status == DocumentStatus.Issued, "Document not in issued status");
        require(doc.expiryDate == 0 || doc.expiryDate > block.timestamp, "Document expired");

        // Actualizar documento
        doc.verifier = msg.sender;
        doc.verifiedDate = block.timestamp;
        
        _changeDocumentStatus(_documentId, DocumentStatus.Verified);

        emit DocumentVerified(_documentId, msg.sender, block.timestamp);
    }

    /**
     * @dev Rechazar documento
     */
    function rejectDocument(bytes32 _documentId, string memory _reason) 
        external onlyRole(VERIFIER_ROLE) whenNotPaused {
        Document storage doc = documents[_documentId];
        require(doc.exists, "Document does not exist");
        require(doc.status == DocumentStatus.Issued, "Document not in issued status");

        _changeDocumentStatus(_documentId, DocumentStatus.Rejected);
    }

    /**
     * @dev Revocar documento
     */
    function revokeDocument(bytes32 _documentId, string memory _reason) 
        external whenNotPaused {
        Document storage doc = documents[_documentId];
        require(doc.exists, "Document does not exist");
        require(
            msg.sender == doc.issuer || 
            hasRole(OPERATOR_ROLE, msg.sender) || 
            hasRole(DEFAULT_ADMIN_ROLE, msg.sender),
            "Not authorized to revoke"
        );
        require(doc.status != DocumentStatus.Revoked, "Document already revoked");

        _changeDocumentStatus(_documentId, DocumentStatus.Revoked);

        emit DocumentRevoked(_documentId, msg.sender, _reason);
    }

    /**
     * @dev Cambiar estado del documento
     */
    function _changeDocumentStatus(bytes32 _documentId, DocumentStatus _newStatus) internal {
        Document storage doc = documents[_documentId];
        DocumentStatus oldStatus = doc.status;
        
        // Actualizar contadores
        documentCountByStatus[oldStatus]--;
        documentCountByStatus[_newStatus]++;
        
        // Cambiar estado
        doc.status = _newStatus;

        emit DocumentStatusChanged(_documentId, oldStatus, _newStatus, msg.sender);
    }

    /**
     * @dev Verificar integridad del documento comparando hashes
     */
    function verifyDocumentIntegrity(bytes32 _documentId, bytes32 _providedHash) 
        external view returns (bool) {
        Document storage doc = documents[_documentId];
        require(doc.exists, "Document does not exist");
        return doc.documentHash == _providedHash;
    }

    /**
     * @dev Verificar si el documento está vigente
     */
    function isDocumentValid(bytes32 _documentId) external view returns (bool) {
        Document storage doc = documents[_documentId];
        if (!doc.exists) return false;
        if (doc.status == DocumentStatus.Revoked || doc.status == DocumentStatus.Rejected) return false;
        if (doc.expiryDate != 0 && doc.expiryDate <= block.timestamp) return false;
        return true;
    }

    /**
     * @dev Obtener información del documento
     */
    function getDocument(bytes32 _documentId) external view returns (
        bytes32 entityId,
        DocumentType docType,
        string memory documentName,
        bytes32 documentHash,
        string memory ipfsHash,
        address issuer,
        address verifier,
        uint256 issuedDate,
        uint256 verifiedDate,
        uint256 expiryDate,
        DocumentStatus status,
        string memory metadata
    ) {
        Document storage doc = documents[_documentId];
        require(doc.exists, "Document does not exist");

        return (
            doc.entityId,
            doc.docType,
            doc.documentName,
            doc.documentHash,
            doc.ipfsHash,
            doc.issuer,
            doc.verifier,
            doc.issuedDate,
            doc.verifiedDate,
            doc.expiryDate,
            doc.status,
            doc.metadata
        );
    }

    /**
     * @dev Obtener documentos por entidad (contrato, embarque, etc.)
     */
    function getDocumentsByEntity(bytes32 _entityId) external view returns (bytes32[] memory) {
        return documentsByEntity[_entityId];
    }

    /**
     * @dev Obtener documentos por emisor
     */
    function getDocumentsByIssuer(address _issuer) external view returns (bytes32[] memory) {
        return documentsByIssuer[_issuer];
    }

    /**
     * @dev Obtener documentos por tipo
     */
    function getDocumentsByType(DocumentType _docType) external view returns (bytes32[] memory) {
        return documentsByType[_docType];
    }

    /**
     * @dev Verificar si una entidad tiene todos los documentos requeridos
     */
    function hasRequiredDocuments(
        bytes32 _entityId, 
        DocumentType[] memory _requiredTypes
    ) external view returns (bool) {
        bytes32[] memory entityDocs = documentsByEntity[_entityId];
        
        for (uint256 i = 0; i < _requiredTypes.length; i++) {
            bool hasType = false;
            for (uint256 j = 0; j < entityDocs.length; j++) {
                Document storage doc = documents[entityDocs[j]];
                if (doc.docType == _requiredTypes[i] && 
                    doc.status == DocumentStatus.Verified &&
                    (doc.expiryDate == 0 || doc.expiryDate > block.timestamp)) {
                    hasType = true;
                    break;
                }
            }
            if (!hasType) return false;
        }
        return true;
    }

    /**
     * @dev Obtener documentos próximos a vencer
     */
    function getExpiringDocuments(uint256 _daysBeforeExpiry) 
        external view returns (bytes32[] memory) {
        // Esta función requeriría iterar sobre todos los documentos
        // En producción se implementaría con eventos o índices adicionales
        bytes32[] memory expiring = new bytes32[](0);
        return expiring;
    }

    /**
     * @dev Obtener estadísticas de documentos
     */
    function getDocumentStats() external view returns (
        uint256 _totalDocuments,
        uint256 issuedCount,
        uint256 verifiedCount,
        uint256 rejectedCount,
        uint256 revokedCount
    ) {
        return (
            totalDocuments,
            documentCountByStatus[DocumentStatus.Issued],
            documentCountByStatus[DocumentStatus.Verified],
            documentCountByStatus[DocumentStatus.Rejected],
            documentCountByStatus[DocumentStatus.Revoked]
        );
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
     * @dev Batch operations para eficiencia
     */
    function batchIssueDocuments(
        bytes32[] memory _entityIds,
        DocumentType[] memory _docTypes,
        string[] memory _documentNames,
        bytes32[] memory _documentHashes,
        string[] memory _ipfsHashes,
        uint256[] memory _expiryDates,
        string[] memory _metadatas
    ) external onlyRole(ISSUER_ROLE) whenNotPaused returns (bytes32[] memory) {
        require(_entityIds.length == _docTypes.length, "Array length mismatch");
        require(_entityIds.length == _documentNames.length, "Array length mismatch");
        require(_entityIds.length == _documentHashes.length, "Array length mismatch");
        require(_entityIds.length == _ipfsHashes.length, "Array length mismatch");
        require(_entityIds.length == _expiryDates.length, "Array length mismatch");
        require(_entityIds.length == _metadatas.length, "Array length mismatch");

        bytes32[] memory documentIds = new bytes32[](_entityIds.length);

        for (uint256 i = 0; i < _entityIds.length; i++) {
            documentIds[i] = this.issueDocument(
                _entityIds[i],
                _docTypes[i],
                _documentNames[i],
                _documentHashes[i],
                _ipfsHashes[i],
                _expiryDates[i],
                _metadatas[i]
            );
        }

        return documentIds;
    }
}