"""
Excel to SystemRDL Importer

This module provides functionality to convert Excel register specifications 
into SystemRDL source code with proper hierarchy and defaults.
"""

import pandas as pd
import os
import re
from typing import Optional, Tuple, Any

class ExcelToSystemRDLImporter:
    """
    Converts Excel register specifications into SystemRDL source code.
    
    The Excel file should contain:
    - A 'Submodules' sheet with submodule hierarchy
    - A 'default' sheet with default properties (optional)  
    - One sheet per submodule containing register/field definitions
    """
    
    def parse_field_bits(self, bits: str) -> Tuple[Optional[int], Optional[int], int]:
        """
        Parse field bits from Excel format like [7:0], [3:3], or just "8".
        
        Args:
            bits: Field bits specification string
            
        Returns:
            Tuple of (msb, lsb, width)
        """
        bits = str(bits).strip()
        
        # Handle [msb:lsb] format
        m = re.match(r"\[(\d+)\s*:\s*(\d+)\]", bits)
        if m:
            msb = int(m.group(1))
            lsb = int(m.group(2))
            width = abs(msb - lsb) + 1
            return (msb, lsb, width)
        
        # Handle [n] single bit format
        m_single = re.match(r"\[(\d+)\]", bits)
        if m_single:
            bit_pos = int(m_single.group(1))
            return (bit_pos, bit_pos, 1)
        
        # Handle just a number - treat as width, calculate position later
        try:
            width = int(bits)
            return (None, None, width)
        except Exception:
            raise ValueError(f"Unrecognized field bits format: {bits}")

    def excel_to_systemrdl(
        self, 
        excel_file: str, 
        top_name: Optional[str] = None, 
        submodule_sheet: str = "Submodules",
        default_sheet: str = "default"
    ) -> str:
        """
        Convert Excel file to SystemRDL source code.
        
        Args:
            excel_file: Path to Excel file
            top_name: Name for top-level addrmap (default: from filename)
            submodule_sheet: Name of sheet containing submodule hierarchy
            default_sheet: Name of sheet containing default properties
            
        Returns:
            Complete SystemRDL source code as string
        """
        if top_name is None:
            top_name = os.path.splitext(os.path.basename(excel_file))[0]

        try:
            xls = pd.ExcelFile(excel_file)
        except Exception as e:
            raise ValueError(f"Cannot read Excel file: {e}")

        if submodule_sheet not in xls.sheet_names:
            raise ValueError(f"Excel file must have a '{submodule_sheet}' sheet for hierarchy")
        
        # Read default values (optional)
        sw_default = None
        hw_default = None
        accesswidth_default = None
        regwidth_default = None
        
        if default_sheet in xls.sheet_names:
            try:
                default_df = pd.read_excel(xls, sheet_name=default_sheet).fillna("")
                if not default_df.empty:
                    first_row = default_df.iloc[0]
                    sw_default = str(first_row.get("SW Access", "")).strip() or None
                    hw_default = str(first_row.get("HW Access", "")).strip() or None
                    accesswidth_default = str(first_row.get("Access Width", "")).strip() or None
                    regwidth_default = str(first_row.get("Reg Width", "")).strip() or None
            except Exception as e:
                raise ValueError(f"Error reading default sheet '{default_sheet}': {e}")

        # Read submodule hierarchy
        submodules_df = pd.read_excel(xls, sheet_name=submodule_sheet).fillna("")
        submodules_info = []
        for _, row in submodules_df.iterrows():
            name = str(row["Submodule Name"]).strip()
            if not name:
                continue
            instances = [inst.strip() for inst in str(row["Instances"]).split(",") if inst.strip()]
            offsets = [offset.strip() for offset in str(row["Base Addresses"]).split(",") if offset.strip()]
            if instances and offsets:
                submodules_info.append((name, instances, offsets))

        rdl_lines = []
        rdl_lines.append("// Auto-generated SystemRDL from Excel")
        rdl_lines.append(f"// Source: {os.path.basename(excel_file)}")
        rdl_lines.append("")

        # Process each submodule sheet
        for sheet in xls.sheet_names:
            if sheet in [submodule_sheet, default_sheet]:
                continue

            try:
                df = pd.read_excel(xls, sheet_name=sheet).fillna("")
            except Exception as e:
                raise ValueError(f"Error reading sheet '{sheet}': {e}")
                
            # Forward fill register name and offset if cells are empty to reduce repetition
            df['Register Name'] = df['Register Name'].replace("", pd.NA).fillna(method='ffill')
            df['Offset'] = df['Offset'].replace("", pd.NA).fillna(method='ffill')

            required_columns = ["Register Name", "Offset", "Field Name", "Field Bits"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Sheet '{sheet}' missing required columns: {missing_columns}")

            grouped = df.groupby(["Register Name", "Offset"], sort=False)

            # Start submodule addrmap
            rdl_lines.append(f"addrmap {sheet} {{")
            rdl_lines.append("")  # blank line                
            rdl_lines.append(f"    name = \"{sheet} Register File\";")                
            rdl_lines.append(f"    desc = \"Register file description for {sheet} Factory FPGA\";")                
            rdl_lines.append(f"    addressing=regalign;")                
            rdl_lines.append("")  # blank line 

            # Add default properties if any
            if accesswidth_default:
                rdl_lines.append(f"    default accesswidth = {accesswidth_default};")
            if regwidth_default:
                rdl_lines.append(f"    default regwidth = {regwidth_default};")
            if sw_default:
                rdl_lines.append(f"    default sw = {sw_default};")
            if hw_default:
                rdl_lines.append(f"    default hw = {hw_default};")

            if any([accesswidth_default, regwidth_default, sw_default, hw_default]):
                rdl_lines.append("")  # Blank line after defaults

            # Process registers
            for (reg_name, offset), group in grouped:
                if not str(reg_name).strip() or not str(offset).strip():
                    continue

                reg_name = str(reg_name).strip()
                rdl_lines.append(f"    reg {{")

                current_bit_pos = 0
                for _, field_row in group.iterrows():
                    field_name = str(field_row["Field Name"]).strip()
                    field_bits = str(field_row["Field Bits"]).strip()
                    if not field_name or not field_bits:
                        continue

                    msb, lsb, width = self.parse_field_bits(field_bits)

                    # Auto-assign positions if missing
                    if msb is None or lsb is None:
                        lsb = current_bit_pos
                        msb = current_bit_pos + width - 1
                        current_bit_pos += width

                    field_desc = str(field_row.get("Field Description", "")).strip()
                    sw_access = str(field_row.get("SW Access", "")).strip()
                    hw_access = str(field_row.get("HW Access", "")).strip()
                    reset_value = str(field_row.get("Reset Value", "")).strip()

                    rdl_lines.append("        field {")
                    rdl_lines.append(f'            name = "{field_name}";')
                    if field_desc:
                        rdl_lines.append(f'            desc = "{field_desc}";')
                    if sw_access:
                        rdl_lines.append(f"            sw = {sw_access};")
                    if hw_access:
                        rdl_lines.append(f"            hw = {hw_access};")
                    if reset_value:
                        rdl_lines.append(f"            reset = {reset_value};")

                    rdl_lines.append(f"        }} {field_name}[{msb}:{lsb}];")

                rdl_lines.append(f"    }} {reg_name} @ {offset};")
                rdl_lines.append("")  # Blank line between registers

            rdl_lines.append("};")  # Close addrmap
            rdl_lines.append("")

        # Create top-level addrmap with submodule instances
        rdl_lines.append(f"addrmap {top_name} {{")
        for name, instances, offsets in submodules_info:
            for i, offset in enumerate(offsets):
                inst_name = instances[i] if i < len(instances) else f"{name}_{i}"
                rdl_lines.append(f"    {name} {inst_name} @ {offset};")
        rdl_lines.append("};")

        return "\n".join(rdl_lines)