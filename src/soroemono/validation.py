"""Numeric acceptance checks on the compiled font, not just build parameters."""

from collections import Counter
import json
from pathlib import Path
import unicodedata

from fontTools.ttLib import TTFont
from fontTools.misc.roundTools import otRound
import uharfbuzz as hb

from .builder import FAMILY, ITALIC_STYLES, JAPANESE_SHEAR, JP_OVERRIDES, WIDE_LATIN, STYLES
from .sources import digest, source_paths


def outline(font: TTFont, name: str) -> tuple:
    coordinates, endpoints, flags = font["glyf"][name].getCoordinates(font["glyf"])
    return tuple(coordinates), tuple(endpoints), tuple(flags)


def instructions(font: TTFont, name: str) -> bytes:
    glyph = font["glyf"][name]
    return bytes(glyph.program.getBytecode()) if hasattr(glyph, "program") else b""


def shape(path: Path, text: str, features: dict | None = None) -> list[tuple]:
    font = hb.Font(hb.Face(path.read_bytes()))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, features or {})
    return [(i.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for i, p in zip(buffer.glyph_infos, buffer.glyph_positions)]


def check(root: Path, path: Path, style: str = "Regular") -> dict:
    inputs = source_paths(root, style)
    font, latin, japanese = [TTFont(p) for p in [path, inputs["latin"], inputs["japanese"]]]
    cmap, left, right = [f.getBestCmap() for f in [font, latin, japanese]]
    failures = []
    counts = {}

    def require(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)

    require(font["head"].unitsPerEm == 1000, "UPM must be 1000")
    require(set(cmap) == set(left) | set(right), "Unicode coverage differs from input union")
    counts["unicode_characters"] = len(cmap)
    for cp, name in cmap.items():
        width = font["hmtx"][name][0]
        if unicodedata.category(chr(cp)).startswith("M") or cp == 0xFEFF:
            require(width == 0, f"Mark U+{cp:04X} is not zero-width")
        else:
            require(width in {600, 1200}, f"U+{cp:04X}: invalid width {width}")
        if unicodedata.east_asian_width(chr(cp)) in {"W", "F"}:
            require(width == 1200 or unicodedata.category(chr(cp)).startswith("M"),
                    f"U+{cp:04X}: fullwidth character is not 1200")
        if 0xFF61 <= cp <= 0xFF9F:
            require(width == 600, f"Halfwidth kana U+{cp:04X} is not 600")
    counts["advances"] = dict(sorted(Counter(font["hmtx"][n][0] for n in cmap.values()).items()))

    # All source Latin glyphs, including unencoded GSUB alternates and composites.
    for name in latin.getGlyphOrder():
        require(name in font.getGlyphOrder(), f"Missing Latin glyph {name}")
        if name not in font.getGlyphOrder():
            continue
        require(outline(font, name) == outline(latin, name), f"Latin outline changed: {name}")
        require(font["hmtx"][name] == latin["hmtx"][name], f"Latin metrics changed: {name}")
        require(instructions(font, name) == instructions(latin, name), f"Latin hints changed: {name}")
    counts["preserved_latin_glyphs"] = len(latin.getGlyphOrder())
    for cp, name in left.items():
        if cp not in JP_OVERRIDES | WIDE_LATIN:
            require(cmap[cp] == name, f"Latin mapping changed: U+{cp:04X}")
    for tag in ["fpgm", "prep", "cvt ", "gasp"]:
        require(font.getTableData(tag) == latin.getTableData(tag), f"Latin hint table changed: {tag}")
    latin_names = set(latin.getGlyphOrder())
    for name in set(font.getGlyphOrder()) - latin_names:
        require(not instructions(font, name), f"Transformed glyph has stale hints: {name}")

    # Merger preserves Latin glyph IDs, so compare actual shaping with the source.
    sample = "á Ä i\u0307\u0301 0O1Il WKQlgjmwkfryu 25689 ЖКУСжку ςϕϖ -> => != === <= >= !== :: ++ // /* */"
    variants = [{}, {"calt": False}]
    variants += [{r.FeatureTag: True} for r in latin["GSUB"].table.FeatureList.FeatureRecord]
    for features in variants:
        require(shape(path, sample, features) == shape(inputs["latin"], sample, features),
                f"Latin shaping changed: {features}")
    for tag in ["GSUB", "GPOS"]:
        tags = [r.FeatureTag for r in font[tag].table.FeatureList.FeatureRecord]
        require(tags == sorted(tags), f"{tag} feature tags are not sorted")

    def variations(f: TTFont) -> dict:
        return {(base, vs): glyph for t in f["cmap"].tables if t.format == 14
                for vs, entries in t.uvsDict.items() for base, glyph in entries}

    before, after = variations(japanese), variations(font)
    require(set(before) == set(after), "IVS coverage changed")
    compared = set()
    for (base, vs), name in after.items():
        target = name or cmap.get(base)
        require(target is not None and font["hmtx"][target][0] == 1200,
                f"IVS target has invalid advance: U+{base:X}/U+{vs:X}")
        source = before.get((base, vs)) or right.get(base)
        if target is not None and source is not None and (source, target) not in compared:
            # BIZ has post format 3; generated names change after subsetting.
            # Compare the resolved outline, not the temporary glyph name.
            coords, ends, flags = outline(japanese, source)
            shear = JAPANESE_SHEAR if style in ITALIC_STYLES else 0
            expected = (tuple((otRound(x * 1080 / 2048 + 60 + y * 1000 / 2048 * shear),
                               otRound(y * 1000 / 2048))
                              for x, y in coords), ends, flags)
            require(outline(font, target) == expected, f"IVS target outline changed: U+{base:X}/U+{vs:X}")
            compared.add((source, target))
    counts["variation_sequences"] = len(after)
    for text in ["元日国語", "ｱｲｳｴｵ", "ｶﾞﾊﾟ", "あ゙", "葛\U000e0100", "｛｝⚡﹢"]:
        require(all(row[0] != 0 for row in shape(path, text)), f"Missing glyph in {text!r}")
    require(shape(path, "ガ") == shape(path, "ガ"), "Kana NFC/NFD shaping differs")
    require(sum(row[1] for row in shape(path, "あ゙")) == 1200, "Combining kana changes cell count")
    require(any(row[3] for row in shape(path, "あ゙")), "Combining kana was not positioned")
    hhea, os2 = font["hhea"], font["OS/2"]
    require((hhea.ascent, hhea.descent, hhea.lineGap) == (1020, -300, 0), "hhea line metrics")
    require((os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (1020, -300, 0), "typo line metrics")
    require(bool(os2.fsSelection & 128), "USE_TYPO_METRICS is not set")
    bounds = [font["glyf"][n] for n in font.getGlyphOrder() if font["glyf"][n].numberOfContours]
    require(os2.usWinAscent >= max(g.yMax for g in bounds), "Win ascent clips a glyph")
    require(os2.usWinDescent >= -min(g.yMin for g in bounds), "Win descent clips a glyph")
    require(font["name"].getDebugName(1) == FAMILY, "Family name mismatch")
    require(font["name"].getDebugName(2) == style, "Style name mismatch")
    require(font["name"].getDebugName(17) == style, "Typographic style name mismatch")
    require(os2.usWeightClass == STYLES[style], "Weight class mismatch")
    bold = STYLES[style] == 700
    italic = style in ITALIC_STYLES
    require(bool(font["head"].macStyle & 1) == bold, "macStyle bold flag mismatch")
    require(bool(font["head"].macStyle & 2) == italic, "macStyle italic flag mismatch")
    require(bool(os2.fsSelection & (1 << 5)) == bold, "fsSelection bold flag mismatch")
    require(bool(os2.fsSelection & 1) == italic, "fsSelection italic flag mismatch")
    require(bool(os2.fsSelection & (1 << 6)) == (style == "Regular"), "fsSelection regular flag mismatch")
    require(font["post"].italicAngle == (-9 if italic else 0), "Italic angle mismatch")
    require(font["name"].getDebugName(5) == "Version 2.000", "Version name mismatch")
    result = {"passed": not failures, "sha256": digest(path.read_bytes()), "counts": counts,
              "failures": failures, "harfbuzz": hb.version_string(),
              "scope": "Static metrics, input preservation and shaping; not Windows rasterization acceptance"}
    if failures:
        raise ValueError(json.dumps(result, ensure_ascii=False, indent=2))
    return result
