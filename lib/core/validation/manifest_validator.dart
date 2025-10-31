import 'package:json_annotation/json_annotation.dart';
import 'package:delta_os_core/core/errors/delta_errors.dart';

part 'manifest_validator.g.dart';

// JSON-serializable manifest class
@JsonSerializable()
class DeltaManifest {
  final String version;
  final String name;
  final String description;
  final List<String> domains;
  final Map<String, dynamic> configuration;
  final List<Dependency> dependencies;
  final EthicalConstraints ethicalConstraints;

  DeltaManifest({
    required this.version,
    required this.name,
    required this.description,
    required this.domains,
    required this.configuration,
    required this.dependencies,
    required this.ethicalConstraints,
  });

  factory DeltaManifest.fromJson(Map<String, dynamic> json) =>
      _$DeltaManifestFromJson(json);

  Map<String, dynamic> toJson() => _$DeltaManifestToJson();

  // Validation method
  List<ValidationError> validate() {
    final errors = <ValidationError>[];
    
    // Version format validation
    if (!_isValidVersion(version)) {
      errors.add(ValidationError(
        field: 'version',
        message: 'Version must follow semantic versioning',
        code: 'INVALID_VERSION_FORMAT',
      ));
    }

    // Domain validation
    for (final domain in domains) {
      if (!_isValidDomain(domain)) {
        errors.add(ValidationError(
          field: 'domains',
          message: 'Invalid domain format: $domain',
          code: 'INVALID_DOMAIN_FORMAT',
        ));
      }
    }

    // Dependency compatibility check
    final dependencyErrors = _validateDependencies();
    errors.addAll(dependencyErrors);

    return errors;
  }

  bool _isValidVersion(String version) {
    // Semantic versioning regex
    final regex = RegExp(r'^\d+\.\d+\.\d+$');
    return regex.hasMatch(version);
  }

  bool _isValidDomain(String domain) {
    // Domain naming conventions
    final regex = RegExp(r'^[a-z][a-z0-9_]*$');
    return regex.hasMatch(domain);
  }
}

// JSON-serializable dependency class
@JsonSerializable()
class Dependency {
  final String name;
  final String version;
  final String type; // 'required', 'optional', 'conflicting'

  Dependency({
    required this.name,
    required this.version,
    required this.type,
  });

  factory Dependency.fromJson(Map<String, dynamic> json) =>
      _$DependencyFromJson(json);

  Map<String, dynamic> toJson() => _$DependencyToJson();
}

// Validation error class
class ValidationError {
  final String field;
  final String message;
  final String code;

  const ValidationError({
    required this.field,
    required this.message,
    required this.code,
  });
}

// Manifest validator service
class ManifestValidator {
  static final _supportedVersions = {'1.0.0', '1.1.0', '2.0.0-alpha'};

  static ValidationResult validateManifest(DeltaManifest manifest) {
    final errors = manifest.validate();
    
    // Version compatibility check
    if (!_supportedVersions.contains(manifest.version)) {
      errors.add(ValidationError(
        field: 'version',
        message: 'Unsupported manifest version: ${manifest.version}',
        code: 'UNSUPPORTED_VERSION',
      ));
    }

    // Ethical constraints validation
    final ethicalErrors = _validateEthicalConstraints(manifest.ethicalConstraints);
    errors.addAll(ethicalErrors);

    return ValidationResult(
      isValid: errors.isEmpty,
      errors: errors,
      warnings: _generateWarnings(manifest),
    );
  }

  static List<ValidationError> _validateEthicalConstraints(EthicalConstraints constraints) {
    final errors = <ValidationError>[];
    
    // Validate ethical framework compatibility
    if (!constraints.frameworks.contains('universal_declaration_of_human_rights')) {
      errors.add(ValidationError(
        field: 'ethicalConstraints.frameworks',
        message: 'Must include universal human rights framework',
        code: 'MISSING_REQUIRED_ETHICAL_FRAMEWORK',
      ));
    }

    return errors;
  }
}
