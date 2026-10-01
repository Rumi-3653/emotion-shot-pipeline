# -*- coding: utf-8 -*-
"""emotion-shot-pipeline CLI:情緒驅動的短片分鏡 → 生成 prompt 編譯器。

流程: new → (寫 concept.md) → gate concept → (寫劇本進 concept.md 正文區)
      → gate script → (寫 script.json + characters/) → validate → gate shots
      → prompts / music → 拿 output/ 去生片。

任何一步不滿意: revise <name> --stage <閘> --note "批註",該閘之後全部退回。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

from core import pipeline, schema, styles
from core.music_director import build_music_prompt
from core.prompt_gen import render_all


def _load_shots(name):
    f = pipeline.project_dir(name) / "script.json"
    if not f.exists():
        raise SystemExit(f"還沒有 script.json: {f}")
    return json.loads(f.read_text(encoding="utf-8"))


def _load_characters(name):
    chars = {}
    for f in (pipeline.project_dir(name) / "characters").glob("*.json"):
        c = json.loads(f.read_text(encoding="utf-8"))
        chars[c.get("name", f.stem)] = c
    return chars


def cmd_new(a):
    d = pipeline.new_project(a.name, a.title or a.name, a.style, a.aspect)
    print(f"✅ 已建立專案: {d}")
    print(f"下一步: 編輯 {d / 'concept.md'} 回答四個定調問題,然後 gate {a.name} --stage concept --confirm")


def cmd_status(a):
    print(pipeline.status_text(a.name))


def cmd_list_styles(a):
    print(styles.list_styles_text())


def cmd_validate(a):
    shots = _load_shots(a.name)
    chars = _load_characters(a.name)
    errors = schema.validate_script(shots)
    for cname, c in chars.items():
        errors += [f"[{cname}] {e}" for e in schema.validate_character(c)]
    known = set(chars)
    for s in shots:
        for n in s.get("characters", []) or []:
            if n not in known:
                errors.append(f"⚠ 鏡號{s.get('id')} 用到角色「{n}」但 characters/ 沒有他的檔案")
    hard, warn = schema.split_errors(errors)
    for w in warn:
        print(w)
    if hard:
        print("\n❌ 驗證失敗:")
        for e in hard:
            print("  " + e)
        raise SystemExit(1)
    emos = [s["emotion"] for s in shots]
    print(f"\n✅ 驗證通過: {len(shots)} 顆鏡頭 / {len(chars)} 個角色檔")
    print("風格配對建議(依情緒弧線):")
    for key, score, hits in styles.match_styles(emos)[:3]:
        print(f"  {styles.STYLE_PRESETS[key]['zh']} ({key}) 契合度 {score:.0%} 命中: {'、'.join(hits) or '—'}")


def cmd_gate(a):
    if a.confirm:
        stage = pipeline.confirm_gate(a.name, a.stage)
        print(f"✅ 「{a.stage}」閘已通過。目前階段: {stage}")
    else:
        print("要通過閘卡請加 --confirm;要退回請用 revise 指令。")


def cmd_revise(a):
    stage = pipeline.revise(a.name, a.stage, a.note)
    print(f"↩ 已退回「{a.stage}」閘(其後閘卡一併重開)。目前階段: {stage}\n批註已記入 revisions.log")


def cmd_prompts(a):
    data = pipeline.load_project(a.name)
    if pipeline.current_stage(data) != "prompts":
        raise SystemExit(f"三道閘還沒走完(目前卡在 {pipeline.current_stage(data)}),先過閘再產 prompt。")
    shots = _load_shots(a.name)
    hard, _ = schema.split_errors(schema.validate_script(shots))
    if hard:
        raise SystemExit("script.json 驗證有硬錯誤,先跑 validate 修完。")
    chars = _load_characters(a.name)
    out = pipeline.project_dir(a.name) / "output"
    md = render_all(shots, chars, data["style_preset"], data["title"], data["aspect"])
    (out / "prompts_all.md").write_text(md, encoding="utf-8")
    print(f"✅ 已輸出 {out / 'prompts_all.md'}({len(shots)} 顆鏡頭 × 首幀/Kling/Seedance 三組)")


def cmd_music(a):
    data = pipeline.load_project(a.name)
    if pipeline.current_stage(data) != "prompts":
        raise SystemExit(f"三道閘還沒走完(目前卡在 {pipeline.current_stage(data)}),先過閘再產配樂 prompt。")
    shots = _load_shots(a.name)
    hard, _ = schema.split_errors(schema.validate_script(shots))
    if hard:
        raise SystemExit("script.json 驗證有硬錯誤,先跑 validate 修完。")
    out = pipeline.project_dir(a.name) / "output"
    md = build_music_prompt(shots, data["style_preset"], data["title"])
    (out / "music_prompt.md").write_text(md, encoding="utf-8")
    print(f"✅ 已輸出 {out / 'music_prompt.md'}")


def main():
    ap = argparse.ArgumentParser(prog="drama", description="emotion-shot-pipeline:情緒驅動的短片分鏡 → 生成 prompt 編譯器")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="建立新專案")
    p.add_argument("name")
    p.add_argument("--title", default=None)
    p.add_argument("--style", default="cinema_real", choices=list(styles.STYLE_PRESETS))
    p.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("status", help="看專案進度(orchestrator 回報)")
    p.add_argument("name")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("list-styles", help="列出風格 preset")
    p.set_defaults(fn=cmd_list_styles)

    p = sub.add_parser("validate", help="驗證 script.json 與角色檔,並給風格配對建議")
    p.add_argument("name")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("gate", help="決策閘卡: --confirm 通過")
    p.add_argument("name")
    p.add_argument("--stage", required=True)
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(fn=cmd_gate)

    p = sub.add_parser("revise", help="退回某道閘並記批註")
    p.add_argument("name")
    p.add_argument("--stage", required=True)
    p.add_argument("--note", required=True)
    p.set_defaults(fn=cmd_revise)

    p = sub.add_parser("prompts", help="產出全片 prompt 包(首幀+Kling+Seedance)")
    p.add_argument("name")
    p.set_defaults(fn=cmd_prompts)

    p = sub.add_parser("music", help="音樂總監: 產出 Suno prompt + 混音備註")
    p.add_argument("name")
    p.set_defaults(fn=cmd_music)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
