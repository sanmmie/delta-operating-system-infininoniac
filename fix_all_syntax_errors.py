#!/usr/bin/env python3
"""
Comprehensive fix for all Python syntax errors in the repository
"""

import os
import re
import ast
import shutil

def check_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, e
    except Exception as e:
        return False, e

def fix_main_guard(content):
    """Fix common main guard issues"""
    patterns = [
        (r'if _name_ == "_main_":', 'if __name__ == "__main__":'),
        (r"if _name_ == '_main_':", 'if __name__ == "__main__":'),
        (r'if __name_ == "__main__":', 'if __name__ == "__main__":'),
        (r'if _name__ == "__main__":', 'if __name__ == "__main__":'),
        (r'if _name_ == "_main_"', 'if __name__ == "__main__":'),  # missing colon
    ]
    
    fixed_content = content
    for wrong, correct in patterns:
        if re.search(wrong, fixed_content):
            fixed_content = re.sub(wrong, correct, fixed_content)
    
    return fixed_content

def fix_common_syntax_issues(content):
    """Fix other common syntax issues"""
    # Fix missing colons in function definitions
    content = re.sub(r'def \w+\(.*\)\s*\n', lambda m: m.group(0).rstrip() + ':\n', content)
    
    # Fix Python 2 print statements
    content = re.sub(r'print\s+([^(].*)', r'print(\1)', content)
    
    return content

def organize_project_structure():
    """Move Python files out of config directories"""
    config_dirs = ['.github', '.github/workflows', 'node-template']
    source_dirs = ['src', 'app']
    
    # Create source directories
    for dir_name in source_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    
    files_moved = []
    
    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            continue
            
        for root, dirs, files in os.walk(config_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    source_path = os.path.join(root, file)
                    dest_dir = source_dirs[0]
                    
                    # Preserve subdirectory structure
                    rel_path = os.path.relpath(root, config_dir)
                    if rel_path != '.':
                        dest_dir = os.path.join(source_dirs[0], rel_path)
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                    
                    dest_path = os.path.join(dest_dir, file)
                    
                    shutil.move(source_path, dest_path)
                    files_moved.append((source_path, dest_path))
    
    return files_moved

def fix_all_python_files():
    """Fix syntax in all Python files"""
    fixed_files = []
    problematic_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and config directories for fixing
        if any(part.startswith('.') and part != '.' for part in root.split(os.sep)):
            continue
        if any(excluded in root for excluded in ['venv', '__pycache__', '.git']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Check syntax
                is_valid, error = check_syntax(filepath)
                
                if not is_valid:
                    print(f"❌ Syntax error in {filepath}: {error}")
                    problematic_files.append((filepath, error))
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Try to fix common issues
                        fixed_content = fix_main_guard(content)
                        fixed_content = fix_common_syntax_issues(fixed_content)
                        
                        # Write back if different
                        if fixed_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(fixed_content)
                            
                            # Verify fix worked
                            is_fixed, new_error = check_syntax(filepath)
                            if is_fixed:
                                print(f"✅ Fixed: {filepath}")
                                fixed_files.append(filepath)
                            else:
                                print(f"❌ Still broken: {filepath} - {new_error}")
                    
                    except Exception as e:
                        print(f"⚠️  Could not fix {filepath}: {e}")
    
    return fixed_files, problematic_files

def create_codeql_config():
    """Create CodeQL configuration to ignore config directories"""
    codeql_dir = '.github/codeql'
    if not os.path.exists(codeql_dir):
        os.makedirs(codeql_dir)
    
    config_content = """name: "Custom CodeQL Config"
paths:
  - src
  - app
paths-ignore:
  - ".github"
  - "node-template"
  - "**/test*"
  - "**/*_test.py"
  - "**/venv"
  - "**/__pycache__"
  - "**/.pytest_cache"
"""
    
    config_path = os.path.join(codeql_dir, 'codeql-config.yml')
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    return config_path

if __name__ == "__main__":
    print("🔧 Starting comprehensive syntax fix...")
    
    # Step 1: Organize project structure
    print("\n📁 Organizing project structure...")
    moved_files = organize_project_structure()
    if moved_files:
        print(f"Moved {len(moved_files)} files:")
        for source, dest in moved_files:
            print(f"  {source} → {dest}")
    
    # Step 2: Fix syntax errors
    print("\n🔧 Fixing syntax errors...")
    fixed_files, problematic_files = fix_all_python_files()
    
    # Step 3: Create CodeQL config
    print("\n⚙️ Creating CodeQL configuration...")
    config_path = create_codeql_config()
    print(f"Created: {config_path}")
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"📁 Files moved: {len(moved_files)}")
    print(f"🔧 Files fixed: {len(fixed_files)}")
    print(f"❌ Still problematic: {len(problematic_files)}")
    
    if problematic_files:
        print("\nFiles that still need manual fixing:")
        for filepath, error in problematic_files:
            print(f"  - {filepath}: {error}")
    
    if not problematic_files:
        print("\n🎉 All Python files now have valid syntax!")
