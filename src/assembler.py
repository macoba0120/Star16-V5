class Assembler:
    def __init__(self):
        self.registers = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'X': 4, 'Y': 5, 'Z': 6, 'SP': 7,
            'MP1': 8, 'MP2': 9, 'MP3': 10, 'MP4': 11,
            'E': 12, 'F': 13, 'G': 14, 'H': 15
        }
        
        self.conditions = {
            'LT': 0b100, 'EQ': 0b010, 'GT': 0b001,
            'LE': 0b110, 'GE': 0b011, 'NE': 0b101, 'AL': 0b111
        }
        
        self.opcodes = {
            # Data manipulation
            'MOV': 0x00, 'STR': 0x01, 'PSH': 0x02, 'POP': 0x03, 'SWP': 0x04,
            # Math
            'ADD': 0x10, 'SUB': 0x11, 'MUL': 0x12, 'DIV': 0x13,
            'AND': 0x14, 'OR': 0x15, 'XOR': 0x16, 'NOT': 0x17,
            'SHL': 0x18, 'SLR': 0x19, 'SAR': 0x1A, 'ROL': 0x1B, 'ROR': 0x1C,
            'INC': 0x1D, 'DEC': 0x1E,
            # Flow control
            'JMP': 0x20, 'JCR': 0x21, 'JSR': 0x22, 'CMP': 0x23, 'RET': 0x24, 
            'HLT': 0x25, 'NOP': 0x26, 'JCF': 0x27,
            # System
            'INT': 0x30, 'RTI': 0x31, 'STI': 0x32, 'CLI': 0x33,
        }
        
        self.labels = {}
        self.address = 0
    
    def assemble(self, source_code):
        """Assemble source code to machine code"""
        lines = self.preprocess(source_code)
        machine_code = []
        
        # First pass: collect labels
        self.address = 0
        for line in lines:
            if line.endswith(':'):
                # Label definition
                label = line[:-1].strip()
                self.labels[label] = self.address
            elif line.strip():
                # Instruction
                self.address += 1
        
        # Second pass: generate machine code
        self.address = 0
        for line in lines:
            if not line.strip() or line.endswith(':'):
                continue
                
            instruction = self.assemble_line(line)
            if instruction is not None:
                machine_code.append(instruction)
                self.address += 1
        
        return machine_code
    
    def preprocess(self, source_code):
        """Remove comments and clean lines"""
        lines = []
        for line in source_code.split('\n'):
            # Remove comments
            if ';' in line:
                line = line.split(';')[0]
            # Clean up
            line = line.strip()
            if line:
                lines.append(line.upper())
        return lines
    
    def assemble_line(self, line):
        """Assemble a single line of assembly"""
        parts = line.split()
        if not parts:
            return None
            
        format_prefix = parts[0]
        rest = ' '.join(parts[1:])
        
        match format_prefix:
            case 'RR':
                return self.assemble_rr(rest)
            case 'RI':
                return self.assemble_ri(rest)
            case 'RM':
                return self.assemble_rm(rest)
            case 'RCM':
                return self.assemble_rcm(rest)
            case _:
                raise ValueError(f"Unknown format prefix: {format_prefix}")
    
    def assemble_rr(self, operands):
        """Assemble Register-Register instruction"""
        opcode_str, regs_str = operands.split(' ', 1)
        opcode = self.opcodes[opcode_str]
        
        # Parse registers: "RD, RS1, RS2" or "RD, RS1" for some instructions
        reg_parts = [r.strip() for r in regs_str.split(',')]
        
        if len(reg_parts) == 3:
            rd, rs1, rs2 = reg_parts
        elif len(reg_parts) == 2:
            rd, rs1 = reg_parts
            rs2 = rd  # Default second register
        else:
            raise ValueError(f"Invalid RR operands: {regs_str}")
        
        rd_num = self.registers[rd]
        rs1_num = self.registers[rs1]
        rs2_num = self.registers[rs2]
        
        # Build instruction: 00 OOOOOO 00000000000 RRRR SSSS TTTT
        instruction = (0b00 << 30) | (opcode << 24) | (rd_num << 8) | (rs1_num << 4) | rs2_num
        return instruction
    
    def assemble_ri(self, operands):
        """Assemble Register-Immediate instruction"""
        opcode_str, rest = operands.split(' ', 1)
        opcode = self.opcodes[opcode_str]
        
        # Parse: "RD, IMMEDIATE"
        rd_str, imm_str = [r.strip() for r in rest.split(',')]
        rd_num = self.registers[rd_str]
        
        # Handle immediate (could be decimal, hex, or label)
        immediate = self.parse_immediate(imm_str)
        
        # Build instruction: 01 OOOOOO 000 RRRR IIIIIIIIIIIIIIII
        instruction = (0b01 << 30) | (opcode << 24) | (rd_num << 16) | (immediate & 0xFFFF)
        return instruction
    
    def assemble_rm(self, operands):
        """Assemble Register-Memory instruction"""
        opcode_str, rest = operands.split(' ', 1)
        opcode = self.opcodes[opcode_str]
        
        # Parse: "RD, [ADDRESSING]"
        rd_str, addr_str = [r.strip() for r in rest.split(',')]
        rd_num = self.registers[rd_str]
        
        # Parse addressing mode
        addr_str = addr_str.strip('[]')
        mode, mem_field = self.parse_addressing(addr_str)
        
        # Build instruction: 10 OOOOOO 0 RRRR MM MMMMMMMMMMMMMMMMM
        instruction = (0b10 << 30) | (opcode << 24) | (rd_num << 19) | (mode << 17) | mem_field
        return instruction
    
    def assemble_rcm(self, operands):
        """Assemble Register-Condition-Memory instruction"""
        opcode_str, rest = operands.split(' ', 1)
        opcode = self.opcodes[opcode_str]
        
        # Parse: "REG, CONDITION, ADDRESS"
        reg_str, cond_str, addr_str = [r.strip() for r in rest.split(',')]
        reg_num = self.registers[reg_str]
        cond_num = self.conditions[cond_str]
        
        # Parse address (could be immediate or label)
        address = self.parse_immediate(addr_str)
        
        # Build instruction: 11 OOOOOO RRRR CCC AAAAAAAAAAAAAAAA
        instruction = (0b11 << 30) | (opcode << 24) | (reg_num << 19) | (cond_num << 16) | (address & 0xFFFF)
        return instruction
    
    def parse_immediate(self, imm_str):
        """Parse immediate value (decimal, hex, or label)"""
        imm_str = imm_str.strip()
        
        if imm_str in self.labels:
            # It's a label
            return self.labels[imm_str]
        elif imm_str.startswith('0X'):
            # Hexadecimal
            return int(imm_str[2:], 16)
        else:
            # Decimal
            return int(imm_str)
    
    def parse_addressing(self, addr_str):
        """Parse memory addressing mode and return (mode, mem_field)"""
        if '+' in addr_str:
            # Has offset: "BASE + OFFSET"
            base, offset = addr_str.split('+')
            base = base.strip()
            offset = offset.strip()
            
            if base.startswith('MP'):
                # Memory pointer with offset
                mp_reg = self.registers[base]
                offset_num = self.parse_immediate(offset)
                
                if offset_num <= 15:
                    # Mode 01: MP + immediate offset
                    mode = 0b01
                    mem_field = ((mp_reg - 8) << 14) | (offset_num << 10)
                else:
                    raise ValueError(f"Offset too large for mode 01: {offset_num}")
                    
            else:
                # Direct address with register offset
                base_addr = self.parse_immediate(base)
                offset_reg = self.registers[offset]
                
                if base_addr <= 0xFFF:
                    # Mode 10: direct + register offset
                    mode = 0b10
                    mem_field = (base_addr << 4) | offset_reg
                else:
                    raise ValueError(f"Base address too large for mode 10: {base_addr:#x}")
                    
        else:
            # Simple direct addressing
            address = self.parse_immediate(addr_str)
            if address <= 0xFFFF:
                # Mode 00: direct
                mode = 0b00
                mem_field = address
            else:
                raise ValueError(f"Address too large: {address:#x}")
        
        return mode, mem_field
    
    # Add to assembler to handle data directives
    def assemble_data(self, line):
        """Assemble data directives"""
        if line.startswith('.DATA '):
            data_str = line[6:].strip('"')
            values = []
            for char in data_str:
                values.append(ord(char))
            values.append(0)  # Null terminator
            return values
        elif line.startswith('.BYTE '):
            return [int(x.strip()) for x in line[6:].split(',')]
        elif line.startswith('.WORD '):
            words = [int(x.strip()) for x in line[6:].split(',')]
            # Split words into bytes (little-endian)
            bytes = []
            for word in words:
                bytes.append(word & 0xFF)
                bytes.append((word >> 8) & 0xFF)
            return bytes
        return None