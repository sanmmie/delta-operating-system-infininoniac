/// DeltaOS Core Library
/// 
/// A coordination layer operating system that enables different domains
/// to work together harmoniously instead of conflicting.
/// 
/// ## Overview
/// 
/// DeltaOS provides:
/// - Multi-domain coordination
/// - Ethical decision making
/// - Conflict resolution
/// - Harmony-based optimization
/// 
/// ## Usage
/// 
/// ```dart
/// import 'package:delta_os_core/delta_os_core.dart';
/// 
/// final orchestrator = Orchestrator();
/// final result = await orchestrator.coordinate(
///   proposedActions: [
///     DomainAction(domain: 'climate', type: 'reduce_emissions'),
///     DomainAction(domain: 'economy', type: 'green_growth'),
///   ],
///   context: CoordinationContext(),
/// );
/// ```
library delta_os_core;

// Core Coordination
export 'core/orchestrator.dart';
