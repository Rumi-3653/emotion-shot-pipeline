---
name: emotion-shot-pipeline
description: 情緒驅動的「單支短片」分鏡→生成 prompt 編譯器。把 30–90 秒短片的劇本拆成 script.json(每鏡必填情緒/感官環境/視覺節拍/運鏡),用 14 個帶 valence-arousal 座標的情緒詞算出全片弧線,推導 Suno 配樂 prompt(調性/BPM/高潮位置/留白點),依情緒命中率配對 9 款風格 preset,產出每鏡「首幀圖/Kling img2video/Seedance」三組 prompt;三道決策閘(concept/script/shots)可回滾,編劇+邏輯審稿+情緒審稿多代理分工。觸發:「做一支敘事短片」「單支短片」「情緒弧線」「分鏡 prompt 包」「首幀圖+img2video」「配樂 prompt」「療癒短片/敘事短片」「照這個流程產 prompt」「script.json」「過閘/退回重寫」。不適用:「短劇」「爽劇」「微短劇」「連載」「分集」這類任務一律歸 Hao0321/ai-short-drama(題材雷達、分集鉤子、爽債台帳);單張生圖 prompt;實際操作生成平台。
---

# emotion-shot-pipeline

完整說明在 [README.md](README.md)。工作方式:

1. 主代理扮演 **藝術總監**(`agents/art_director.md`):定調 concept 四問、派工、把關、回報,自己不寫劇本。
2. **編劇**(`agents/screenwriter.md`)寫梗概→正文→`script.json` + `characters/*.json`。
3. **邏輯審稿** 與 **情緒審稿**(`agents/logic_reviewer.md`、`agents/emotion_reviewer.md`)並行審,P0/P1 清單回給編劇修到零 P0。
4. 每個階段用 `python drama.py gate <專案> --stage <閘> --confirm` 過閘,使用者沒點頭不推進;不滿意用 `revise` 退回。
5. 三閘全過才跑 `prompts` 與 `music`,交付 `projects/<專案>/output/`。

動手前先讀 `references/img2video-field-notes.md`(首幀起幅、連戲、Kling 洩漏真人臉等實測坑)。既有 IP 角色先查 `story-bible/`,殺青後有更新要回存。
