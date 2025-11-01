/// DeltaOS Core - Command Line Interface
/// 
/// Entry point for deployment and demonstration of DeltaOS Core coordination engine.

import 'package:delta_os_core/delta_os_core.dart';

void main(List<String> arguments) {
  print('🚀 DeltaOS Core - Coordination Layer Operating System');
  print('=' * 60);
  print('Version: 0.1.0-alpha');
  print('Repository: https://github.com/sanmmie/delta-os-core');
  print('=' * 60);
  
  if (arguments.contains('--demo') || arguments.isEmpty) {
    runCoordinationDemo();
  } else if (arguments.contains('--version')) {
    print('DeltaOS Core v0.1.0-alpha');
  } else if (arguments.contains('--help')) {
    printUsage();
  }
}

void runCoordinationDemo() {
  print('🌍 Running DeltaOS Core Coordination Demo');
  print('');
  
  // Demonstrate core functionality
  final orchestrator = Orchestrator();
  
  // Scenario 1: Climate & Economy Harmony
  print('📈 Scenario 1: Climate & Economy Coordination');
  final climateActions = [
    DomainAction(domain: 'climate', type: 'reduce_emissions'),
    DomainAction(domain: 'economy', type: 'green_growth'),
  ];
  
  print('   Proposed Actions:');
  for (final action in climateActions) {
    print('     - ${action.domain}: ${action.type}');
  }
  
  // Simulate coordination result
  final climateResult = CoordinationResult(
    actions: climateActions,
    harmonyScore: 0.85,
    ethicalAudit: EthicalAudit(isApproved: true, violations: [], auditedActions: 2),
    coordinationContext: CoordinationContext(),
  );
  
  print('   ✅ Harmony Score: ${climateResult.harmonyScore}');
  print('   ✅ Ethical Approval: ${climateResult.ethicalAudit.isApproved}');
  
  print('');
  
  // Scenario 2: Healthcare Crisis Response
  print('🏥 Scenario 2: Healthcare Crisis Coordination');
  final healthActions = [
    DomainAction(domain: 'health', type: 'expand_capacity'),
    DomainAction(domain: 'economy', type: 'support_workers'),
    DomainAction(domain: 'education', type: 'remote_learning'),
  ];
  
  final healthResult = CoordinationResult(
    actions: healthActions,
    harmonyScore: 0.92,
    ethicalAudit: EthicalAudit(isApproved: true, violations: [], auditedActions: 3),
    coordinationContext: CoordinationContext(),
  );
  
  print('   ✅ Harmony Score: ${healthResult.harmonyScore}');
  print('   ✅ Coordinated Actions: ${healthResult.actions.length}');
  
  print('');
  print('🎉 DeltaOS Core Demo Complete!');
  print('');
  print('📚 Next Steps:');
  print('   - Use in Flutter apps: import package:delta_os_core/delta_os_core.dart');
  print('   - View documentation: https://github.com/sanmmie/delta-os-core');
  print('   - Read architecture: ARCHITECTURE.md');
  print('=' * 60);
}

void printUsage() {
  print('Usage: dart bin/delta_os_core.dart [options]');
  print('');
  print('Options:');
  print('  --demo     Run coordination demo (default)');
  print('  --version  Display version information');
  print('  --help     Show this help message');
  print('');
  print('DeltaOS Core is a Flutter package for multi-domain coordination.');
  print('For app integration, add to your pubspec.yaml:');
  print('  dependencies:');
  print('    delta_os_core: ^0.1.0');
}
