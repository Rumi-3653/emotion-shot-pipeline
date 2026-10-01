# -*- coding: utf-8 -*-
"""Prompt 產生器:script.json + 角色檔 + 風格 preset → 每 shot 的
首幀圖 prompt、Kling img2video prompt、Seedance prompt。

Kling 與 Seedance 都吃中文,主體描述走中文,風格關鍵字保留英文。
Seedance 用 @角色名 引用格式(先在平台上建好角色資產)。
"""
from .styles import STYLE_PRESETS


def _s(text):
    """去尾端句號再補一個,避免欄位串接出現「。。」。"""
    return str(text).rstrip("。").strip() + "。"


def _c(text):
    """Seedance 逗號串接用:去尾端句讀。"""
    return str(text).rstrip("。,、").strip()


def _char_desc(shot, characters):
    """把 shot 出場角色的外貌注入 prompt。"""
    descs = []
    for name in shot.get("characters", []) or []:
        c = characters.get(name)
        if c:
            descs.append(f"{name}({c['appearance']})")
        else:
            descs.append(name)
    return ";".join(descs)


def shot_prompts(shot, characters, style_key, aspect="9:16"):
    p = STYLE_PRESETS[style_key]
    chars = _char_desc(shot, characters)
    subject = _s(shot['scene']) + _s(shot['action'])
    if chars:
        subject = _s(chars) + subject

    props = shot.get("props") or []
    props_txt = "畫面內物件狀態:" + ";".join(_c(x) for x in props) + "。" if props else ""

    tail = f", {aspect} vertical composition" if aspect == "9:16" else ""
    ff = shot.get("first_frame")
    if ff:
        # 起幅欄:首幀只畫鏡頭運動的起點,不帶 action 全程、不帶 visual_beat(常是鏡中動態)。
        # 角色外貌只在起幅文字點名該角色時才注入——frame0 沒有人就別把人描進畫面。
        ff_named = [n for n in (shot.get("characters") or []) if n in ff]
        ff_chars = _char_desc({"characters": ff_named}, characters)
        body = _s(shot['scene']) + (_s(ff_chars) if ff_chars else "") + _s(ff)
        first_frame = (
            f"{body}{props_txt}環境氛圍:{_s(shot['sensory_env'])}"
            f"情緒基調:{shot['emotion']}。 {p['keywords']}{tail}"
        )
    else:
        first_frame = (
            f"{subject}{props_txt}環境氛圍:{_s(shot['sensory_env'])}"
            f"視覺重點:{_s(shot['visual_beat'])}情緒基調:{shot['emotion']}。 "
            f"{p['keywords']}{tail}"
        )

    kling_video = (
        f"{_s(shot['camera'])}{_s(shot['action'])}情緒:{shot['emotion']},"
        f"動作幅度小而準確,不要無關的肢體晃動。鏡頭穩定,不要突然變速。避免憑空出現或消失的物件、額外的人物入鏡。"
    )

    seedance_names = "".join(f"@{n} " for n in (shot.get("characters") or []))
    seedance_props = ("," + ",".join(_c(x) for x in props)) if props else ""
    seedance = (
        f"{seedance_names}{_c(shot['scene'])},{_c(shot['action'])},"
        f"{_c(shot['camera'])},{_c(shot['sensory_env'])}{seedance_props},"
        f"情緒{shot['emotion']},{p['keywords']}"
    )

    return {
        "first_frame": first_frame,
        "kling_video": kling_video,
        "seedance": seedance,
        "negative": p["negative"],
    }


def render_shot_md(shot, characters, style_key, aspect="9:16"):
    pr = shot_prompts(shot, characters, style_key, aspect)
    dlg = shot.get("dialogue") or "(無)"
    ios = shot.get("inner_os") or "(未填)"
    props = shot.get("props") or []
    props_line = [f"- 道具狀態: {';'.join(props)}"] if props else []
    return "\n".join([
        f"## 鏡號 {shot['id']}|{shot['scene']}|{shot['duration_s']}s|情緒:{shot['emotion']}",
        "",
        f"- 台詞/旁白: {dlg}",
        f"- 內心OS: {ios}",
        f"- 視覺節拍: {shot['visual_beat']}",
        *props_line,
        "",
        "### ① 首幀圖 prompt(Nano Banana / Seedream / Midjourney 皆可)",
        "```", pr["first_frame"], "```",
        "",
        f"### ② Kling(img2video,首幀=①的產出,{aspect},5s 檔)",
        "```", pr["kling_video"], "```",
        f"負面提示:`{pr['negative']}`",
        "",
        "### ③ Seedance(文生影片或 img2video 皆可)",
        "```", pr["seedance"], "```",
        "",
    ])


def render_all(shots, characters, style_key, title, aspect="9:16"):
    p = STYLE_PRESETS[style_key]
    head = [
        f"# 《{title}》全片 prompt 包",
        "",
        f"- 風格 preset: {p['zh']} (`{style_key}`)",
        f"- 畫幅: {aspect}",
        f"- 鏡頭數: {len(shots)},總長 {sum(float(s['duration_s']) for s in shots):.0f} 秒",
        f"- 用法: 每顆鏡頭先用①生首幀圖 → 挑圖 → 餵②(Kling)或③(Seedance)生片段 → ffmpeg 串接",
        f"- 角色一致性: 先生成一張人物主參考圖(乾淨正面或四分之三臉的定裝照),"
        f"之後每顆鏡的①都掛它當角色參考(Kling 角色參考/Seedream・Nano Banana 參考圖);"
        f"Seedance 用同一張主參考建 @角色 資產再引用。臉部特寫鏡是必鎖優先級",
        f"- 畫作一致性: 片中若有「會演進的畫/物」,先用最能看清它的那顆鏡生一張 hero plate,"
        f"其他露出鏡以同一張 plate 參考圖/inpaint 衍生,靠圖鎖不靠文字鎖",
        "",
        "---",
        "",
    ]
    body = [render_shot_md(s, characters, style_key, aspect) for s in shots]
    return "\n".join(head) + "\n".join(body)
