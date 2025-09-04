"""
PyUVM RAL Generator - Fixed to Follow Proper UVM Structure

This module generates PyUVM Register Abstraction Layer (RAL) models in Python
that follow the same hierarchical structure as industry-standard SystemVerilog UVM RAL models.
"""

from systemrdl.node import RootNode, AddrmapNode, RegNode, FieldNode, RegfileNode, MemNode
from systemrdl import RDLWalker, RDLListener
from systemrdl.rdltypes import AccessType
from typing import Optional, Dict, Any, List
import os
import re
from datetime import datetime

class PyUVMRALGenerator:
    """
    Generates Python-based PyUVM RAL models from compiled SystemRDL designs.
    
    This creates Python classes using the PyUVM framework that follow
    the same hierarchical structure as SystemVerilog UVM RAL models.
    """
    
    def __init__(self, **kwargs):
        """Initialize the PyUVM RAL generator."""
        self.user_template_dir = kwargs.get('user_template_dir', None)
        self.package_name = kwargs.get('package_name', 'generated_ral')
        self.use_enhanced_classes = kwargs.get('use_enhanced_classes', True)
        self.output_file = None
    
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
            
        Raises:
            ValueError: If generation fails
            FileNotFoundError: If output directory doesn't exist
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_file))
            if output_dir and not os.path.exists(output_dir):
                raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
            
            # Handle the node type similar to PeakRDL-UVM
            node = root_node
            
            # If it is the root node, skip to top addrmap
            if isinstance(node, RootNode):
                if not hasattr(node, 'top') or node.top is None:
                    raise ValueError("Root node does not contain a top-level addrmap")
                node = node.top
            
            if not isinstance(node, AddrmapNode):
                raise ValueError(f"Expected AddrmapNode, got {type(node)}")
            
            print(f"DEBUG: Working with top node: {node.inst_name} (type: {type(node)})")
            
            # Set configuration
            self.output_file = output_file
            self.use_enhanced_classes = use_enhanced_classes
            
            # Derive names if not provided
            if not package_name:
                package_name = f"{node.inst_name}_ral"
            if not top_name:
                top_name = node.inst_name
                
            self.package_name = package_name
            
            # Walk the SystemRDL tree and collect register information - FIXED APPROACH
            walker_listener = PyUVMRALWalker(node)
            
            # Use RDLWalker to walk the tree with the listener
            RDLWalker(unroll=True, skip_not_present=False).walk(node, walker_listener)
            
            # Debug: Check what the walker found
            print(f"DEBUG: Found {len(walker_listener.register_classes)} register classes")
            print(f"DEBUG: Found {len(walker_listener.block_classes)} block classes") 
            print(f"DEBUG: Top class: {walker_listener.top_class is not None}")
            
            # Validate walker results
            if walker_listener.top_class is None:
                raise ValueError("Walker did not find top-level addrmap block")
            
            if not walker_listener.register_classes:
                raise ValueError("Walker did not find any register classes")
            
            # Generate the Python RAL model with proper UVM structure
            with open(output_file, 'w', encoding='utf-8') as f:
                self._generate_file_header(f)
                self._generate_imports(f)
                self._generate_register_classes(f, walker_listener.register_classes)
                self._generate_block_classes(f, walker_listener.block_classes)
                self._generate_top_level_class(f, walker_listener.top_class, node.inst_name)
                self._generate_builder_function(f, walker_listener.top_class, node.inst_name)
            
            print(f"✅ PyUVM RAL model generated: {output_file}")
            
        except Exception as e:
            raise ValueError(f"PyUVM RAL generation failed: {e}") from e
    
    def _generate_file_header(self, f):
        """Generate file header with documentation"""
        f.write(f'''"""
PyUVM Register Abstraction Layer Model

Auto-generated from SystemRDL specification using excel2pyral converter

Package: {self.package_name}
Generated: {self._get_timestamp()}

This file contains Python-based PyUVM RAL classes that follow proper UVM structure
for use in Python verification environments using the PyUVM framework.

Usage:
    from {os.path.splitext(os.path.basename(self.output_file))[0]} import build_ral_model
    
    ral = build_ral_model()
    # Use ral in your PyUVM testbench
"""

''')

    def _generate_imports(self, f):
        """Generate necessary imports"""
        if self.use_enhanced_classes:
            f.write('''from pyuvm import *
from typing import Optional, Dict, Any, List
import asyncio

# Enhanced UVM classes (if available)
try:
    from uvm_reg_enhanced import uvm_reg
    from uvm_reg_map_enhanced import uvm_reg_map  
    from uvm_reg_coverage import enable_register_coverage, enable_block_coverage
    from uvm_mem import uvm_mem
    ENHANCED_CLASSES_AVAILABLE = True
except ImportError:
    # Fall back to standard PyUVM classes
    ENHANCED_CLASSES_AVAILABLE = False
    print("Warning: Enhanced UVM classes not available, using standard PyUVM")

''')
        else:
            f.write('''from pyuvm import *
from typing import Optional, Dict, Any, List
import asyncio

ENHANCED_CLASSES_AVAILABLE = False

''')

    def _generate_register_classes(self, f, register_classes: Dict[str, Any]):
        """Generate register classes following UVM structure"""
        f.write('''# ============================================================================
# Register Classes (Type-Based)
# ============================================================================

''')
        
        for class_name, reg_info in register_classes.items():
            type_name = reg_info['type_name']
            width = reg_info.get('width', 32)
            
            f.write(f'''class {class_name}(uvm_reg):
    """Register: {type_name}"""
    
    def __init__(self, name="{type_name}"):
        super().__init__(name, {width}, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Create fields
''')
            
            # Generate field declarations and configurations
            for field_info in reg_info.get('fields', []):
                field_name = field_info['name']
                field_width = field_info['width']
                field_lsb = field_info['lsb']
                field_access = field_info['access']
                field_reset = field_info.get('reset', 0)
                field_desc = field_info.get('description', '')
                
                f.write(f'''        self.{field_name} = uvm_reg_field.type_id.create("{field_name}")
        self.{field_name}.configure(
            parent=self,
            size={field_width},
            lsb={field_lsb},
            access="{field_access}",
            has_reset=True,
            reset_value=0x{field_reset:X},
            has_coverage=uvm_cvr_t.UVM_CVR_ALL
        )
        # {field_desc}
        
''')
            
            f.write(f'''    def build(self):
        """Build phase - configure register"""
        super().build()
        # Additional register-specific configuration can be added here
        pass

''')

    def _generate_block_classes(self, f, block_classes: Dict[str, Any]):
        """Generate register block classes (type-based, not instances)"""
        f.write('''# ============================================================================
# Register Block Classes (Type-Based)
# ============================================================================

''')
        
        for class_name, block_info in block_classes.items():
            type_name = block_info['type_name']
            description = block_info.get('description', f'Register Block {type_name}')
            
            f.write(f'''class {class_name}(uvm_reg_block):
    """Register Block: {description}"""
    
    def __init__(self, name="{type_name}"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Create register instances
''')
            
            # Create register instances
            for reg_info in block_info.get('registers', []):
                reg_name = reg_info['name']
                reg_class = reg_info['class_name']
                f.write(f'''        self.{reg_name} = {reg_class}.type_id.create("{reg_name}")
''')
            
            # Create memories if any
            for mem_info in block_info.get('memories', []):
                mem_name = mem_info['name']
                mem_size = mem_info['size']
                mem_width = mem_info['width']
                f.write(f'''        self.{mem_name} = uvm_mem.type_id.create("{mem_name}")
        self.{mem_name}.configure(
            parent=self,
            size={mem_size},
            n_bits={mem_width},
            access="RW"
        )
''')
            
            f.write(f'''
    def build_phase(self, phase):
        """Build phase - create register map and configure registers"""
        super().build_phase(phase)
        
        # Create default map
        self.default_map = uvm_reg_map.type_id.create("default_map") if ENHANCED_CLASSES_AVAILABLE else create_reg_map("default_map")
        self.default_map.configure(self, 0x0)
        
        # Configure and add registers to map
''')
            
            # Configure registers and add to map
            for reg_info in block_info.get('registers', []):
                reg_name = reg_info['name']
                offset = reg_info.get('offset', 0)
                f.write(f'''        self.{reg_name}.configure(self)
        self.{reg_name}.build()
        self.default_map.add_reg(self.{reg_name}, 0x{offset:X}, "RW")
        
''')
            
            # Add memories to map
            for mem_info in block_info.get('memories', []):
                mem_name = mem_info['name']
                offset = mem_info.get('offset', 0)
                f.write(f'''        self.default_map.add_mem(self.{mem_name}, 0x{offset:X}, "RW")
''')
            
            f.write(f'''        
        # Lock the model
        self.lock_model()
        
    def get_registers(self) -> List[uvm_reg]:
        """Get all registers in this block"""
        registers = []
''')
            
            for reg_info in block_info.get('registers', []):
                reg_name = reg_info['name']
                f.write(f'''        registers.append(self.{reg_name})
''')
            
            f.write(f'''        return registers

''')

    def _generate_top_level_class(self, f, top_class_info: Dict[str, Any], inst_name: str):
        """Generate top-level class with sub-block instances (following UVM structure)"""
        class_name = self._to_class_name(top_class_info['name'])
        type_name = top_class_info['type_name']
        
        f.write(f'''# ============================================================================
# Top-Level RAL Class (Contains Sub-Block Instances)
# ============================================================================

class {class_name}(uvm_reg_block):
    """Top-level register block: {type_name}"""
    
    def __init__(self, name="{inst_name}"):
        super().__init__(name, has_coverage=uvm_cvr_t.UVM_CVR_ALL)
        
        # Create sub-block instances (like SystemVerilog UVM structure)
''')
        
        # Create sub-block instances
        for sub_block_info in top_class_info.get('sub_blocks', []):
            sub_block_name = sub_block_info['name']
            sub_block_class = sub_block_info['class_name']
            f.write(f'''        self.{sub_block_name} = {sub_block_class}.type_id.create("{sub_block_name}")
''')

        f.write(f'''
    def build_phase(self, phase):
        """Build phase - create register map and configure sub-blocks"""
        super().build_phase(phase)
        
        # Create default map
        self.default_map = uvm_reg_map.type_id.create("default_map") if ENHANCED_CLASSES_AVAILABLE else create_reg_map("default_map")
        self.default_map.configure(self, 0x0)
        
        # Configure and add sub-blocks to map (equivalent to add_submap)
''')
        
        # Configure sub-blocks and add to map
        for sub_block_info in top_class_info.get('sub_blocks', []):
            sub_block_name = sub_block_info['name']
            offset = sub_block_info.get('offset', 0)
            
            f.write(f'''        self.{sub_block_name}.configure(self)
        self.{sub_block_name}.build_phase(phase)
        # Add submap at base address 0x{offset:X} (like SystemVerilog add_submap)
        self.default_map.add_submap(self.{sub_block_name}.default_map, 0x{offset:X})
        
''')
        
        f.write(f'''        
        # Lock the model
        self.lock_model()
        
    def get_all_registers(self) -> List[uvm_reg]:
        """Get all registers from all sub-blocks"""
        all_registers = []
''')
        
        for sub_block_info in top_class_info.get('sub_blocks', []):
            sub_block_name = sub_block_info['name']
            f.write(f'''        all_registers.extend(self.{sub_block_name}.get_registers())
''')
        
        f.write(f'''        return all_registers

''')

    def _generate_builder_function(self, f, top_class_info: Dict[str, Any], inst_name: str):
        """Generate top-level build function"""
        top_class = self._to_class_name(top_class_info['name'])
        
        f.write(f'''# ============================================================================
# RAL Model Builder Functions
# ============================================================================

def build_ral_model():
    """
    Build and return the top-level RAL model
    
    Returns:
        {top_class}: The top-level register block instance
    """
    ral = {top_class}.type_id.create("{inst_name}")
    
    # Build the model
    phase = uvm_build_phase("build")
    ral.build_phase(phase)
    
    # Enable coverage if enhanced classes are available
    if ENHANCED_CLASSES_AVAILABLE:
        try:
            enable_block_coverage(ral)
        except:
            pass  # Coverage enhancement not available
    
    return ral

def get_ral_model():
    """Legacy function name for compatibility"""
    return build_ral_model()

def create_reg_map(name: str):
    """Helper function to create register map when enhanced classes not available"""
    # Fallback implementation
    class BasicRegMap:
        def __init__(self, name):
            self.name = name
            self._registers = []
            self._submaps = []
            
        def configure(self, parent, base_addr):
            self.parent = parent
            self.base_addr = base_addr
            
        def add_reg(self, reg, addr, access):
            self._registers.append((reg, addr, access))
            
        def add_submap(self, submap, addr):
            """Add submap at specified address (like SystemVerilog add_submap)"""
            self._submaps.append((submap, addr))
            
        def add_mem(self, mem, addr, access):
            pass  # Basic implementation
            
    return BasicRegMap(name)

# ============================================================================
# Usage Example and Testing
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("Building RAL model...")
    model = build_ral_model()
    
    all_registers = model.get_all_registers()
    print(f"Generated RAL model with {{len(all_registers)}} total registers:")
    
    # Show hierarchy like SystemVerilog UVM
    print("\\nRAL Hierarchy:")
''')
        
        # Show the hierarchy structure
        for sub_block_info in top_class_info.get('sub_blocks', []):
            sub_block_name = sub_block_info['name']
            sub_block_class = sub_block_info['class_name']
            offset = sub_block_info.get('offset', 0)
            f.write(f'''    print(f"  {inst_name}.{sub_block_name} ({sub_block_class}) @ 0x{{0x{offset:X}:X}}")
''')
        
        f.write(f'''    
    print("\\nRAL model ready for use in PyUVM testbench!")
    
    # Example of how to use in a test (following UVM structure)
    print("\\nExample usage in test:")
    print("  ral = build_ral_model()")
''')
        
        # Show usage examples
        if top_class_info.get('sub_blocks'):
            first_sub = top_class_info['sub_blocks'][0]
            sub_name = first_sub['name']
            f.write(f'''    print("  await ral.{sub_name}.some_register.write(0x1234)")
    print("  value = await ral.{sub_name}.some_register.read()")
''')

    def _to_class_name(self, name: str) -> str:
        """Convert SystemRDL name to Python class name"""
        # Remove invalid characters and convert to CamelCase
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        parts = clean_name.split('_')
        return ''.join(part.capitalize() for part in parts if part)

    def _get_timestamp(self) -> str:
        """Get current timestamp for header"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PyUVMRALWalker(RDLListener):
    """
    Walker listener class to traverse SystemRDL tree and collect register information
    following proper UVM hierarchical structure.
    """
    
    def __init__(self, top_node: AddrmapNode):
        super().__init__()
        self.top_node = top_node
        self.register_classes = {}  # Type-based register classes
        self.block_classes = {}     # Type-based block classes
        self.top_class = None       # Top-level class info
        self.current_block_stack = []
        self.seen_types = set()

    def enter_Addrmap(self, node: AddrmapNode):
        """Enter an address map"""
        print(f"DEBUG: Entering addrmap: {node.inst_name} (type: {node.type_name})")
        
        type_name = node.type_name or node.inst_name
        class_name = self._to_class_name(type_name)
        
        block_info = {
            'name': node.inst_name,
            'type_name': type_name,
            'class_name': class_name,
            'description': node.get_property('desc', default=''),
            'registers': [],
            'memories': [],
            'sub_blocks': [],
            'base_address': node.absolute_address,
            'offset': node.address_offset if hasattr(node, 'address_offset') else 0
        }
        
        self.current_block_stack.append(block_info)
        
        # If this is the top node, store it separately
        if node == self.top_node:
            self.top_class = block_info
            print(f"DEBUG: Set as top-level class: {node.inst_name}")
        
        return None

    def exit_Addrmap(self, node: AddrmapNode):
        """Exit an address map"""
        print(f"DEBUG: Exiting addrmap: {node.inst_name}")
        
        if not self.current_block_stack:
            return None
            
        current_block = self.current_block_stack.pop()
        type_name = current_block['type_name']
        
        # If this is not the top node, add it as a block class
        if node != self.top_node and type_name not in self.seen_types:
            self.block_classes[type_name] = current_block.copy()
            self.seen_types.add(type_name)
            print(f"DEBUG: Added block class '{type_name}' with {len(current_block['registers'])} registers")
        
        # If there's a parent block (top-level), add this as a sub-block
        if len(self.current_block_stack) > 0 and node != self.top_node:
            parent_block = self.current_block_stack[-1]
            if parent_block == self.top_class:  # Only add to top-level
                sub_block_info = {
                    'name': current_block['name'],
                    'type_name': current_block['type_name'],
                    'class_name': current_block['class_name'],
                    'offset': current_block['base_address']
                }
                parent_block['sub_blocks'].append(sub_block_info)
                print(f"DEBUG: Added '{current_block['name']}' as sub-block to top-level")
        
        return None

    def enter_Reg(self, node: RegNode):
        """Enter a register"""
        print(f"DEBUG: Entering register: {node.inst_name} (type: {node.type_name})")
        
        if not self.current_block_stack:
            return None
            
        current_block = self.current_block_stack[-1]
        parent_type = current_block['type_name']
        reg_type = node.type_name or node.inst_name
        
        # Generate class name like SystemVerilog UVM: PARENT__REGISTER
        class_name = f"{parent_type}__{reg_type}".replace(' ', '_')
        class_name = self._to_class_name(class_name)
        
        # Collect field information
        fields = []
        for field_node in node.fields():
            field_info = {
                'name': field_node.inst_name,
                'description': field_node.get_property('desc', default=''),
                'width': field_node.width,
                'lsb': field_node.lsb,
                'msb': field_node.msb,
                'access': self._get_access_str(field_node),
                'reset': field_node.get_property('reset', default=0)
            }
            fields.append(field_info)
        
        # Create register class if not seen before
        if class_name not in self.register_classes:
            reg_class_info = {
                'name': reg_type,
                'type_name': f"{parent_type}::{reg_type}",
                'class_name': class_name,
                'description': node.get_property('desc', default=''),
                'width': node.get_property('regwidth'),
                'fields': fields
            }
            self.register_classes[class_name] = reg_class_info
            print(f"DEBUG: Added register class '{class_name}'")
        
        # Add register instance to current block
        reg_instance_info = {
            'name': node.inst_name,
            'type_name': reg_type,
            'class_name': class_name,
            'offset': node.address_offset,
            'absolute_address': node.absolute_address
        }
        current_block['registers'].append(reg_instance_info)
        
        return None

    def enter_Mem(self, node: MemNode):
        """Enter a memory"""
        print(f"DEBUG: Entering memory: {node.inst_name}")
        
        if not self.current_block_stack:
            return None
            
        current_block = self.current_block_stack[-1]
        
        mem_info = {
            'name': node.inst_name,
            'description': node.get_property('desc', default=''),
            'size': node.size,
            'width': node.get_property('memwidth'),
            'offset': node.address_offset,
            'absolute_address': node.absolute_address
        }
        
        current_block['memories'].append(mem_info)
        return None

    def _get_access_str(self, node) -> str:
        """Convert SystemRDL access to string"""
        access_map = {
            AccessType.r: "RO",
            AccessType.w: "WO", 
            AccessType.rw: "RW",
            AccessType.w1: "W1",
            AccessType.rw1: "RW1"
        }
        
        access = node.get_property('sw', default=None)
        return access_map.get(access, "RW")
    
    def _to_class_name(self, name: str) -> str:
        """Convert SystemRDL name to Python class name"""
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        parts = clean_name.split('_')
        return ''.join(part.capitalize() for part in parts if part)
