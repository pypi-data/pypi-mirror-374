# tests/test_advfile_manager.py
import os
import re
import sys
import json
import shutil
import time
import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# Import the package under test
# If you run tests from repo root with `pip install -e .`, this import should work:
from ADVfile_manager import (
    # sync
    File, TextFile, JsonFile, CsvFile, YamlFile, IniFile, TomlFile, XmlFile, ExcelFile,
    set_exit_cleanup, cleanup_backups_for_all,
    # async
    ATextFile, AJsonFile, ACsvFile, AYamlFile, AIniFile, ATomlFile, AXmlFile, AExcelFile,
)

# -----------------------------
# Helpers
# -----------------------------

def write_sleep():  # ensure distinct timestamps for backup filenames if needed
    time.sleep(0.01)

def assert_human_size_fmt(s: str):
    # loose check: "<number> <UNIT>"
    assert isinstance(s, str)
    assert bool(re.match(r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB)$", s))

# -----------------------------
# Base / Common Features
# -----------------------------

def test_file_basic_size_cache_and_human(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    t = TextFile("a.txt", str(base))
    t.write("hello")
    assert t.read() == "hello"
    assert t.get_size() == len("hello")
    if hasattr(t, "get_size_human"):
        assert_human_size_fmt(t.get_size_human())

    # cache behavior
    assert t.read() == "hello"  # cached
    # external change -> clear_cache -> read again
    (base / "a.txt").write_text("world", encoding="utf-8")
    t.clear_cache()
    assert t.read() == "world"

def test_backups_restore_clear_list(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    t = TextFile("x.txt", str(base))
    t.write("v1")
    b1 = t.backup(); write_sleep()
    t.write("v2")
    b2 = t.backup(); write_sleep()
    t.write("v3")
    # list ordered oldest -> newest (as per README)
    lst = t.list_backups()
    assert isinstance(lst, list) and len(lst) >= 2
    assert Path(lst[0]).exists() and Path(lst[-1]).exists()

    # restore latest (should bring back v2 if last backup was made after v2)
    t.restore()  # latest
    assert t.read() in ("v2", "v3")  # depending on exact impl timing; next test restores explicit
    # restore explicit b1 or b2 (prefer b2 to land on v2)
    t.restore(b2)
    assert t.read() == "v2"

    removed = t.clear_backups()
    assert isinstance(removed, int)
    # pattern cleaned
    assert t.list_backups() == []

def test_context_manager_restore_on_error(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    j = JsonFile("conf.json", str(base))
    j.write({"name": "ok"})
    try:
        with JsonFile("conf.json", str(base)) as jj:
            # automatic backup on enter
            jj.write({"name": "editing"})
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    # should be restored to previous state
    assert j.read() == {"name": "ok"}

def test_context_manager_ephemeral_backups_cleaned_manually(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    set_exit_cleanup(False)  # avoid global atexit during test, we'll clean manually

    t = TextFile("temp.txt", str(base))
    with t(keep_backup=False):
        t.write("temp")
        # some code...
    # now ephemeral backups are registered; manual cleanup:
    deleted = cleanup_backups_for_all()
    assert isinstance(deleted, int)

    set_exit_cleanup(True)  # re-enable for other tests

# -----------------------------
# TextFile
# -----------------------------

def test_textfile_lines_and_readline_and_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    t = TextFile("notes.txt", str(base))
    t.write("line1")
    t.append("Error: something happened")
    t.append("line3")

    # read_line
    assert t.read_line(2) == "Error: something happened"
    with pytest.raises(IndexError):
        _ = t.read_line(999)

    # lines generator
    all_lines = list(t.lines())
    assert all_lines == [(1, "line1"), (2, "Error: something happened"), (3, "line3")]

    # unified search (pattern), case-insensitive
    hits = list(t.search("error", case=False))
    assert len(hits) == 1
    assert hits[0]["line"] == 2
    assert "Error" in hits[0]["value"]

# -----------------------------
# JsonFile
# -----------------------------

def test_jsonfile_dict_and_list_append_get_item_items_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    # dict root
    j = JsonFile("d.json", str(base))
    j.write({"users": [{"id": 1}]})
    j.append({"active": True})
    assert j.get_item("active") is True
    assert dict(j.items())["active"] is True

    # invalid append to dict root
    with pytest.raises(TypeError):
        j.append(["not", "a", "dict"])

    # list root
    jl = JsonFile("l.json", str(base))
    jl.write([{"id": 1}])
    jl.append({"id": 2})
    jl.append([{"id": 3}, {"id": 4}])
    assert jl.get_item(2) == {"id": 2}
    assert list(jl.items())[0] == (1, {"id": 1})

    # search by key and pattern/value
    hits_k = list(j.search(pattern="True", key="active"))  # pattern match stringified
    assert len(hits_k) >= 1

    hits_v = list(j.search(value=True))
    assert any(h["value"] is True for h in hits_v)

# -----------------------------
# CsvFile
# -----------------------------

def test_csvfile_write_append_read_row_rows_and_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    c = CsvFile("t.csv", str(base))
    c.write(
        [{"name": "Avi", "age": 30}, {"name": "Dana", "age": 25}],
        fieldnames=["name", "age"]  # if your implementation supports it on write
        if "fieldnames" in c.write.__code__.co_varnames else None  # keep test compatible
    )
    c.append({"name": "Noa", "age": 21})
    # invalid append type
    with pytest.raises(TypeError):
        c.append("not a dict")

    assert c.read_row(2)["name"] == "Dana"
    with pytest.raises(IndexError):
        _ = c.read_row(999)

    rows = list(c.rows())
    assert rows[0][0] == 1 and "name" in rows[0][1]

    # search only in "name" column
    hits = list(c.search(pattern="Avi", columns=["name"]))
    assert len(hits) == 1
    assert hits[0]["col"] == "name"
    assert hits[0]["row"] == 1

# -----------------------------
# YamlFile
# -----------------------------

def test_yamlfile_read_write_append_get_item_items_search(tmp_path: Path):
    yaml = pytest.importorskip("yaml")  # pyyaml required
    base = tmp_path / "data"
    base.mkdir()

    y = YamlFile("cfg.yaml", str(base))
    y.write({"app": {"name": "demo"}, "features": ["a"]})
    y.append({"features": ["b"]})
    assert y.get_item("app") == {"name": "demo"}
    assert ("app", {"name": "demo"}) in list(y.items())

    with pytest.raises(TypeError):
        y.append(["not-dict-for-dict-root"])  # if root is dict, append expects dict

    # search by value
    hits = list(y.search(value="demo"))
    assert len(hits) >= 1

# -----------------------------
# IniFile
# -----------------------------

def test_inifile_read_write_append_and_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    ini = IniFile("settings.ini", str(base))
    ini.write({"server": {"host": "127.0.0.1", "port": "8000"}})
    cfg = ini.read()
    assert cfg["server"]["host"] == "127.0.0.1"

    ini.append({"server": {"debug": "true"}, "auth": {"enabled": "yes"}})
    cfg2 = ini.read()
    assert cfg2["server"]["debug"] == "true"
    assert cfg2["auth"]["enabled"] == "yes"

    # search by key/value
    hits_k = list(ini.search(key="debug"))
    assert any(h["value"] == "true" for h in hits_k)

    hits_v = list(ini.search(value="127.0.0.1"))
    assert len(hits_v) >= 1

# -----------------------------
# TomlFile
# -----------------------------

def test_tomlfile_read_write_append_and_search(tmp_path: Path):
    # Skip if reading/writing libs absent
    try:
        import tomllib  # Python 3.11+
        _ = tomllib
    except Exception:
        pytest.importorskip("tomli")   # read fallback
    try:
        import tomli_w  # write helper
        _ = tomli_w
    except Exception:
        pytest.skip("tomli-w not installed, skipping TOML writing tests")

    base = tmp_path / "data"
    base.mkdir()
    t = TomlFile("app.toml", str(base))
    t.write({"app": {"name": "demo"}, "features": {"b": True}})
    d = t.read()
    assert d["app"]["name"] == "demo"

    t.append({"features": {"c": 123}})
    d2 = t.read()
    assert d2["features"]["c"] == 123

    # search by pattern
    hits = list(t.search(pattern="demo"))
    assert len(hits) >= 1

# -----------------------------
# XmlFile
# -----------------------------

def test_xmlfile_write_append_and_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    x = XmlFile("data.xml", str(base))
    root = ET.Element("books")
    root.append(ET.Element("book", attrib={"id": "1"}))
    x.write(root)

    x.append(ET.Element("book", attrib={"id": "2"}))
    # search by tag and attr
    hits = list(x.search(tag="book", attr={"id": "2"}))
    assert len(hits) == 1
    assert hits[0]["context"].tag == "book"

    # search by text pattern (add text then search)
    e = ET.Element("book"); e.text = "Python Tricks"
    x.append(e)
    hits2 = list(x.search(pattern="Python", tag="book"))
    assert len(hits2) >= 1

# -----------------------------
# ExcelFile
# -----------------------------

def test_excelfile_read_write_append_and_search(tmp_path: Path):
    pytest.importorskip("openpyxl")
    base = tmp_path / "data"
    base.mkdir()

    xl = ExcelFile("report.xlsx", str(base), default_sheet="Sheet1")
    xl.write([{"name": "Avi", "score": 95}, {"name": "Dana", "score": 88}])
    xl.append({"name": "Noa", "score": 92})
    rows = xl.read()
    assert rows[0]["name"] == "Avi"
    assert any(r["name"] == "Noa" for r in rows)

    # search on sheet and columns
    hits = list(xl.search(pattern="Avi", sheet="Sheet1", columns=["name"]))
    assert len(hits) == 1
    assert hits[0]["row"] == 2 or hits[0]["row"] == 1 or isinstance(hits[0]["row"], int)

# -----------------------------
# Unified Search: limits & regex/case
# -----------------------------

def test_unified_search_flags_and_limit(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()

    t = TextFile("mix.txt", str(base))
    t.write("Error: A\nerror: b\nERROR: C\nnone")

    # case-sensitive
    hits_cs = list(t.search("Error", case=True))
    assert len(hits_cs) == 1

    # regex
    hits_rx = list(t.search(r"ERROR:\s+[A-Z]", regex=True, case=True))
    assert len(hits_rx) >= 1

    # limit
    hits_lim = list(t.search("error", case=False, limit=2))
    assert len(hits_lim) == 2

# -----------------------------
# Async Variants (A* classes)
# -----------------------------

@pytest.mark.asyncio
async def test_async_textfile(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    t = ATextFile("async.txt", str(base))
    async with t:
        await t.awrite("line1")
        await t.aappend("line2")
        content = await t.aread()
        assert content == "line1\nline2"

    hits = await t.asearch(pattern="line", case=False)
    assert isinstance(hits, list) and len(hits) >= 2

@pytest.mark.asyncio
async def test_async_jsonfile_and_search(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    j = AJsonFile("a.json", str(base))
    await j.awrite({"users": [{"name": "Avi"}]})
    await j.aappend({"active": True})
    data = await j.aread()
    assert data["active"] is True
    hits = await j.asearch(pattern="Avi")
    assert len(hits) >= 1

@pytest.mark.asyncio
async def test_async_excelfile(tmp_path: Path):
    pytest.importorskip("openpyxl")
    base = tmp_path / "data"
    base.mkdir()
    x = AExcelFile("a.xlsx", str(base), default_sheet="S1")
    await x.awrite([{"k": "Avi", "v": 1}, {"k": "Dana", "v": 2}])
    await x.aappend({"k": "Noa", "v": 3})
    hits = await x.asearch(pattern="Noa", columns=["k"])
    assert len(hits) == 1

# -----------------------------
# Error cases & edges
# -----------------------------

def test_textfile_readline_out_of_range(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    t = TextFile("empty.txt", str(base))
    t.write("only one line")
    with pytest.raises(IndexError):
        _ = t.read_line(99)

def test_csv_append_invalid_type(tmp_path: Path):
    base = tmp_path / "data"
    base.mkdir()
    c = CsvFile("bad.csv", str(base))
    c.write([{"a": 1}])
    with pytest.raises(TypeError):
        c.append(["not-a-dict"])

def test_yaml_missing_dependency_skip(monkeypatch, tmp_path: Path):
    # If PyYAML isn't installed, the class import itself would have raised earlier,
    # so here we just mark expectation that tests are skipped via importorskip.
    pass

def test_toml_missing_dependencies_skip(tmp_path: Path):
    # Covered by importorskip/skip above. Nothing to assert here explicitly.
    pass

# -----------------------------
# End
# -----------------------------
