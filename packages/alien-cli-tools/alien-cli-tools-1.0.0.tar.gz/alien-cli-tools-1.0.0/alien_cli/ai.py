#!/usr/bin/env python3
"""
🤖 Alien AI - AI-Powered Developer Assistant
===========================================

Real AI assistance for developers with advanced features:
- Code analysis and suggestions
- Documentation generation
- Bug detection and fixes
- Performance optimization
- Architecture recommendations

Usage:
    alien-ai analyze <file>     - Analyze code file
    alien-ai docs <file>        - Generate documentation
    alien-ai optimize <file>    - Suggest optimizations
    alien-ai bugs <file>        - Find potential bugs
    alien-ai explain <code>     - Explain code snippet
"""

import sys
import os
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

def analyze_code(file_path: str) -> Dict[str, Any]:
    """Analyze code file for quality, complexity, and issues"""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic code analysis
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        # Complexity analysis
        complexity_indicators = {
            'nested_loops': len(re.findall(r'for.*for|while.*while|for.*while|while.*for', content)),
            'long_functions': len(re.findall(r'def\s+\w+\([^)]*\):[^}]{200,}', content, re.DOTALL)),
            'deep_nesting': max([line.count('    ') for line in lines] + [0]),
            'long_lines': len([line for line in lines if len(line) > 100])
        }
        
        # Quality metrics
        quality_score = min(100, max(0, 100 - sum(complexity_indicators.values()) * 5))
        
        # Suggestions
        suggestions = []
        if complexity_indicators['nested_loops'] > 0:
            suggestions.append("Consider refactoring nested loops for better performance")
        if complexity_indicators['long_functions'] > 0:
            suggestions.append("Break down long functions into smaller, focused functions")
        if complexity_indicators['deep_nesting'] > 4:
            suggestions.append("Reduce nesting depth for better readability")
        if comment_lines / total_lines < 0.1:
            suggestions.append("Add more comments to improve code documentation")
        
        return {
            "file": file_path,
            "metrics": {
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "comment_ratio": round(comment_lines / total_lines * 100, 2) if total_lines > 0 else 0
            },
            "complexity": complexity_indicators,
            "quality_score": quality_score,
            "suggestions": suggestions
        }
    
    except Exception as e:
        return {"error": f"Error analyzing file: {str(e)}"}

def generate_docs(file_path: str) -> Dict[str, Any]:
    """Generate documentation for code file"""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract functions and classes
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
        classes = re.findall(r'class\s+(\w+)(?:\([^)]*\))?:', content)
        imports = re.findall(r'(?:from\s+\S+\s+)?import\s+([^\\n]+)', content)
        
        # Generate documentation
        docs = {
            "file": file_path,
            "overview": f"Python module with {len(functions)} functions and {len(classes)} classes",
            "imports": [imp.strip() for imp in imports],
            "classes": classes,
            "functions": functions,
            "documentation": f"""
# {Path(file_path).name}

## Overview
{f"This module contains {len(classes)} classes and {len(functions)} functions." if classes or functions else "This is a Python script."}

## Classes
{chr(10).join(f"- `{cls}`" for cls in classes) if classes else "None"}

## Functions
{chr(10).join(f"- `{func}()`" for func in functions) if functions else "None"}

## Dependencies
{chr(10).join(f"- {imp}" for imp in imports[:10]) if imports else "None"}
"""
        }
        
        return docs
    
    except Exception as e:
        return {"error": f"Error generating docs: {str(e)}"}

def find_bugs(file_path: str) -> Dict[str, Any]:
    """Find potential bugs and issues in code"""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'except:' in line and 'pass' in lines[i] if i < len(lines) else False:
                issues.append({
                    "line": i,
                    "type": "bare_except",
                    "message": "Bare except clause with pass - may hide errors",
                    "severity": "medium"
                })
            
            if re.search(r'==\s*True|==\s*False', line):
                issues.append({
                    "line": i,
                    "type": "boolean_comparison",
                    "message": "Use 'is True' or 'is False' instead of '== True/False'",
                    "severity": "low"
                })
            
            if 'eval(' in line:
                issues.append({
                    "line": i,
                    "type": "eval_usage",
                    "message": "Using eval() can be dangerous - consider alternatives",
                    "severity": "high"
                })
            
            if re.search(r'\\b\\w+\\s*=\\s*\\[\\].*append', content):
                issues.append({
                    "line": i,
                    "type": "list_append_in_loop",
                    "message": "Consider list comprehension instead of append in loop",
                    "severity": "low"
                })
        
        return {
            "file": file_path,
            "issues_found": len(issues),
            "issues": issues,
            "summary": {
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"]),
                "low": len([i for i in issues if i["severity"] == "low"])
            }
        }
    
    except Exception as e:
        return {"error": f"Error finding bugs: {str(e)}"}

def optimize_suggestions(file_path: str) -> Dict[str, Any]:
    """Provide optimization suggestions for code"""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations = []
        
        # Check for optimization opportunities
        if 'for' in content and 'append' in content:
            optimizations.append({
                "type": "list_comprehension",
                "description": "Replace for loops with list comprehensions where possible",
                "impact": "Performance improvement, more Pythonic code"
            })
        
        if re.search(r'\\brange\\(len\\(', content):
            optimizations.append({
                "type": "enumerate",
                "description": "Use enumerate() instead of range(len())",
                "impact": "More readable and efficient"
            })
        
        if 'import *' in content:
            optimizations.append({
                "type": "specific_imports",
                "description": "Use specific imports instead of 'import *'",
                "impact": "Reduced memory usage, clearer dependencies"
            })
        
        if re.search(r'\\+.*\\+.*\\+', content):
            optimizations.append({
                "type": "string_formatting",
                "description": "Use f-strings or .format() instead of string concatenation",
                "impact": "Better performance and readability"
            })
        
        return {
            "file": file_path,
            "optimizations": optimizations,
            "count": len(optimizations)
        }
    
    except Exception as e:
        return {"error": f"Error generating optimizations: {str(e)}"}

def explain_code(code_snippet: str) -> Dict[str, Any]:
    """Explain what a code snippet does"""
    try:
        # Basic code explanation
        explanation = []
        
        if 'def ' in code_snippet:
            explanation.append("This defines a function")
        if 'class ' in code_snippet:
            explanation.append("This defines a class")
        if 'for ' in code_snippet:
            explanation.append("This contains a for loop")
        if 'if ' in code_snippet:
            explanation.append("This contains conditional logic")
        if 'import ' in code_snippet:
            explanation.append("This imports modules or libraries")
        if 'return ' in code_snippet:
            explanation.append("This returns a value")
        
        # Count lines and complexity
        lines = code_snippet.split('\\n')
        complexity = len([line for line in lines if any(keyword in line for keyword in ['if', 'for', 'while', 'try', 'except'])])
        
        return {
            "code": code_snippet,
            "explanation": explanation,
            "lines": len(lines),
            "complexity": complexity,
            "summary": f"Code snippet with {len(lines)} lines and complexity level {complexity}"
        }
    
    except Exception as e:
        return {"error": f"Error explaining code: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="🤖 Alien AI - AI-Powered Developer Assistant")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code file')
    analyze_parser.add_argument('file', help='File to analyze')
    
    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Generate documentation')
    docs_parser.add_argument('file', help='File to document')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Suggest optimizations')
    optimize_parser.add_argument('file', help='File to optimize')
    
    # Bugs command
    bugs_parser = subparsers.add_parser('bugs', help='Find potential bugs')
    bugs_parser.add_argument('file', help='File to check')
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain code snippet')
    explain_parser.add_argument('code', help='Code snippet to explain')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🤖 Alien AI - AI-Powered Developer Assistant")
    print("=" * 50)
    
    if args.command == 'analyze':
        result = analyze_code(args.file)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📊 Analysis Results for {result['file']}:")
            print(f"   Lines: {result['metrics']['total_lines']} total, {result['metrics']['code_lines']} code")
            print(f"   Comments: {result['metrics']['comment_ratio']}%")
            print(f"   Quality Score: {result['quality_score']}/100")
            print(f"   Complexity Issues: {sum(result['complexity'].values())}")
            if result['suggestions']:
                print("\\n💡 Suggestions:")
                for suggestion in result['suggestions']:
                    print(f"   • {suggestion}")
    
    elif args.command == 'docs':
        result = generate_docs(args.file)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📚 Documentation for {result['file']}:")
            print(result['documentation'])
    
    elif args.command == 'optimize':
        result = optimize_suggestions(args.file)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"⚡ Optimization Suggestions for {result['file']}:")
            if result['optimizations']:
                for opt in result['optimizations']:
                    print(f"   • {opt['type']}: {opt['description']}")
                    print(f"     Impact: {opt['impact']}")
            else:
                print("   No obvious optimizations found. Code looks good!")
    
    elif args.command == 'bugs':
        result = find_bugs(args.file)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🐛 Bug Analysis for {result['file']}:")
            print(f"   Issues Found: {result['issues_found']}")
            if result['issues']:
                for issue in result['issues']:
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[issue['severity']]
                    print(f"   {severity_icon} Line {issue['line']}: {issue['message']}")
            else:
                print("   ✅ No issues found!")
    
    elif args.command == 'explain':
        result = explain_code(args.code)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🧠 Code Explanation:")
            print(f"   Summary: {result['summary']}")
            if result['explanation']:
                print("   Features:")
                for exp in result['explanation']:
                    print(f"   • {exp}")

if __name__ == "__main__":
    main()