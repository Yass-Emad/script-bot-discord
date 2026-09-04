#!/usr/bin/env python3
"""Extract Python script from CyberControl.bat"""
import sys
import base64
import re

def extract_script(bat_path, output_path):
    with open(bat_path, 'r', encoding='utf-8') as f:
        bat_content = f.read()
    
    # Extract all base64 chunks
    chunks = re.findall(r'echo ([A-Za-z0-9+/=]+)> "%TEMP_B64%"', bat_content)
    chunks += re.findall(r'echo ([A-Za-z0-9+/=]+)>> "%TEMP_B64%"', bat_content)
    
    if not chunks:
        print("ERROR: No base64 chunks found in bat file")
        sys.exit(1)
    
    # Reconstruct and decode
    encoded = ''.join(chunks)
    decoded = base64.b64decode(encoded)
    
    with open(output_path, 'wb') as f:
        f.write(decoded)
    
    print(f"✓ Extracted {len(decoded)} bytes to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_script.py <bat_file> <output_py>")
        sys.exit(1)
    
    extract_script(sys.argv[1], sys.argv[2])
