# -*- coding: utf-8 -*-
"""script.json 與角色檔的資料格式定義與驗證。"""

# 情緒座標: (valence 情緒正負 -1..1, arousal 能量強度 0..1)
# 音樂總監與風格配對都靠這張表推情緒弧線。
EMOTIONS = {
    "平靜":  (0.2, 0.15),
    "溫暖":  (0.7, 0.30),
    "期待":  (0.5, 0.55),
    "喜悅":  (0.8, 0.70),
    "好奇":  (0.4, 0.45),
    "緊張":  (-0.3, 0.75),
    "恐懼":  (-0.7, 0.85),
    "悲傷":  (-0.6, 0.35),
    "憤怒":  (-0.7, 0.90),
    "孤獨":  (-0.4, 0.25),
    "釋然":  (0.6, 0.25),
    "敬畏":  (0.3, 0.65),
    "決絕":  (0.1, 0.80),
    "失落":  (-0.5, 0.30),
}

REQUIRED_SHOT_FIELDS = [
    "id",           # 鏡號 (int, 從 1 起)
    "scene",        # 場景 (str)
    "duration_s",   # 秒數 (number)
    "action",       # 畫面動作 (str)
    "emotion",      # 情緒錨定 (str, 必須在 EMOTIONS 表內)
    "sensory_env",  # 感官環境: 光線/聲音/氣味/溫度 (str)
    "visual_beat",  # 視覺節拍: 這顆鏡頭要觀眾看見的那「一下」(str)
    "camera",       # 運鏡 (str)
]
OPTIONAL_SHOT_FIELDS = [
    "characters",   # 出場角色名列表 (list[str])
    "dialogue",     # 台詞/旁白 (str)
    "inner_os",     # 內心OS (str) — 強烈建議填,質感三件套之一
    "props",        # 本鏡入鏡道具的當下狀態 (list[str]),接 props.md 逐鏡狀態鏈,
                    # 直接注入首幀 prompt 防連戲穿幫(閉合的盒/憑空的杯/復活的乾罐)
    "first_frame",  # 起幅畫面 (str)——揭示型/過程型鏡頭必填:img2video 的首幀是
                    # 「鏡頭運動的起點」,不能畫終點或全程(首幀畫完成品,影片就沒東西可演)。
                    # 有此欄時首幀 prompt 用它取代 action,props 也要描述 frame0 可見狀態
]

REQUIRED_CHARACTER_FIELDS = [
    "name",               # 名字
    "age",                # 年齡
    "relations",          # 關係 (與其他角色)
    "background",         # 背景
    "personality",        # 性格
    "appearance",         # 外貌 (生圖時直接注入——只放恆定可視特徵,含2~3個五官定錨;
                          #  作者備註/指引寫到 appearance_note,那欄永不注入 prompt)
    "narrative_function", # 敘事功能 (主角/鏡像/催化劑/阻力...)
    "arc",                # 弧線 (這個故事裡他從哪裡走到哪裡)
]


def validate_script(shots):
    """回傳錯誤訊息列表;空列表 = 通過。"""
    errors = []
    if not isinstance(shots, list) or not shots:
        return ["script.json 必須是非空的 shot 陣列"]
    seen_ids = set()
    for i, shot in enumerate(shots):
        tag = f"shot[{i}]"
        if not isinstance(shot, dict):
            errors.append(f"{tag} 不是物件")
            continue
        sid = shot.get("id")
        if sid in seen_ids:
            errors.append(f"{tag} 鏡號 {sid} 重複")
        seen_ids.add(sid)
        for f in REQUIRED_SHOT_FIELDS:
            if f not in shot or shot[f] in ("", None):
                errors.append(f"{tag} (鏡號{sid}) 缺必填欄位: {f}")
        emo = shot.get("emotion")
        if emo and emo not in EMOTIONS:
            errors.append(
                f"{tag} (鏡號{sid}) 情緒「{emo}」不在情緒表內,"
                f"可用: {'、'.join(EMOTIONS)}"
            )
        dur = shot.get("duration_s")
        if dur is not None and not isinstance(dur, (int, float)):
            errors.append(f"{tag} (鏡號{sid}) duration_s 必須是數字")
        chars = shot.get("characters")
        if chars is not None and not isinstance(chars, list):
            errors.append(f"{tag} (鏡號{sid}) characters 必須是列表")
        props = shot.get("props")
        if props is not None and not isinstance(props, list):
            errors.append(f"{tag} (鏡號{sid}) props 必須是列表(每項一個道具的當下狀態字串)")
        ff = shot.get("first_frame")
        if ff is not None and not isinstance(ff, str):
            errors.append(f"{tag} (鏡號{sid}) first_frame 必須是字串(frame0 的靜態畫面描述)")
        if not shot.get("inner_os"):
            errors.append(f"{tag} (鏡號{sid}) ⚠ 建議補 inner_os(內心OS)——警告,不擋驗證")
    # 警告類(⚠開頭)不算失敗
    return errors


def split_errors(errors):
    """把驗證結果分成 (硬錯誤, 警告)。"""
    hard = [e for e in errors if "⚠" not in e]
    warn = [e for e in errors if "⚠" in e]
    return hard, warn


def validate_character(data):
    errors = []
    for f in REQUIRED_CHARACTER_FIELDS:
        if f not in data or data[f] in ("", None):
            errors.append(f"角色檔缺必填欄位: {f}")
    return errors
