from ._models import PeripheralDef


stm32_peripheral_db = {
    "adc": {
        "[f4][*][*]": [
            PeripheralDef((1, 2, 3), "default"),
        ],
    },
    "can": {
        "[f4][*][*]": [
            PeripheralDef((1, 2), "default"),
        ]
    },
    "crc": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "dac": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "fsmc": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "i2c": {
        "[f4][*][*]": [
            PeripheralDef((1, 2, 3), "default"),
        ]
    },
    "i2s": {
        "[f4][*][*]": [
            PeripheralDef((1, 2, 3), "default"),
        ]
    },
    "iwdg": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "rcc": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "rng": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "rtc": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "sdio": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "spi": {
        "[f4][*][*]": [
            PeripheralDef((1, 2, 3), "default"),
        ]
    },
    "sys": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "tim": {
        "[f4][05|07|12|13|15|17|23|27|29|37|39|46|69|79][*]": [
            PeripheralDef((1, 8), "advanced"),
            PeripheralDef((2, 5), "general_purpose_32"),
            PeripheralDef((3, 4), "general_purpose_16"),
            PeripheralDef((6, 7), "basic"),
            PeripheralDef((10, 11, 13, 14), "1ch"),
            PeripheralDef((9, 12), "2ch"),
        ],
    },
    "uart": {
        "[f4][*][*]": [
            PeripheralDef((4, 5), "default"),
        ]
    },
    "usart": {
        "[f4][*][*]": [
            PeripheralDef((1, 2, 3, 6), "default"),
        ]
    },
    "gpio": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
    "dma": {
        "[f4][*][*]": [
            PeripheralDef((0,), "default"),
        ]
    },
}
