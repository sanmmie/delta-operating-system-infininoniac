// lib/core/errors/delta_errors.dart
// Comprehensive error hierarchy for DeltaOS

abstract class DeltaError implements Exception {
  final String message;
  final ErrorSeverity severity;
  final String domain;
  final String code;
  final DateTime timestamp;
  final Map<String, dynamic> context;

  const DeltaError({
    required this.message,
    required this.severity,
    required this.domain,
    required this.code,
    DateTime? timestamp,
    this.context = const {},
  }) : timestamp = timestamp ?? DateTime.now();

  @override
  String toString() => '[$domain::$code] $message (${severity.name})';

  // Standardized error reporting
  Future<void> report() async {
    await ErrorTracker.capture(
      error: this,
      context: ErrorContext.current(),
    );
  }
}

// Error severity levels
enum ErrorSeverity {
  low('Low impact, system continues normally'),
  medium('Moderate impact, some features degraded'),
  high('High impact, significant functionality affected'),
  critical('Critical impact, system stability compromised');

  const ErrorSeverity(this.description);
  final String description;
}

// Specific error types
class CoordinationError extends DeltaError {
  CoordinationError({
    required String message,
    required String domain,
    Map<String, dynamic> context = const {},
  }) : super(
          message: message,
          severity: ErrorSeverity.high,
          domain: domain,
          code: 'COORDINATION_FAILED',
          context: context,
        );
}

class EthicalConstraintError extends DeltaError {
  EthicalConstraintError({
    required String message,
    required List<EthicalViolation> violations,
  }) : super(
          message: message,
          severity: ErrorSeverity.critical,
          domain: 'ethics',
          code: 'ETHICAL_VIOLATION',
          context: {'violations': violations.map((v) => v.toJson()).toList()},
        );
}

class DomainConflictError extends DeltaError {
  DomainConflictError({
    required String domainA,
    required String domainB,
    required String conflictDescription,
  }) : super(
          message: 'Conflict between $domainA and $domainB: $conflictDescription',
          severity: ErrorSeverity.medium,
          domain: 'coordination',
          code: 'DOMAIN_CONFLICT',
          context: {
            'domain_a': domainA,
            'domain_b': domainB,
            'conflict': conflictDescription,
          },
        );
}

// Error recovery strategies
class ErrorRecovery {
  static Future<RecoveryResult> attemptRecovery(DeltaError error) async {
    switch (error.severity) {
      case ErrorSeverity.low:
        return await _handleLowSeverity(error);
      case ErrorSeverity.medium:
        return await _handleMediumSeverity(error);
      case ErrorSeverity.high:
        return await _handleHighSeverity(error);
      case ErrorSeverity.critical:
        return await _handleCriticalSeverity(error);
    }
  }

  static Future<RecoveryResult> _handleLowSeverity(DeltaError error) async {
    // Log and continue normal operation
    return RecoveryResult.success();
  }

  static Future<RecoveryResult> _handleMediumSeverity(DeltaError error) async {
    // Attempt local fallback or degraded mode
    return RecoveryResult.partial();
  }

  static Future<RecoveryResult> _handleHighSeverity(DeltaError error) async {
    // For high severity errors, attempt graceful degradation
    if (error is CoordinationError) {
      return await _degradeCoordinationGracefully(error);
    }
    return RecoveryResult.failed();
  }

  static Future<RecoveryResult> _handleCriticalSeverity(DeltaError error) async {
    // For critical errors, trigger safe mode or system alert
    return RecoveryResult.failed();
  }

  static Future<RecoveryResult> _degradeCoordinationGracefully(
      CoordinationError error) async {
    // Example graceful degradation logic
    return RecoveryResult.partial();
  }
}

// Placeholder classes for demonstration
class ErrorTracker {
  static Future<void> capture({
    required DeltaError error,
    required ErrorContext context,
  }) async {
    // Implement error tracking integration here
  }
}

class ErrorContext {
  static ErrorContext current() => ErrorContext();
}

class RecoveryResult {
  final bool success;
  final bool partial;

  const RecoveryResult._(this.success, this.partial);

  static RecoveryResult success() => const RecoveryResult._(true, false);
  static RecoveryResult partial() => const RecoveryResult._(false, true);
  static RecoveryResult failed() => const RecoveryResult._(false, false);
}

class EthicalViolation {
  final String rule;
  final String description;

  EthicalViolation(this.rule, this.description);

  Map<String, String> toJson() => {
        'rule': rule,
        'description': description,
      };
}
