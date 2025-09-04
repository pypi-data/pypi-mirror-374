"""
Excel-to-PyUVM: Convert Excel register specifications to PyUVM RAL models

This package provides a complete end-to-end solution for converting Excel 
register specifications into PyUVM Register Abstraction Layer (RAL) models
via SystemRDL intermediate representation.

Main Classes:
- ExcelToPyRALConverter: Main converter class
- ExcelToSystemRDLImporter: Excel to SystemRDL conversion
- SystemRDLCompiler: SystemRDL compilation wrapper  
- PyUVMRALGenerator: PyUVM RAL model generation (Python-based)

Example usage:
    from excel2pyral import ExcelToPyRALConverter
    
    converter = ExcelToPyRALConverter()
    result = converter.convert("registers.xlsx", "output/")
    print(f"Generated: {result}")
"""

__version__ = "1.1.4"
__author__ = "Sanjay Singh"
__email__ = "your.email@example.com"

from .excel_importer import ExcelToSystemRDLImporter
from .systemrdl_compiler import SystemRDLCompiler
from .pyuvm_generator import PyUVMRALGenerator

import os
import tempfile
import shutil
from typing import Dict, Optional

class ExcelToPyRALConverter:
    """
    Main converter class that orchestrates the Excel → SystemRDL → PyUVM pipeline.
    
    This class provides the high-level interface for converting Excel register 
    specifications into Python-based PyUVM RAL models.
    """
    
    def __init__(self):
        """Initialize the converter with all necessary components."""
        self.excel_importer = ExcelToSystemRDLImporter()
        self.rdl_compiler = SystemRDLCompiler()
        self.uvm_generator = PyUVMRALGenerator()
    
    def convert(
        self, 
        excel_file: str, 
        output: str = "output",
        top_name: Optional[str] = None,
        submodule_sheet: str = "Submodules",
        default_sheet: str = "default",
        keep_rdl: bool = False,
        package_name: Optional[str] = None,
        use_enhanced_classes: bool = True
    ) -> Dict[str, str]:
        """
        Convert Excel file to PyUVM RAL model.
        
        Args:
            excel_file: Path to input Excel file
            output: Output directory for generated files
            top_name: Override top-level module name (default: from filename)
            submodule_sheet: Name of sheet containing submodule hierarchy
            default_sheet: Name of sheet containing default properties  
            keep_rdl: Whether to keep intermediate SystemRDL file
            package_name: Name for Python package (default: from filename)
            use_enhanced_classes: Whether to use enhanced PyUVM classes
            
        Returns:
            Dictionary with paths to generated files
        """
        
        # Create output directory
        os.makedirs(output, exist_ok=True)
        
        # Derive names if not provided
        if not top_name:
            top_name = os.path.splitext(os.path.basename(excel_file))[0]
        if not package_name:
            package_name = f"{top_name}_ral"
        
        print(f"🔄 Converting {excel_file} to PyUVM RAL model...")
        
        # Step 1: Excel → SystemRDL
        print("📊 Step 1: Converting Excel to SystemRDL...")
        systemrdl_content = self.excel_importer.excel_to_systemrdl(
            excel_file=excel_file,
            top_name=top_name,
            submodule_sheet=submodule_sheet,
            default_sheet=default_sheet
        )
        
        rdl_file = os.path.join(output, f"{top_name}.rdl")
        with open(rdl_file, 'w', encoding='utf-8') as f:
            f.write(systemrdl_content)
        print(f"✅ SystemRDL generated: {rdl_file}")
        
        # Step 2: Compile SystemRDL
        print("⚙️ Step 2: Compiling SystemRDL...")
        compiled_root = self.rdl_compiler.compile(rdl_file)
        print("✅ SystemRDL compiled successfully")
        
        # Step 3: Generate PyUVM RAL (Python-based)
        print("🎯 Step 3: Generating PyUVM RAL model (Python)...")
        pyuvm_file = os.path.join(output, f"{package_name}.py")
        self.uvm_generator.generate(
            root_node=compiled_root,
            output_file=pyuvm_file,
            package_name=package_name,
            use_enhanced_classes=use_enhanced_classes
        )
        print(f"✅ PyUVM RAL generated: {pyuvm_file}")
        
        result = {
            'excel_file': excel_file,
            'systemrdl_file': rdl_file,
            'pyuvm_file': pyuvm_file,
            'output': output
        }
        
        # Cleanup intermediate file if requested
        if not keep_rdl:
            try:
                os.remove(rdl_file)
                result['systemrdl_file'] = "(removed)"
            except Exception:
                pass  # Keep file if removal fails
        
        print(f"🎉 Conversion complete! Files generated in: {output}")
        return result

# Convenience function for quick conversion
def convert_excel2pyral(excel_file: str, output: str = "output", **kwargs) -> Dict[str, str]:
    """
    Convenience function for quick Excel to PyUVM conversion.
    
    Args:
        excel_file: Path to Excel file
        output: Output directory
        **kwargs: Additional arguments passed to ExcelToPyRALConverter.convert()
        
    Returns:
        Dictionary with paths to generated files
    """
    converter = ExcelToPyRALConverter()
    return converter.convert(excel_file, output, **kwargs)

__all__ = [
    'ExcelToPyRALConverter',
    'ExcelToSystemRDLImporter', 
    'SystemRDLCompiler',
    'PyUVMRALGenerator',
    'convert_excel2pyral'
]
