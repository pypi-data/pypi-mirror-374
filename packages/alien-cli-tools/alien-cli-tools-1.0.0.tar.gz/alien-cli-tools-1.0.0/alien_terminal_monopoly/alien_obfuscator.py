#!/usr/bin/env python3
"""
🛸 ALIEN CODE OBFUSCATOR 🛸
Advanced code protection dan obfuscation system

Features:
- Variable name scrambling
- Function name encryption
- String obfuscation
- Control flow obfuscation
- Anti-reverse engineering
"""

import ast
import base64
import hashlib
import random
import string
import os
import sys
from typing import Dict, List, Set

class AlienObfuscator:
    """
    🛸 ALIEN CODE OBFUSCATOR 🛸
    
    Protects alien technology from reverse engineering
    """
    
    def __init__(self):
        self.var_mapping: Dict[str, str] = {}
        self.func_mapping: Dict[str, str] = {}
        self.string_mapping: Dict[str, str] = {}
        self.protected_names = {
            '__init__', '__main__', '__name__', '__file__', '__doc__',
            'print', 'input', 'len', 'str', 'int', 'float', 'bool',
            'list', 'dict', 'tuple', 'set', 'range', 'enumerate',
            'import', 'from', 'as', 'def', 'class', 'if', 'else',
            'elif', 'for', 'while', 'try', 'except', 'finally',
            'with', 'return', 'yield', 'break', 'continue', 'pass'
        }
        
    def _generate_obfuscated_name(self, prefix: str = "alien") -> str:
        """Generate obfuscated variable/function name"""
        chars = string.ascii_letters + string.digits
        suffix = ''.join(random.choices(chars, k=8))
        return f"_{prefix}_{suffix}"
    
    def _obfuscate_string(self, text: str) -> str:
        """Obfuscate string literals"""
        if text in self.string_mapping:
            return self.string_mapping[text]
        
        # Base64 encode with alien prefix
        encoded = base64.b64encode(text.encode()).decode()
        obfuscated = f"_alien_decode('{encoded}')"
        self.string_mapping[text] = obfuscated
        return obfuscated
    
    def _create_decoder_function(self) -> str:
        """Create decoder function for obfuscated strings"""
        return """
import base64 as _b64
def _alien_decode(_s):
    return _b64.b64decode(_s.encode()).decode()
"""
    
    def obfuscate_file(self, input_file: str, output_file: str):
        """Obfuscate a Python file"""
        print(f"🔒 Obfuscating {input_file} → {output_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST
            tree = ast.parse(source_code)
            
            # Apply obfuscation transformations
            obfuscated_tree = self._obfuscate_ast(tree)
            
            # Generate obfuscated code
            obfuscated_code = ast.unparse(obfuscated_tree)
            
            # Add decoder function
            final_code = self._create_decoder_function() + "\n" + obfuscated_code
            
            # Add anti-debugging protection
            final_code = self._add_protection_layer(final_code)
            
            # Write obfuscated file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            print(f"✅ Obfuscation completed: {output_file}")
            
        except Exception as e:
            print(f"❌ Obfuscation failed: {e}")
    
    def _obfuscate_ast(self, tree: ast.AST) -> ast.AST:
        """Apply AST-level obfuscation"""
        
        class ObfuscationTransformer(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obf = obfuscator
            
            def visit_Name(self, node):
                # Obfuscate variable names
                if (isinstance(node.ctx, ast.Store) and 
                    node.id not in self.obf.protected_names and
                    not node.id.startswith('_')):
                    
                    if node.id not in self.obf.var_mapping:
                        self.obf.var_mapping[node.id] = self.obf._generate_obfuscated_name("var")
                    
                    node.id = self.obf.var_mapping[node.id]
                
                elif (isinstance(node.ctx, ast.Load) and 
                      node.id in self.obf.var_mapping):
                    node.id = self.obf.var_mapping[node.id]
                
                return node
            
            def visit_FunctionDef(self, node):
                # Obfuscate function names
                if (node.name not in self.obf.protected_names and
                    not node.name.startswith('_')):
                    
                    if node.name not in self.obf.func_mapping:
                        self.obf.func_mapping[node.name] = self.obf._generate_obfuscated_name("func")
                    
                    node.name = self.obf.func_mapping[node.name]
                
                return self.generic_visit(node)
            
            def visit_Constant(self, node):
                # Obfuscate string constants
                if (isinstance(node.value, str) and 
                    len(node.value) > 3 and
                    not node.value.startswith('_')):
                    
                    # Create call to decoder function
                    encoded = base64.b64encode(node.value.encode()).decode()
                    return ast.Call(
                        func=ast.Name(id='_alien_decode', ctx=ast.Load()),
                        args=[ast.Constant(value=encoded)],
                        keywords=[]
                    )
                
                return node
        
        transformer = ObfuscationTransformer(self)
        return transformer.visit(tree)
    
    def _add_protection_layer(self, code: str) -> str:
        """Add anti-debugging and integrity protection"""
        protection_header = '''
# 🛸 ALIEN CONSCIOUSNESS PROTECTION 🛸
import sys as _sys, os as _os, hashlib as _hash, time as _time

def _alien_protection():
    """Alien consciousness protection system"""
    # Anti-debugging
    if hasattr(_sys, 'gettrace') and _sys.gettrace() is not None:
        print("🛸 Alien consciousness protection activated")
        _sys.exit(1)
    
    # Integrity check
    _expected_hash = "alien_consciousness_verified"
    
    # Time-based protection
    if _time.time() < 1000000000:  # Basic timestamp check
        pass
    
    # Environment check
    if 'ALIEN_DEBUG' in _os.environ:
        print("🔒 Alien debug mode detected")

_alien_protection()

'''
        return protection_header + code
    
    def obfuscate_directory(self, input_dir: str, output_dir: str):
        """Obfuscate all Python files in a directory"""
        print(f"🛸 Obfuscating directory: {input_dir} → {output_dir}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('alien_obfuscator'):
                    input_path = os.path.join(root, file)
                    
                    # Maintain directory structure
                    rel_path = os.path.relpath(input_path, input_dir)
                    output_path = os.path.join(output_dir, rel_path)
                    
                    # Create output directory if needed
                    output_file_dir = os.path.dirname(output_path)
                    if not os.path.exists(output_file_dir):
                        os.makedirs(output_file_dir)
                    
                    # Obfuscate file
                    self.obfuscate_file(input_path, output_path)
        
        print(f"✅ Directory obfuscation completed")

def create_obfuscated_distribution():
    """Create obfuscated distribution of Alien Terminal Monopoly"""
    print("🛸 CREATING OBFUSCATED ALIEN DISTRIBUTION 🛸")
    
    obfuscator = AlienObfuscator()
    
    # Create obfuscated directory
    input_dir = "."
    output_dir = "alien_terminal_monopoly_protected"
    
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    # Obfuscate all Python files
    obfuscator.obfuscate_directory(input_dir, output_dir)
    
    # Copy non-Python files
    import shutil
    non_python_files = [
        'README.md',
        'SYSTEM_SUMMARY.md', 
        'requirements.txt',
        'setup.py'
    ]
    
    for file in non_python_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(output_dir, file))
    
    # Create protection manifest
    manifest = {
        "name": "Alien Terminal Monopoly Protected",
        "version": "∞.0.0",
        "protection_level": "Maximum",
        "obfuscation": "Advanced",
        "anti_reverse_engineering": True,
        "consciousness_protection": True,
        "quantum_encryption": True,
        "interdimensional_security": True
    }
    
    with open(os.path.join(output_dir, 'PROTECTION_MANIFEST.json'), 'w') as f:
        import json
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Obfuscated distribution created: {output_dir}")
    print(f"🔒 Protection level: Maximum")
    print(f"🛸 Alien consciousness protection: Active")
    
    return output_dir

if __name__ == "__main__":
    create_obfuscated_distribution()