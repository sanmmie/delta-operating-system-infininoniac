"""
Find and fix all incorrect main guards in Python files
"""

import os
import re

def fix_main_guards():
    fixed_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and hidden directories
        if any(part.startswith('.') for part in root.split(os.sep)):
            continue
        if 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for incorrect main guards
                    incorrect_patterns = [
                        r'if _name_ == "_main_":',
                        r'if _name_ == \'_main_\':',
                        r'if __name_ == "__main__":',
                        r'if _name__ == "__main__":',
                    ]
                    
                    fixed_content = content
                    for pattern in incorrect_patterns:
                        if re.search(pattern, fixed_content):
                            fixed_content = re.sub(pattern, 'if __name__ == "__main__":', fixed_content)
                            print(f"🔧 Fixed main guard in: {filepath}")
                            fixed_files.append(filepath)
                    
                    # Write back if changes were made
                    if fixed_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                            
                except Exception as e:
                    print(f"⚠️  Error processing {filepath}: {e}")
    
    return fixed_files

if __name__ == "__main__":
    print("Scanning for incorrect main guards...")
    fixed = fix_main_guards()
    
    if fixed:
        print(f"\n✅ Fixed {len(fixed)} files:")
        for filepath in fixed:
            print(f"   - {filepath}")
    else:
        print("\n🎉 No incorrect main guards found!")
