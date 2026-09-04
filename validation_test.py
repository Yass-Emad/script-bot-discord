
from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("FINAL COMPREHENSIVE VALIDATION")
print("=" * 60)

# Test 1: Verify script syntax
print("\n[1/5] Syntax Validation...")
script_path = Path(r"C:\Users\Twins\Desktop\AI\cyber_bot_app.py")
try:
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, str(script_path), 'exec')
    print("✓ Script compiles without syntax errors")
except SyntaxError as e:
    print(f"✗ SYNTAX ERROR: {e}")
    sys.exit(1)

# Test 2: Verify async isolation
print("\n[2/5] Async Isolation Check...")
import re
async_funcs = re.findall(r'async def (\w+)\(.*?\):', code)
print(f"  Found {len(async_funcs)} async functions")

for func_name in async_funcs:
    pattern = rf'async def {func_name}\(.*?\):(.*?)(?=\n    (?:async )?def |\Z)'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        body = match.group(1)
        if 'questionary' in body:
            print(f"  ✗ ERROR: {func_name} contains questionary call!")
            sys.exit(1)
print("✓ No questionary calls inside async functions")

# Test 3: Verify encoding integrity
print("\n[3/5] Encoding Integrity Check...")
import base64
bat_path = Path(r"C:\Users\Twins\Desktop\AI\CyberControl.bat")
bat_content = bat_path.read_text(encoding='utf-8')

chunks = re.findall(r'echo ([A-Za-z0-9+/=]+)> "%TEMP_B64%"', bat_content)
chunks += re.findall(r'echo ([A-Za-z0-9+/=]+)>> "%TEMP_B64%"', bat_content)

if not chunks:
    print("✗ No base64 chunks found")
    sys.exit(1)

encoded = ''.join(chunks)
decoded_text = base64.b64decode(encoded).decode('utf-8')

if decoded_text == code:
    print(f"✓ Encoding integrity verified ({len(code)} bytes)")
else:
    print(f"✗ Encoding mismatch!")
    sys.exit(1)

# Test 4: Verify all methods exist
print("\n[4/5] Method Existence Check...")
required_methods = [
    'print_banner', 'validate_token', 'start_bot_client', 
    'prompt_token_login', 'show_dashboard', 'run_coroutine',
    'status_presence_menu', 'list_and_inspect_servers',
    'inspect_single_guild', 'broadcast_announcement_menu',
    'moderation_action_menu', 'guide_menu', 'run_main_loop'
]

for method in required_methods:
    if f'def {method}' not in code:
        print(f"  ✗ Missing method: {method}")
        sys.exit(1)
print(f"✓ All {len(required_methods)} required methods present")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE - ALL TESTS PASSED!")
print("=" * 60)
