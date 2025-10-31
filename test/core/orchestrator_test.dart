import 'package:flutter_test/flutter_test.dart';
import 'package:delta_os_core/core/orchestrator.dart';

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
      expect(result.harmonyScore, greaterThan(0.0));
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
    });

    test('detects and resolves conflicts', () async {
      // Arrange
      final conflictingActions = [
        DomainAction(domain: 'climate', type: 'stop_production'),
        DomainAction(domain: 'economy', type: 'increase_production'),
      ];

      final context = CoordinationContext();

      // Act
      final result = await orchestrator.coordinate(
        proposedActions: conflictingActions,
        context: context,
      );

      // Assert
      expect(result.harmonyScore, greaterThan(0.0));
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
    });
  });
}
