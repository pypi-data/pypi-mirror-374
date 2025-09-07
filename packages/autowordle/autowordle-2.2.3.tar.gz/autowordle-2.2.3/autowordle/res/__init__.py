import importlib
from types import SimpleNamespace
from importlib import resources

def colr_res(colour):
    return f"canvas:{colour}"

def file_res(filename):
    return resources.files(__package__)/filename

colours = SimpleNamespace(
    theme1="#AF2303", theme2="#FFC800",
    border="#222222",
    black="#31373D",
    white="#E6E7E8",
    red="#DD2E44",
    blue="#55ACEE",
    orange="#F4900C",
    yellow="#FDCB58",
    green="#78B159",
    purple="#AA8ED6",
    brown="#C1694F",
)

CHAR_TO_FILE = {
    # Generic
    chr(0x2B1B):  colr_res(colours.black),
    chr(0x25A1):  colr_res(colours.white), # old-style
    chr(0x2B1C):  colr_res(colours.white), # new-style
    chr(0x1F7E5): colr_res(colours.red),
    chr(0x1F7E6): colr_res(colours.blue),
    chr(0x1F7E7): colr_res(colours.orange),
    chr(0x1F7E8): colr_res(colours.yellow),
    chr(0x1F7E9): colr_res(colours.green),
    chr(0x1F7EA): colr_res(colours.purple),
    chr(0x1F7EB): colr_res(colours.brown),

    # Cell Tower
    chr(0x2B07): file_res("down.png"),
    chr(0x2B06): file_res("up.png"),
    chr(0x27A1): file_res("right.png"),
    chr(0x2B05): file_res("left.png"),
    chr(0x23F9): colr_res(colours.blue),

    # Hexcodle
    chr(0x23EB):  file_res("dup.png"),
    chr(0x1F53C): file_res("up.png"),
    chr(0x2705):  colr_res(colours.green),
    chr(0x1F53D): file_res("down.png"),
    chr(0x23EC):  file_res("ddown.png"),

    # Kotoba de Asobou
    chr(0x2194):  file_res("lr.png"),
    chr(0x2195):  file_res("ud.png"),
    chr(0x1F7E2): colr_res(colours.orange),
}
