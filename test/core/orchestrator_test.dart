import 'package:flutter_test/flutter_test.dart';
import 'package:delta_os_core/core/orchestrator.dart';

void main() {
  group('Orchestrator Basic Tests', () {
    test('DomainAction creation works', () {
      final action = DomainAction(
        domain: 'climate',
        type: 'reduce_emissions',
      );

      expect(action.domain, 'climate');
      expect(action.type, 'reduce_emissions');
    });

    test('CoordinationContext creation works', () {
      final context = CoordinationContext();

      expect(context.environment, isEmpty);
      expect(context.ethicalConstraints.prohibitedActionTypes, isNotEmpty);
    });

    test('ActionPriority values exist', () {
      expect(ActionPriority.immediate, isNotNull);
      expect(ActionPriority.strategic, isNotNull);
      expect(ActionPriority.longTerm, isNotNull);
    });
  });

  group('Ethical Governance', () {
    test('EthicalConstraints has prohibited types', () {
      final constraints = EthicalConstraints();
      
      expect(constraints.prohibitedActionTypes, contains('exploitative'));
      expect(constraints.prohibitedActionTypes, contains('harmful'));
    });

    test('EthicalAudit creation works', () {
      final audit = EthicalAudit(
        isApproved: true,
        violations: [],
        auditedActions: 5,
      );

      expect(audit.isApproved, isTrue);
      expect(audit.violations, isEmpty);
    });
  });
}
