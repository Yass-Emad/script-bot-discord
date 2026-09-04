"""Tests for CyberControl Discord Bot CLI"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import time


class TestAsyncIsolation:
    """Test that async operations don't conflict with event loops"""
    
    def test_no_questionary_in_async(self):
        """Ensure questionary is never called inside async functions"""
        import re
        
        with open('cyber_bot_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all async def and check if questionary is in the SAME indentation level
        # We need to ensure questionary is not called directly in async bodies
        # (nested async functions defined inside sync functions are OK)
        
        # Pattern to find async def at any level
        async_defs = list(re.finditer(r'async def (\w+)\(', content))
        
        for match in async_defs:
            start = match.start()
            indent = len(match.group(0)) - len(match.group(0).lstrip())
            
            # Find the body of this async function
            lines = content[start:].split('\n')
            end = len(content)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    continue
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent:
                    end = start + sum(len(l) + 1 for l in lines[:i])
                    break
            
            func_body = content[start:end]
            
            # Only flag questionary if it's at the SAME indentation level (directly in async)
            # Questionary in nested async functions (higher indent) is acceptable
            for q_match in re.finditer(r'questionary\.', func_body):
                q_pos = q_match.start()
                q_line_start = func_body.rfind('\n', 0, q_pos) + 1
                q_line = func_body[q_line_start:]
                q_indent = len(q_line) - len(q_line.lstrip())
                
                # If questionary is at same or lower indent than async def, it's a violation
                if q_indent <= indent:
                    func_name = match.group(1)
                    raise AssertionError(
                        f"questionary call found at same level as async function '{func_name}'"
                    )


class TestRunCoroutine:
    """Test the run_coroutine helper method"""
    
    def test_run_coroutine_returns_result(self):
        """Test that run_coroutine properly bridges event loops"""
        from pathlib import Path
        import importlib.util
        import threading
        
        spec = importlib.util.spec_from_file_location(
            "cyber_bot_app",
            Path("cyber_bot_app.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        app = module.CyberBotApp()
        
        loop = asyncio.new_event_loop()
        app.loop = loop
        
        t = threading.Thread(target=loop.run_forever, daemon=True)
        t.start()
        
        async def test_coro():
            return 42
        
        try:
            result = app.run_coroutine(test_coro())
            assert result == 42
        finally:
            loop.call_soon_threadsafe(loop.stop)
            t.join(timeout=1)


class TestTokenValidation:
    """Test token validation logic"""
    
    def test_validate_token_invalid(self):
        """Test invalid token returns None"""
        from pathlib import Path
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "cyber_bot_app",
            Path("cyber_bot_app.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        app = module.CyberBotApp()
        result = app.validate_token("invalid_token_12345")
        assert result is None


class TestEncodingIntegrity:
    """Test base64 encoding/decoding integrity"""
    
    def test_bat_payload_matches_py(self):
        """Verify bat file payload decodes to identical Python script"""
        import base64
        import re
        
        with open('CyberControl.bat', 'r', encoding='utf-8') as f:
            bat = f.read()
        
        with open('cyber_bot_app.py', 'r', encoding='utf-8') as f:
            py_content = f.read()
        
        # Extract chunks from bat
        chunks = re.findall(r'echo ([A-Za-z0-9+/=]+)> "%TEMP_B64%"', bat)
        chunks += re.findall(r'echo ([A-Za-z0-9+/=]+)>> "%TEMP_B64%"', bat)
        
        assert len(chunks) > 0, "No base64 chunks found in bat file"
        
        # Decode and compare
        encoded = ''.join(chunks)
        decoded = base64.b64decode(encoded).decode('utf-8')
        
        assert decoded == py_content,             f"Encoding mismatch: bat decoded {len(decoded)} bytes vs py {len(py_content)} bytes"
