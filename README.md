# emotion-shot-pipeline — 情緒驅動的短片分鏡 → 生成 prompt 編譯器

把一支 30–90 秒短片的劇本,編譯成每顆鏡頭可直接貼進「生圖 / img2video / Suno」的 prompt 包。
中間用**情緒座標**驅動風格配對與配樂結構,用**三道決策閘 + 雙審稿**把品質卡住,
用**三個連戲欄位**把 img2video 最常穿幫的地方寫進 schema(props / first_frame 的格式由 validate 檢查,appearance_note 由 prompt 產生器保證不注入)。

全程本機、零依賴(Python 3.8+ 標準庫),只有最後拿 prompt 去 Kling / Seedance / Nano Banana / Suno 生成時才花平台額度。

## 這不是什麼

- **不是連載爽劇的敘事系統。** 題材雷達、分集鉤子、揭露階梯、爽債台帳請用 [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama);它負責「做什麼故事、怎麼連載」,本管線負責「一支片怎麼真的生出來」。它的單集劇本可以拆成本管線的 `script.json` 當下游。
- **不生圖、不生片。** 輸出是 prompt 與結構指示,拿去平台執行。
- **不是通用 prompt 產生器。** 它只做「一支片、多顆鏡頭、要連戲」這件事。

## 為什麼存在(跟其他工具的差別)

| | 一般做法 | 本管線 |
|---|---|---|
| 情緒 | 形容詞寫在 prompt 裡 | 14 個情緒詞各帶 valence/arousal 座標;全片弧線算出來後,Suno 的調性 / BPM / 高潮位置 / 留白點由座標推導,風格 preset 則依各款 emotion_affinity 的命中率配對 |
| 連戲 | 叮嚀「注意一致性」 | `props` 逐鏡狀態、`first_frame` 起幅、`appearance_note` 永不注入——三個機制寫進 schema |
| 品管 | 寫完直接生 | concept → script → shots 三道閘;任一閘退回,其後全部重開並記 `revisions.log`;邏輯審稿 + 情緒審稿並行出 P0/P1 |
| 經驗 | 每個人重踩 | `references/img2video-field-notes.md`:一支真片燒出來的 Kling img2video 坑與解法(首幀起幅、真人臉洩漏、參考圖帶偏畫風…) |

## 快速開始

```bash
python drama.py status demo_還傘
python drama.py validate demo_還傘
python drama.py prompts demo_還傘     # → projects/demo_還傘/output/prompts_all.md
python drama.py music demo_還傘       # → projects/demo_還傘/output/music_prompt.md
```

`projects/demo_還傘/` 是一支完整範例(5 場 / 8 鏡 / 2 角色;全片帶 props 逐鏡狀態鏈,鏡 3 / 7 / 8 示範 first_frame 起幅):`concept.md` 定調四問 + 梗概 + 正文、`script.json`、`characters/*.json`、兩份產出。先把它跑一遍,再開自己的專案。

## 流程

```
new(建專案)
  → 寫 concept.md(切入視角 / 核心意象 / 情緒弧線 / 戲劇問題 四問)
  → gate --stage concept --confirm        ← 決策閘①
  → 編劇寫梗概 + 分場正文(concept.md 下半)
  → gate --stage script --confirm         ← 決策閘②
  → 拆 script.json + characters/*.json(+ props.md 道具檯帳)
  → validate(格式驗證 + 風格配對建議)
  → gate --stage shots --confirm          ← 決策閘③
  → prompts(首幀圖 + Kling + Seedance 三組 / 鏡)
  → music(Suno prompt + 結構指示 + 混音備註)
```

不滿意任何一步:`python drama.py revise <專案> --stage <閘> --note "批註"`,該閘之後全部退回重跑,批註記在 `revisions.log`。閘沒過,`prompts` 會拒跑。

## 指令

```bash
python drama.py new 專案名 --title 片名 --style morandi_heal --aspect 9:16
python drama.py list-styles          # 9 款風格 preset
python drama.py status 專案名        # 進度回報(閘卡狀態 + 修訂紀錄)
python drama.py validate 專案名      # 驗證 + 依情緒命中率給風格配對建議
python drama.py gate 專案名 --stage concept --confirm
python drama.py revise 專案名 --stage script --note "第 3 場動機不足"
python drama.py prompts 專案名       # → output/prompts_all.md
python drama.py music 專案名         # → output/music_prompt.md
```

## script.json 每顆鏡頭的欄位

必填:`id / scene / duration_s / action / emotion / sensory_env / visual_beat / camera`

選填:`characters / dialogue / inner_os / props / first_frame`

- **質感三件套** = `sensory_env`(感官環境,至少兩種感官)+ `inner_os`(內心 OS,不等於台詞)+ `visual_beat`(這顆鏡頭要觀眾記住的那「一下」)。`sensory_env` 與 `visual_beat` 直接進首幀圖 prompt(有 `first_frame` 的鏡頭只進 `sensory_env`);`inner_os` 不進任何 prompt,供審稿與旁白用,沒填會警告。
- **`emotion` 只能用 `core/schema.py` 情緒表的 14 個詞**:平靜、溫暖、期待、喜悅、好奇、緊張、恐懼、悲傷、憤怒、孤獨、釋然、敬畏、決絕、失落。音樂總監與風格配對靠它算弧線。
- **`props`**:本鏡 camera 框內道具的「當下狀態」列表,直接注入首幀 prompt,防閉合的盒、憑空的杯、復活的乾罐。逐鏡狀態鏈用 `templates/props.md` 維護。
- **`first_frame`**:起幅畫面。img2video 的首幀只能是「鏡頭運動的起點」,不能畫終點或全程——揭示型(微距推開揭示全景)、過程型(畫面內容在鏡中發生不可逆變化)鏡頭必填。有此欄時首幀 prompt 用它取代 `action`,角色外貌只在起幅文字點名該角色時才注入。

## 角色檔 characters/<名>.json

8 必填欄:`name / age / relations(dict) / background / personality / appearance / narrative_function / arc`

- `appearance` 會**原文注入**首幀 prompt:只寫恆定可視特徵,含 2–3 個五官定錨、體態、髮型髮色、服裝(顏色 + 材質 + 剪裁)、一項標誌性細節。
- `appearance_note`(慣例欄)永不注入:道具外觀存放處、「此角色不入鏡」等作者備註寫這裡。
- 既有 IP 角色的正本在 `story-bible/`(三層卡:視覺 / 敘事 / 聲演),開新專案時從卡匯出 8 欄,殺青後有更新要回存卡。欄位映射見 `story-bible/references/欄位指南.md` §四。

## 風格 preset(core/styles.py)

9 款:電影寫實、賽博龐克、莫蘭迪療癒、水墨國風、動畫厚塗、懸疑冷調、國風水墨插畫、國風寫實 3D 動畫、日系清新。每款含 keywords / palette / lighting / camera_bias / negative / emotion_affinity / music_palette;`validate` 會依全片情緒命中率排序建議。

> `guofeng_3d` 的 keywords/negative 帶有作者某支片主角的臉型與瀏海約束(圓潤短寬鵝蛋臉、側分瀏海等),是為了對抗生成模型對「中國動畫電影質感」的系統性偏移而逐輪加上去的。用在你的角色前請改成自己的定錨,或刪掉臉型相關子句。

## 多代理分工(在 Claude Code 之類的代理環境裡跑)

| 角色 | 檔案 | 職責 |
|---|---|---|
| 藝術總監 | `agents/art_director.md` | 定調、派工、把關、回報,不自己寫 |
| 編劇 | `agents/screenwriter.md` | 梗概 → 正文 → script.json;鐵律含起幅原則、核心意象兩現、台詞能省則省 |
| 邏輯審稿 | `agents/logic_reviewer.md` | 因果 / 戲劇問題 / 空間時間 / 角色一致 / 道具守恆 |
| 情緒審稿 | `agents/emotion_reviewer.md` | 弧線形狀 / 高潮鋪陳 / 留白 / 開場鉤子 / OS 與台詞落差 |

跑法:主代理當藝術總監,編劇與兩個審稿用 subagent 派工,審稿可並行;審稿的 P0/P1 清單發回**同一個**編劇 agent 修(保留上下文),清到零 P0 才送使用者過閘。`SKILL.md` 是給代理環境讀的入口。

## 下游接法

1. 每鏡 ① 首幀圖 prompt → Nano Banana / Seedream / Midjourney 生首幀 → 挑圖(挑「動作還沒發生」的那個瞬間,見 field notes)
2. 角色一致性:先生一張人物主參考圖(定裝照),之後每顆鏡的首幀都掛它當參考——不是拿同一張首幀
3. 會演進的畫 / 物:用最能看清它的那顆鏡生一張 hero plate,其他露出鏡以它衍生,靠圖鎖不靠字鎖
4. Kling:首幀 img2video 貼 ② 段;Seedance:先建 @角色 資產再貼 ③ 段
5. 片段回來 → ffmpeg 串接 → 旁白 → Suno 配樂(`music_prompt.md` 直接貼)→ sidechain ducking 混音

## 延伸閱讀

- `references/img2video-field-notes.md` — 實測坑與解法(必讀)
- `templates/props.md` — 道具逐鏡狀態檯帳範本
- `story-bible/` — 角色 / 場景 / 世界觀三層設定卡範本與欄位指南

## 授權

MIT。範例專案《還傘》的文字內容可自由改作;風格 preset 與情緒表歡迎回饋修正。
