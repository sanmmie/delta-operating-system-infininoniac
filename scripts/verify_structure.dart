import 'dart:io';

void main() {
  print('🔍 Verifying DeltaOS Core Structure...');
  
  final requiredDirs = [
    'lib/core',
    'lib/core/orchestrator',
    'lib/core/domains', 
    'lib/core/ethics',
    'lib/core/errors',
    'lib/coordination',
    'test/core',
    'test/domains',
  ];
  
  final requiredFiles = [
    'pubspec.yaml',
    'analysis_options.yaml', 
    'lib/delta_os_core.dart',
    'README.md',
    'ARCHITECTURE.md',
    'SECURITY.md',
  ];
  
  // Check directories
  for (final dir in requiredDirs) {
    if (!Directory(dir).existsSync()) {
      print('❌ Missing directory: $dir');
      exit(1);
    } else {
      print('✅ Directory exists: $dir');
    }
  }
  
  // Check files
  for (final file in requiredFiles) {
    if (!File(file).existsSync()) {
      print('❌ Missing file: $file');
      exit(1);
    } else {
      print('✅ File exists: $file');
    }
  }
  
  // Check for incorrect Python files
  final pythonFiles = Directory('.').listSync(recursive: true).where((entity) {
    return entity.path.endsWith('.py') && 
           !entity.path.contains('.dart_tool') &&
           !entity.path.contains('build/');
  });
  
  if (pythonFiles.isNotEmpty) {
    print('⚠️  Found Python files (may cause issues):');
    for (final file in pythonFiles) {
      print('   - ${file.path}');
    }
  }
  
  print('✅ DeltaOS Core structure verification complete!');
}
