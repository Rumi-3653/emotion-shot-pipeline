# -*- coding: utf-8 -*-
"""管線狀態機:專案建立、階段推進、決策閘卡、修訂回滾。

階段順序: concept → script → shots → prompts(完成)
三道決策閘: concept / script / shots,各自要 --confirm 之後才能往下走。
revise 指令會把該閘退回 pending 並在 revisions.log 記一筆批註。
"""
import json
import datetime
from pathlib import Path

STAGES = ["concept", "script", "shots", "prompts"]
GATES = ["concept", "script", "shots"]

CONCEPT_TEMPLATE = """# 概念定調(concept)

> 四個問題全部回答完才算定調。這一步想清楚,後面全部省力。

## 1. 切入視角
(誰的眼睛看這個故事?為什麼是他?)

## 2. 核心意象
(一個貫穿全片、可以反覆出現的視覺符號)

## 3. 情緒弧線
(觀眾從什麼情緒進場,經過什麼,帶著什麼離場)

## 4. 戲劇問題
(開場 10 秒內立起、結尾必須回答的那個問題)

---

## 梗概(synopsis)
(定調通過後,在這裡寫 150~300 字梗概)

## 正文(treatment)
(梗概通過後,分場寫正文,每場標情緒)
"""


def root():
    return Path(__file__).resolve().parent.parent


def project_dir(name):
    return root() / "projects" / name


def load_project(name):
    f = project_dir(name) / "project.json"
    if not f.exists():
        raise SystemExit(f"找不到專案「{name}」——先跑 drama.py new {name}")
    return json.loads(f.read_text(encoding="utf-8"))


def save_project(name, data):
    f = project_dir(name) / "project.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def new_project(name, title, style="cinema_real", aspect="9:16"):
    d = project_dir(name)
    if d.exists():
        raise SystemExit(f"專案「{name}」已存在: {d}")
    (d / "characters").mkdir(parents=True)
    (d / "output").mkdir()
    (d / "concept.md").write_text(CONCEPT_TEMPLATE, encoding="utf-8")
    data = {
        "name": name,
        "title": title,
        "style_preset": style,
        "aspect": aspect,
        "created": datetime.date.today().isoformat(),
        "gates": {g: "pending" for g in GATES},
    }
    save_project(name, data)
    return d


def current_stage(data):
    for g in GATES:
        if data["gates"][g] != "confirmed":
            return g
    return "prompts"


def confirm_gate(name, stage):
    data = load_project(name)
    if stage not in GATES:
        raise SystemExit(f"沒有「{stage}」這道閘,只有: {'、'.join(GATES)}")
    idx = GATES.index(stage)
    for earlier in GATES[:idx]:
        if data["gates"][earlier] != "confirmed":
            raise SystemExit(f"「{earlier}」閘還沒過,不能先過「{stage}」")
    data["gates"][stage] = "confirmed"
    save_project(name, data)
    return current_stage(data)


def revise(name, stage, note):
    data = load_project(name)
    if stage not in GATES:
        raise SystemExit(f"沒有「{stage}」這道閘,只有: {'、'.join(GATES)}")
    idx = GATES.index(stage)
    for g in GATES[idx:]:
        data["gates"][g] = "pending"
    save_project(name, data)
    log = project_dir(name) / "revisions.log"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] 退回「{stage}」: {note}\n")
    return current_stage(data)


def status_text(name):
    data = load_project(name)
    stage = current_stage(data)
    marks = {"confirmed": "✅", "pending": "⬜"}
    lines = [
        f"專案《{data['title']}》({name})",
        f"風格: {data['style_preset']}|畫幅: {data['aspect']}|建立: {data['created']}",
        "",
        "決策閘進度:",
    ]
    for g in GATES:
        cur = " ← 目前在這" if g == stage else ""
        lines.append(f"  {marks[data['gates'][g]]} {g}{cur}")
    if stage == "prompts":
        out = project_dir(name) / "output"
        done = (out / "prompts_all.md").exists() and (out / "music_prompt.md").exists()
        lines.append(f"  {'✅' if done else '⬜'} prompts(產出)"
                     + ("" if done else " ← 目前在這,跑 drama.py prompts"))
    log = project_dir(name) / "revisions.log"
    if log.exists():
        lines += ["", "修訂紀錄:"] + ["  " + x for x in
                  log.read_text(encoding="utf-8").strip().splitlines()]
    return "\n".join(lines)
