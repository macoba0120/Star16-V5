# StarCPU V5

StarCPU V5 is a CPU simulation project that provides a framework for executing instructions and managing memory. It includes an assembler that converts assembly language source code into machine code, allowing users to write and execute programs on a simulated CPU.

## Features

- **CPU Simulation**: The `cpu.py` file defines a `cpu` class that simulates a CPU with registers, memory, and instruction execution capabilities.
- **Assembler**: The `assembler.py` file provides an `Assembler` class that converts assembly language into machine code, supporting various instruction formats.
- **BIOS Support**: The `cpu` class includes a subclass `BIOSCPU` for handling BIOS-related functionalities and a Pygame interface.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/macoba0120/StarCPU-V5.git
   ```
2. Navigate to the project directory:
   ```
   cd StarCPU-V5
   ```

## Usage

To use the CPU simulator and assembler, you can run the Python scripts in the `src` directory. You can modify the source code to add new instructions or features as needed.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

I need someone to refactor my Python code into C++ for da speedz. Thank you in advance.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
