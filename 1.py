import pygame
import zipfile
import os
import requests
import time
import random

# Constants for Chip-8 emulator
CHIP8_MEMORY_SIZE = 4096
CHIP8_REGISTER_COUNT = 16
CHIP8_STACK_SIZE = 16
CHIP8_KEYS = 16
CHIP8_WIDTH = 64
CHIP8_HEIGHT = 32

# Fontset used by the Chip-8 (each character is 5 bytes)
CHIP8_FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

class Chip8:
    def __init__(self):
        # Initialize Chip-8 state
        self.memory = [0] * CHIP8_MEMORY_SIZE
        self.v = [0] * CHIP8_REGISTER_COUNT  # V registers (V0 to VF)
        self.i = 0  # Index register
        self.pc = 0x200  # Program counter starts at 0x200
        self.gfx = [0] * (CHIP8_WIDTH * CHIP8_HEIGHT)  # Screen (64x32)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * CHIP8_STACK_SIZE
        self.sp = 0  # Stack pointer
        self.keys = [0] * CHIP8_KEYS  # Hex-based keypad (0x0-0xF)
        self.draw_flag = False

        # Load fontset into memory
        for i in range(len(CHIP8_FONTSET)):
            self.memory[i] = CHIP8_FONTSET[i]

    def load_rom(self, rom_path):
        # Load a ROM file into memory starting at 0x200
        with open(rom_path, 'rb') as f:
            rom = f.read()
        for idx, byte in enumerate(rom):
            self.memory[0x200 + idx] = byte

    def load_bios(self, bios_path):
        # Load BIOS if necessary (this is optional for Chip-8)
        pass

    def emulate_cycle(self):
        # Fetch, decode, and execute opcode
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.pc += 2

        # Decode opcode (this is just a simple example with a few opcodes)
        if opcode == 0x00E0:  # CLS (Clear the display)
            self.gfx = [0] * (CHIP8_WIDTH * CHIP8_HEIGHT)
            self.draw_flag = True
        elif opcode == 0x00EE:  # RET (Return from subroutine)
            self.sp -= 1
            self.pc = self.stack[self.sp]
        else:
            print(f"Unknown opcode: {opcode:X}")

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP!")
            self.sound_timer -= 1

    def set_keys(self, keys):
        self.keys = keys

class GUI:
    def __init__(self, chip8):
        pygame.init()
        self.screen = pygame.display.set_mode((CHIP8_WIDTH * 10, CHIP8_HEIGHT * 10))
        pygame.display.set_caption("Chip-8 Emulator")
        self.chip8 = chip8
        self.clock = pygame.time.Clock()

    def draw(self):
        # Draw the Chip-8's screen state to the window
        if self.chip8.draw_flag:
            self.screen.fill((0, 0, 0))
            for y in range(CHIP8_HEIGHT):
                for x in range(CHIP8_WIDTH):
                    if self.chip8.gfx[x + (y * CHIP8_WIDTH)] == 1:
                        pygame.draw.rect(self.screen, (255, 255, 255), (x * 10, y * 10, 10, 10))
            pygame.display.flip()
            self.chip8.draw_flag = False

    def handle_events(self):
        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.chip8.keys[0x1] = 1
                # Handle other keys as needed...
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    self.chip8.keys[0x1] = 0
                # Handle other keys as needed...

    def run(self):
        while True:
            self.chip8.emulate_cycle()
            self.draw()
            self.handle_events()
            self.clock.tick(60)  # 60 cycles per second

def inspect_zip_for_modules(zip_path):
    # Inspect a zipfile for modules (could be adapted for ROMs)
    result = []
    with zipfile.ZipFile(zip_path, "r") as zfile:
        for name in zfile.namelist():
            if name.endswith(".ch8"):  # Assuming .ch8 is the file extension for ROMs
                result.append(name)
    return result

def download_bios(url, bios_path):
    # Download a BIOS file from the internet
    response = requests.get(url)
    with open(bios_path, 'wb') as f:
        f.write(response.content)

def main():
    # Create the Chip-8 emulator and GUI
    chip8 = Chip8()
    gui = GUI(chip8)

    # Load a ROM
    roms = inspect_zip_for_modules('roms.zip')
    if roms:
        with zipfile.ZipFile('roms.zip', 'r') as zfile:
            zfile.extract(roms[0], 'temp_rom.ch8')
            chip8.load_rom('temp_rom.ch8')

    # Download and load a BIOS (optional)
    # download_bios('http://example.com/bios.ch8', 'bios.ch8')
    # chip8.load_bios('bios.ch8')

    # Run the emulator
    gui.run()

if __name__ == '__main__':
    main()
