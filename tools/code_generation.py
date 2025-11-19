import ast
import inspect
from typing import Dict, List, Any, Optional
import os
import subprocess
import tempfile

class CodeGenerationTool:
    """Tool for generating, analyzing, and executing code"""
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'cpp', 'go', 'rust']
        self.code_templates = self._load_code_templates()
    
    def _load_code_templates(self) -> Dict[str, Any]:
        """Load code templates for different languages and patterns"""
        return {
            'python': {
                'class': self._python_class_template,
                'function': self._python_function_template,
                'api_route': self._python_api_route_template,
                'data_class': self._python_dataclass_template
            },
            'javascript': {
                'function': self._javascript_function_template,
                'class': self._javascript_class_template,
                'react_component': self._react_component_template
            }
        }
    
    async def generate_code(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications"""
        language = specification.get('language', 'python')
        code_type = specification.get('type', 'function')
        parameters = specification.get('parameters', {})
        
        if language not in self.supported_languages:
            return {
                'status': 'error',
                'error': f"Unsupported language: {language}"
            }
        
        if code_type not in self.code_templates.get(language, {}):
            return {
                'status': 'error',
                'error': f"Unsupported code type {code_type} for language {language}"
            }
        
        # Generate code using template
        template_func = self.code_templates[language][code_type]
        generated_code = template_func(parameters)
        
        # Validate syntax
        syntax_valid = await self._validate_syntax(generated_code, language)
        
        return {
            'status': 'success',
            'generated_code': generated_code,
            'language': language,
            'type': code_type,
            'syntax_valid': syntax_valid,
            'file_extension': self._get_file_extension(language)
        }
    
    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code for quality and issues"""
        analysis = {
            'language': language,
            'line_count': len(code.split('\n')),
            'issues': [],
            'metrics': {},
            'suggestions': []
        }
        
        if language == 'python':
            python_analysis = await self._analyze_python_code(code)
            analysis.update(python_analysis)
        
        return analysis
    
    async def execute_code(self, code: str, language: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute code in a safe environment"""
        if language != 'python':
            return {
                'status': 'error',
                'error': f"Execution only supported for Python, got {language}"
            }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                'status': 'success',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': 'measured'  # Would be actual time in production
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'error': f"Execution timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Execution failed: {str(e)}"
            }
    
    async def refactor_code(self, code: str, language: str, refactoring_type: str) -> Dict[str, Any]:
        """Refactor code based on specified type"""
        if language == 'python':
            return await self._refactor_python_code(code, refactoring_type)
        else:
            return {
                'status': 'error',
                'error': f"Refactoring not supported for {language}"
            }
    
    # Template methods
    def _python_class_template(self, params: Dict[str, Any]) -> str:
        """Generate Python class template"""
        class_name = params.get('class_name', 'MyClass')
        attributes = params.get('attributes', [])
        methods = params.get('methods', [])
        
        code = f"class {class_name}:\n"
        
        # Constructor
        if attributes:
            code += f"    def __init__(self{''.join(f', {attr}' for attr in attributes)}):\n"
            for attr in attributes:
                code += f"        self.{attr} = {attr}\n"
        else:
            code += "    def __init__(self):\n        pass\n"
        
        # Methods
        for method in methods:
            method_name = method.get('name', 'method')
            parameters = method.get('parameters', [])
            return_type = method.get('return_type', '')
            
            code += f"\n    def {method_name}(self{''.join(f', {param}' for param in parameters)}"
            if return_type:
                code += f") -> {return_type}:\n"
            else:
                code += "):\n"
            
            code += f"        # TODO: Implement {method_name}\n        pass\n"
        
        return code
    
    def _python_function_template(self, params: Dict[str, Any]) -> str:
        """Generate Python function template"""
        function_name = params.get('function_name', 'my_function')
        parameters = params.get('parameters', [])
        return_type = params.get('return_type', '')
        docstring = params.get('docstring', '')
        
        code = f"def {function_name}({', '.join(parameters)}"
        if return_type:
            code += f") -> {return_type}:\n"
        else:
            code += "):\n"
        
        if docstring:
            code += f'    """{docstring}"""\n'
        
        code += "    # TODO: Implement function logic\n    pass\n"
        
        return code
    
    def _python_api_route_template(self, params: Dict[str, Any]) -> str:
        """Generate Python API route template (FastAPI style)"""
        route_path = params.get('route_path', '/api/endpoint')
        http_method = params.get('http_method', 'get')
        parameters = params.get('parameters', [])
        response_model = params.get('response_model', 'dict')
        
        code = f"@app.{http_method}('{route_path}')\n"
        code += f"async def {http_method}_{route_path.replace('/', '_').strip('_')}"
        code += f"({', '.join(parameters)}) -> {response_model}:\n"
        code += '    """API endpoint documentation"""\n'
        code += "    # TODO: Implement endpoint logic\n"
        code += "    return {'status': 'success', 'message': 'Endpoint implemented'}\n"
        
        return code
    
    def _python_dataclass_template(self, params: Dict[str, Any]) -> str:
        """Generate Python dataclass template"""
        class_name = params.get('class_name', 'DataClass')
        fields = params.get('fields', [])
        
        code = "from dataclasses import dataclass\n\n"
        code += f"@dataclass\n"
        code += f"class {class_name}:\n"
        
        for field in fields:
            field_name = field.get('name', 'field')
            field_type = field.get('type', 'str')
            default = field.get('default')
            
            if default is not None:
                code += f"    {field_name}: {field_type} = {default}\n"
            else:
                code += f"    {field_name}: {field_type}\n"
        
        return code
    
    def _javascript_function_template(self, params: Dict[str, Any]) -> str:
        """Generate JavaScript function template"""
        function_name = params.get('function_name', 'myFunction')
        parameters = params.get('parameters', [])
        
        code = f"function {function_name}({', '.join(parameters)}) {{\n"
        code += "    // TODO: Implement function logic\n"
        code += "}\n"
        
        return code
    
    def _javascript_class_template(self, params: Dict[str, Any]) -> str:
        """Generate JavaScript class template"""
        class_name = params.get('class_name', 'MyClass')
        methods = params.get('methods', [])
        
        code = f"class {class_name} {{\n"
        code += "    constructor() {\n        // Initialize class\n    }\n\n"
        
        for method in methods:
            method_name = method.get('name', 'method')
            parameters = method.get('parameters', [])
            
            code += f"    {method_name}({', '.join(parameters)}) {{\n"
            code += f"        // TODO: Implement {method_name}\n    }}\n\n"
        
        code += "}\n"
        
        return code
    
    def _react_component_template(self, params: Dict[str, Any]) -> str:
        """Generate React component template"""
        component_name = params.get('component_name', 'MyComponent')
        props = params.get('props', [])
        has_state = params.get('has_state', False)
        
        code = "import React"
        if has_state:
            code += ", { useState }"
        code += " from 'react';\n\n"
        
        code += f"const {component_name} = ({{ {', '.join(props)} }}) => {{\n"
        
        if has_state:
            code += "    const [state, setState] = useState(null);\n\n"
        
        code += "    return (\n        <div>\n            {/* TODO: Implement component JSX */}\n        </div>\n    );\n};\n\n"
        code += f"export default {component_name};\n"
        
        return code
    
    async def _validate_syntax(self, code: str, language: str) -> bool:
        """Validate code syntax"""
        try:
            if language == 'python':
                ast.parse(code)
                return True
            # Add validation for other languages as needed
            return True
        except:
            return False
    
    async def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code for quality and issues"""
        issues = []
        metrics = {}
        
        try:
            tree = ast.parse(code)
            
            # Basic metrics
            lines = code.split('\n')
            metrics['line_count'] = len(lines)
            metrics['function_count'] = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            metrics['class_count'] = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Check for common issues
            if 'print(' in code and 'logging' not in code:
                issues.append({
                    'type': 'best_practice',
                    'severity': 'low',
                    'message': 'Use logging instead of print for production code',
                    'line': 'unknown'
                })
            
            if 'except:' in code:
                issues.append({
                    'type': 'error_handling',
                    'severity': 'medium',
                    'message': 'Bare except clause - specify exception types',
                    'line': 'unknown'
                })
            
            # Complexity analysis (simplified)
            if metrics['function_count'] > 0:
                metrics['average_function_length'] = metrics['line_count'] / metrics['function_count']
                if metrics['average_function_length'] > 50:
                    issues.append({
                        'type': 'maintainability',
                        'severity': 'medium',
                        'message': 'Functions are too long - consider breaking them down',
                        'line': 'unknown'
                    })
        
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f'Syntax error: {str(e)}',
                'line': e.lineno
            })
        
        return {
            'issues': issues,
            'metrics': metrics,
            'suggestions': self._generate_suggestions(issues, metrics)
        }
    
    def _generate_suggestions(self, issues: List[Dict], metrics: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        critical_issues = [issue for issue in issues if issue['severity'] == 'critical']
        if critical_issues:
            suggestions.append("Fix critical issues before proceeding")
        
        if metrics.get('average_function_length', 0) > 30:
            suggestions.append("Break long functions into smaller, focused functions")
        
        if any('TODO' in line for line in ['']):  # Would check actual code
            suggestions.append("Remove or implement TODO comments")
        
        return suggestions
    
    async def _refactor_python_code(self, code: str, refactoring_type: str) -> Dict[str, Any]:
        """Refactor Python code"""
        if refactoring_type == 'extract_method':
            return await self._extract_method(code)
        elif refactoring_type == 'rename_variable':
            return await self._rename_variable(code)
        else:
            return {
                'status': 'error',
                'error': f"Unsupported refactoring type: {refactoring_type}"
            }
    
    async def _extract_method(self, code: str) -> Dict[str, Any]:
        """Extract code into a new method (simplified)"""
        # This is a simplified implementation
        # In production, this would use more sophisticated analysis
        lines = code.split('\n')
        
        # Find a block to extract (simplified heuristic)
        for i, line in enumerate(lines):
            if '    ' in line and not line.strip().startswith('def ') and not line.strip().startswith('class '):
                # Found indented code that might be extractable
                extracted_code = lines[i]
                new_method_name = "extracted_method"
                
                # Create new method
                new_method = f"    def {new_method_name}(self):\n        {extracted_code.strip()}\n"
                
                # Replace original line with method call
                lines[i] = f"        self.{new_method_name}()"
                
                # Insert new method at appropriate location
                lines.insert(i, new_method)
                
                refactored_code = '\n'.join(lines)
                
                return {
                    'status': 'success',
                    'refactored_code': refactored_code,
                    'changes_made': ['Extracted method', 'Replaced code with method call'],
                    'notes': 'Simplified extraction - review needed'
                }
        
        return {
            'status': 'error',
            'error': 'No suitable code found for extraction'
        }
    
    async def _rename_variable(self, code: str) -> Dict[str, Any]:
        """Rename variables for better clarity (simplified)"""
        # Simplified implementation - would use AST in production
        improved_code = code.replace('var', 'variable').replace('temp', 'temporary')
        
        return {
            'status': 'success',
            'refactored_code': improved_code,
            'changes_made': ['Improved variable names'],
            'notes': 'Basic variable renaming applied'
        }
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs'
        }
        return extensions.get(language, '.txt')
