#!fontforge --lang=py -script

import configparser
import os
import shutil
import fontforge
import psMat

# iniファイルを読み込む
config = configparser.ConfigParser()
config.read("build.ini")

VERSION = config.get("DEFAULT", "VERSION")
FONT_NAME = config.get("DEFAULT", "FONT_NAME")
JP_FONT = config.get("DEFAULT", "JP_FONT")
ENG_FONT = config.get("DEFAULT", "EN_FONT")
BUILD_FONTS_DIR = config.get("DEFAULT", "BUILD_FONTS_DIR")
EM_ASCENT = int(config.get("DEFAULT", "EM_ASCENT"))
EM_DESCENT = int(config.get("DEFAULT", "EM_DESCENT"))
INTERMEDIATE_WIDTH = int(config.get("DEFAULT", "INTERMEDIATE_WIDTH"))
FINAL_WIDTH = int(config.get("DEFAULT", "FINAL_WIDTH"))

def clear_build_directory(directory):
    """distディレクトリを空にする"""
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def adjust_em(font, em_ascent, em_descent):
    """フォントのEMをJetBrainsMonoに揃える"""
    font.em = em_ascent + em_descent
    font.ascent = em_ascent
    font.descent = em_descent

def adjust_width_jp_font(jp_font):
    """BIZUDGothicの幅をJetBrainsMonoに合わせて調整"""
    target_width = 600  # JetBrainsMonoの標準幅
    for glyph in jp_font.glyphs():
        if glyph.width > target_width:
            scale_factor = target_width / glyph.width
            glyph.transform(psMat.scale(scale_factor, 1))
            glyph.width = target_width

def delete_duplicate_glyphs(base_font, overwrite_font):
    """jp_fontとeng_fontの重複するグリフを削除"""
    for glyph in overwrite_font.glyphs():
        if glyph.unicode != -1 and glyph.unicode in base_font:
            base_font.removeGlyph(glyph.unicode)

def merge_fonts(jp_font, eng_font):
    """英語フォントを日本語フォントにマージ"""
    jp_font.mergeFonts(eng_font)

def resize_japanese_glyphs(font, intermediate_width, final_width):
    """日本語の全角グリフの幅を1080に拡大し、次に1200に設定"""
    for glyph in font.glyphs():
        if glyph.width == 600:  # 600幅のグリフを全角として扱う
            # 一旦1080に拡大
            scale_factor = intermediate_width / 600
            glyph.transform(psMat.scale(scale_factor, 1))
            glyph.width = intermediate_width

            # 中心を維持したまま1200に設定
            glyph.transform(psMat.translate((final_width - intermediate_width) / 2, 0))
            glyph.width = final_width

def update_font_metadata(font, weight):
    """フォントのメタデータを更新"""
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
        ("English (US)", "Version", VERSION),
    )

def save_font(font, weight):
    """フォントを保存"""
    output_dir = BUILD_FONTS_DIR
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_path = os.path.join(output_dir, f"{FONT_NAME}-{weight}.ttf")
    font.generate(output_path)

def main():
    """フォントの生成を行うメイン処理"""
    # distフォルダを空にする
    clear_build_directory(BUILD_FONTS_DIR)

    weights = ["Regular", "Bold"]

    for weight in weights:
        # フォントファイルを開く
        jp_font = fontforge.open(JP_FONT.format(weight=weight))
        eng_font = fontforge.open(ENG_FONT.format(weight=weight))

        # EMスクエアをJetBrainsMonoに揃える
        adjust_em(jp_font, EM_ASCENT, EM_DESCENT)

        # BIZUDGothicの幅をJetBrainsMonoに合わせて調整
        adjust_width_jp_font(jp_font)

        # 重複するグリフを削除
        delete_duplicate_glyphs(jp_font, eng_font)

        # フォントをマージ
        merge_fonts(jp_font, eng_font)

        # マージ後に日本語グリフを一旦1080に拡大し、その後1200にリサイズ
        resize_japanese_glyphs(jp_font, INTERMEDIATE_WIDTH, FINAL_WIDTH)

        # メタデータを更新
        update_font_metadata(jp_font, weight)

        # フォントを保存
        save_font(jp_font, weight)

    # ZIPファイルを作成してdistディレクトリに移動
    zip_filename = f"{FONT_NAME}_v{VERSION}"
    shutil.make_archive(zip_filename, 'zip', BUILD_FONTS_DIR)

    # distディレクトリにZIPファイルを移動
    shutil.move(f"{zip_filename}.zip", os.path.join(BUILD_FONTS_DIR, f"{zip_filename}.zip"))

if __name__ == "__main__":
    main()
