"""Build the four static SOROEMONO 2.0.0 styles from locked inputs."""

from copy import deepcopy
import json
from pathlib import Path
import platform
import shutil
from tempfile import TemporaryDirectory
import unicodedata

from fontTools import subset
from fontTools import version as fonttools_version
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.merge import Merger
from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

from .sources import STYLE_SOURCES, digest, lock, source_paths

FAMILY = "SOROEMONO"
STYLES = {"Regular": 400, "Bold": 700, "Italic": 400, "Bold Italic": 700}
ITALIC_STYLES = {"Italic", "Bold Italic"}
# A nine-degree oblique for BIZ glyphs. Latin italics come from JetBrains Mono.
JAPANESE_SHEAR = 0.1583844403


def filename(style: str) -> str:
    if style not in STYLES:
        raise ValueError(f"Unsupported style: {style}")
    return f"SOROEMONO-{style.replace(' ', '')}.ttf"


JP_OVERRIDES = {0xFF5B, 0xFF5D}
WIDE_LATIN = {0x26A1, 0xFE62}
JP_FEATURES = ["ccmp", "locl", "jp78", "jp83", "jp90", "hojo", "nlck", "trad", "expt"]
TIMESTAMP = 2082844800 + 1723507200  # 2024-08-13, OpenType's 1904 epoch


def set_mapping(font: TTFont, cp: int, name: str | None) -> None:
    for table in font["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            if name is None:
                table.cmap.pop(cp, None)
            elif cp in table.cmap:
                table.cmap[cp] = name


def transformed(font: TTFont, name: str, sx: float, sy: float, dx: float,
                shear: float = 0) -> Glyph:
    original = font["glyf"][name]
    coordinates, endpoints, flags = original.getCoordinates(font["glyf"])
    result = Glyph()
    result.numberOfContours = len(endpoints)
    if coordinates:
        result.coordinates = GlyphCoordinates(
            [(otRound(x * sx + dx + y * sy * shear), otRound(y * sy))
             for x, y in coordinates]
        )
        result.endPtsOfContours = list(endpoints)
        result.flags = flags[:]
    result.removeHinting()
    result.recalcBounds(font["glyf"])
    return result


def prepare_japanese(font: TTFont, latin: TTFont, style: str) -> dict[int, str]:
    """Keep Unicode aliases, layout dependencies and UVS targets through subsetting."""
    cmap = font.getBestCmap()
    selected = set(cmap) - set(latin.getBestCmap()) | JP_OVERRIDES
    selectors = {vs for t in font["cmap"].tables if t.format == 14 for vs in t.uvsDict}
    options = subset.Options()
    options.layout_features = JP_FEATURES
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.glyph_names = True
    options.hinting = False
    options.recalc_timestamp = False
    options.drop_tables += ["vhea", "vmtx", "meta"]
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=selected | selectors)
    sub.subset(font)
    # A retained glyph can have another Unicode alias owned by the Latin input.
    for cp in set(font.getBestCmap()) - selected:
        set_mapping(font, cp, None)
    cmap = font.getBestCmap()
    marks = {cp: g for cp, g in cmap.items() if unicodedata.category(chr(cp)).startswith("M")}
    mark_names = set(marks.values())
    spacing_names = {g for cp, g in cmap.items() if cp not in marks}
    if mark_names & spacing_names:
        raise ValueError("A glyph aliases both a spacing character and a mark; add an explicit policy")
    upm = font["head"].unitsPerEm
    # Generate all outlines before replacing any components.
    updates = {}
    for name in font.getGlyphOrder():
        width, lsb = font["hmtx"][name]
        if width == upm:
            sx, dx, advance = 1080 / upm, 60, 1200
        elif width == upm // 2:
            sx, dx, advance = 1000 / upm, 50, 600
        elif width == 0:
            sx, dx, advance = 1000 / upm, 0, 0
        else:
            raise ValueError(f"Unclassified Japanese glyph width: {name}={width}")
        if name in mark_names:
            advance = 0
        glyph = transformed(font, name, sx, 1000 / upm, dx,
                            JAPANESE_SHEAR if style in ITALIC_STYLES else 0)
        updates[name] = (glyph, (advance, getattr(glyph, "xMin", 0)))
    for name, (glyph, metrics) in updates.items():
        font["glyf"][name] = glyph
        font["hmtx"][name] = metrics
    font["head"].unitsPerEm = 1000
    # These are temporary input metrics; set the final metrics after merging.
    font["hhea"].ascent, font["hhea"].descent, font["hhea"].lineGap = 880, -120, 0
    os2 = font["OS/2"]
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = 880, -120, 0
    os2.usWinAscent, os2.usWinDescent = 880, 120
    return marks


def add_mark_positioning(font: TTFont, extra_marks: set[int]) -> None:
    """Append GPOS for BIZ-only marks without rebuilding JetBrains' layout tables.

    Japanese dakuten uses a top-right anchor. Additional IPA marks use declared
    combining classes with above/below/overlay anchors; these need further proofing.
    """
    cmap = font.getBestCmap()
    definitions, bases = [], []
    classes = set()
    for cp in sorted(extra_marks):
        name = cmap[cp]
        g = font["glyf"][name]
        cc = unicodedata.combining(chr(cp))
        if cp in {0x3099, 0x309A}:
            category, x, y = "Kana", g.xMax, g.yMax
        elif cc in {220, 202}:
            category, x, y = "Below", (g.xMin + g.xMax) // 2, g.yMax
        elif cc == 1:
            category, x, y = "Overlay", (g.xMin + g.xMax) // 2, (g.yMin + g.yMax) // 2
        else:
            category, x, y = "Above", (g.xMin + g.xMax) // 2, g.yMin
        definitions.append(f"markClass {name} <anchor {x} {y}> @BIZ{category};")
        classes.add(category)
    mark_names = {cmap[cp] for cp in extra_marks}
    for name in font.getGlyphOrder():
        g = font["glyf"][name]
        width = font["hmtx"][name][0]
        if name in mark_names or width not in {600, 1200} or not g.numberOfContours:
            continue
        anchors = {
            "Kana": (width - 60, 880),
            "Above": (width // 2, max(g.yMax + 50, 730)),
            "Below": (width // 2, min(g.yMin - 50, -100)),
            "Overlay": (width // 2, (g.yMin + g.yMax) // 2),
        }
        marks = " ".join(f"<anchor {anchors[c][0]} {anchors[c][1]}> mark @BIZ{c}" for c in sorted(classes))
        bases.append(f"pos base {name} {marks};")
    auxiliary = TTFont()
    auxiliary.setGlyphOrder(font.getGlyphOrder())
    feature = "\n".join([
        "languagesystem DFLT dflt;", "languagesystem latn dflt;",
        "languagesystem kana dflt;", "languagesystem hani dflt;",
        *definitions, "feature mark {", *bases, "} mark;",
    ])
    addOpenTypeFeaturesFromString(auxiliary, feature)
    target = font["GPOS"].table
    addition = auxiliary["GPOS"].table
    lookup_offset = len(target.LookupList.Lookup)
    feature_offset = len(target.FeatureList.FeatureRecord)
    target.LookupList.Lookup.extend(addition.LookupList.Lookup)
    target.LookupList.LookupCount = len(target.LookupList.Lookup)
    for record in addition.FeatureList.FeatureRecord:
        record.Feature.LookupListIndex = [i + lookup_offset for i in record.Feature.LookupListIndex]
        target.FeatureList.FeatureRecord.append(record)
    target.FeatureList.FeatureCount = len(target.FeatureList.FeatureRecord)
    records = {r.ScriptTag: r for r in target.ScriptList.ScriptRecord}
    for record in addition.ScriptList.ScriptRecord:
        indices = [i + feature_offset for i in record.Script.DefaultLangSys.FeatureIndex]
        if record.ScriptTag not in records:
            record.Script.DefaultLangSys.FeatureIndex = indices
            target.ScriptList.ScriptRecord.append(record)
        else:
            script = records[record.ScriptTag].Script
            if script.DefaultLangSys is None:
                script.DefaultLangSys = deepcopy(record.Script.DefaultLangSys)
                script.DefaultLangSys.FeatureIndex = []
            for lang in [script.DefaultLangSys, *(r.LangSys for r in script.LangSysRecord)]:
                lang.FeatureIndex.extend(indices)
                lang.FeatureCount = len(lang.FeatureIndex)
    target.ScriptList.ScriptRecord.sort(key=lambda r: r.ScriptTag)
    target.ScriptList.ScriptCount = len(target.ScriptList.ScriptRecord)
    # Preserve existing mark-attachment classes; add only the BIZ mark glyphs.
    gdef = font["GDEF"].table
    if gdef.GlyphClassDef is None:
        gdef.GlyphClassDef = otTables.ClassDef()
        gdef.GlyphClassDef.classDefs = {}
    for name in mark_names:
        gdef.GlyphClassDef.classDefs[name] = 3


def metadata(font: TTFont, latin: TTFont, japanese: TTFont, style: str) -> None:
    names = font["name"]
    # Keep IDs >= 256, which name the original OpenType feature choices.
    names.names = [n for n in names.names if n.nameID >= 256]
    copyright_text = "\n".join(f["name"].getDebugName(0) for f in [latin, japanese])
    values = {
        0: copyright_text, 1: FAMILY, 2: style, 3: f"SOROEMONO-2.000-{style.replace(' ', '')}",
        4: FAMILY + " " + style, 5: "Version 2.000", 6: f"SOROEMONO-{style.replace(' ', '')}",
        13: "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        14: "https://openfontlicense.org", 16: FAMILY, 17: style,
    }
    for name_id, value in values.items():
        names.setName(value, name_id, 3, 1, 0x409)
        names.setName(value, name_id, 0, 4, 0)
    head, hhea, os2 = font["head"], font["hhea"], font["OS/2"]
    head.fontRevision, head.created, head.modified = 2.0, TIMESTAMP, TIMESTAMP
    bold = STYLES[style] == 700
    italic = style in ITALIC_STYLES
    head.macStyle = (1 if bold else 0) | (2 if italic else 0)
    hhea.ascent, hhea.descent, hhea.lineGap = 1020, -300, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = 1020, -300, 0
    os2.fsSelection = (1 << 7) | ((1 << 5) if bold else 0) | ((1 << 0) if italic else 0) | ((1 << 6) if style == "Regular" else 0)
    os2.usWeightClass = STYLES[style]
    os2.usWidthClass = 5
    # CJK dual-width compatibility: advertise the halfwidth cell, as UDEV Gothic
    # does, instead of the merger's all-glyph average (1115). Native applications
    # may use this value as a cell width; Windows acceptance is tested separately.
    os2.xAvgCharWidth = 600
    os2.panose.bProportion = 9
    font["post"].italicAngle = -9 if italic else 0
    bounds = [font["glyf"][name] for name in font.getGlyphOrder() if font["glyf"][name].numberOfContours]
    os2.usWinAscent = max(1020, max(g.yMax for g in bounds))
    os2.usWinDescent = max(300, -min(g.yMin for g in bounds))
    font["post"].isFixedPitch = 1  # CJK dual-width terminal convention; verified separately.
    # Keep stable names for provenance checks, including unencoded Latin alternates.
    font["post"].formatType = 2.0
    font["post"].extraNames = []
    font["post"].mapping = {}
    font.recalcTimestamp = False


def sort_layout_features(font: TTFont) -> None:
    """fontTools' merger concatenates per-script features; restore tag ordering."""
    for tag in ["GSUB", "GPOS"]:
        table = font[tag].table
        ordered = sorted(enumerate(table.FeatureList.FeatureRecord), key=lambda p: p[1].FeatureTag)
        indices = {old: new for new, (old, _) in enumerate(ordered)}
        table.FeatureList.FeatureRecord = [record for _, record in ordered]
        for record in table.ScriptList.ScriptRecord:
            script = record.Script
            for lang in [script.DefaultLangSys, *(r.LangSys for r in script.LangSysRecord)]:
                if lang is not None:
                    lang.FeatureIndex = sorted(indices[i] for i in lang.FeatureIndex)
                    if lang.ReqFeatureIndex != 0xFFFF:
                        lang.ReqFeatureIndex = indices[lang.ReqFeatureIndex]


def build(root: Path, output_dir: Path | None = None, style: str = "Regular") -> Path:
    paths = source_paths(root, style)
    output_dir = output_dir or root / "build" / "formal"
    output_dir.mkdir(parents=True, exist_ok=True)
    latin = TTFont(paths["latin"], recalcTimestamp=False)
    japanese = TTFont(paths["japanese"], recalcTimestamp=False)
    original_latin = TTFont(paths["latin"], recalcTimestamp=False)
    original_japanese = TTFont(paths["japanese"], recalcTimestamp=False)
    marks = prepare_japanese(japanese, latin, style)
    for cp in JP_OVERRIDES:
        set_mapping(latin, cp, None)
    for cp in sorted(WIDE_LATIN):
        source = latin.getBestCmap()[cp]
        name = f"soro.wide{cp:04X}"
        glyph = transformed(latin, source, 1, 1, 300)
        order = list(latin.getGlyphOrder())
        latin["glyf"][name] = glyph
        latin["hmtx"][name] = (1200, glyph.xMin)
        latin.setGlyphOrder([*order, name])
        set_mapping(latin, cp, name)
    with TemporaryDirectory(prefix="soroemono-") as work:
        left, right = Path(work) / "latin.ttf", Path(work) / "japanese.ttf"
        latin.save(left)
        japanese.save(right)
        font = Merger().merge([str(left), str(right)])
    add_mark_positioning(font, set(marks))
    sort_layout_features(font)
    metadata(font, original_latin, original_japanese, style)
    font.cfg["fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER"] = False
    output = output_dir / filename(style)
    if output.resolve() in {p.resolve() for p in paths.values()}:
        raise ValueError("Refusing to overwrite an input font")
    font.save(output)
    report = {
        "version": "2.0.0", "style": style, "sha256": digest(output.read_bytes()),
        "sources": lock(root)[STYLE_SOURCES[style]], "japanese_features": JP_FEATURES,
        "japanese_shear": JAPANESE_SHEAR if style in ITALIC_STYLES else 0,
        "tools": {"python": platform.python_version(), "fonttools": fonttools_version,
                  "unicode": unicodedata.unidata_version, "uv_lock_sha256": digest((root / "uv.lock").read_bytes())},
        "overrides": {f"U+{cp:04X}": "BIZ UDGothic" for cp in sorted(JP_OVERRIDES)},
        "wide_latin_clones": [f"U+{cp:04X}" for cp in sorted(WIDE_LATIN)],
        "extra_marks": [f"U+{cp:04X}" for cp in sorted(marks)],
        "metrics": {"upm": 1000, "half": 600, "full": 1200, "typo": [1020, -300, 0],
                    "x_avg_char_width": font["OS/2"].xAvgCharWidth,
                    "is_fixed_pitch": font["post"].isFixedPitch,
                    "panose_proportion": font["OS/2"].panose.bProportion,
                    "win": [font["OS/2"].usWinAscent, font["OS/2"].usWinDescent]},
        "limitations": ["Additional IPA mark anchors need visual review",
                        "Windows native app acceptance not automated yet"],
    }
    report_name = f"build-{style.lower().replace(' ', '-')}.json"
    (output_dir / report_name).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for name in ["JetBrainsMono", "BIZUDGothic"]:
        shutil.copyfile(root / "resource" / name / "OFL.txt", output_dir / f"OFL-{name}.txt")
    return output
