# excel2pyral Converter

A comprehensive tool for converting Excel register specifications into Python PyUVM Register Abstraction Layer (RAL) models via SystemRDL intermediate representation.

⚠️ **Note:**  
excel2pyral is currently **under active development**. Features and interfaces may change, and some functionalities might be incomplete or unstable.  
Please use it **carefully** and report any issues or feedback to help improve the project. 🙏


[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)](https://github.com)

## 🚀 Features

- **Excel to PyUVM RAL**: Convert Excel register specs directly to Python PyUVM RAL models
- **Proper UVM Structure**: Generates hierarchical RAL models matching industry standards  
- **SystemRDL Integration**: Uses SystemRDL as intermediate representation for accuracy
- **Submodule Support**: Handles complex hierarchical designs with multiple IP blocks
- **Field-Level Detail**: Supports register fields with access types, reset values, descriptions
- **Memory Support**: Handles both registers and memories in the same design
- **Debug Support**: Comprehensive logging and intermediate file preservation options

## 📁 Project Structure

```
excel2pyral/                      # Root project directory
├── README.md                     # This file
├── requirements.txt              # required python package list
├── pyproject.toml                # Build system and configuration for your Python project
├── excel2pyral/                  # Main Python package
│   ├── __init__.py               # Package initialization
│   ├── excel_importer.py         # Excel to SystemRDL converter
│   ├── systemrdl_compiler.py     # SystemRDL compiler wrapper
│   ├── pyuvm_generator.py        # PyUVM RAL generator
│   └── main.py                   # Main converter logic
├── docs/                         # Documentation
|   └── README_api.md             # README file for API
├── examples/                     # Example files
|   ├── mychip.rdl                # Genearted systemrdl file
|   ├── mychip.xlsx               # Input excel file to generate pyral model
|   └── mychip_ral.py             # Generate pyral model
└── setup.py                      # Package installation
```

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Excel File Format](#excel-file-format)
- [Usage Examples](#usage-examples)
- [Command Line Interface](#command-line-interface)
- [Python API](#python-api)
- [Generated PyUVM Structure](#generated-pyuvm-structure)
- [Advanced Features](#advanced-features)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

```bash
# Required dependencies
pip install systemrdl-compiler
pip install pyuvm
pip install pandas
pip install openpyxl
```

### Install Package

```bash
# Clone the repository
git clone https://github.com/SanCodex/excel2pyral.git
cd excel2pyral

# Install in development mode
pip install -e .
```

## ⚡ Quick Start

### 1. Prepare Your Excel File

Create an Excel file with register specifications:

**Sheet: "Submodules"**
| Submodule Name |  Instances  | Base Addresses |
|----------------|-------------|----------------|
| GPIO           | gpio0,gpio1 | 0x1000,0x1100  | 
| UART           | uart0,uart1 | 0x2000,0x3000  |

**Sheet: "GPIO"**
| Register Name | Offset | Width | Reset Value | Field Name | Field Bits | Field Description | SW Access | HW Access |
|---------------|--------|-------|-------------|------------|------------|-------------------|-----------|-----------|
| CRTL_REG      | 0x0    | 32    |  0x00       | ENABLE     | [0:0]      | Enable GPIO       |  rw       |  r        |
| CRTL_REG      | 0x0    | 32    |  0x00       | MODE       | [3:1]      | Mode Select       |  rw       |  r        |
| STATUS_REG    | 0x4    | 32    |  0x00       | READY      | [0:0]      | Ready flag        |  rw       |  r        |

**Sheet: "UART"**
| Register Name | Offset | Width | Reset Value | Field Name | Field Bits | Field Description | SW Access | HW Access |
|---------------|--------|-------|-------------|------------|------------|-------------------|-----------|-----------|
| RESET_REG     | 0x8    | 32    |  0x00       | PAUSE      | [0:0]      | Pause txn UART    | rw        | r         |
| RESET_REG     | 0x8    | 32    |  0x00       | START      | [3:1]      | Start txn UART    | rw        | r         |
| STOP_REG      | 0x16   | 32    |  0x00       | END        | [0:0]      | Stop txn UART     | rw        | r         |

### 2. Run Conversion

```bash
# Command line usage
pyral mychip.xlsx --keep-rdl

# Or using Python API
from excel2pyral import ExcelToPyRALConverter

converter = ExcelToPyRALConverter()
result = converter.convert("mychip.xlsx", "output/")
print(f"Generated PyUVM RAL: {result['pyuvm_file']}")
```

### 3. Use Generated PyUVM RAL

```python
# Import the generated RAL model
from output.mychip_ral import build_ral_model

# Build the RAL model in your test class
class MyTest(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ral = build_ral_model()
    
    async def run_phase(self, phase):
        # Access registers through proper hierarchy
        await self.ral.gpio0.CRTL_REG.write(0x5)
        data = await self.ral.uart0.RESET_REG.read()
        
        # Access individual fields
        await self.ral.gpio0.CRTL_REG.ENABLE.write(1)
        enable_val = await self.ral.gpio0.CRTL_REG.ENABLE.read()
        
        # Use with sequences
        reg_seq = uvm_reg_sequence.type_id.create("reg_seq")
        reg_seq.model = self.ral
        await reg_seq.start(None)
```

## 📊 Excel File Format

### Required Sheets

#### 1. **"Submodules" Sheet** (Required for hierarchical designs)
Defines the top-level module hierarchy:

| Column | Description | Example |
|--------|-------------|---------|
| Submodule Name | Name of the module type/class | GPIO, UART, SPI |
| Instances | Unique instance name | gpio0, uart_primary |
| Base Addresses | Hexadecimal base address | 0x1000, 0x2000 |

#### 2. **Module Type Sheets** (One per module type)
Define registers and fields for each module type:

| Column | Description | Example |
|--------|-------------|---------|
| Register Name | Name of the register | CONTROL_REG |
| Offset | Offset within module | 0x0, 0x4 |
| Width | Register Width | 32, 64 |
| Reset Value | Reset value (hex/decimal) | 0, 0x5A |
| Field Name | Name of the register field | ENABLE, MODE |
| Field Bits | Field bit positions | [0:0], [7:4] |
| Field Descripton | Description of field bits | Start txn UART |
| SW Access | Access type | rw |
| HW Access | Hardware access | r |

#### 3. **"default" Sheet** (Optional)
Global default properties:

| Property | Value | Description |
|----------|-------|-------------|
| regwidth | 32 | Default register width |
| accesswidth | 32 | Default access width |
| addressing | regalign | Address alignment |

## 💻 Command Line Interface

### Basic Usage

```bash
pyral [OPTIONS] EXCEL_FILE
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o` or `--output DIR` | Output directory | `output` |
| `-t` or `--top-name NAME` | Override top module name | From filename |
| `--package-name NAME` | Python package name | `{top_name}_ral` |
| `-r` or `--keep-rdl` | Keep intermediate SystemRDL file | False |
| `--submodule-sheet NAME` | Submodules sheet name | `Submodules` |
| `--default-sheet NAME` | Default properties sheet | `default` |
| `--enhanced-classes` | Use enhanced PyUVM classes | True |

### Examples

```bash
# Basic conversion
pyral registers.xlsx

# Custom output directory and keep SystemRDL
pyral chip_spec.xlsx --output-dir results/ --keep-rdl

# Custom sheet names
pyral design.xlsx --submodule-sheet "Modules" --default-sheet "Properties"

# Custom package name
pyral my_chip.xlsx --package-name custom_ral
```

## 🐍 Python API

### ExcelToPyRALConverter Class

```python
from excel2pyral import ExcelToPyRALConverter

converter = ExcelToPyRALConverter()

result = converter.convert(
    excel_file="registers.xlsx",
    output="output",
    top_name="my_chip",
    package_name="my_chip_ral",
    keep_rdl=True,
    use_enhanced_classes=True
)

print(f"Generated files: {result}")
```

### Individual Components

```python
# Use individual components
from excel2pyral import (
    ExcelToSystemRDLImporter,
    SystemRDLCompiler, 
    PyUVMRALGenerator
)

# Step 1: Excel to SystemRDL
excel_importer = ExcelToSystemRDLImporter()
systemrdl_content = excel_importer.excel_to_systemrdl(
    excel_file="registers.xlsx",
    top_name="my_chip"
)

# Step 2: Compile SystemRDL
rdl_compiler = SystemRDLCompiler()
compiled_root = rdl_compiler.compile_string(systemrdl_content)

# Step 3: Generate PyUVM RAL
ral_generator = PyUVMRALGenerator()
ral_generator.generate(
    root_node=compiled_root,
    output_file="my_chip_ral.py"
)
```

## 🏗️ Generated PyUVM Structure

The generated PyUVM RAL follows proper UVM hierarchical structure:

### Type-Based Register Classes
```python
class GpioCrtlReg(uvm_reg):
    """Register: GPIO::CRTL_REG"""
    def __init__(self, name="CRTL_REG"):
        super().__init__(name, 32, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Fields
        self.ENABLE = uvm_reg_field.type_id.create("ENABLE")
        self.MODE = uvm_reg_field.type_id.create("MODE")
```

### Type-Based Block Classes  
```python
class GPIO(uvm_reg_block):
    """Register Block: GPIO"""
    def __init__(self, name="GPIO"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Register instances
        self.CRTL_REG = GpioCrtlReg.type_id.create("CRTL_REG")
        self.STATUS_REG = GpioStatusReg.type_id.create("STATUS_REG")
    
    def build_phase(self, phase):
        # Create register map and add registers
        self.default_map = uvm_reg_map.type_id.create("default_map")
        self.default_map.add_reg(self.CRTL_REG, 0x0, "RW")
        self.default_map.add_reg(self.STATUS_REG, 0x4, "RW")
```

### Top-Level Class with Sub-Block Instances
```python
class Mychip(uvm_reg_block):
    """Top-level register block: mychip"""
    def __init__(self, name="mychip"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Sub-block instances (like SystemVerilog UVM)
        self.gpio0 = GPIO.type_id.create("gpio0")
        self.gpio1 = GPIO.type_id.create("gpio1") 
        self.uart0 = UART.type_id.create("uart0")
        self.uart1 = UART.type_id.create("uart1")
    
    def build_phase(self, phase):
        # Add submaps at proper addresses (like add_submap)
        self.default_map.add_submap(self.gpio0.default_map, 0x1000)
        self.default_map.add_submap(self.gpio1.default_map, 0x1100)
        self.default_map.add_submap(self.uart0.default_map, 0x2000) 
        self.default_map.add_submap(self.uart1.default_map, 0x3000)
```

## 🔧 Advanced Features

### Memory Support

Add memories to your module sheets:

| Memory Name | Address Offset | Size | Width | Access | Description |
|-------------|----------------|------|-------|--------|-------------|
| DATA_MEM    | 0x100         | 1024 | 32    | RW     | Data buffer |

### Array Registers

Support for register arrays (future feature):

| Register Name | Address Offset | Array Size | Field Name | Bit Range |
|---------------|----------------|------------|------------|-----------|
| CH_CFG[4]     | 0x20          | 4          | ENABLE     | [0:0]     |

### Enhanced PyUVM Classes

Enable enhanced PyUVM classes for additional features:

```python
converter.convert(
    excel_file="registers.xlsx",
    use_enhanced_classes=True  # Enables coverage, callbacks, etc.
)
```

## Best Practices

### Excel File Organization

1. **Use consistent naming:** Keep module, register, and field names consistent
2. **Group related functionality:** Put similar registers together  
3. **Document thoroughly:** Use description fields extensively
4. **Validate addresses:** Ensure no overlapping address ranges
5. **Standard bit ranges:** Use standard field sizes where possible

### Module Design

1. **Logical grouping:** Group related registers in the same module
2. **Address alignment:** Align register addresses to natural boundaries
3. **Reserved fields:** Include reserved fields for future expansion

### PyUVM Integration

1. **Register model early:** Create RAL model during build phase
2. **Use callbacks:** Implement register callbacks for monitoring
3. **Enable coverage:** Turn on register coverage for verification
4. **Sequence integration:** Use with standard UVM register sequences

### Development Workflow

1. **Start simple:** Begin with basic register definitions
2. **Test incrementally:** Test after each module addition
3. **Use version control:** Track changes to Excel files
4. **Keep intermediate files:** Use `--keep-rdl` for debugging
5. **Validate generated code:** Review generated PyUVM RAL model


## 🐛 Troubleshooting

### Common Issues

#### "Walker did not find any top-level addrmap block"
**Cause:** Missing or incorrectly formatted Submodules sheet
**Solution:** 
- Ensure Submodules sheet exists
- Check column names match exactly: "Module Type", "Instance Name", "Base Address", "Description"
- Verify sheet name is exactly "Submodules"

#### "SystemRDL compilation failed"
**Cause:** Invalid register/field definitions  
**Solution:**
- Check bit ranges are valid: `[MSB:LSB]` where MSB >= LSB
- Verify access types are supported: RW, RO, WO, etc.
- Ensure no address overlaps between registers
- Use `--keep-rdl --verbose` to inspect SystemRDL file

#### "No registers found in design"
**Cause:** Module type sheets missing or incorrectly named
**Solution:**
- Ensure each Module Type in Submodules sheet has corresponding sheet
- Check sheet names match Module Type exactly (case-sensitive)
- Verify register definitions have all required columns

#### Import errors in generated PyUVM
**Cause:** PyUVM not installed or wrong version
**Solution:**
- Install PyUVM: `pip install pyuvm`
- Check Python environment is correct
- Verify all dependencies are installed

### Debug Mode

Enable detailed debugging:

```bash
pyral registers.xlsx --keep-rdl --verbose
```

This provides:
- Step-by-step conversion progress
- Intermediate SystemRDL file for inspection
- Detailed error messages with context
- Generated file locations and sizes


### Validation Checklist

Before conversion, verify your Excel file:

- [ ] Submodules sheet exists with correct column names
- [ ] All module types have corresponding sheets
- [ ] Register definitions have all required columns
- [ ] Bit ranges are in correct format `[MSB:LSB]`
- [ ] Access types are valid (RW, RO, WO, etc.)
- [ ] Addresses are in hexadecimal format
- [ ] No overlapping address ranges
- [ ] Field names are valid identifiers
- [ ] Reset values are properly formatted


### Validation

Validate your Excel file before conversion:

```python
from excel2pyral import ExcelToSystemRDLImporter

importer = ExcelToSystemRDLImporter()
validation = importer.validate_excel_file("registers.xlsx")

if not validation['valid']:
    print("Validation errors:", validation['errors'])
```

## 📈 Performance

### File Size Guidelines

| Excel File Size | Processing Time | Memory Usage |
|------------------|-----------------|--------------|
| < 1MB           | < 5 seconds     | < 50MB       |
| 1-10MB          | 5-30 seconds    | 50-200MB     |
| > 10MB          | > 30 seconds    | > 200MB      |

### Optimization Tips

1. **Minimize sheets**: Only include necessary module types
2. **Reduce fields**: Combine related fields where possible  
3. **Use templates**: Reuse register/field definitions
4. **Batch processing**: Process multiple files in sequence

## 🤝 Contributing

### Development Setup

```bash
git clone https://github.com/SanCodex/excel2pyral.git
cd excel2pyral

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Code Style

```bash
# Format code
black excel2pyral/
isort excel2pyral/

# Lint code
flake8 excel2pyral/
mypy excel2pyral/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SystemRDL Compiler](https://github.com/SystemRDL/systemrdl-compiler) for SystemRDL support
- [PyUVM](https://github.com/pyuvm/pyuvm) for Python UVM framework
- [PeakRDL](https://github.com/SystemRDL/PeakRDL) ecosystem for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SanCodex/excel2pyral/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SanCodex/excel2pyral/discussions)

---

**⭐ If this project helped you, please consider giving it a star on GitHub!**
