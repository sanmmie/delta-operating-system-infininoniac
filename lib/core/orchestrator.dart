/// DeltaOS Core Orchestrator
/// 
/// The central coordination engine that enables different domains
/// to work together harmoniously instead of conflicting.
library delta_os_core.orchestrator;

/// Main orchestrator class that coordinates actions across domains.
class Orchestrator {
  final Map<String, Domain> _registeredDomains = {};
  final EthicalGovernance _ethicalGovernance = EthicalGovernance();

  /// Register a domain with the orchestrator
  void registerDomain(Domain domain) {
    _registeredDomains[domain.id] = domain;
    _log('Domain registered: ${domain.id}');
  }

  /// Coordinate actions across multiple domains to find harmonious solutions
  Future<CoordinationResult> coordinate({
    required List<DomainAction> proposedActions,
    required CoordinationContext context,
  }) async {
    _log('Starting coordination with ${proposedActions.length} actions');

    // Step 1: Ethical validation
    final ethicalAudit = await _ethicalGovernance.auditActions(
      proposedActions,
      context,
    );

    if (!ethicalAudit.isApproved) {
      throw EthicalConstraintException(
        'Actions failed ethical audit: ${ethicalAudit.violations}',
        ethicalAudit.violations,
      );
    }

    // Step 2: Conflict detection and resolution
    final resolvedActions = _resolveConflicts(proposedActions, context);

    // Step 3: Harmony calculation
    final harmonyScore = _calculateHarmonyScore(resolvedActions);

    // Step 4: Action sequencing
    final sequencedPlan = _sequenceActions(resolvedActions, context);

    _log('Coordination completed with harmony score: $harmonyScore');

    return CoordinationResult(
      actions: sequencedPlan,
      harmonyScore: harmonyScore,
      ethicalAudit: ethicalAudit,
      coordinationContext: context,
    );
  }

  /// Resolve conflicts between domain actions
  List<DomainAction> _resolveConflicts(
    List<DomainAction> actions,
    CoordinationContext context,
  ) {
    final conflicts = _detectConflicts(actions);
    
    if (conflicts.isEmpty) {
      return actions; // No conflicts found
    }

    _log('Found ${conflicts.length} conflicts, resolving...');

    // Simple conflict resolution: remove conflicting actions
    final nonConflictingActions = actions.where((action) {
      return !conflicts.any((conflict) => conflict.involvesAction(action));
    }).toList();

    return nonConflictingActions;
  }

  /// Detect conflicts between domain actions
  List<DomainConflict> _detectConflicts(List<DomainAction> actions) {
    final conflicts = <DomainConflict>[];

    for (var i = 0; i < actions.length; i++) {
      for (var j = i + 1; j < actions.length; j++) {
        final actionA = actions[i];
        final actionB = actions[j];

        if (_actionsConflict(actionA, actionB)) {
          conflicts.add(DomainConflict(
            actions: [actionA, actionB],
            conflictType: _determineConflictType(actionA, actionB),
            severity: _calculateConflictSeverity(actionA, actionB),
          ));
        }
      }
    }

    return conflicts;
  }

  /// Check if two actions conflict with each other
  bool _actionsConflict(DomainAction a, DomainAction b) {
    // Simple conflict detection based on domain and type
    if (a.domain == b.domain) {
      return _sameDomainConflicts(a, b);
    }

    // Cross-domain conflict detection
    return _crossDomainConflicts(a, b);
  }

  bool _sameDomainConflicts(DomainAction a, DomainAction b) {
    // Same domain actions conflict if they have opposite intents
    final conflictingPairs = [
      ['increase', 'decrease'],
      ['expand', 'reduce'],
      ['accelerate', 'decelerate'],
    ];

    for (final pair in conflictingPairs) {
      if (a.type.contains(pair[0]) && b.type.contains(pair[1])) {
        return true;
      }
      if (a.type.contains(pair[1]) && b.type.contains(pair[0])) {
        return true;
      }
    }

    return false;
  }

  bool _crossDomainConflicts(DomainAction a, DomainAction b) {
    // Common cross-domain conflicts
    final crossDomainConflicts = [
      // Climate vs Economy conflicts
      {'climate': 'reduce_emissions', 'economy': 'increase_production'},
      {'climate': 'protect_forest', 'economy': 'expand_agriculture'},
    ];

    for (final conflict in crossDomainConflicts) {
      final domainA = conflict.keys.first;
      final typeA = conflict[domainA]!;
      final domainB = conflict.keys.last;
      final typeB = conflict[domainB]!;

      if ((a.domain == domainA && a.type == typeA && 
           b.domain == domainB && b.type == typeB) ||
          (a.domain == domainB && a.type == typeB && 
           b.domain == domainA && b.type == typeA)) {
        return true;
      }
    }

    return false;
  }

  /// Calculate harmony score for a set of actions (0.0 to 1.0)
  double _calculateHarmonyScore(List<DomainAction> actions) {
    if (actions.isEmpty) return 1.0;

    final domains = actions.map((a) => a.domain).toSet();
    final totalPossibleConflicts = (domains.length * (domains.length - 1)) / 2;
    
    if (totalPossibleConflicts == 0) return 1.0;

    final actualConflicts = _detectConflicts(actions).length;
    final conflictRatio = actualConflicts / totalPossibleConflicts;

    return (1.0 - conflictRatio).clamp(0.0, 1.0);
  }

  /// Sequence actions for optimal execution
  List<DomainAction> _sequenceActions(
    List<DomainAction> actions,
    CoordinationContext context,
  ) {
    // Simple sequencing: immediate actions first, then strategic
    final immediateActions = actions.where((action) =>
      action.priority == ActionPriority.immediate
    ).toList();

    final strategicActions = actions.where((action) =>
      action.priority == ActionPriority.strategic
    ).toList();

    final longTermActions = actions.where((action) =>
      action.priority == ActionPriority.longTerm
    ).toList();

    return [...immediateActions, ...strategicActions, ...longTermActions];
  }

  void _log(String message) {
    // Simple logging
    print('DeltaOS Orchestrator: $message');
  }
}

/// Domain action with priority and metadata
class DomainAction {
  final String domain;
  final String type;
  final Map<String, dynamic> parameters;
  final ActionPriority priority;
  final DateTime timestamp;

  const DomainAction({
    required this.domain,
    required this.type,
    this.parameters = const {},
    this.priority = ActionPriority.strategic,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  @override
  String toString() => 'DomainAction(domain: $domain, type: $type, priority: $priority)';
}

/// Action priority levels
enum ActionPriority {
  immediate,   // Execute now (crisis response)
  strategic,   // Short-term coordination
  longTerm,    // Strategic planning
}

/// Coordination context providing environmental information
class CoordinationContext {
  final Map<String, dynamic> environment;
  final EthicalConstraints ethicalConstraints;
  final DateTime timestamp;

  const CoordinationContext({
    this.environment = const {},
    this.ethicalConstraints = const EthicalConstraints(),
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

/// Result of coordination process
class CoordinationResult {
  final List<DomainAction> actions;
  final double harmonyScore;
  final EthicalAudit ethicalAudit;
  final CoordinationContext coordinationContext;
  final DateTime completedAt;

  const CoordinationResult({
    required this.actions,
    required this.harmonyScore,
    required this.ethicalAudit,
    required this.coordinationContext,
    DateTime? completedAt,
  }) : completedAt = completedAt ?? DateTime.now();

  /// Check if coordination was successful
  bool get isSuccessful => harmonyScore >= 0.7 && ethicalAudit.isApproved;

  @override
  String toString() => 'CoordinationResult('
      'actions: ${actions.length}, '
      'harmony: ${harmonyScore.toStringAsFixed(2)}, '
      'ethical: ${ethicalAudit.isApproved}'
      ')';
}

/// Domain conflict information
class DomainConflict {
  final List<DomainAction> actions;
  final String conflictType;
  final double severity; // 0.0 to 1.0

  const DomainConflict({
    required this.actions,
    required this.conflictType,
    required this.severity,
  });

  bool involvesAction(DomainAction action) => actions.contains(action);
}

/// Ethical constraints for coordination
class EthicalConstraints {
  final Set<String> prohibitedActionTypes;
  final Map<String, dynamic> requirements;

  const EthicalConstraints({
    this.prohibitedActionTypes = const {
      'exploitative',
      'harmful',
      'discriminatory',
      'unsustainable',
    },
    this.requirements = const {},
  });
}

/// Ethical governance system
class EthicalGovernance {
  Future<EthicalAudit> auditActions(
    List<DomainAction> actions,
    CoordinationContext context,
  ) async {
    final violations = <EthicalViolation>[];

    for (final action in actions) {
      final actionViolations = _auditSingleAction(action, context);
      violations.addAll(actionViolations);
    }

    return EthicalAudit(
      isApproved: violations.isEmpty,
      violations: violations,
      auditedActions: actions.length,
    );
  }

  List<EthicalViolation> _auditSingleAction(
    DomainAction action,
    CoordinationContext context,
  ) {
    final violations = <EthicalViolation>[];

    // Check against prohibited action types
    for (final prohibitedType in context.ethicalConstraints.prohibitedActionTypes) {
      if (action.type.contains(prohibitedType)) {
        violations.add(EthicalViolation(
          action: action,
          principle: 'non_maleficence',
          description: 'Action type "$prohibitedType" is prohibited',
          severity: 0.8,
        ));
      }
    }

    return violations;
  }
}

/// Ethical audit result
class EthicalAudit {
  final bool isApproved;
  final List<EthicalViolation> violations;
  final int auditedActions;

  const EthicalAudit({
    required this.isApproved,
    required this.violations,
    required this.auditedActions,
  });
}

/// Ethical violation details
class EthicalViolation {
  final DomainAction action;
  final String principle;
  final String description;
  final double severity; // 0.0 to 1.0

  const EthicalViolation({
    required this.action,
    required this.principle,
    required this.description,
    required this.severity,
  });

  @override
  String toString() => 'EthicalViolation('
      'principle: $principle, '
      'action: ${action.type}, '
      'severity: ${severity.toStringAsFixed(2)}'
      ')';
}

/// Domain interface
abstract class Domain {
  String get id;
  String get name;
  List<String> get capabilities;
}

/// Exception for ethical constraint violations
class EthicalConstraintException implements Exception {
  final String message;
  final List<EthicalViolation> violations;

  const EthicalConstraintException(this.message, this.violations);

  @override
  String toString() => 'EthicalConstraintException: $message\n'
      'Violations: ${violations.map((v) => v.toString()).join(", ")}';
}

/// Conflict type enumeration
String _determineConflictType(DomainAction a, DomainAction b) {
  if (a.domain == b.domain) return 'intra_domain_conflict';
  return 'cross_domain_conflict';
}

/// Calculate conflict severity (0.0 to 1.0)
double _calculateConflictSeverity(DomainAction a, DomainAction b) {
  double severity = 0.5; // Base severity

  // Increase severity for high-priority actions
  if (a.priority == ActionPriority.immediate || 
      b.priority == ActionPriority.immediate) {
    severity += 0.3;
  }

  return severity.clamp(0.0, 1.0);
}
