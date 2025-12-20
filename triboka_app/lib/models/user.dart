/// Modelo de usuario para la aplicación TRIBOKA
class User {
  final String id;
  final String name;
  final String email;
  final String role; 
  final String? avatarUrl; 
  final String? phone; // New field
  final String? taxId; // New field (RUC)
  final String? address; // New field
  final String? company; // New field
  final DateTime createdAt;
  final bool isActive;

  const User({
    required this.id,
    required this.name,
    required this.email,
    this.role = 'user',
    this.avatarUrl,
    this.phone,
    this.taxId,
    this.address,
    this.company,
    required this.createdAt,
    this.isActive = true,
  });

  /// Constructor desde Map (útil para JSON)
  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: map['id'] as String,
      name: map['name'] as String,
      email: map['email'] as String,
      role: map['role'] as String? ?? 'user',
      avatarUrl: map['avatarUrl'] as String?,
      phone: map['phone'] as String?,
      taxId: map['taxId'] as String? ?? map['ruc'] as String?, // Support both naming conventions
      address: map['address'] as String? ?? map['direccion'] as String?,
      company: map['company'] as String? ?? map['empresa'] as String?,
      createdAt: DateTime.parse(map['createdAt'] as String),
      isActive: map['isActive'] as bool? ?? true,
    );
  }

  /// Convierte el usuario a Map (útil para JSON)
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'role': role,
      'avatarUrl': avatarUrl,
      'phone': phone,
      'taxId': taxId,
      'address': address,
      'company': company,
      'createdAt': createdAt.toIso8601String(),
      'isActive': isActive,
    };
  }

  /// Crea una copia del usuario con los cambios especificados
  User copyWith({
    String? id,
    String? name,
    String? email,
    String? role,
    String? avatarUrl,
    String? phone,
    String? taxId,
    String? address,
    String? company,
    DateTime? createdAt,
    bool? isActive,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      role: role ?? this.role,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      phone: phone ?? this.phone,
      taxId: taxId ?? this.taxId,
      address: address ?? this.address,
      company: company ?? this.company,
      createdAt: createdAt ?? this.createdAt,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is User &&
        other.id == id &&
        other.name == name &&
        other.email == email &&
        other.role == role &&
        other.avatarUrl == avatarUrl &&
        other.phone == phone &&
        other.taxId == taxId &&
        other.address == address &&
        other.company == company &&
        other.createdAt == createdAt &&
        other.isActive == isActive;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        name.hashCode ^
        email.hashCode ^
        role.hashCode ^
        avatarUrl.hashCode ^
        phone.hashCode ^
        taxId.hashCode ^
        address.hashCode ^
        company.hashCode ^
        createdAt.hashCode ^
        isActive.hashCode;
  }

  @override
  String toString() {
    return 'User(id: $id, name: $name, email: $email, role: $role, phone: $phone, company: $company, createdAt: $createdAt, isActive: $isActive)';
  }
}