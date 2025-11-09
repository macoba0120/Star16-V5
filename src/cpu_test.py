# Print "Hello World" using BIOS calls
hello_bios = """
    RI MOV A, 0x0301    ; INT 03, function 01 (print string)
    RI MOV B, HELLO_MSG ; String address
    RI INT 0x03         ; Call console service
    RI HLT 0

HELLO_MSG:
    .data "Hello, World!", 0
"""

# Interactive input/output
interactive_io = """
START:
    ; Print prompt
    RI MOV A, 0x0301
    RI MOV B, PROMPT
    RI INT 0x03
    
    ; Read character
    RI MOV A, 0x0302
    RI INT 0x03
    
    ; Echo character
    RI MOV A, 0x0300
    RI MOV B, A        ; Move input to B
    RI INT 0x03
    
    ; Newline
    RI MOV A, 0x0300
    RI MOV B, 10
    RI INT 0x03
    
    RI JMP START

PROMPT:
    .data "Press a key: ", 0
"""

# Timer example
timer_demo = """
    RI MOV A, 0x0502    ; Get timer
    RI INT 0x05
    RI MOV B, A         ; Save start time
    
DELAY_LOOP:
    RI MOV A, 0x0502    ; Get current time
    RI INT 0x05
    RR SUB C, A, B      ; Calculate elapsed
    RI MOV A, 100       ; Delay for 100 ticks
    RR CMP C, A
    RCM JCN C, LT, DELAY_LOOP
    
    ; Delay finished
    RI MOV A, 0x0301
    RI MOV B, DONE_MSG
    RI INT 0x03
    RI HLT 0

DONE_MSG:
    .data "Delay complete!", 0
"""
from assembler import Assembler
from IO import IOCPU

test_programs = (hello_bios, interactive_io, timer_demo)

for program in test_programs:
    
    assembler = Assembler()
    machine_code = assembler.assemble(program)
    
    cpu = IOCPU()
    cpu.load_program(machine_code)
    cpu.run()