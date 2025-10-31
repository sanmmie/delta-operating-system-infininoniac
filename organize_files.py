#!/usr/bin/env python3
"""
Organize Python files into proper directories
"""

import os
import shutil

def organize_python_files():
    # Define proper directories
    source_dirs = ['src', 'app', 'delta_os']
    config_dirs = ['.github', '.github/workflows']
    
    # Create source directory if it doesn't exist
    for dir_name in source_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")
    
    # Files to move from config directories to source directories
    files_moved = []
    
    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            continue
            
        for file in os.listdir(config_dir):
            if file.endswith('.py') and file != '__init__.py':
                source_path = os.path.join(config_dir, file)
                dest_path = os.path.join(source_dirs[0], file)
                
                # Move the file
                shutil.move(source_path, dest_path)
                files_moved.append((source_path, dest_path))
                print(f"📁 Moved: {source_path} → {dest_path}")
    
    return files_moved

if __name__ == "__main__":
    print("Organizing Python files...")
    moved = organize_python_files()
    
    if moved:
        print(f"\n✅ Moved {len(moved)} files to proper directories:")
        for source, dest in moved:
            print(f"   {source} → {dest}")
    else:
        print("\n✅ All files are already in proper locations!")
