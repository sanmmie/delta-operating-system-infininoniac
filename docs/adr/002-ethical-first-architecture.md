# ADR 002: Ethical-First Architecture

## Status
Accepted

## Context
Coordination without ethical constraints can lead to harmful outcomes. We need to embed ethics at the architectural level.

## Decision
Ethical validation occurs **before** any coordination decision, not as an afterthought.

## Implementation
```dart
class EthicalGatekeeper {
  static Future<EthicalAudit> validatePreCoordination(
    List<ProposedAction> actions,
    CoordinationContext context
  ) async {
    // Ethical validation happens BEFORE coordination
    final audit = await EthicalEngine.comprehensiveAudit(actions);
    if (!audit.approved) {
      throw EthicalConstraintViolation(audit.violations);
    }
    return audit;
  }
}
