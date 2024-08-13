import fontforge
import os
import configparser
import psMat
import shutil

config = configparser.ConfigParser()
config.read("build.ini")

VERSION = config.get("DEFAULT", "VERSION")
FONT_NAME = config.get("DEFAULT", "FONT_NAME")
EN_FONT_PATH = config.get("DEFAULT", "EN_FONT")
JP_FONT_PATH = config.get("DEFAULT", "JP_FONT")

WEIGHTS = ["Regular", "Bold"]

def adjust_width_with_scale(font, target_width, original_width):
    scale_factor = target_width / original_width
    for glyph in font.glyphs():
        if glyph.width == original_width:
            glyph.transform(psMat.scale(scale_factor, 1))
            glyph.width = target_width

def adjust_width_without_scale(font, new_width, current_width):
    for glyph in font.glyphs():
        if glyph.width == current_width:
            glyph.width = new_width

def delete_overlapping_glyphs(base_font, overwrite_font):
    for glyph in overwrite_font.glyphs():
        try:
            if glyph.unicode != -1 and base_font[glyph.unicode].isWorthOutputting():
                base_font.removeGlyph(glyph.unicode)
        except TypeError:
            continue

def merge_fonts(jp_font, en_font):
    jp_font.mergeFonts(en_font)

def update_font_metadata(font, weight):
    font.familyname = FONT_NAME
    font.fullname = f"{FONT_NAME} {weight}"
    font.fontname = f"{FONT_NAME}-{weight}".replace(" ", "")
    font.sfnt_names = (
        (
            "English (US)",
            "License",
            """This Font Software is licensed under the SIL Open Font License,
Version 1.1. This license is available with a FAQ
at: http://scripts.sil.org/OFL""",
        ),
        ("English (US)", "License URL", "http://scripts.sil.org/OFL"),
    )

def save_font(font, weight):
    output_dir = "dist"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_path = os.path.join(output_dir, f"{FONT_NAME}-{weight}.ttf")
    font.generate(output_path)

def read_license(license_path):
    with open(license_path, "r", encoding="utf-8") as f:
        return f.read()

def create_zip_archive(source_dir, output_filename):
    shutil.make_archive(output_filename, 'zip', source_dir)

for weight in WEIGHTS:
    en_font_path = EN_FONT_PATH.format(weight=weight)
    jp_font_path = JP_FONT_PATH.format(weight=weight)

    en_font = fontforge.open(en_font_path)
    jp_font = fontforge.open(jp_font_path)

    adjust_width_with_scale(jp_font, 1100, 1000)
    adjust_width_without_scale(jp_font, 1200, 1100)
    delete_overlapping_glyphs(jp_font, en_font)
    merge_fonts(jp_font, en_font)
    update_font_metadata(jp_font, weight)
    save_font(jp_font, weight)


zip_filename = f"{FONT_NAME}_v{VERSION}"
create_zip_archive("dist", zip_filename)

print("Fonts merged and saved successfully.")
