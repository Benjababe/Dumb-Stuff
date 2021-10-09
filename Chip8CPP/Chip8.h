#include <stdint.h>
#include <stack>

using namespace std;

namespace Chip8Space
{
    class Chip8
    {
    public:
        Chip8(){};

        uint8_t MEMORY[4096];
        uint8_t REG[16];
        stack<uint16_t> STACK;

        uint8_t DELAY_TIMER, SOUND_TIMER;
        uint16_t PC = 0x200, I, OPCODE;

        bool DISPLAY[64][32];
    };
}