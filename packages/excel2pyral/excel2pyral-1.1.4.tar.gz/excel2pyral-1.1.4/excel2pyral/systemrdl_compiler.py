"""
SystemRDL Compiler Wrapper

This module provides a wrapper around the SystemRDL compiler for use
in the Excel-to-PyUVM conversion pipeline.
"""

from systemrdl import RDLCompiler, RDLCompileError
from systemrdl.node import RootNode
from typing import Optional
import os

class SystemRDLCompiler:
    """
    Wrapper around SystemRDL compiler with error handling and convenience methods.
    """
    
    def __init__(self):
        """Initialize the SystemRDL compiler."""
        self.rdlc = RDLCompiler()
        self._root = None
    
    def compile(self, rdl_file: str, top_def_name: Optional[str] = None) -> RootNode:
        """
        Compile a SystemRDL file and return the elaborated root node.
        
        Args:
            rdl_file: Path to SystemRDL file to compile
            top_def_name: Name of top-level definition to elaborate (optional)
            
        Returns:
            Elaborated root node
            
        Raises:
            ValueError: If compilation fails
            FileNotFoundError: If RDL file doesn't exist
        """
        if not os.path.exists(rdl_file):
            raise FileNotFoundError(f"SystemRDL file not found: {rdl_file}")
        
        try:
            # Compile the SystemRDL source
            print(f"DEBUG: Compiling SystemRDL file: {rdl_file}")
            self.rdlc.compile_file(rdl_file)
            print("DEBUG: SystemRDL compilation successful")
            
            # Elaborate the design - like PeakRDL-UVM does
            print(f"DEBUG: Elaborating with top_def_name: {top_def_name}")
            self._root = self.rdlc.elaborate(top_def_name=top_def_name)
            
            print(f"DEBUG: Elaborated root node type: {type(self._root)}")
            
            if hasattr(self._root, 'top'):
                print(f"DEBUG: Root has top: {self._root.top}")
                if self._root.top:
                    print(f"DEBUG: Top node type: {type(self._root.top)}")
                    print(f"DEBUG: Top node name: {self._root.top.inst_name}")
                else:
                    print("DEBUG: Root.top is None")
            else:
                print("DEBUG: Root has no 'top' attribute")
            
            return self._root
            
        except RDLCompileError as e:
            error_msg = f"SystemRDL compilation failed: {e}"
            # Add more context if available
            if hasattr(e, 'src_ref') and e.src_ref:
                error_msg += f"\nFile: {e.src_ref.filename}"
                error_msg += f"\nLine: {e.src_ref.line}"
                if hasattr(e.src_ref, 'col'):
                    error_msg += f", Column: {e.src_ref.col}"
            raise ValueError(error_msg) from e
        
        except Exception as e:
            raise ValueError(f"Unexpected error during SystemRDL compilation: {e}") from e
    
    def compile_string(self, rdl_content: str, top_def_name: Optional[str] = None) -> RootNode:
        """
        Compile SystemRDL content from string and return elaborated root node.
        
        Args:
            rdl_content: SystemRDL source code as string
            top_def_name: Name of top-level definition to elaborate (optional)
            
        Returns:
            Elaborated root node
            
        Raises:
            ValueError: If compilation fails
        """
        try:
            # Compile the SystemRDL source
            print("DEBUG: Compiling SystemRDL from string")
            self.rdlc.compile_string(rdl_content, "<string>")
            print("DEBUG: SystemRDL string compilation successful")
            
            # Elaborate the design  
            print(f"DEBUG: Elaborating with top_def_name: {top_def_name}")
            self._root = self.rdlc.elaborate(top_def_name=top_def_name)
            
            print(f"DEBUG: Elaborated root node type: {type(self._root)}")
            
            return self._root
            
        except RDLCompileError as e:
            error_msg = f"SystemRDL compilation failed: {e}"
            if hasattr(e, 'src_ref') and e.src_ref:
                error_msg += f"\nLine: {e.src_ref.line}"
                if hasattr(e.src_ref, 'col'):
                    error_msg += f", Column: {e.src_ref.col}"
            raise ValueError(error_msg) from e
            
        except Exception as e:
            raise ValueError(f"Unexpected error during SystemRDL compilation: {e}") from e
    
    def get_root(self) -> Optional[RootNode]:
        """
        Get the last compiled root node.
        
        Returns:
            Root node if compilation was successful, None otherwise
        """
        return self._root
    
    def validate_syntax(self, rdl_file: str) -> bool:
        """
        Validate SystemRDL syntax without full elaboration.
        
        Args:
            rdl_file: Path to SystemRDL file
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            temp_compiler = RDLCompiler()
            temp_compiler.compile_file(rdl_file)
            return True
        except RDLCompileError:
            return False
        except Exception:
            return False
    
    def get_compilation_info(self) -> dict:
        """
        Get information about the last compilation.
        
        Returns:
            Dictionary with compilation information
        """
        info = {
            'compiled': self._root is not None,
            'top_name': None,
            'num_addrmaps': 0,
            'num_registers': 0,
            'num_fields': 0
        }
        
        if self._root and hasattr(self._root, 'top') and self._root.top:
            info['top_name'] = self._root.top.inst_name
            
            # Count elements (basic traversal)
            def count_elements(node):
                counts = {'addrmaps': 0, 'registers': 0, 'fields': 0}
                
                if hasattr(node, 'children'):
                    for child in node.children():
                        if hasattr(child, 'inst') and hasattr(child.inst, 'type_name'):
                            if child.inst.type_name == 'addrmap':
                                counts['addrmaps'] += 1
                                sub_counts = count_elements(child)
                                for key in counts:
                                    counts[key] += sub_counts[key]
                            elif child.inst.type_name == 'reg':
                                counts['registers'] += 1
                                if hasattr(child, 'fields'):
                                    counts['fields'] += len(list(child.fields()))
                
                return counts
            
            counts = count_elements(self._root.top)
            info.update({
                'num_addrmaps': counts['addrmaps'],
                'num_registers': counts['registers'], 
                'num_fields': counts['fields']
            })
        
        return info