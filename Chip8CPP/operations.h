#include <stdint.h>
#include <stack>
#include <Chip8.h>

using namespace std;

namespace Chip8Space
{
    void operate(Chip8Space::Chip8 *c8);

    void operate(Chip8Space::Chip8 *c8)
    {
        uint8_t X = (c8->OPCODE >> 8) & 0x0F;
        uint8_t Y = (c8->OPCODE >> 4) & 0x00F;
        uint8_t N = c8->OPCODE & 0x000F;
        uint8_t NN = c8->OPCODE & 0x00FF;
        uint16_t NNN = c8->OPCODE & 0x0FFF;

        switch (c8->OPCODE >> 12)
        {
        case 0x8:
        {
            switch (c8->OPCODE & 0xF)
            {
            case 0:
                c8->REG[X] = c8->REG[Y]; // Set
                break;

            case 1:
                c8->REG[X] = c8->REG[X] | c8->REG[Y]; // Logical OR
                break;

            case 2:
                c8->REG[X] = c8->REG[X] & c8->REG[Y]; // Logical AND
                break;

            case 3:
                c8->REG[X] = c8->REG[X] ^ c8->REG[Y]; // Logical XOR
                break;

            case 4:
                c8->REG[X] += c8->REG[Y]; // Add
                break;

            case 5:
                c8->REG[X] -= c8->REG[Y]; // Subtract
                break;

            case 7:
                c8->REG[X] = c8->REG[Y] - c8->REG[X]; // Subtract
                break;

            case 6:
                c8->REG[X] = c8->REG[Y]; // Shift right
                c8->REG[0xF] = c8->REG[X] & 0x01;
                c8->REG[X] >>= 1;
                break;

            case 0xE:
                c8->REG[X] = c8->REG[Y]; // Shift left
                c8->REG[0xF] = (c8->REG[X] & 0x80) >> 7;
                c8->REG[X] <<= 1;
                break;
            }
        }
        break;
        }
    }
}