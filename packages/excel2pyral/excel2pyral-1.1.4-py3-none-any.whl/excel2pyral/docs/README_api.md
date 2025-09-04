# Excel2PyRAL API Reference

This document provides detailed API reference for all classes, methods, and functions in the excel2pyuvm package.

## Table of Contents

1. [Package Overview](#package-overview)
2. [Main Classes](#main-classes)
3. [Core Components](#core-components)
4. [Utility Functions](#utility-functions)
5. [Exception Classes](#exception-classes)
6. [Constants and Types](#constants-and-types)

## Package Overview

The excel2pyuvm package consists of several main components that work together to convert Excel register specifications into PyUVM RAL models:

```python
import excel2pyral

# Main converter class
converter = excel2pyral.ExcelToPyRALConverter()

# Individual components
importer = excel2pyral.ExcelToSystemRDLImporter()
compiler = excel2pyral.SystemRDLCompiler()
generator = excel2pyral.PyUVMRALGenerator()
```

## Main Classes

### ExcelToPyRALConverter

The primary interface for converting Excel files to PyUVM RAL models.

#### Class Definition

```python
class ExcelToPyRALConverter:
    """
    Main converter class that orchestrates the Excel → SystemRDL → PyUVM pipeline.
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """
    Initialize the converter with all necessary components.
    
    Creates instances of ExcelToSystemRDLImporter, SystemRDLCompiler, 
    and PyUVMRALGenerator for the conversion pipeline.
    """
```

#### Methods

##### convert()

```python
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
        excel_file: Path to input Excel file containing register specifications
        output: Output directory for generated files (default: "output")
        top_name: Override top-level module name (default: derived from filename)
        submodule_sheet: Name of Excel sheet containing submodule hierarchy
        default_sheet: Name of Excel sheet containing default properties
        keep_rdl: Whether to keep intermediate SystemRDL file for debugging
        package_name: Name for Python package (default: {top_name}_ral)
        use_enhanced_classes: Whether to use enhanced PyUVM classes
        
    Returns:
        Dictionary containing paths to generated files:
        {
            'excel_file': str,           # Input Excel file path
            'systemrdl_file': str,       # Generated SystemRDL file path (or "(removed)")
            'pyral_file': str,           # Generated PyUVM RAL file path
            'output': str,               # Output directory path
            'package_name': str          # Generated package name
        }
        
    Raises:
        FileNotFoundError: If input Excel file doesn't exist
        ValueError: If Excel file format is invalid
        Exception: If conversion pipeline fails at any stage
    """
```

**Example Usage:**

```python
converter = ExcelToPyRALConverter()

# Basic conversion
result = converter.convert("registers.xlsx")

# Advanced conversion with custom options
result = converter.convert(
    excel_file="chip_design.xlsx",
    output="generated/",
    top_name="my_chip",
    package_name="my_chip_ral",
    keep_rdl=True,
    use_enhanced_classes=True
)
```

## Core Components

### ExcelToSystemRDLImporter

Converts Excel register specifications to SystemRDL intermediate representation.

#### Class Definition

```python
class ExcelToSystemRDLImporter:
    """
    Converts Excel register specifications into SystemRDL format.
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """Initialize the Excel to SystemRDL importer."""
```

#### Methods

##### excel_to_systemrdl()

```python
def excel_to_systemrdl(
    self,
    excel_file: str,
    top_name: str,
    submodule_sheet: str = "Submodules",
    default_sheet: str = "default"
) -> str:
    """
    Convert Excel file to SystemRDL content.
    
    Args:
        excel_file: Path to Excel file containing register specifications
        top_name: Name for the top-level addrmap in SystemRDL
        submodule_sheet: Name of sheet containing submodule hierarchy
        default_sheet: Name of sheet containing default properties
        
    Returns:
        SystemRDL content as a string
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        KeyError: If required sheets or columns are missing
        ValueError: If register/field definitions are invalid
    """
```

##### validate_excel_file()

```python
def validate_excel_file(self, excel_file: str) -> Dict[str, Any]:
    """
    Validate Excel file format and structure.
    
    Args:
        excel_file: Path to Excel file to validate
        
    Returns:
        Validation result dictionary:
        {
            'valid': bool,              # Overall validation result
            'errors': List[str],        # List of validation errors
            'warnings': List[str],      # List of validation warnings
            'sheets_found': List[str],  # Sheets found in Excel file
            'modules_found': List[str]  # Module types found
        }
    """
```

### SystemRDLCompiler

Compiles SystemRDL specifications into an internal representation.

#### Class Definition

```python
class SystemRDLCompiler:
    """
    Wrapper around systemrdl-compiler for compiling SystemRDL specifications.
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """Initialize the SystemRDL compiler."""
```

#### Methods

##### compile()

```python
def compile(self, rdl_file: str) -> RootNode:
    """
    Compile SystemRDL file into internal representation.
    
    Args:
        rdl_file: Path to SystemRDL file to compile
        
    Returns:
        Compiled SystemRDL root node
        
    Raises:
        FileNotFoundError: If SystemRDL file doesn't exist
        SystemRDLCompilerError: If compilation fails
    """
```

##### compile_string()

```python
def compile_string(self, rdl_content: str) -> RootNode:
    """
    Compile SystemRDL content string into internal representation.
    
    Args:
        rdl_content: SystemRDL content as string
        
    Returns:
        Compiled SystemRDL root node
        
    Raises:
        SystemRDLCompilerError: If compilation fails
    """
```

### PyUVMRALGenerator

Generates Python PyUVM RAL models from compiled SystemRDL.

#### Class Definition

```python
class PyUVMRALGenerator:
    """
    Generates Python-based PyUVM RAL models from compiled SystemRDL designs.
    """
```

#### Constructor

```python
def __init__(self, **kwargs) -> None:
    """
    Initialize the PyUVM RAL generator.
    
    Args:
        **kwargs: Optional configuration parameters:
            - package_name: Default package name
            - use_enhanced_classes: Whether to use enhanced PyUVM classes
    """
```

#### Methods

##### generate()

```python
def generate(
    self,
    root_node: RootNode,
    output_file: str,
    package_name: Optional[str] = None,
    top_name: Optional[str] = None,
    use_enhanced_classes: bool = True,
    **kwargs
) -> None:
    """
    Generate PyUVM RAL model from compiled SystemRDL.
    
    Args:
        root_node: Compiled SystemRDL root node
        output_file: Path for output Python file
        package_name: Name for Python package/module (optional)
        top_name: Name for top-level RAL class (optional)
        use_enhanced_classes: Whether to use enhanced PyUVM classes
        **kwargs: Additional generation options
        
    Raises:
        ValueError: If generation fails
        FileNotFoundError: If output directory doesn't exist
    """
```

## Utility Functions

### convert_excel2pyral()

```python
def convert_excel2pyral(
    excel_file: str, 
    output_dir: str = "output", 
    **kwargs
) -> Dict[str, str]:
    """
    Convenience function for quick Excel to PyUVM conversion.
    
    Args:
        excel_file: Path to Excel file
        output_dir: Output directory
        **kwargs: Additional arguments passed to ExcelToPyRALConverter.convert()
        
    Returns:
        Dictionary with paths to generated files
        
    Example:
        result = convert_excel2pyral("registers.xlsx", "output/")
    """
```

## Exception Classes

### ExcelImportError

```python
class ExcelImportError(Exception):
    """
    Raised when Excel file import fails.
    
    Attributes:
        message: Error description
        excel_file: Path to Excel file that caused the error
        sheet_name: Name of problematic sheet (if applicable)
    """
```

### SystemRDLCompilerError

```python
class SystemRDLCompilerError(Exception):
    """
    Raised when SystemRDL compilation fails.
    
    Attributes:
        message: Error description
        rdl_content: SystemRDL content that failed to compile
        line_number: Line number where error occurred (if available)
    """
```

### PyUVMGenerationError

```python
class PyUVMGenerationError(Exception):
    """
    Raised when PyUVM RAL generation fails.
    
    Attributes:
        message: Error description
        output_file: Target output file path
        stage: Generation stage where error occurred
    """
```

## Constants and Types

### Access Types

```python
from typing import Literal

AccessType = Literal[
    "RW",   # Read/Write
    "RO",   # Read Only
    "WO",   # Write Only
    "W1C",  # Write 1 to Clear
    "W1S",  # Write 1 to Set
    "W1T"   # Write 1 to Toggle
]
```

### Field Information

```python
from typing import TypedDict

class FieldInfo(TypedDict):
    name: str           # Field name
    description: str    # Field description
    width: int          # Field width in bits
    lsb: int           # Least significant bit position
    msb: int           # Most significant bit position
    access: AccessType  # Access type
    reset: int         # Reset value
```

### Register Information

```python
class RegisterInfo(TypedDict):
    name: str                    # Register name
    description: str             # Register description
    width: int                   # Register width in bits
    offset: int                  # Address offset within module
    fields: List[FieldInfo]      # List of register fields
```

### Module Information

```python
class ModuleInfo(TypedDict):
    name: str                     # Module instance name
    type_name: str               # Module type name
    description: str             # Module description
    base_address: int            # Base address in memory map
    registers: List[RegisterInfo] # List of registers in module
```

## Generated PyUVM Model Structure

### Register Classes

The generated PyUVM model creates register classes following this pattern:

```python
class ModuleTypeRegisterName(uvm_reg):
    """Generated register class"""
    
    def __init__(self, name: str = "RegisterName"):
        super().__init__(name, width, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Field instances
        self.field_name = uvm_reg_field.type_id.create("field_name")
        # ... field configuration
    
    def build(self) -> None:
        """Build phase - configure register"""
        super().build()
```

### Block Classes

Module types become block classes:

```python
class ModuleType(uvm_reg_block):
    """Generated block class for module type"""
    
    def __init__(self, name: str = "ModuleType"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Register instances
        self.register_name = RegisterClass.type_id.create("register_name")
    
    def build_phase(self, phase: uvm_phase) -> None:
        """Build phase - create register map"""
        super().build_phase(phase)
        
        # Create and configure register map
        self.default_map = uvm_reg_map.type_id.create("default_map")
        self.default_map.configure(self, 0x0)
        
        # Add registers to map
        self.default_map.add_reg(self.register_name, offset, "RW")
```

### Top-Level Class

The top-level design becomes the main RAL class:

```python
class TopLevelName(uvm_reg_block):
    """Top-level RAL class with sub-block instances"""
    
    def __init__(self, name: str = "top_level_name"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Sub-block instances
        self.module_instance = ModuleType.type_id.create("module_instance")
    
    def build_phase(self, phase: uvm_phase) -> None:
        """Build phase - create memory map with submaps"""
        super().build_phase(phase)
        
        # Create default map
        self.default_map = uvm_reg_map.type_id.create("default_map")
        self.default_map.configure(self, 0x0)
        
        # Configure sub-blocks and add submaps
        self.module_instance.configure(self)
        self.module_instance.build_phase(phase)
        self.default_map.add_submap(self.module_instance.default_map, base_address)
```

### Builder Function

Each generated model includes a builder function:

```python
def build_ral_model() -> TopLevelName:
    """
    Build and return the top-level RAL model.
    
    Returns:
        Configured and built RAL model instance
    """
    ral = TopLevelName.type_id.create("top_level_name")
    
    # Build the model
    phase = uvm_build_phase("build")
    ral.build_phase(phase)
    
    return ral
```

## Version Information

```python
# Package version
__version__ = "1.0.0"

# Compatible SystemRDL compiler version
SYSTEMRDL_COMPILER_MIN_VERSION = "1.25.0"

# Compatible PyUVM version  
PYUVM_MIN_VERSION = "2.8.0"
```

## Usage Examples

### Complete API Usage Example

```python
from excel2pyral import (
    ExcelToPyRALConverter,
    ExcelToSystemRDLImporter,
    SystemRDLCompiler,
    PyUVMRALGenerator
)

# Method 1: High-level converter
converter = ExcelToPyRALConverter()
result = converter.convert("chip.xlsx", "output/")

# Method 2: Individual components
importer = ExcelToSystemRDLImporter()
systemrdl_content = importer.excel_to_systemrdl("chip.xlsx", "my_chip")

compiler = SystemRDLCompiler()
compiled_root = compiler.compile_string(systemrdl_content)

generator = PyUVMRALGenerator()
generator.generate(compiled_root, "my_chip_ral.py", "my_chip_ral")

# Method 3: Validation first
validation = importer.validate_excel_file("chip.xlsx")
if validation['valid']:
    result = converter.convert("chip.xlsx")
else:
    print("Validation errors:", validation['errors'])
```

For more examples and detailed usage instructions, see the User Guide.
