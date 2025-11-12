class cpu:
    def __init__(self):
        self.regs = [0] * 16
        self.pc = 0
        self.mem = [0] * 65536
        
        # Flags
        self.zf = False
        self.cf = False  
        self.sf = False
        self.ie = False
        
        self.run = True
        
        # Register name mapping for debugging
        self.reg_names = ["A", "B", "C", "D", "X", "Y", "Z", "SP", 
                         "MP1", "MP2", "MP3", "MP4", "E", "F", "G", "H"]

    def execute(self, instruction):
        format = (instruction >> 30) & 0b11
        opcode = (instruction >> 24) & 0b111111
        
        try:
            match format:
                case 0b00:  # Register-Register
                    rd = (instruction >> 8) & 0xF
                    rs1 = (instruction >> 4) & 0xF
                    rs2 = instruction & 0xF
                    self.exec_rr(opcode, rd, rs1, rs2)
                
                case 0b01:  # Register-Immediate
                    rd = (instruction >> 16) & 0xF
                    imm = instruction & 0xFFFF
                    # Sign extend 16-bit immediate
                    if imm & 0x8000:
                        imm |= 0xFFFF0000
                    self.exec_ri(opcode, rd, imm)
                
                case 0b10:  # Register-Memory
                    rd = (instruction >> 19) & 0xF
                    mode = (instruction >> 17) & 0b11
                    mem_field = instruction & 0x1FFFF
                    address = self.calc_address(mode, mem_field)
                    self.exec_rm(opcode, rd, address)
                
                case 0b11:  # Register-Condition-Memory
                    reg = (instruction >> 19) & 0xF
                    condition = (instruction >> 16) & 0b111
                    address = instruction & 0xFFFF
                    self.exec_rcm(opcode, reg, condition, address)
        except ValueError as verr:
            print("ERR: Error when parsing instruction: ", verr)
            input("Press a key to continue... ")
        except ZeroDivisionError as zde:
            print("ERR: Division by 0 occured.")
            input("Press a key to continue... ")
        except Exception as exe:
            print("FATAL: Other error occured... ", exe)
            print("If you're reading this, I messed up somehow.")
            self.run = False
            print("CPU halted.")

    def calc_address(self, mode, mem_field):
        match mode:
            case 0b00:  # direct
                base = mem_field & 0xFFFF
                return base
                
            case 0b01:  # memory pointer + immediate 4-bit offset
                mp_reg = (mem_field >> 14) & 0b11  # MP1-MP4
                offset = (mem_field >> 10) & 0b1111
                base = self.regs[8 + mp_reg]  # MP1=8, MP2=9, etc.
                return base + offset
                
            case 0b10:  # direct + register offset
                base = (mem_field >> 4) & 0xFFF
                offset_reg = mem_field & 0b1111
                return base + self.regs[offset_reg]
                
            case 0b11:  # memory pointer + register offset
                mp_reg = (mem_field >> 14) & 0b11
                offset_reg = (mem_field >> 10) & 0b1111
                base = self.regs[8 + mp_reg]
                return base + self.regs[offset_reg]

    def update_flags(self, value):
        """Update flags after arithmetic operation"""
        self.zf = (value & 0xFFFF) == 0
        self.sf = (value & 0x8000) != 0
        self.cf = value > 0xFFFF or value < 0

    def check_condition(self, condition, value):
        """Check condition codes: 100=LT, 010=EQ, 001=GT"""
        lt = (condition & 0b100) and value < 0
        eq = (condition & 0b010) and value == 0  
        gt = (condition & 0b001) and value > 0
        return lt or eq or gt

    def push(self, value):
        """Push value onto stack"""
        self.regs[7] -= 1  # SP is register 7
        self.mem[self.regs[7]] = value & 0xFFFF

    def pop(self):
        """Pop value from stack"""
        value = self.mem[self.regs[7]]
        self.regs[7] += 1
        return value

    def exec_rr(self, opcode, rd, rs1, rs2):
        """Execute Register-Register instructions"""
        match opcode:
            case 0x00:  # MOV
                self.regs[rd] = self.regs[rs1]
                
            case 0x02:  # PSH
                self.push(self.regs[rd])
                
            case 0x03:  # POP
                self.regs[rd] = self.pop()
                
            case 0x04:  # SWP
                self.regs[rd], self.regs[rs1] = self.regs[rs1], self.regs[rd]
                
            case 0x10:  # ADD
                result = self.regs[rs1] + self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
                
            case 0x11:  # SUB
                result = self.regs[rs1] - self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x12:  # MUL
                result = self.regs[rs1] * self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x13:  # DIV
                result = self.regs[rs1] // self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x14:  # AND
                result = self.regs[rs1] & self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x15:  # OR
                result = self.regs[rs1] | self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x16:  # XOR
                result = self.regs[rs1] ^ self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x17:  # NOT
                result = ~self.regs[rs1]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x18:  # SHL
                result = self.regs[rs1] << self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x1A:  # SAR
                result = self.regs[rs1] >> self.regs[rs2]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
                
            case 0x1D:  # INC
                self.regs[rd] = (self.regs[rd] + 1) & 0xFFFF
                self.update_flags(self.regs[rd])
                
            case 0x1E:  # DEC
                self.regs[rd] = (self.regs[rd] - 1) & 0xFFFF
                self.update_flags(self.regs[rd])

            case 0x23:  # CMP
                result = self.regs[rd] - self.regs[rs1]
                self.update_flags(result)

            case 0x24:  # RET
                self.pc = self.pop()

            case 0x25:  # HLT
                self.run = False

            case 0x26:  # NOP
                pass

            case 0x31:  # RTI
                self.pc = self.pop()

            case 0x32:  # STI
                self.ie = True

            case 0x33:  # CLI
                self.ie = False
                
            case _:
                raise ValueError(f"Unknown RR opcode: {opcode:#x}")

    def exec_ri(self, opcode, rd, imm):
        """Execute Register-Immediate instructions"""
        match opcode:
            case 0x00:  # MOV (immediate)
                self.regs[rd] = imm & 0xFFFF
                
            case 0x10:  # ADD (immediate)
                result = self.regs[rd] + imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x11:  # SUB
                result = self.regs[rd] - imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x12:  # MUL
                result = self.regs[rd] * imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x13:  # DIV
                result = self.regs[rd] // imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x14:  # AND
                result = self.regs[rd] & imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x15:  # OR
                result = self.regs[rd] | imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x16:  # XOR
                result = self.regs[rd] ^ imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x17:  # NOT
                result = ~imm
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x18:  # SHL (immediate)
                shift_amount = imm & 0xF  # Only use bottom 4 bits
                result = self.regs[rd] << shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x19:  # SLR (immediate)
                shift_amount = imm & 0xF
                result = self.regs[rd] >> shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x1A:  # SAR (immediate)
                shift_amount = imm & 0xF
                value = self.regs[rd]
                if value & 0x8000:  # If negative
                    result = (value >> shift_amount) | (0xFFFF << (16 - shift_amount))
                else:
                    result = value >> shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x1B:  # ROL (immediate)
                shift_amount = imm & 0xF
                value = self.regs[rd]
                result = ((value << shift_amount) | (value >> (16 - shift_amount))) & 0xFFFF
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x1C:  # ROR (immediate)
                shift_amount = imm & 0xF
                value = self.regs[rd]
                result = ((value >> shift_amount) | (value << (16 - shift_amount))) & 0xFFFF
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x1D:  # INC
                result = self.regs[rd] + 1
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x1E:  # DEC
                result = self.regs[rd] - 1
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x23:  # CMP
                result = self.regs[rd] - imm
                self.update_flags(result)

            case 0x24:  # RET
                self.pc = self.pop()

            case 0x25:  # HLT
                self.run = False

            case 0x26:  # NOP
                pass

            case 0x30:  # INT - Software Interrupt
                # imm is the interrupt number (0-255), not the address!
                interrupt_vector = 0xFF00 + (imm * 1)  # Each vector is 2 bytes
                self.push(self.pc)        # Save return address
                self.push(self.regs[0])   # Save A register (or save all registers)
                self.ie = False           # Disable interrupts
                # Read the interrupt handler address from the vector table
                self.pc = self.mem[interrupt_vector]

            case 0x31:  # RTI
                self.pc = self.pop()

            case 0x32:  # STI
                self.ie = True

            case 0x33:  # CLI
                self.ie = False
                
            case _:
                raise ValueError(f"Unknown RI opcode: {opcode:#x}")

    def exec_rm(self, opcode, rd, address):
        """Execute Register-Memory instructions"""
        match opcode:
            # Data manipulation (0x0X)
            case 0x00:  # MOV (load from memory)
                self.regs[rd] = self.mem[address]
            
            case 0x01:  # STR (store to memory)
                self.mem[address] = self.regs[rd]
            
            # Math instructions (0x1X)
            case 0x10:  # ADD (with memory)
                result = self.regs[rd] + self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x11:  # SUB (with memory)
                result = self.regs[rd] - self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x12:  # MUL (with memory)
                result = self.regs[rd] * self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x13:  # DIV (with memory)
                divisor = self.mem[address]
                if divisor == 0:
                    # Handle division by zero - maybe trigger interrupt?
                    self.regs[rd] = 0xFFFF
                else:
                    result = self.regs[rd] // divisor
                    self.update_flags(result)
                    self.regs[rd] = result & 0xFFFF
            
            case 0x14:  # AND (with memory)
                result = self.regs[rd] & self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x15:  # OR (with memory)
                result = self.regs[rd] | self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x16:  # XOR (with memory)
                result = self.regs[rd] ^ self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x17:  # NOT (with memory) - uses memory as source
                result = ~self.mem[address]
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x18:  # SHL (with memory as shift amount)
                shift_amount = self.mem[address] & 0xF
                result = self.regs[rd] << shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF

            case 0x19:  # SLR (with memory as shift amount)
                shift_amount = self.mem[address] & 0xF
                result = self.regs[rd] >> shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x1A:  # SAR (with memory as shift amount)
                shift_amount = self.mem[address] & 0xF
                value = self.regs[rd]
                if value & 0x8000:  # If negative
                    result = (value >> shift_amount) | (0xFFFF << (16 - shift_amount))
                else:
                    result = value >> shift_amount
                self.update_flags(result)
                self.regs[rd] = result & 0xFFFF
            
            case 0x1B:  # ROL (with memory as rotate amount)
                shift_amount = self.mem[address] & 0xF
                value = self.regs[rd]
                result = ((value << shift_amount) | (value >> (16 - shift_amount))) & 0xFFFF
                self.update_flags(result)
                self.regs[rd] = result
            
            case 0x1C:  # ROR (with memory as rotate amount)
                shift_amount = self.mem[address] & 0xF
                value = self.regs[rd]
                result = ((value >> shift_amount) | (value << (16 - shift_amount))) & 0xFFFF
                self.update_flags(result)
                self.regs[rd] = result
            
            # Flow control (0x2X)
            case 0x20:  # JMP
                self.pc = address & 0xFFFF
            
            case 0x22:  # JSR
                self.push(self.pc)
                self.pc = address & 0xFFFF

            case 0x23:  # CMP (with memory)
                result = self.regs[rd] - self.mem[address]
                self.update_flags(result)
            
            case _:
                raise ValueError(f"Unknown RM opcode: {opcode:#x}")

    def exec_rcm(self, opcode, reg, condition, address):
        """Execute Register-Condition-Memory instructions"""
        match opcode:
            case 0x20:  # JMP (unconditional in RC format)
                self.pc = address
                
            case 0x21:  # JCR (jump conditional with register)
                if self.check_condition(condition, self.regs[reg]):
                    self.pc = address

            case 0x27:  # JCF (jump conditional with flags)
                if self.check_flags(condition):
                    self.pc = address
                    
            case 0x22:  # JSR (jump to subroutine)
                self.push(self.pc)
                self.pc = address & 0xFFFF
                    
            case _:
                raise ValueError(f"Unknown RCM opcode: {opcode:#x}")

    def step(self):
        """Execute one instruction"""
        if not self.run:
            return
            
        instruction = self.mem[self.pc]
        self.pc += 1
        self.execute(instruction)

    def run_continuous(self):
        """Run until HLT instruction or error"""
        while self.run:
            self.step()

    def debug_state(self):
        """Print current CPU state for debugging"""
        print(f"PC: {self.pc:#06x}")
        for i in range(0, 16, 4):
            regs = [f"{self.reg_names[j]}={self.regs[j]:#06x}" for j in range(i, i+4)]
            print("  ".join(regs))
        print(f"Flags: Z={self.zf} S={self.sf} C={self.cf}")

    def check_flags(self, condition):
        lt = (condition & 0b100) and self.sf
        eq = (condition & 0b010) and self.zf 
        gt = (condition & 0b001) and ((not self.sf) and (not self.zf))
        return lt or eq or gt

class BIOSCPU(cpu):
    def __init__(self):
        super().__init__()
        # BIOS Data Area addresses
        self.BDA_BASE = 0xE000
        self.CURSOR_X = self.BDA_BASE + 0x00    # 1 byte
        self.CURSOR_Y = self.BDA_BASE + 0x01    # 1 byte  
        self.VIDEO_MODE = self.BDA_BASE + 0x02  # 1 byte
        self.SCREEN_WIDTH = self.BDA_BASE + 0x03 # 1 byte
        self.SCREEN_HEIGHT = self.BDA_BASE + 0x04 # 1 byte
        self.KEYBOARD_BUFFER = self.BDA_BASE + 0x10 # 32 bytes
        self.KEYBOARD_BUFFER_HEAD = self.BDA_BASE + 0x30 # 1 byte
        self.KEYBOARD_BUFFER_TAIL = self.BDA_BASE + 0x31 # 1 byte
        self.SYSTEM_TIME = self.BDA_BASE + 0x40 # 4 bytes (ticks)
        self.VIDEO_MEMORY_BASE = self.BDA_BASE + 0x50 # 2 bytes
        self.INSTALLED_MEMORY = self.BDA_BASE + 0x60 # 2 bytes
        
        self.initialize_bios_data()
    
    def initialize_bios_data(self):
        """Initialize BIOS Data Area with default values"""
        # Cursor and video
        self.write_bda_byte(self.CURSOR_X, 0)
        self.write_bda_byte(self.CURSOR_Y, 0) 
        self.write_bda_byte(self.VIDEO_MODE, 0x03)  # 80x25 text
        self.write_bda_byte(self.SCREEN_WIDTH, 80)
        self.write_bda_byte(self.SCREEN_HEIGHT, 25)
        
        # Keyboard buffer (circular buffer)
        self.write_bda_byte(self.KEYBOARD_BUFFER_HEAD, 0)
        self.write_bda_byte(self.KEYBOARD_BUFFER_TAIL, 0)
        
        # System information
        self.write_bda_word(self.VIDEO_MEMORY_BASE, 0xA000)
        self.write_bda_word(self.INSTALLED_MEMORY, 65536)  # 64KB
        
        # Clear keyboard buffer area
        for i in range(32):
            self.write_bda_byte(self.KEYBOARD_BUFFER + i, 0)
    
    def read_bda_byte(self, address):
        """Read byte from BIOS Data Area"""
        if self.BDA_BASE <= address < self.BDA_BASE + 4096:
            return self.mem[address]
        else:
            raise ValueError(f"Invalid BDA access: {address:#06x}")
    
    def write_bda_byte(self, address, value):
        """Write byte to BIOS Data Area"""
        if self.BDA_BASE <= address < self.BDA_BASE + 4096:
            self.mem[address] = value & 0xFF
        else:
            raise ValueError(f"Invalid BDA access: {address:#06x}")
    
    def read_bda_word(self, address):
        """Read word from BIOS Data Area"""
        if self.BDA_BASE <= address < self.BDA_BASE + 4095:
            return self.mem[address] | (self.mem[address + 1] << 8)
        else:
            raise ValueError(f"Invalid BDA access: {address:#06x}")
    
    def write_bda_word(self, address, value):
        """Write word to BIOS Data Area"""
        if self.BDA_BASE <= address < self.BDA_BASE + 4095:
            self.mem[address] = value & 0xFF
            self.mem[address + 1] = (value >> 8) & 0xFF
        else:
            raise ValueError(f"Invalid BDA access: {address:#06x}")
        
    def bios_video_services(self):
        """INT 0x01 - Video Services using BDA"""
        function = self.regs[0]
    
        match function:
            case 0x00:  # Set Video Mode
                mode = self.regs[1]
                self.write_bda_byte(self.VIDEO_MODE, mode)
            
            case 0x01:  # Clear Screen
                self.clear_screen()
    
            case 0x02:  # Set Cursor Position
                x = self.regs[1] & 0xFF
                y = self.regs[2] & 0xFF
                self.write_bda_byte(self.CURSOR_X, x)
                self.write_bda_byte(self.CURSOR_Y, y)
            
            case 0x03:  # Get Cursor Position
                self.regs[1] = self.read_bda_byte(self.CURSOR_X)  # B = X
                self.regs[2] = self.read_bda_byte(self.CURSOR_Y)  # C = Y
            
            case 0x0E:  # Teletype Output
                char = self.regs[1] & 0xFF
                self.bios_print_char(char)

    def bios_print_char(self, char):
        """Print character using BDA cursor position"""
        # Get current cursor from BDA
        cursor_x = self.read_bda_byte(self.CURSOR_X)
        cursor_y = self.read_bda_byte(self.CURSOR_Y)
        screen_width = self.read_bda_byte(self.SCREEN_WIDTH)
        screen_height = self.read_bda_byte(self.SCREEN_HEIGHT)
        video_base = self.read_bda_word(self.VIDEO_MEMORY_BASE)
    
        if char == 10:  # Newline
            cursor_x = 0
            cursor_y += 1
        elif char == 13:  # Carriage return
            cursor_x = 0
        else:
            # Write character to video memory
            pos = cursor_y * screen_width + cursor_x
            if video_base + pos < len(self.mem):
                self.mem[video_base + pos] = char
            cursor_x += 1
    
        # Handle line wrap and screen scroll
        if cursor_x >= screen_width:
            cursor_x = 0
            cursor_y += 1
    
        if cursor_y >= screen_height:
            self.scroll_screen()
            cursor_y = screen_height - 1
    
        # Update cursor in BDA
        self.write_bda_byte(self.CURSOR_X, cursor_x)
        self.write_bda_byte(self.CURSOR_Y, cursor_y)

    def scroll_screen(self):
        """Scroll screen up one line"""
        screen_width = self.read_bda_byte(self.SCREEN_WIDTH)
        screen_height = self.read_bda_byte(self.SCREEN_HEIGHT)
        video_base = self.read_bda_word(self.VIDEO_MEMORY_BASE)
    
        # Move lines up
        for y in range(1, screen_height):
            for x in range(screen_width):
                src_pos = video_base + (y * screen_width + x)
                dst_pos = video_base + ((y - 1) * screen_width + x)
                if src_pos < len(self.mem) and dst_pos < len(self.mem):
                    self.mem[dst_pos] = self.mem[src_pos]
    
        # Clear bottom line
        bottom_line = video_base + ((screen_height - 1) * screen_width)
        for x in range(screen_width):
            if bottom_line + x < len(self.mem):
                self.mem[bottom_line + x] = 0x20  # Space

    def bios_keyboard_services(self):
        """INT 0x02 - Keyboard Services using BDA circular buffer"""
        function = self.regs[0]
    
        match function:
            case 0x00:  # Get Keystroke
                head = self.read_bda_byte(self.KEYBOARD_BUFFER_HEAD)
                tail = self.read_bda_byte(self.KEYBOARD_BUFFER_TAIL)
            
                if head == tail:  # Buffer empty
                    self.regs[0] = 0  # No key
                else:
                    # Read from buffer
                    key = self.read_bda_byte(self.KEYBOARD_BUFFER + head)
                    head = (head + 1) % 32
                    self.write_bda_byte(self.KEYBOARD_BUFFER_HEAD, head)
                    self.regs[0] = key  # Return key
        
            case 0x01:  # Check for Keystroke
                head = self.read_bda_byte(self.KEYBOARD_BUFFER_HEAD)
                tail = self.read_bda_byte(self.KEYBOARD_BUFFER_TAIL)
                self.regs[0] = 0xFFFF if head != tail else 0x0000

    def add_key_to_buffer(self, key):
        """Add key to keyboard buffer (called by hardware)"""
        head = self.read_bda_byte(self.KEYBOARD_BUFFER_HEAD)
        tail = self.read_bda_byte(self.KEYBOARD_BUFFER_TAIL)
    
        next_tail = (tail + 1) % 32
        if next_tail != head:  # Buffer not full
            self.write_bda_byte(self.KEYBOARD_BUFFER + tail, key & 0xFF)
            self.write_bda_byte(self.KEYBOARD_BUFFER_TAIL, next_tail)
