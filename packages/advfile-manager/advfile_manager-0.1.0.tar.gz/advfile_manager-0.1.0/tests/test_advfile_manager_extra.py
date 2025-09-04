# tests/test_advfile_manager_extra.py
import os
import io
import re
import json
import shutil
import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from ADVfile_manager import (
    File, TextFile, JsonFile, CsvFile, YamlFile, IniFile, TomlFile, XmlFile, ExcelFile,
    ATextFile, AJsonFile, ACsvFile, AYamlFile, AIniFile, ATomlFile, AXmlFile, AExcelFile,
    set_exit_cleanup, cleanup_backups_for_all,
)

# -------------------------------------------------------------------
# Utilities / markers
# -------------------------------------------------------------------

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")

def create_big_text(lines=5000):
    for i in range(1, lines + 1):
        yield f"row-{i}"

# -------------------------------------------------------------------
# Backups: error paths and retention simulation
# -------------------------------------------------------------------

def test_backup_on_missing_file_raises(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    t = TextFile("nofile.txt", str(base))
    # no file written yet
    with pytest.raises(FileNotFoundError):
        _ = t.backup()

def test_restore_without_backups_raises(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    j = JsonFile("x.json", str(base))
    j.write({"v": 1})
    j.clear_backups()  # ensure none
    # explicitly check error
    with pytest.raises(FileNotFoundError):
        j.restore()

def test_ephemeral_backups_manual_cleanup_count(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    set_exit_cleanup(False)  # manual control for test
    t = TextFile("e.txt", str(base))
    with t(keep_backup=False):
        t.write("v1")
        # create user backup explicitly too (should be ephemeral-listed)
        try:
            t.backup()
        except FileNotFoundError:
            pass
    removed = cleanup_backups_for_all()
    assert isinstance(removed, int)
    set_exit_cleanup(True)

# -------------------------------------------------------------------
# Context manager: ensures restore on error, and cache cleared on exit
# -------------------------------------------------------------------

def test_context_manager_clears_cache_on_exit(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    t = TextFile("c.txt", str(base))
    t.write("one"); _ = t.read()  # cache
    with t:
        t.write("two")
    # mutate file externally
    (base / "c.txt").write_text("external-edit", encoding="utf-8")
    # after context exit, cache is cleared -> should read latest from disk
    assert t.read() == "external-edit"

def test_context_manager_restore_on_exception_then_continue(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    j = JsonFile("r.json", str(base))
    j.write({"ok": True})
    with pytest.raises(RuntimeError):
        with JsonFile("r.json", str(base)) as jj:
            jj.write({"broken": 1})
            raise RuntimeError("err")
    # restored to original
    assert j.read() == {"ok": True}
    # continue working after exception
    j.write({"after": 2})
    assert j.read() == {"after": 2}

# -------------------------------------------------------------------
# TextFile: huge file, unicode, regex search
# -------------------------------------------------------------------

def test_textfile_large_unicode_and_regex_search(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    t = TextFile("big.txt", str(base))
    # write multi-lingual + large content
    stream = io.StringIO()
    stream.write("שלום\n")   # Hebrew
    stream.write("こんにちは\n")  # Japanese
    for line in create_big_text(500):
        stream.write(line + "\n")
    t.write(stream.getvalue())

    # regex search for row-4xx
    hits = list(t.search(r"row-4\d{2}$", regex=True, case=True, limit=5))
    assert 1 <= len(hits) <= 5
    # exact line read check
    assert t.read_line(1) == "שלום"

# -------------------------------------------------------------------
# JSON/YAML/TOML: deepish updates and errors
# -------------------------------------------------------------------

def test_json_append_wrong_type_for_dict_root_raises(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    j = JsonFile("conf.json", str(base))
    j.write({"a": 1})
    with pytest.raises(TypeError):
        j.append([1, 2, 3])  # not a dict for dict root

def test_yaml_list_root_append_and_search(tmp_path: Path):
    yaml = pytest.importorskip("yaml")
    base = tmp_path / "data"; base.mkdir()
    y = YamlFile("list.yaml", str(base))
    y.write([{"k": "a"}, {"k": "b"}])
    y.append({"k": "c"})
    assert y.get_item(3) == {"k": "c"}
    hits = list(y.search(pattern="c"))
    assert len(hits) >= 1

def test_toml_merge_nested_and_search(tmp_path: Path):
    # read/write deps
    try:
        import tomllib
    except Exception:
        pytest.importorskip("tomli")
    try:
        import tomli_w
    except Exception:
        pytest.skip("tomli-w not installed")
    base = tmp_path / "data"; base.mkdir()
    t = TomlFile("cfg.toml", str(base))
    t.write({"app": {"name": "demo", "ver": 1}, "flags": {"x": True}})
    t.append({"flags": {"y": False}, "extra": {"note": "ok"}})
    d = t.read()
    assert d["flags"]["x"] is True and d["flags"]["y"] is False
    # search
    hits = list(t.search(pattern="demo"))
    assert len(hits) >= 1

# -------------------------------------------------------------------
# CSV: header inference, missing keys, wrong types, search with columns
# -------------------------------------------------------------------

def test_csv_header_inference_and_missing_keys(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    c = CsvFile("infer.csv", str(base))
    rows = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]  # union: a,b,c
    c.write(rows)
    # append with partial dict
    c.append({"a": 5})
    all_rows = c.read()
    # values are strings after csv reading
    assert all_rows[-1]["a"] == "5" and all_rows[-1].get("b", "") == ""

    # search in a specific column
    hits = list(c.search(pattern="5", columns=["a"]))
    assert len(hits) == 1 and hits[0]["row"] >= 1

def test_csv_append_invalid_iterable_type_raises(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    c = CsvFile("bad.csv", str(base))
    c.write([{"x": 1}])
    with pytest.raises(TypeError):
        c.append(123)  # not dict nor iterable-of-dicts

# -------------------------------------------------------------------
# INI: case-insensitivity and search by value and key
# -------------------------------------------------------------------

def test_ini_case_insensitive_and_search(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    ini = IniFile("s.ini", str(base))
    ini.write({"Server": {"Host": "LOCALHOST", "Port": "8000"}})
    cfg = ini.read()
    # configparser default is case-insensitive sections/keys
    assert cfg["server"]["host"] == "LOCALHOST"
    # search by key (case-insensitive on our side — up to impl)
    hits = list(ini.search(key="host"))
    assert len(hits) >= 1
    # search by value
    hits_v = list(ini.search(value="8000"))
    assert len(hits_v) >= 1

# -------------------------------------------------------------------
# XML: tag-only search, attr mismatch, text pattern, element context
# -------------------------------------------------------------------

def test_xml_tag_only_and_attr_mismatch_and_text(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    x = XmlFile("t.xml", str(base))
    root = ET.Element("root")
    root.append(ET.Element("item", attrib={"kind": "a"}))
    e = ET.Element("item", attrib={"kind": "b"}); e.text = "Hello XML"
    root.append(e)
    x.write(root)

    # tag-only search returns both items
    both = list(x.search(tag="item"))
    assert len(both) == 2 and all(h["context"].tag == "item" for h in both)

    # attr mismatch returns none
    none = list(x.search(tag="item", attr={"kind": "z"}))
    assert len(none) == 0

    # text pattern
    hits = list(x.search(pattern="hello", tag="item", case=False))
    assert len(hits) == 1 and hits[0]["value"] == "Hello XML"

# -------------------------------------------------------------------
# Excel: multiple sheets, missing columns on append, search by sheet
# -------------------------------------------------------------------

def test_excel_multi_sheets_and_search(tmp_path: Path):
    pytest.importorskip("openpyxl")
    base = tmp_path / "data"; base.mkdir()
    x = ExcelFile("m.xlsx", str(base), default_sheet="S1")
    x.write([{"name": "Avi", "score": 100}], sheet="S1")
    x.write([{"name": "Dana", "score": 90}], sheet="S2")

    # append with missing key: should write empty string for missing column
    x.append({"name": "Noa"}, sheet="S1")  # score missing
    rows = x.read(sheet="S1")
    assert rows[-1]["score"] in ("", None)

    # search only on S2
    hits = list(x.search(pattern="Dana", sheet="S2", columns=["name"]))
    assert len(hits) == 1

# -------------------------------------------------------------------
# Unified search: case, regex, limit, value-only
# -------------------------------------------------------------------

def test_unified_search_value_only_and_case_and_limit(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    y = YamlFile("u.yaml", str(base))
    data = {"flags": {"A": True, "B": False}, "names": ["AVI", "Avi", "avi"]}
    y.write(data)

    # value-only search for True
    hits_v = list(y.search(value=True))
    assert any(h["value"] is True for h in hits_v)

    # case-sensitive pattern: should find only "AVI" when case=True and pattern="AVI"
    hits_cs = list(y.search(pattern="AVI", case=True))
    assert any(h["value"] == "AVI" for h in hits_cs)

    # limit
    hits_lim = list(y.search(pattern="avi", case=False, limit=2))
    assert len(hits_lim) == 2

# -------------------------------------------------------------------
# Human-readable size formatting sanity on various types
# -------------------------------------------------------------------

def test_human_size_various_files(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    # Text
    t = TextFile("hs.txt", str(base)); t.write("x"*2048)
    assert hasattr(t, "get_size_human")
    assert isinstance(t.get_size_human(), str)

    # CSV
    c = CsvFile("hs.csv", str(base)); c.write([{"a": 1}])
    assert isinstance(c.get_size_human(), str)

    # Excel (skip if missing)
    try:
        import openpyxl  # noqa: F401
        x = ExcelFile("hs.xlsx", str(base)); x.write([{"a": 1}])
        assert isinstance(x.get_size_human(), str)
    except Exception:
        pass

# -------------------------------------------------------------------
# Async: context, errors, search, sheets
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_context_restore_and_search(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    aj = AJsonFile("ax.json", str(base))
    await aj.awrite({"ok": 1})
    try:
        async with AJsonFile("ax.json", str(base)) as j2:
            await j2.awrite({"bad": True})
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    # restored
    assert await aj.aread() == {"ok": 1}
    # search
    hits = await aj.asearch(pattern="ok")
    assert isinstance(hits, list) and len(hits) >= 1

@pytest.mark.asyncio
async def test_async_excel_multi_sheet_search(tmp_path: Path):
    try:
        import openpyxl  # noqa: F401
    except Exception:
        pytest.skip("openpyxl not installed")
    base = tmp_path / "data"; base.mkdir()
    ax = AExcelFile("ax.xlsx", str(base), default_sheet="S1")
    await ax.awrite([{"name": "Avi", "v": 1}], sheet="S1")
    await ax.awrite([{"name": "Dana", "v": 2}], sheet="S2")
    res = await ax.asearch(pattern="Dana", sheet="S2", columns=["name"])
    assert len(res) == 1

# -------------------------------------------------------------------
# External modification + clear_cache consistency (JSON)
# -------------------------------------------------------------------

def test_external_modify_then_clear_cache_json(tmp_path: Path):
    base = tmp_path / "data"; base.mkdir()
    j = JsonFile("ext.json", str(base))
    j.write({"v": 1})
    # fill cache
    _ = j.read()
    # external overwrite
    (base / "ext.json").write_text(json.dumps({"v": 2}), encoding="utf-8")
    # without clear_cache it would return cached 1; with clear_cache it should see 2
    j.clear_cache()
    assert j.read() == {"v": 2}

# -------------------------------------------------------------------
# End
# -------------------------------------------------------------------
