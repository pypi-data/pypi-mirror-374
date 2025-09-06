import os, yaml, polib, pathlib, sys, glob
from datetime import datetime, timezone
from typing import Mapping, Any

# ────────────────────────────────────────────────
# 1) 유틸리티
# ────────────────────────────────────────────────
def flatten(node: Mapping[str, Any], prefix: str = "") -> dict[str, str]:
    """중첩 딕셔너리를 'a.b.c': 'value' 형태로 평탄화"""
    items: dict[str, str] = {}
    for k, v in node.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(flatten(v, key))
        else:
            items[key] = v
    return items


def deep_merge(dst: dict, src: dict) -> dict:
    """재귀적으로 딕셔너리를 머지(중첩 구조 유지)"""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            dst[k] = deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def yaml2trans(yaml_file_path: str, translations_dir: str):
    yaml_file  = pathlib.Path(os.path.expanduser(yaml_file_path))
    translations_dir = pathlib.Path(os.path.expanduser(translations_dir))
    data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    for lang, tree in data.items():
        mapping = flatten(tree)              # {'home.title': '...', ...}

        po_path = translations_dir / lang / "LC_MESSAGES" / "messages.po"
        po_path.parent.mkdir(parents=True, exist_ok=True)

        po = polib.POFile()
        po.metadata = {
            "Language": lang,
            "PO-Revision-Date": now,
            "Content-Type": "text/plain; charset=utf-8",
            "Plural-Forms": (
                "nplurals=1; plural=0;" if lang == "ko"
                else "nplurals=2; plural=(n != 1);"
            ),
        }

        for msgid, msgstr in mapping.items():
            po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

        po.save(po_path)
        po.save_as_mofile(po_path.with_suffix(".mo"))
        print("✓", po_path.relative_to(pathlib.Path.cwd()))


# ────────────────────────────────────────────────
# 2) 메인 함수
# ────────────────────────────────────────────────
def yaml_dir2trans(yaml_dir: str, translations_dir: str ):
    """
    yaml_dir 안의 모든 .yml/.yaml 파일을 읽어 언어별 messages.po/.mo 파일 생성
    """
    yaml_dir = pathlib.Path(os.path.expanduser(yaml_dir))
    translations_dir = pathlib.Path(os.path.expanduser(translations_dir))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M %z")

    # ── 2-1. 디렉터리 전체를 메모리에 머지 ──────────────────────────
    merged: dict[str, dict] = {}          # {lang: {nested dict}}
    for path in sorted(yaml_dir.glob("*.y*ml")):
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for lang, tree in data.items():
            merged.setdefault(lang, {})
            merged[lang] = deep_merge(merged[lang], tree)

    # ── 2-2. 언어별로 PO/MO 생성 ───────────────────────────────────
    for lang, tree in merged.items():
        mapping = flatten(tree)            # {'home.title': '...', ...}

        po_path = translations_dir / lang / "LC_MESSAGES" / "messages.po"
        po_path.parent.mkdir(parents=True, exist_ok=True)

        po = polib.POFile()
        po.metadata = {
            "Language": lang,
            "PO-Revision-Date": now,
            "Content-Type": "text/plain; charset=utf-8",
            "Plural-Forms": (
                "nplurals=1; plural=0;" if lang == "ko"
                else "nplurals=2; plural=(n != 1);"
            ),
        }

        for msgid, msgstr in mapping.items():
            po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

        po.save(po_path)
        po.save_as_mofile(po_path.with_suffix(".mo"))
        rel = po_path.relative_to(pathlib.Path.cwd())
        print(f"✓ {rel} → .mo 완료")

