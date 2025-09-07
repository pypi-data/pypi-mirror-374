from ..memory import MemSeg, MemSegType

stm32_memory_db = {
    "[f4][05|07|15|17][*]": [
        MemSeg(MemSegType.FLASH, 0x08000000, None),
        MemSeg(MemSegType.CCM, 0x10000000, 64 * 1024),
        MemSeg(MemSegType.SRAM1, 0x20000000, 112 * 1024),
        MemSeg(MemSegType.SRAM2, 0x2001C000, 16 * 1024),
        MemSeg(MemSegType.BACKUP, 0x40024000, 4 * 1024),
    ],
}
