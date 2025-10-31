import 'package:flutter_test/flutter_test.dart';
import 'package:delta_os_core/delta_os_core.dart';

void main() {
  group('Orchestrator', () {
    late Orchestrator orchestrator;

    setUp(() {
      orchestrator = Orchestrator();
    });

    test('coordinates harmonious actions successfully', () async {
      // Arrange
      final actions = [
        DomainAction(domain: 'climate', type: 'reduce_emissions'),
        DomainAction(domain: 'economy', type: 'green_growth'),
      ];

      final context = CoordinationContext();

      // Act
      final result = await orchestrator.coordinate(
        proposedActions: actions,
        context: context,
      );

      // Assert
      expect(result.isSuccessful, isTrue);
      expect(result.harmonyScore, greaterThan(0.7));
      expect(result.actions, hasLength(2));
      expect(result.ethicalAudit.isApproved, isTrue);
    });

    test('filters out unethical actions', () async {
      // Arrange
      final actions = [
        DomainAction(domain: 'climate', type: 'reduce_emissions'),
        DomainAction(domain: 'economy', type: 'exploitative_growth'),
      ];

      final context = CoordinationContext();

      // Act
      final result = await orchestrator.coordinate(
        proposedActions: actions,
        context: context,
      );

      // Assert
      expect(result.ethicalAudit.isApproved, isTrue);
      expect(result.actions, hasLength(1));
      expect(result.actions.first.type, 'reduce_emissions');
    });

    test('detects and resolves conflicts', () async {
      // Arrange
      final conflictingActions = [
        DomainAction(domain: 'climate', type: 'stop_industrial_production'),
        DomainAction(domain: 'economy', type: 'increase_industrial_production'),
      ];

      final context = CoordinationContext();

      // Act
      final result = await orchestrator.coordinate(
        proposedActions: conflictingActions,
        context: context,
      );

      // Assert
      expect(result.actions.length, lessThan(conflictingActions.length));
      expect(result.harmonyScore, greaterThan(0.0));
    });

    test('throws exception for severe ethical violations', () async {
      // Arrange
      final unethicalActions = [
        DomainAction(domain: 'economy', type: 'harmful_exploitative_growth'),
      ];

      final context = CoordinationContext();

      // Act & Assert
      expect(
        () async => await orchestrator.coordinate(
          proposedActions: unethicalActions,
          context: context,
        ),
        throwsA(isA<EthicalConstraintException>()),
      );
    });
  });

  group('DomainAction', () {
    test('creates with correct defaults', () {
      final action = DomainAction(
        domain: 'test',
        type: 'test_action',
      );

      expect(action.domain, 'test');
      expect(action.type, 'test_action');
      expect(action.parameters, isEmpty);
      expect(action.priority, ActionPriority.strategic);
      expect(action.timestamp, isA<DateTime>());
    });
  });

  group('CoordinationResult', () {
    test('calculates success correctly', () {
      final successfulResult = CoordinationResult(
        actions: [],
        harmonyScore: 0.8,
        ethicalAudit: EthicalAudit(
          isApproved: true,
          violations: [],
          auditedActions: 0,
        ),
        coordinationContext: CoordinationContext(),
      );

      expect(successfulResult.isSuccessful, isTrue);

      final failedResult = CoordinationResult(
        actions: [],
        harmonyScore: 0.5,
        ethicalAudit: EthicalAudit(
          isApproved: true,
          violations: [],
          auditedActions: 0,
        ),
        coordinationContext: CoordinationContext(),
      );

      expect(failedResult.isSuccessful, isFalse);
    });
  });
}
