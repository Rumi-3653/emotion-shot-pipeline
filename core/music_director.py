# -*- coding: utf-8 -*-
"""音樂總監:讀 script.json 的情緒弧線,輸出 Suno prompt + 混音備註。

規則來源是實戰經驗:
- 高潮前要有鋪陳,高潮後要留白再收尾(brooding 開場→高潮→留白收,比全程高動態好聽)。
- 旁白混音走 sidechain ducking,音樂在人聲段自動壓低。
"""
from .schema import EMOTIONS
from .styles import STYLE_PRESETS

# Suno prompt 用英文情緒詞,中文只留在給人看的結構指示裡
EMOTION_EN = {
    "平靜": "calm", "溫暖": "warm", "期待": "anticipation", "喜悅": "joy",
    "好奇": "curious", "緊張": "tense", "恐懼": "fearful", "悲傷": "sorrowful",
    "憤怒": "angry", "孤獨": "lonely", "釋然": "relieved", "敬畏": "awe",
    "決絕": "resolute", "失落": "dejected",
}


def _arc(shots):
    """回傳 [(id, emotion, valence, arousal, start_s, dur_s)]。"""
    out, t = [], 0.0
    for s in shots:
        v, a = EMOTIONS[s["emotion"]]
        out.append((s["id"], s["emotion"], v, a, t, float(s["duration_s"])))
        t += float(s["duration_s"])
    return out


def build_music_prompt(shots, style_key, title=""):
    arc = _arc(shots)
    total = sum(x[5] for x in arc)
    avg_v = sum(x[2] for x in arc) / len(arc)
    avg_a = sum(x[3] for x in arc) / len(arc)
    peak = max(arc, key=lambda x: x[3])
    opening, closing = arc[0], arc[-1]
    style = STYLE_PRESETS[style_key]

    key_hint = "minor key" if avg_v < 0.05 else "major key"
    bpm = int(58 + avg_a * 74)  # 58~132 之間依平均能量落點

    # 找留白點:高潮後 arousal 掉幅 >= 0.35 的第一個 shot
    breath = None
    peak_i = arc.index(peak)
    for prev, cur in zip(arc[peak_i:], arc[peak_i + 1:]):
        if prev[3] - cur[3] >= 0.35:
            breath = cur
            break

    def pct(t):
        return f"{int(round(t / total * 100))}%"

    lines = [
        f"# 音樂總監輸出{'——' + title if title else ''}",
        "",
        f"全片 {total:.0f} 秒 / {len(arc)} 顆鏡頭 / 風格 preset: {style['zh']}",
        f"情緒弧線: " + " → ".join(f"{x[1]}({x[0]})" for x in arc),
        "",
        "## Suno prompt(直接貼)",
        "```",
        f"{style['music_palette']}, {key_hint}, around {bpm} bpm, "
        f"instrumental, no vocals, cinematic short-film underscore, "
        f"emotional arc: opens with a {EMOTION_EN[opening[1]]} mood, "
        f"builds to a {EMOTION_EN[peak[1]]} peak, "
        f"then falls into silence before a {EMOTION_EN[closing[1]]} resolution",
        "```",
        "",
        "## 結構指示(挑版本時對照)",
        f"- 開場({pct(0)}~): 錨定「{opening[1]}」,低動態進場,別搶戲",
        f"- 高潮(約 {pct(peak[4])} 處,鏡號{peak[0]}「{peak[1]}」): 全曲能量頂點,"
        f"前一段必須有明顯堆疊,不能平地起高樓",
    ]
    if breath:
        lines.append(
            f"- 留白(約 {pct(breath[4])} 處,鏡號{breath[0]}): 高潮後抽掉配器,"
            f"只留一件樂器或環境聲——這口氣是整支片的呼吸"
        )
    else:
        lines.append("- 留白: 弧線裡沒有明顯的能量驟降點,建議收尾前人工留 2 秒空拍")
    lines += [
        f"- 收尾({pct(closing[4])}~): 落在「{closing[1]}」,"
        + ("向上收,尾音亮" if closing[2] > 0 else "向下收,尾音沉,不要圓滿感"),
        "",
        "## 混音備註",
        "- 有旁白/台詞的段落走 sidechain ducking,音樂 -8dB 左右自動讓位",
        "- 挑版本標準: 開場收斂、高潮有堆疊、收尾有留白的優先;全程同動態的直接淘汰",
    ]
    return "\n".join(lines)
