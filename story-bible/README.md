# story-bible — 角色/場景/世界觀設定卡(公開範本)

連載 IP 的角色設定通常散在四處:生圖的視覺錨、劇本的角色 json、配音腳本裡的聲線參數、節目企劃裡的語氣人設,互不相通,全靠人腦記。story-bible 的做法是建立**唯一正本**:每個角色一張三層卡,下游各取所需,下游改了設定必須回存。

- **視覺層**:外貌(只寫恆定可視特徵)、角色鎖逐字句(引用時一字不差)、鎖臉參考圖、最佳平台。
- **敘事層**:性格、背景、關係網(dict)、敘事功能、弧線、主導/底噪情緒——供編劇與審稿。
- **聲演層**:語氣人設、語癖、對白樣本、engine/voice/rate/pitch、唸法校正表、混音預設——供配音。

`templates/` 是三張空卡,`references/欄位指南.md` 說明每個欄位誰吃它、格式、以及往 emotion-shot-pipeline `characters/<名>.json` 的 8 必填欄映射。

兩個鐵則:
1. **appearance 只寫恆定可視特徵**,逐鏡會變的道具狀態寫 props 檯帳,作者備註寫 appearance_note(永不注入 prompt)。
2. **下游改了設定沒回存正本,下次召回就是舊資料**——這是整套唯一會爛掉的方式。

指南中提到的 novel-analysis / storytelling-coach / nine-grid-storyboard / ai-voiceover（scripts/tts.py、tts_expressive.py、mix.py）/ ai-media-generator 都是作者另外的工作流或第三方工具，不在本 repo；聲演層的旗標是那些工具的慣用值，換成你的工具即可，欄位語意不變。語音克隆只限本人聲音或有合法授權的參考音。
