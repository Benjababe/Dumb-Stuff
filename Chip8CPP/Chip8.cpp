#include "Chip8.h"
#include "operations.h"
#include "fonts.h"

using namespace std;
using namespace Chip8Space;

void setOpCode(Chip8Space::Chip8 *);

int main()
{
    Chip8Space::Chip8 chip8;

    for (int i = 0; i < 4096; i++)
    {
        chip8.MEMORY[i] = 0;
    }

    // initialising fonts in memory
    for (int i = 0x50; i < 0xA0; i++)
    {
        chip8.MEMORY[i] = FONTS[i - 0x50];
    }

    while (1)
    {
        chip8.MEMORY[0x200] = 0x80;
        chip8.MEMORY[0x202] = 0x00;
        setOpCode(&chip8);
        operate(&chip8);
    }
}

void setOpCode(Chip8Space::Chip8 *chip8)
{
    uint16_t opCode = chip8->MEMORY[chip8->PC];
    chip8->PC += 2;
    opCode = (opCode << 8) + chip8->MEMORY[chip8->PC];
    chip8->PC += 2;

    chip8->OPCODE = opCode;
}