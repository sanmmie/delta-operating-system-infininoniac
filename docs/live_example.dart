// DeltaOS Core Live Example - Run in DartPad
// Go to: https://dartpad.dev/ and paste this code

import 'dart:async';

// Simplified DeltaOS Core for demonstration
class DeltaOSDemo {
  Future<CoordinationResult> coordinate(List<DomainAction> actions) async {
    print('🌍 DeltaOS Coordination Starting...');
    print('Proposed Actions: ${actions.map((a) => '${a.domain}: ${a.type}').join(', ')}');
    
    // Simulate coordination process
    await Future.delayed(Duration(seconds: 1));
    
    // Conflict detection
    final conflicts = _detectConflicts(actions);
    if (conflicts.isNotEmpty) {
      print('⚖️  Conflicts detected: $conflicts');
    }
    
    // Ethical audit
    final ethicalScore = _ethicalAudit(actions);
    print('🔒 Ethical Audit Score: ${ethicalScore.toStringAsFixed(2)}');
    
    // Harmony calculation
    final harmonyScore = _calculateHarmony(actions);
    print('🎯 Harmony Score: ${harmonyScore.toStringAsFixed(2)}');
    
    return CoordinationResult(
      actions: actions,
      harmonyScore: harmonyScore,
      ethicalScore: ethicalScore,
    );
  }
  
  List<String> _detectConflicts(List<DomainAction> actions) {
    final conflicts = <String>[];
    
    for (var i = 0; i < actions.length; i++) {
      for (var j = i + 1; j < actions.length; j++) {
        final a = actions[i];
        final b = actions[j];
        
        // Simple conflict detection
        if ((a.domain == 'climate' && a.type.contains('reduce') &&
             b.domain == 'economy' && b.type.contains('increase')) ||
            (a.domain == 'health' && a.type.contains('restrict') &&
             b.domain == 'economy' && b.type.contains('boost'))) {
          conflicts.add('${a.domain} vs ${b.domain}');
        }
      }
    }
    
    return conflicts;
  }
  
  double _ethicalAudit(List<DomainAction> actions) {
    var score = 1.0;
    
    for (final action in actions) {
      if (action.type.contains('exploitative') || 
          action.type.contains('harmful')) {
        score -= 0.3;
      }
    }
    
    return score.clamp(0.0, 1.0);
  }
  
  double _calculateHarmony(List<DomainAction> actions) {
    final conflicts = _detectConflicts(actions);
    final baseScore = 1.0 - (conflicts.length * 0.2);
    final ethicalScore = _ethicalAudit(actions);
    
    return (baseScore * 0.6 + ethicalScore * 0.4).clamp(0.0, 1.0);
  }
}

class DomainAction {
  final String domain;
  final String type;
  
  const DomainAction({required this.domain, required this.type});
  
  @override
  String toString() => '$domain: $type';
}

class CoordinationResult {
  final List<DomainAction> actions;
  final double harmonyScore;
  final double ethicalScore;
  
  const CoordinationResult({
    required this.actions,
    required this.harmonyScore,
    required this.ethicalScore,
  });
  
  bool get isSuccessful => harmonyScore >= 0.7 && ethicalScore >= 0.8;
  
  @override
  String toString() {
    return '''
🎉 Coordination Result:
   Actions: ${actions.length}
   Harmony: ${harmonyScore.toStringAsFixed(2)}
   Ethical: ${ethicalScore.toStringAsFixed(2)}
   Success: ${isSuccessful ? '✅ YES' : '❌ NO'}
''';
  }
}

// Live Demo Execution
void main() async {
  print('🚀 DeltaOS Core Live Demo');
  print('=' * 40);
  
  final deltaOS = DeltaOSDemo();
  
  // Demo 1: Climate vs Economy
  print('\n📈 Demo 1: Climate & Economy Coordination');
  final result1 = await deltaOS.coordinate([
    DomainAction(domain: 'climate', type: 'reduce_emissions'),
    DomainAction(domain: 'economy', type: 'sustainable_growth'),
  ]);
  print(result1);
  
  // Demo 2: Healthcare Crisis
  print('\n🏥 Demo 2: Healthcare Crisis Response');
  final result2 = await deltaOS.coordinate([
    DomainAction(domain: 'health', type: 'expand_capacity'),
    DomainAction(domain: 'economy', type: 'support_workers'),
    DomainAction(domain: 'education', type: 'remote_learning'),
  ]);
  print(result2);
  
  // Demo 3: Conflict Scenario
  print('\n⚡ Demo 3: Conflict Resolution');
  final result3 = await deltaOS.coordinate([
    DomainAction(domain: 'climate', type: 'stop_industrial'),
    DomainAction(domain: 'economy', type: 'boost_production'), // Conflict!
  ]);
  print(result3);
  
  print('\n🎊 DeltaOS Demo Complete!');
  print('Visit: https://github.com/sanmmie/delta-os-core');
}
