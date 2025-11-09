from cpu import BIOSCPU

class IOCPU(BIOSCPU):
    def __init__(self):
        super().__init__()
        self.console_output = ""
        self.keyboard_buffer = []
        self.timer_ticks = 0
        self.disk_data = [0] * 1024  # Simple disk simulation
        self.initialize_io()
    
    def initialize_io(self):
        """Initialize I/O devices"""
        # Set up default I/O device states
        self.timer_ticks = 0
        self.console_output = ""
        self.keyboard_buffer = []
    
    def read_io(self, address):
        """Read from I/O address"""
        if not (0x9000 <= address <= 0x9FFF):
            return self.mem[address]  # Normal memory
        
        device = address & 0xFF  # Get device number
        
        match device:
            case 0x00:  # Console Input
                return self.read_console_input()
            case 0x02:  # Timer Value
                return self.timer_ticks & 0xFFFF
            case 0x04:  # Keyboard Status
                return 0xFFFF if self.keyboard_buffer else 0x0000
            case 0x05:  # Keyboard Data
                return self.read_keyboard()
            case 0x09:  # Serial Status
                return 0x0001  # Always ready for now
            case 0x0A:  # Serial Data
                return 0x00  # No serial data yet
            case _:
                return 0x00  # Default for unimplemented devices
    
    def write_io(self, address, value):
        """Write to I/O address"""
        if not (0x9000 <= address <= 0x9FFF):
            self.mem[address] = value  # Normal memory
            return
        
        device = address & 0xFF
        
        match device:
            case 0x00:  # Console Output
                self.write_console(value)
            case 0x03:  # Timer Control
                self.write_timer_control(value)
            case 0x06:  # Sound Control
                self.write_sound_control(value)
            case 0x07:  # Disk Control
                self.write_disk_control(value)
            case 0x08:  # Disk Data
                self.write_disk_data(value)
            case 0x0A:  # Serial Data
                self.write_serial_data(value)
            case 0x0B:  # System Control
                self.write_system_control(value)
    
    def read_console_input(self):
        """Read character from console input (simulated)"""
        # In a real system, this would read from actual keyboard
        if self.keyboard_buffer:
            return self.keyboard_buffer.pop(0)
        return 0
    
    def write_console(self, value):
        """Write character to console output"""
        char = value & 0xFF
        if char == 10:  # Newline
            print(self.console_output)
            self.console_output = ""
        else:
            self.console_output += chr(char)
    
    def read_keyboard(self):
        """Read from keyboard buffer"""
        if self.keyboard_buffer:
            return self.keyboard_buffer.pop(0)
        return 0
    
    def write_timer_control(self, value):
        """Control timer behavior"""
        # Could start/stop timer, set frequency, etc.
        pass
    
    def write_sound_control(self, value):
        """Control sound output"""
        # In a real system, this would control a speaker
        frequency = value & 0xFFFF
        # Simulate beep
        if frequency > 0:
            print(f"BEEP at {frequency}Hz")
    
    def write_disk_control(self, value):
        """Control disk operations"""
        # value could specify read/write, sector number, etc.
        self.disk_operation = value
    
    def write_disk_data(self, value):
        """Write data to disk buffer"""
        # In a real system, this would write to actual disk
        self.disk_buffer = value
    
    def write_serial_data(self, value):
        """Write data to serial port"""
        char = value & 0xFF
        # Simulate serial output
        print(f"[SERIAL] {chr(char)}", end='')
    
    def write_system_control(self, value):
        """System control functions"""
        if value == 0x0001:
            self.reset_system()
        elif value == 0x0002:
            self.shutdown_system()
    
    def reset_system(self):
        """Reset the computer"""
        self.pc = 0x8000  # Jump to BIOS
        self.regs = [0] * 16
        self.regs[7] = 0xFF00  # Reset stack pointer
        self.run = True
        print("System reset")
    
    def shutdown_system(self):
        """Shutdown the computer"""
        self.run = False
        print("System shutdown")
    
    def simulate_keypress(self, key):
        """Simulate a keypress (for testing)"""
        self.keyboard_buffer.append(ord(key) & 0xFF)
    
    def tick_timer(self):
        """Advance timer (call this periodically)"""
        self.timer_ticks += 1
        if self.timer_ticks % 1000 == 0:  # Timer interrupt every 1000 ticks
            self.trigger_interrupt(0x04)  # Timer interrupt