#!/usr/bin/env python3
"""
Script to fix RST title underlines that are too short.
This script scans all .rst files in a directory and its subdirectories,
and makes sure that title underlines are at least as long as the title text.
"""

import os
import re
import sys

def fix_rst_underlines(directory):
    """
    Fix underlines in all RST files in the given directory and its subdirectories.
    """
    fixed_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.rst'):
                filepath = os.path.join(root, file)
                if fix_file_underlines(filepath):
                    fixed_files += 1
    
    return fixed_files

def fix_file_underlines(filepath):
    """
    Fix underlines in a single RST file.
    Returns True if any changes were made, False otherwise.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match a title line followed by an underline
    # The underline can be any of these characters: = - ` : ' " ~ ^ _ * + # < >
    pattern = r'([^\n]+)\n([=\-`:\'"~^_*+#<>]+)\n'
    
    def replace_match(match):
        title = match.group(1)
        underline = match.group(2)
        
        if len(underline) < len(title):
            # Underline is too short, extend it
            char = underline[0]  # Get the underline character
            new_underline = char * len(title)
            return f"{title}\n{new_underline}\n"
        
        # Underline is fine, return unchanged
        return match.group(0)
    
    new_content = re.sub(pattern, replace_match, content)
    
    if new_content != content:
        # Changes were made, write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed underlines in {filepath}")
        return True
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory
    
    fixed_files = fix_rst_underlines(directory)
    
    if fixed_files > 0:
        print(f"Fixed underlines in {fixed_files} files.")
    else:
        print("No files needed fixing.")