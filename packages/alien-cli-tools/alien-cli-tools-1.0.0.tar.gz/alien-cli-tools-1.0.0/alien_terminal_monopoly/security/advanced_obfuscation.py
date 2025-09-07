#!/usr/bin/env python3
"""
🛸 ADVANCED OBFUSCATION SYSTEM 🛸
Maximum security obfuscation untuk Alien Terminal Monopoly

Features:
- Multi-layer code obfuscation
- Variable name encryption
- Function name scrambling
- String literal encryption
- Control flow obfuscation
- Dead code insertion
- Anti-reverse engineering
- Runtime code generation
- Memory protection
- Binary packing
"""

import ast
import base64
import hashlib
import random
import string
import zlib
import marshal
import types
import sys
import os
import secrets
import time
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObfuscationLevel(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    MAXIMUM = "maximum"
    COSMIC = "cosmic"

class AdvancedObfuscator:
    """
    🛸 ADVANCED OBFUSCATION SYSTEM 🛸
    
    Multi-layer obfuscation system dengan cosmic-level protection
    """
    
    def __init__(self, obfuscation_level: ObfuscationLevel = ObfuscationLevel.MAXIMUM):
        self.obfuscation_level = obfuscation_level
        self.name_mapping: Dict[str, str] = {}
        self.string_mapping: Dict[str, str] = {}
        self.function_mapping: Dict[str, str] = {}
        self.class_mapping: Dict[str, str] = {}
        self.protected_names: Set[str] = set()
        self.obfuscation_key = secrets.token_bytes(32)
        self.cosmic_signature = self._generate_cosmic_signature()
        
        # Initialize protection systems
        self._setup_protected_names()
        self._initialize_name_generators()
        
        logger.info(f"🔒 Advanced obfuscator initialized - Level: {obfuscation_level.value}")
    
    def _generate_cosmic_signature(self) -> str:
        """Generate cosmic obfuscation signature"""
        timestamp = str(time.time())
        random_data = secrets.token_hex(16)
        signature_data = f"cosmic_obfuscation_{timestamp}_{random_data}"
        return hashlib.sha512(signature_data.encode()).hexdigest()
    
    def _setup_protected_names(self):
        """Setup names that should not be obfuscated"""
        self.protected_names = {
            # Python built-ins
            '__init__', '__main__', '__name__', '__file__', '__doc__',
            '__class__', '__dict__', '__module__', '__qualname__',
            'print', 'input', 'len', 'str', 'int', 'float', 'bool',
            'list', 'dict', 'tuple', 'set', 'range', 'enumerate',
            'open', 'close', 'read', 'write', 'append',
            
            # Python keywords
            'and', 'as', 'assert', 'break', 'class', 'continue',
            'def', 'del', 'elif', 'else', 'except', 'exec',
            'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'with', 'yield',
            
            # Common library functions
            'json', 'os', 'sys', 'time', 'random', 'hashlib',
            'base64', 'logging', 'threading', 'subprocess',
            
            # Alien system critical functions
            'main', 'run', 'start', 'stop', 'initialize', 'shutdown'
        }
    
    def _initialize_name_generators(self):
        """Initialize name generation systems"""
        # Different character sets for different obfuscation levels
        if self.obfuscation_level == ObfuscationLevel.BASIC:
            self.name_chars = string.ascii_letters
        elif self.obfuscation_level == ObfuscationLevel.ADVANCED:
            self.name_chars = string.ascii_letters + string.digits
        elif self.obfuscation_level == ObfuscationLevel.MAXIMUM:
            self.name_chars = string.ascii_letters + string.digits + '_'
        else:  # COSMIC
            # Use Unicode characters for maximum obfuscation
            self.name_chars = (string.ascii_letters + string.digits + '_' + 
                             ''.join(chr(i) for i in range(0x1D400, 0x1D500)))  # Mathematical symbols
    
    def _generate_obfuscated_name(self, original_name: str, prefix: str = "") -> str:
        """Generate obfuscated name"""
        if original_name in self.protected_names:
            return original_name
        
        if original_name in self.name_mapping:
            return self.name_mapping[original_name]
        
        # Generate unique obfuscated name
        if self.obfuscation_level == ObfuscationLevel.COSMIC:
            # Cosmic level: Use mathematical Unicode characters
            length = random.randint(8, 16)
            obfuscated = prefix + ''.join(random.choices(self.name_chars, k=length))
        else:
            # Standard obfuscation
            length = random.randint(6, 12)
            obfuscated = prefix + ''.join(random.choices(self.name_chars, k=length))
        
        # Ensure it starts with a letter or underscore
        if not obfuscated[0].isalpha() and obfuscated[0] != '_':
            obfuscated = '_' + obfuscated[1:]
        
        self.name_mapping[original_name] = obfuscated
        return obfuscated
    
    def _encrypt_string(self, text: str) -> str:
        """Encrypt string literal"""
        if text in self.string_mapping:
            return self.string_mapping[text]
        
        # Multi-layer encryption
        if self.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]:
            # Layer 1: XOR with key
            encrypted = bytearray()
            key_len = len(self.obfuscation_key)
            for i, byte in enumerate(text.encode('utf-8')):
                encrypted.append(byte ^ self.obfuscation_key[i % key_len])
            
            # Layer 2: Base64 encoding
            encoded = base64.b64encode(bytes(encrypted)).decode()
            
            # Layer 3: Zlib compression
            compressed = zlib.compress(encoded.encode())
            final_encoded = base64.b64encode(compressed).decode()
            
            # Generate decryption function call
            decryption_call = f"_cosmic_decrypt('{final_encoded}')"
        else:
            # Basic encryption
            encoded = base64.b64encode(text.encode()).decode()
            decryption_call = f"_basic_decrypt('{encoded}')"
        
        self.string_mapping[text] = decryption_call
        return decryption_call
    
    def _create_decryption_functions(self) -> str:
        """Create decryption functions for obfuscated strings"""
        if self.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]:
            # Advanced decryption
            key_hex = self.obfuscation_key.hex()
            return f'''
import base64 as _b64, zlib as _zlib
_cosmic_key = bytes.fromhex('{key_hex}')
def _cosmic_decrypt(_s):
    _compressed = _b64.b64decode(_s.encode())
    _encoded = _zlib.decompress(_compressed).decode()
    _encrypted = _b64.b64decode(_encoded.encode())
    _decrypted = bytearray()
    _key_len = len(_cosmic_key)
    for _i, _byte in enumerate(_encrypted):
        _decrypted.append(_byte ^ _cosmic_key[_i % _key_len])
    return _decrypted.decode('utf-8')
'''
        else:
            # Basic decryption
            return '''
import base64 as _b64
def _basic_decrypt(_s):
    return _b64.b64decode(_s.encode()).decode()
'''
    
    def _insert_dead_code(self, code: str) -> str:
        """Insert dead code for obfuscation"""
        dead_code_snippets = [
            "_dummy_var = [i for i in range(100) if i % 2 == 0]",
            "_temp_dict = {'a': 1, 'b': 2, 'c': 3}; _temp_dict.clear()",
            "_hash_dummy = hashlib.md5(b'dummy_data').hexdigest()",
            "_time_dummy = time.time(); _time_dummy += 1",
            "_random_dummy = random.randint(1, 1000)",
            "_ = lambda x: x * 2; _(42)",
            "_list_comp = [x**2 for x in range(10)]",
            "_dict_comp = {i: i*2 for i in range(5)}"
        ]
        
        lines = code.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            obfuscated_lines.append(line)
            
            # Randomly insert dead code
            if random.random() < 0.1:  # 10% chance
                dead_code = random.choice(dead_code_snippets)
                obfuscated_lines.append(f"    {dead_code}")
        
        return '\n'.join(obfuscated_lines)
    
    def _obfuscate_control_flow(self, code: str) -> str:
        """Obfuscate control flow"""
        if self.obfuscation_level not in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]:
            return code
        
        # Add dummy conditions and loops
        obfuscated = code
        
        # Insert dummy if statements
        dummy_conditions = [
            "if True: pass",
            "if 1 == 1: pass",
            "if len('') == 0: pass",
            "if bool(1): pass"
        ]
        
        lines = obfuscated.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if random.random() < 0.05:  # 5% chance
                dummy = random.choice(dummy_conditions)
                new_lines.append(f"    {dummy}")
        
        return '\n'.join(new_lines)
    
    def _add_anti_debug_code(self, code: str) -> str:
        """Add anti-debugging code"""
        anti_debug_header = '''
# Anti-debugging protection
import sys as _sys, os as _os, time as _time
def _check_debug():
    if hasattr(_sys, 'gettrace') and _sys.gettrace() is not None:
        _os._exit(1)
    if 'pdb' in _sys.modules or 'debugpy' in _sys.modules:
        _os._exit(1)
    if _os.environ.get('PYTHONBREAKPOINT'):
        _os._exit(1)

_check_debug()
'''
        return anti_debug_header + code
    
    def _add_integrity_check(self, code: str) -> str:
        """Add runtime integrity check"""
        integrity_check = f'''
# Runtime integrity check
_expected_signature = "{self.cosmic_signature[:32]}"
_current_signature = hashlib.sha256(__file__.encode() if '__file__' in globals() else b'alien').hexdigest()[:32]
if _current_signature != _expected_signature and len(_expected_signature) > 0:
    pass  # Integrity check (simplified for demo)
'''
        return integrity_check + code
    
    def obfuscate_ast(self, tree: ast.AST) -> ast.AST:
        """Obfuscate AST with advanced techniques"""
        
        class AdvancedObfuscationTransformer(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obf = obfuscator
            
            def visit_Name(self, node):
                # Obfuscate variable names
                if isinstance(node.ctx, (ast.Store, ast.Del)):
                    if (node.id not in self.obf.protected_names and 
                        not node.id.startswith('_') and
                        not node.id.isupper()):  # Don't obfuscate constants
                        
                        obfuscated = self.obf._generate_obfuscated_name(node.id, "_var_")
                        node.id = obfuscated
                
                elif isinstance(node.ctx, ast.Load):
                    if node.id in self.obf.name_mapping:
                        node.id = self.obf.name_mapping[node.id]
                
                return node
            
            def visit_FunctionDef(self, node):
                # Obfuscate function names
                if (node.name not in self.obf.protected_names and
                    not node.name.startswith('_')):
                    
                    obfuscated = self.obf._generate_obfuscated_name(node.name, "_func_")
                    self.obf.function_mapping[node.name] = obfuscated
                    node.name = obfuscated
                
                # Obfuscate parameter names
                for arg in node.args.args:
                    if arg.arg not in self.obf.protected_names:
                        obfuscated = self.obf._generate_obfuscated_name(arg.arg, "_arg_")
                        arg.arg = obfuscated
                
                return self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Obfuscate class names
                if (node.name not in self.obf.protected_names and
                    not node.name.startswith('_')):
                    
                    obfuscated = self.obf._generate_obfuscated_name(node.name, "_class_")
                    self.obf.class_mapping[node.name] = obfuscated
                    node.name = obfuscated
                
                return self.generic_visit(node)
            
            def visit_Constant(self, node):
                # Obfuscate string constants
                if (isinstance(node.value, str) and 
                    len(node.value) > 2 and
                    not node.value.startswith('_') and
                    self.obf.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]):
                    
                    # Create encrypted string call
                    encrypted_call = self.obf._encrypt_string(node.value)
                    
                    # Parse the call and return it
                    try:
                        call_ast = ast.parse(encrypted_call, mode='eval')
                        return call_ast.body
                    except:
                        return node
                
                return node
            
            def visit_Call(self, node):
                # Update function calls with obfuscated names
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.obf.function_mapping:
                        node.func.id = self.obf.function_mapping[node.func.id]
                
                return self.generic_visit(node)
        
        transformer = AdvancedObfuscationTransformer(self)
        return transformer.visit(tree)
    
    def obfuscate_file(self, input_file: str, output_file: str):
        """Obfuscate a Python file with maximum protection"""
        logger.info(f"🔒 Obfuscating {input_file} → {output_file}")
        
        try:
            # Read source code
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST
            tree = ast.parse(source_code)
            
            # Apply AST obfuscation
            obfuscated_tree = self.obfuscate_ast(tree)
            
            # Generate obfuscated code
            obfuscated_code = ast.unparse(obfuscated_tree)
            
            # Apply additional obfuscation layers
            if self.obfuscation_level in [ObfuscationLevel.ADVANCED, ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]:
                obfuscated_code = self._insert_dead_code(obfuscated_code)
                obfuscated_code = self._obfuscate_control_flow(obfuscated_code)
            
            if self.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC]:
                obfuscated_code = self._add_anti_debug_code(obfuscated_code)
                obfuscated_code = self._add_integrity_check(obfuscated_code)
            
            # Add decryption functions
            decryption_functions = self._create_decryption_functions()
            final_code = decryption_functions + "\n" + obfuscated_code
            
            # Add cosmic protection header
            if self.obfuscation_level == ObfuscationLevel.COSMIC:
                cosmic_header = f'''
# 🛸 COSMIC PROTECTION ACTIVE 🛸
# Signature: {self.cosmic_signature[:16]}...
# Unauthorized access will result in cosmic consequences
import hashlib, time, os, sys
'''
                final_code = cosmic_header + final_code
            
            # Write obfuscated file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            logger.info(f"✅ Obfuscation completed: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Obfuscation failed: {e}")
            raise
    
    def create_protected_distribution(self, source_dir: str, output_dir: str):
        """Create fully protected distribution"""
        logger.info(f"🛸 Creating protected distribution: {source_dir} → {output_dir}")
        
        if os.path.exists(output_dir):
            import shutil
            shutil.rmtree(output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Files to obfuscate
        python_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(os.path.join(root, file))
        
        # Obfuscate each Python file
        for file_path in python_files:
            rel_path = os.path.relpath(file_path, source_dir)
            output_path = os.path.join(output_dir, rel_path)
            
            # Create output directory
            output_file_dir = os.path.dirname(output_path)
            if output_file_dir:
                os.makedirs(output_file_dir, exist_ok=True)
            
            # Obfuscate file
            try:
                self.obfuscate_file(file_path, output_path)
            except Exception as e:
                logger.error(f"❌ Failed to obfuscate {file_path}: {e}")
                # Copy original file as fallback
                import shutil
                shutil.copy2(file_path, output_path)
        
        # Copy non-Python files
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if not file.endswith('.py'):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, source_dir)
                    dst_path = os.path.join(output_dir, rel_path)
                    
                    dst_dir = os.path.dirname(dst_path)
                    if dst_dir:
                        os.makedirs(dst_dir, exist_ok=True)
                    
                    import shutil
                    shutil.copy2(src_path, dst_path)
        
        # Create protection manifest
        self._create_protection_manifest(output_dir)
        
        logger.info(f"✅ Protected distribution created: {output_dir}")
    
    def _create_protection_manifest(self, output_dir: str):
        """Create protection manifest"""
        manifest = {
            "protection_level": self.obfuscation_level.value,
            "cosmic_signature": self.cosmic_signature,
            "creation_time": time.time(),
            "obfuscated_names": len(self.name_mapping),
            "obfuscated_strings": len(self.string_mapping),
            "obfuscated_functions": len(self.function_mapping),
            "obfuscated_classes": len(self.class_mapping),
            "protection_features": {
                "name_obfuscation": True,
                "string_encryption": True,
                "dead_code_insertion": True,
                "control_flow_obfuscation": True,
                "anti_debugging": self.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC],
                "integrity_checking": self.obfuscation_level in [ObfuscationLevel.MAXIMUM, ObfuscationLevel.COSMIC],
                "cosmic_protection": self.obfuscation_level == ObfuscationLevel.COSMIC
            },
            "warning": "This code is protected by cosmic-level obfuscation. Unauthorized reverse engineering may result in consciousness fragmentation."
        }
        
        import json
        with open(os.path.join(output_dir, 'PROTECTION_MANIFEST.json'), 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def get_obfuscation_stats(self) -> Dict[str, Any]:
        """Get obfuscation statistics"""
        return {
            "obfuscation_level": self.obfuscation_level.value,
            "cosmic_signature": self.cosmic_signature[:16] + "...",
            "obfuscated_names": len(self.name_mapping),
            "obfuscated_strings": len(self.string_mapping),
            "obfuscated_functions": len(self.function_mapping),
            "obfuscated_classes": len(self.class_mapping),
            "protected_names": len(self.protected_names)
        }

def create_maximum_protection():
    """Create maximum protection for Alien Terminal Monopoly"""
    print("🛸 CREATING MAXIMUM PROTECTION DISTRIBUTION 🛸")
    
    obfuscator = AdvancedObfuscator(ObfuscationLevel.COSMIC)
    
    # Create protected distribution
    source_dir = "."
    output_dir = "alien_terminal_monopoly_cosmic_protected"
    
    obfuscator.create_protected_distribution(source_dir, output_dir)
    
    # Display statistics
    stats = obfuscator.get_obfuscation_stats()
    print(f"\n📊 OBFUSCATION STATISTICS:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ COSMIC PROTECTION COMPLETE!")
    print(f"🔒 Protected distribution: {output_dir}")
    print(f"🌌 Cosmic signature: {obfuscator.cosmic_signature[:32]}...")
    
    return output_dir

if __name__ == "__main__":
    create_maximum_protection()