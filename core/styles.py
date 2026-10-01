# -*- coding: utf-8 -*-
"""風格 preset 表 + 依情緒命中率自動配對。

每個 preset 是自寫的視覺語言規格,不引用任何外部平台的風格庫。
emotion_affinity 列出這個風格「天生擅長」的情緒,配對分數靠它算。
"""
STYLE_PRESETS = {
    "cinema_real": {
        "zh": "電影寫實",
        "keywords": "cinematic realism, 35mm film grain, shallow depth of field, natural skin texture",
        "palette": "自然色調,略壓飽和,膚色優先",
        "lighting": "單一主光源動機光(窗光/路燈/檯燈),高光柔、陰影有細節",
        "camera_bias": "定機位或緩慢推軌,少手持",
        "negative": "cartoon, anime, oversaturated, plastic skin, watermark",
        "emotion_affinity": ["平靜", "悲傷", "溫暖", "失落", "釋然"],
        "music_palette": "acoustic, piano, ambient strings, intimate",
    },
    "cyberpunk_neon": {
        "zh": "賽博龐克",
        "keywords": "cyberpunk, neon-lit rain, teal and orange, volumetric fog, reflective wet streets",
        "palette": "冷藍×暖橘對撞,黑底霓虹",
        "lighting": "多彩補光,輪廓光強,體積光穿霧",
        "camera_bias": "低角度仰拍、緩慢滑軌、霓虹反射前景遮擋",
        "negative": "daylight, pastel, flat lighting, watermark",
        "emotion_affinity": ["緊張", "決絕", "孤獨", "恐懼", "敬畏"],
        "music_palette": "dark synthwave, pulsing bass, brooding electronic",
    },
    "morandi_heal": {
        "zh": "莫蘭迪療癒",
        "keywords": "muted morandi palette, soft diffused light, minimal composition, gentle grain",
        "palette": "灰豆綠/霧藍/燕麥/藕粉,全程低飽和",
        "lighting": "大面積柔光,無硬影,清晨或陰天質感",
        "camera_bias": "固定機位、極緩推近,呼吸感節奏",
        "negative": "high contrast, neon, harsh shadows, clutter, watermark",
        "emotion_affinity": ["平靜", "溫暖", "釋然", "孤獨", "期待"],
        "music_palette": "lo-fi, soft piano, warm pads, slow tempo",
    },
    "ink_wuxia": {
        "zh": "水墨國風",
        "keywords": "chinese ink wash painting, xuan paper texture, flowing brush strokes, negative space",
        "palette": "墨色五階+一點硃砂或黛青點色",
        "lighting": "留白即光,不寫實打光",
        "camera_bias": "橫向卷軸式平移、大遠景小人物",
        "negative": "photorealistic, 3d render, saturated colors, watermark",
        "emotion_affinity": ["敬畏", "平靜", "決絕", "悲傷", "釋然"],
        "music_palette": "guzheng, xiao flute, sparse percussion, meditative",
    },
    "anime_impasto": {
        "zh": "動畫厚塗",
        "keywords": "dark impasto digital painting, painterly brushwork, dramatic rim light, anime-influenced",
        "palette": "低明度厚塗底+單一強調色",
        "lighting": "強輪廓光+局部高光,大面積暗部",
        "camera_bias": "特寫與大特寫為主,構圖敢裁切",
        "negative": "flat cel shading, photorealistic, bright cheerful palette, watermark",
        "emotion_affinity": ["決絕", "憤怒", "恐懼", "緊張", "敬畏"],
        "music_palette": "cinematic hybrid, taiko, string ostinato, D minor",
    },
    "noir_suspense": {
        "zh": "懸疑冷調",
        "keywords": "neo-noir, low-key lighting, cold desaturated tones, venetian blind shadows, anamorphic",
        "palette": "冷灰藍為主,近單色,一處暖色當線索",
        "lighting": "低調光,硬光切割,人物半張臉在暗部",
        "camera_bias": "偷窺視角、門縫/玻璃後拍攝、緩慢橫移",
        "negative": "warm cozy tones, flat even lighting, watermark",
        "emotion_affinity": ["緊張", "恐懼", "好奇", "孤獨", "失落"],
        "music_palette": "tense drones, sparse piano notes, sub bass swells",
    },
    "guofeng_painterly": {
        "zh": "國風水墨插畫",
        "keywords": "semi-realistic painterly digital illustration, soft matte painted skin, delicate flowing hair strands, muted celadon-green and warm cream palette, thin ink-line geometric accents (circles, orbits), watercolor wash background, botanical ink linework (bamboo/plum branch), serene contemplative mood",
        "palette": "豆綠/米白為主,水墨潑墨暈染背景,細線幾何圓環點綴,膚色柔霧不寫實",
        "lighting": "柔霧漫射光,無硬光源,畫面本身自帶光暈感",
        "camera_bias": "定機位人像構圖為主,淺景深,留白多",
        "negative": "3d render, pixar style, photorealistic photo, harsh shadows, watermark",
        "emotion_affinity": ["平靜", "釋然", "孤獨", "敬畏", "悲傷", "好奇"],
        "music_palette": "guzheng, xiao flute, sparse percussion, meditative",
    },
    "guofeng_3d": {
        "zh": "國風寫實3D動畫",
        "keywords": "Chinese CG animated film still, realistic mature 3D character render in the style of contemporary Chinese animated features (Light Chaser Animation aesthetic, e.g. New Gods: Nezha Reborn, White Snake), painterly semi-realistic 3D illustration texture with subtle natural skin texture and visible pores, matte muted finish (NOT glossy plastic skin), softly rounded full oval face with a short-wide proportion (face length only marginally greater than cheekbone width, roughly 1:1.1-1.2 ratio, NOT an elongated egg-shaped or long face), soft cheeks with natural volume but a visible subtle transition from cheekbone to jawline (NOT a uniform round blob, NOT chipmunk cheeks), gently rounded receding chin tucked inward (NOT a sharp pointed chin, NOT a gaunt narrow V-shaped jaw), very subtle diffuse natural cheek flush (NOT circular cartoon blush stickers), naturally arched relaxed soft eyebrows, naturalistic almond eyes with soft catchlight and a relaxed mellow-tired droop (NOT sharp winged eyeliner, NOT cartoon eye outline, NOT oversized doll eyes), smooth unlined forehead (NOT forehead wrinkles), side-parted loose wispy bangs with strands grazing both temples, most of the mid-to-upper forehead exposed (NOT hair fully swept back, NOT a blunt full-coverage fringe), NOT cartoonish, NOT big round anime/Disney eyes, soft subsurface scattering skin, volumetric soft lighting, muted celadon-green and warm cream color grading, delicate flowing hair strands with fine strand rendering, thin ink-line geometric circle motifs as 3D set dressing, bamboo/plum branch silhouettes in scene, serene contemplative mood, cinematic depth of field",
        "palette": "3D 立體渲染,寫實成熟五官比例、圓潤短寬鵝蛋臉非拉長蛋形非尖下巴、側分鬆散瀏海露額非整片瀏海(國產動畫電影質感,非西方卡通萌臉),色調維持豆綠/米白莫蘭迪基調,竹枝與幾何圓環當場景裝飾物件",
        "lighting": "柔和體積光,無高對比卡通打光,光線偏霧面漫射",
        "camera_bias": "定機位或極緩推移,淺景深,電影感構圖",
        "negative": "flat 2d illustration, ink wash painting texture, photorealistic photo, Disney style, Pixar style, big round cartoon anime eyes, cute chibi proportions, western cartoon character design, bright saturated cartoon colors, harsh cel shading, sharp pointed chin, narrow V-shaped jaw, gaunt angular face, elongated egg-shaped face, hair fully swept back, blunt full-coverage bangs, forehead wrinkles, circular blush stickers, glossy plastic skin, sharp winged eyeliner, watermark",
        "emotion_affinity": ["平靜", "釋然", "孤獨", "敬畏", "悲傷", "好奇", "溫暖", "期待"],
        "music_palette": "lo-fi, soft piano, warm pads, slow tempo",
    },
    "japan_fresh": {
        "zh": "日系清新",
        "keywords": "japanese fresh film look, airy highlights, slight overexposure, green-teal cast",
        "palette": "高明度低對比,白色透氣,綠意入畫",
        "lighting": "順光或逆光眩光,午後日光",
        "camera_bias": "手持微晃、生活視角、過肩與空鏡穿插",
        "negative": "dark moody, heavy contrast, neon, watermark",
        "emotion_affinity": ["喜悅", "期待", "溫暖", "好奇", "平靜"],
        "music_palette": "acoustic guitar, bells, light percussion, major key",
    },
}


def match_styles(emotions):
    """輸入情緒列表(整部片各 shot 的 emotion),回傳 [(key, 分數, 命中情緒), ...] 由高到低。"""
    scores = []
    uniq = list(dict.fromkeys(emotions))
    for key, p in STYLE_PRESETS.items():
        hits = [e for e in emotions if e in p["emotion_affinity"]]
        score = len(hits) / max(len(emotions), 1)
        scores.append((key, round(score, 2), sorted(set(hits), key=uniq.index)))
    return sorted(scores, key=lambda x: -x[1])


def list_styles_text():
    lines = ["可用風格 preset(共 %d 款):" % len(STYLE_PRESETS), ""]
    for key, p in STYLE_PRESETS.items():
        lines.append(f"[{key}] {p['zh']}")
        lines.append(f"  色彩: {p['palette']}")
        lines.append(f"  打光: {p['lighting']}")
        lines.append(f"  運鏡傾向: {p['camera_bias']}")
        lines.append(f"  擅長情緒: {'、'.join(p['emotion_affinity'])}")
        lines.append("")
    return "\n".join(lines)
