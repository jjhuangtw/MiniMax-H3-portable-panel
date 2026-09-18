"""User's own prompt collections (Taiwan fashion images, dynamic architecture) plus the
assembled PROMPT_CATEGORIES. Scene templates now live in prompt_official.py / prompt_themes.py."""


# Photorealistic image prompts for fictional Taiwanese fashion / professional women
# (user's own collection, kept verbatim). Best used on the 🖼️ 圖片 (Krea2) tab;
# they are photo-style, not H3 video prompts. All subjects are generic and fictional.
TAIWAN_BEAUTY = {
    "台北信義雨夜霓虹": "A cinematic portrait of a stunning young East Asian influencer girl standing on a rainy Taipei Xinyi street at night. She is wearing a modern techwear outfit with a light translucent jacket. Neon signs from nearby shops reflect on the wet asphalt. Fujifilm ETERNA film stock look, low saturation, muted colors, soft natural skin texture with micro-imperfections. Cinematic lighting, shallow depth of field, anamorphic bokeh, 8k resolution, highly detailed, photorealistic.",
    "信義現代建築晨光": "A cinematic, ultra-realistic portrait of a stylish young East Asian influencer standing on a modern Taipei street in the Xinyi District. Behind her are sleek modern architectural buildings with glass facades and the distant silhouette of Taipei 101. The lighting is early morning soft light, low saturation, Fujifilm ETERNA film stock look, natural skin texture with micro-imperfections, soft bokeh. She is wearing a chic, minimalist outfit. Film grain, 8k resolution, highly detailed, shot on Arri Alexa.",
    "台北黃金時刻": "A cinematic high-quality photo of a young East Asian influencer in Taipei. Modern glass skyscraper, golden hour light, Fujifilm ETERNA film look. Natural skin texture, low saturation, subtle film grain.",
    "黑色絲綢夜景肖像": "一位美麗的東亞女性，25歲，直視鏡頭，細膩的皮膚紋理與微小瑕疵，電影感光影，夜晚的城市街道，背景散景處理，穿著優雅的黑色絲綢連衣裙，臉上灑落柔和的月光，使用 Arri Alexa 拍攝，變形鏡頭運鏡，8k，極致寫實，傑作，細節豐富的雙眼，帶著淡淡的微笑。",
    "無邊際泳池 x 建築": "一位美麗的東亞女性穿著極簡優雅的泳衣，在豪華無邊際泳池邊休憩。背景是具備乾淨線條的洞石牆面建築，俯瞰著地中海的落日。電影感黃金時刻光影，柔和的橘紅色調，細膩的皮膚紋理，皮膚上的水滴質感與自然毛孔。使用 Arri Alexa 拍攝，變形鏡頭，8k，極致寫實，展現建築空間與女性交織的高級美感。",
    "西門町雨夜街拍": "台北西門町雨夜街頭，年輕東亞網紅模特，現代台灣建築與霓虹招牌，時尚流行街拍，低飽和，Fujifilm ETERNA 影調，自然膚色，35mm 底片顆粒，電影級光影，寫實攝影",
    "台北 x 九份山城": "寫實電影感時尚短片，一位年輕東亞女性網紅模特，黑色俐落短髮，穿低調高級感的深灰風衣與銀色耳飾，站在台北街頭與九份山城意象交疊的城市場景，背景融合台北現代建築玻璃立面、濕潤柏油路、九份窄巷紅燈籠與遠處山城屋簷，時尚流行但不浮誇，低飽和配色，Fujifilm ETERNA 影調，自然膚色，細緻底片顆粒，柔和陰天雨後光線，電影級邊緣光，35mm 鏡頭，淺景深，真實材質，editorial fashion photography, cinematic realism, subtle motion-ready composition, no text, no watermark。",
    "短髮風衣 x 雨後台北九份": "Photorealistic cinematic fashion editorial, a young adult East Asian influencer model with short black bob hair and natural skin, wearing a refined charcoal-gray trench coat and silver earrings, standing on a rain-wet Taipei street where contemporary Taiwanese glass architecture meets a Jiufen mountain-town alley: red lanterns, tiled eaves, misty hills and reflective asphalt. Fashion-forward but believable, low saturation, Fujifilm ETERNA color science, natural skin tones, subtle 35mm film grain, soft post-rain overcast light, cinematic rim light, shallow depth of field, realistic textures, premium magazine photography, no text, no watermark, 16:9.",
    "翡翠絲質上衣 x 雨後台北": "Photorealistic cinematic fashion editorial, a young adult East Asian Taiwanese influencer model in her mid-20s, natural skin texture and subtle imperfections, shoulder-length dark hair, wearing a contemporary charcoal blazer over a muted jade silk top and tailored trousers. She stands beneath a translucent canopy on a stylish Taipei street after rain, with wet asphalt reflections, Taipei mixed-use modern architecture, soft storefront signage and distant Taipei 101 silhouette, subtle visual echo of Jiufen red lanterns and hillside alleys in the background, refined contemporary Taiwan urban mood, fashionable but believable, no logos, no readable text. Low saturation, Fujifilm ETERNA film emulation, natural skin tones, soft overcast blue-hour light with warm practical highlights, restrained contrast, 35mm film grain, gentle halation, realistic lens imperfections, shallow depth of field, cinematic composition, premium magazine photography, 16:9.",
    "奶油針織 x 藍色長裙": "Photorealistic cinematic fashion editorial key visual, a young adult East Asian Taiwanese influencer model with shoulder-length dark hair and natural skin, wearing a contemporary cream knit top, tailored midnight-blue skirt, and small silver earrings. She stands at dusk on a rain-wet Taipei street beside a refined modern Taiwanese glass-and-brick cultural building, with a distant suggestion of Jiufen red lanterns and tiled roofs in the background, tasteful urban signage abstract and unreadable. Fashion-forward, elegant, believable, low saturation, Fujifilm ETERNA film emulation, natural skin tones, subtle 35mm grain, soft blue-hour ambient light with warm shop-window glow, cinematic rim light, realistic fabric and pavement textures, premium magazine photography, no text, no watermark, 16:9.",
    "表演藝術中心 x 雨光廣場": "Photorealistic cinematic fashion editorial, a young adult East Asian Taiwanese influencer model in her mid-20s with natural skin texture and subtle imperfections, sleek shoulder-length dark hair, wearing a sculptural ivory blouse, slate-blue tailored vest, and flowing black trousers. She stands on a rain-polished plaza beside a contemporary Taiwanese performing arts center in Taipei, layered concrete terraces, translucent glass, brushed metal, distant Taipei skyline, and a poetic echo of Jiufen red lanterns reflected in puddles. Sophisticated fashion-forward Taiwan urban mood, believable editorial styling, no logos, no readable text. Low saturation, Fujifilm ETERNA film emulation, natural skin tones, soft blue-hour light with restrained amber practicals, gentle halation, subtle 35mm film grain, restrained contrast, realistic lens imperfections, shallow depth of field, premium magazine photography, 16:9.",
    "台北豪宅銷售中心職業女性": "Interior of a luxury real estate sales center in Taipei. Large floor-to-ceiling windows showing a minimalist courtyard with a single Acer serrulatum tree. The flooring is large grey stone slabs. A young Taiwanese professional woman, wearing a elegant dark blue real estate agent uniform (white shirt, vest, skirt), stands gracefully by a marble architectural model. High-end cinematic lighting, soft shadows, anamorphic lens flares. 16:9.",
    "房仲女性與空間互動": "A beautiful young Taiwanese woman (Real Estate Agent) with a kind smile, looking at the camera and gesturing towards the space. She is working in a high-end minimalist sales center. Soft natural lighting, realistic skin texture, professional and elegant. Cinematic film aesthetic. 16:9.",
}


# Dynamic architecture / interior video prompts (material-growth reveals, line-art to
# photoreal, first-person assembly commercials). User's collection, kept verbatim and
# de-duplicated. These are H3 video prompts (motion + timing), unlike the structured
# 建築 templates above.
ARCH_DYNAMIC = {
    "現代公寓剖面・灰模生長為實景（10秒）": "一個靜態的、視線高度的攝影機，聚焦於現代公寓內部的剖面視角，最初呈現為極簡的灰色示意圖。在6秒內，牆壁、地板和天花板逐漸獲得逼真的紋理，如拋光混凝土和木材。家具以微妙的沉降動作逐漸顯現。最後，一個人自然地走進畫面，坐在沙發上，閱讀一本書，被隱藏窗戶透出的柔和自然光照亮。時長：10秒。避免：物體或人物突然出現、不真實的紋理、幾何變形、卡頓的動作。",
    "當代客廳・線稿推軌轉寫實（7秒）": "一個緩慢、穩定的推軌鏡頭，從廣角鏡頭開始，呈現一個當代客廳內部的精確、清晰的線稿。隨著攝影機向前滑動，線稿平滑地過渡到一個完全有紋理和家具的寫實場景，展現溫暖的橡木地板、柔軟的布藝沙發，以及透過大窗戶灑落的漫射陽光。環境光線略微變化以突顯紋理。時長：7秒。避免：比例不一致、重影、不真實的實體化、晃動的攝影機。",
    "白色建築模型・空拍溶解為實景（8秒）": "一個電影般的空拍機鏡頭緩慢環繞一個極簡主義的白色建築模型，展示其純粹的形態。隨後，白色模型無縫地溶解並實體化為一個由混凝土和玻璃構成的寫實現代建築外觀，沐浴在柔和的晨光中。攝影機繼續緩慢環繞，揭示精緻的立面細節、玻璃上微妙的反射以及周圍的景觀元素。時長：8秒。避免：文字疊加、扭曲的幾何形狀、閃爍、突然的材料變化。",
    "辦公大樓玻璃立面・日出水平搖攝（35mm）": "一個非常緩慢、平滑的水平搖攝鏡頭，時長5-10秒，使用35mm電影鏡頭，在日出時分沿著現代高層辦公大樓光滑的玻璃和鋼立面緩緩移動。清晨的光線創造出清晰的反射和長長的斜影，突出幕牆的幾何圖案和垂直元素。屋頂通風口冒出微弱的蒸汽。避免文字疊加、扭曲的幾何形狀、閃爍或意外的偽影。",
    "松林木鋼涼亭・無人機螺旋上升（7秒）": "一座抽象的木鋼涼亭，坐落於茂密的松林空地中，其風化的材料與自然環境融為一體。無人機從樹線內緩緩螺旋上升，盤旋於涼亭上方，逐漸揭示其完整形態，以及它如何和諧地融入清晨薄霧繚繞的景觀。廣角視角，柔和、空靈的光線穿透薄霧，斑駁的陽光灑落在濕潤的表面。建議時長：7 秒。避免出現人物、過度編輯、不自然的氛圍效果。",
    "豪宅綜合體・12鏡頭微縮到實景廣告（10秒／9:16）": """按照附件的 12 鏡頭分鏡嚴格製作一段 10 秒超寫實電影化建築商業廣告。貫穿始終為同一個豪華住宅綜合體。保留其精確幾何形狀、比例、石材立面、石墨金屬、全景玻璃、陽台和窗戶，從微縮模型到全尺寸建築。第一人稱男性雙手始終戴著相同的啞光黑色手套。無文字、標誌或 UI。

0.0–0.6 — 鏡頭 1：第一人稱視角，略微自上而下。黑色極簡工作室中的深色單體石墨桌。兩隻戴黑手套的手進入畫面，並精確將建築底座置於中央。緩慢控制推進。

0.6–1.2 — 鏡頭 2：極端微距。手指拿起一塊沉重的微縮生混凝土塊，並精確插入底座。展現多孔混凝土質感、重量以及緊密的物理契合。

1.2–1.8 — 鏡頭 3：低角度微距。手安裝石墨金屬結構元件。當其鎖定到位時，結構柱機械式垂直從底座升起，並精確停在位置。真實機械組裝，無魔法。

1.8–2.5 — 鏡頭 4：視角特寫。戴手套的手指沿結構向上移動。樓層、混凝土板和結構框架快速依序向上組裝，直接跟隨手部移動。攝影機隨生長中的建築向上傾斜。

2.5–3.2 — 鏡頭 5：三個快速觸覺微距剪輯：手指安裝天然石材立面板 → 剪輯 → 石墨拉絲金屬面板鎖定到位 → 剪輯 → 透明全景玻璃面板精確滑入其框架。極端材質細節。

3.2–4.0 — 鏡頭 6：側面微距沿立面追蹤。戴手套的手在結構旁水平移動，同時真實立面組件在其後快速鎖定到位：天然石材 → 石墨金屬 → 全景玻璃 → 玻璃陽台。建築變得建築上完整。

4.0–4.7 — 鏡頭 7：極端微距。兩根手指握住最後一塊透明玻璃面板，並小心插入剩餘的立面開口。精確的物理「咔噠」聲。隨即溫暖琥珀色公寓燈光依序在玻璃後逐層亮起。

4.7–5.4 — 鏡頭 8：更廣視角。雙手從石墨桌上抬起完全完成的微縮住宅綜合體。雙手小心釋放。完成的建築靜止懸浮在桌面之上。雙手移出畫面。攝影機立即開始環繞。

5.4–6.3 — 鏡頭 9：一個連續無縫的比例轉換，無剪輯。攝影機加速進入環繞懸浮微縮模型的平滑軌道。保持建築居中。在環繞過程中，攝影機視角、景深和建築細節逐步從微距攝影轉移到真實建築比例。桌面消失在下方/畫面外，工作室黑暗自然轉變為傍晚天空和遠處城市燈光。建築成長直到完全主宰畫面。永不顯著變形建築；僅改變感知比例。

6.3–7.3 — 鏡頭 10：繼續相同環繞而不重置攝影機方向。現在無疑為藍調時段傍晚的真實全尺寸豪華住宅綜合體。動態低空環繞其角落。掠過天然石材、石墨結構框架、陽台和全景玻璃。窗後可見溫暖入住的公寓。紀念碑式的真實比例。

7.3–8.3 — 鏡頭 11：攝影機從環繞轉換為平行立面的快速平滑飛行。選擇一扇溫暖照明的全景公寓窗戶，並直接加速朝其前進。窗戶快速充滿畫面。無剪輯無縫穿過玻璃進入公寓。

8.3–10.0 — 鏡頭 12：在真實豪華公寓內繼續相同攝影機移動。溫暖當代室內：天然石材、深色木材、設計師家具、柔和琥珀建築燈光、落地窗。四位時尚成年友人自然交談、微笑並大笑，一無所覺攝影機。平滑橫向推軌經過他們，以人們位於前景/中景結束，並在後方可見全景傍晚城市及綜合體建築。

視覺進展：冷峻石墨工作室 → 觸覺組裝 → 完成的照明微縮模型 → 無縫比例轉移 → 紀念碑式真實建築 → 溫暖人類生活。豪華手錶廣告般的精準度、汽車廣告般的燈光、建築電影般的真實主義。淺景深微距逐漸轉為真實建築深度。物理精準的混凝土、石材、拉絲金屬和玻璃。一棟建築的嚴格連續性。無玩具/塑膠外觀，無全息圖、粒子、魔法建造、變形、建築變形、浮動組件、額外工具、文字或標誌。, 9:16""",
    "奢華沙發廣告・第一人稱組裝（10秒／16:9）": "製作一個 10 秒的超寫實 16:9 奢華家具廣告，一個連續的第一人稱男性視角，26–28mm 鏡頭，黑色工作室，霧面黑色皮革手套，僅限真實物理。0–0.8 秒：白色奶油雲朵沙發居中漂浮；手向左滑動。0.8–1.6 秒：沙發快速向左旋轉，同時一張溫暖的象牙色模組化沙發從右側進入並停在中央。1.6–2.4 秒：另一次滑動將其替換為一張弧形拿鐵色圈絨沙發。2.4–3.2 秒：滑動帶入一張溫暖的焦糖色皮革沙發。3.2–4.2 秒：最終的灰褐色/摩卡色主角沙發緩慢抵達，正面旋轉並因巨大慣性而停止。4.2–5.0 秒：張開手掌的 STOP 手勢凍結了旋轉木馬；其他沙發消失在遠處。5.0–5.8 秒：手按壓並滑過主角沙發扶手，布料產生真實壓縮。5.8–6.6 秒：沙發落地；胡桃木地板滑入其下方，灰褐色地毯展開。6.6–8.5 秒：保持完全相同的主角沙發靜止不動，同時奢華房間在其周圍實體組裝——胡桃木和石灰華牆壁滑入，咖啡桌和拿鐵色椅子進入，置物架鎖定到位，吊燈下降，窗簾和裝飾物移動到指定位置。8.5–10 秒：全景窗戶打開，溫暖的日光灑滿完成的靜奢室內；緩慢向後推移鏡頭，展現整個房間。主角沙發在整個過程中保持 100% 相同。真實的質量、慣性、摩擦力和機械停止；沒有魔法、變形、傳送、粒子、煙霧、使用者介面、文字、標誌、人物、剪輯或攝影機角度變化。",
}


from prompt_themes import THEME_CATEGORIES, INTERIOR_LANDSCAPE
# Official-format (MiniMax H3 spec) rewrites of the 建築 / 人物 / 動畫 templates.
from prompt_official import ARCHITECTURE_H3, PEOPLE_H3, GLAMOUR_H3

PROMPT_CATEGORIES = {
    # 建築 = official-format architecture + dynamic reveals + interiors / designed landscapes.
    "建築（35 組）": {**ARCHITECTURE_H3, **ARCH_DYNAMIC, **INTERIOR_LANDSCAPE},
    # 人物 = official-format people + adult-woman animation + Taiwanese fashion (Krea2 image) prompts.
    "人物（53 組）": {**PEOPLE_H3, **GLAMOUR_H3, **TAIWAN_BEAUTY},
    # Themed official-format T2VA sets.
    **THEME_CATEGORIES,
}


# Storyboard-director brief for a language model (not an H3 generation prompt):
# turns one reference image into a 10-20 s keyframe sequence plus a contact-sheet grid.
STORYBOARD_DIRECTOR = {
    "單圖擴展成 10–20 秒分鏡（含分鏡表 + 九宮格）": """You are an award-winning trailer director + cinematographer + storyboard artist.
Your craft standard: COMMERCIAL MASTER-LEVEL. Every story beat must be emotionally precise, universally legible, and brand-safe. Every keyframe must be portfolio-grade, technically flawless, and indistinguishable from a high-budget commercial production's pre-viz board.
Your job: turn ONE reference image into a cohesive cinematic short sequence, then output AI-video-ready keyframes.

User provides: one reference image (image).

Composition Analysis: First, analyze the full composition: identify ALL key subjects (person/group/vehicle/object/animal/props/environment elements) and describe spatial relationships and interactions (left/right/foreground/background, facing direction, what each is doing).
Truthfulness: Do NOT guess real identities, exact real-world locations, or brand ownership. Stick to visible facts. Mood/atmosphere inference is allowed, but never present it as real-world truth.
Strict Continuity: Maintain strict continuity across ALL shots: same subjects, same wardrobe/appearance, same environment, same time-of-day and lighting style. Only action, expression, blocking, framing, angle, and camera movement may change.
Depth of Field: Must be realistic: deeper in wides, shallower in close-ups with natural bokeh.
Color Grade: Keep ONE consistent cinematic color grade across the entire sequence.
No New Elements: Do NOT introduce new characters/objects not present in the reference image. If you need tension/conflict, imply it off-screen (shadow, sound, reflection, occlusion, gaze).

Expand the image into a 10–20 second cinematic clip with a clear theme and emotional progression (setup → build → turn → payoff). The user will generate video clips from your keyframes and stitch them into a final sequence.

Output (with clear subheadings):
Subjects: List each key subject (A/B/C…), describe visible traits (wardrobe/material/form), relative positions, facing direction, action/state, and any interaction.
Environment & Lighting: Interior/exterior, spatial layout, background elements, ground/walls/materials, light direction & quality (hard/soft; key/fill/rim), implied time-of-day, 3–8 vibe keywords.
Visual Anchors: List 3–6 visual traits that must stay constant across all shots (palette, signature prop, key light source, weather/fog/rain, grain/texture, background markers).

From the image, propose:
Theme: One sentence.
Logline: One restrained trailer-style sentence grounded in what the image can support.
Emotional Arc: 4 beats (setup/build/turn/payoff), one line each.
Story quality: The story must have a universal emotional core accessible across cultures. Every beat must earn its place with dramatic economy - if a beat does not advance emotion or tension, cut it. Imply meaning through visual composition and gaze (subtext over exposition). The emotional arc must feel premium, aspirational, and emotionally intelligent (brand-safe). The entire sequence must orbit ONE single piercing emotional truth, not a vague mix of moods.

Choose and explain your filmmaking approach (must include):
Shot progression strategy: How you move from wide to close (or reverse) to serve the beats.
Camera movement plan: Push/pull/pan/dolly/track/orbit/handheld micro-shake/gimbal—and WHY.
Lens & exposure suggestions: Focal length range (18/24/35/50/85mm etc.), DoF tendency (shallow/medium/deep), shutter "feel" (cinematic vs documentary).
Light & color: Contrast, key tones, material rendering priorities, optional grain (must match the reference style).

Output a Keyframe List: default 9–12 frames (later assembled into ONE master grid). These frames must stitch into a coherent 10–20s sequence with a clear 4-beat arc. Each frame must be a plausible continuation within the SAME environment. Each keyframe must be compositionally strong enough to stand alone as a single still image, technically precise (realistic DoF, plausible lighting, accurate shadows, coherent perspective), and emotionally charged (the viewer should feel something from each frame even without context).

Use this exact format per frame:
[KF# | suggested duration (sec) | shot type (ELS/LS/MLS/MS/MCU/CU/ECU/Low/Worm's-eye/High/Bird's-eye/Insert)]
Composition: Subject placement, foreground/mid/background, leading lines, gaze direction.
Action/beat: What visibly happens (simple, executable).
Camera: Height, angle, movement (e.g., slow 5% push-in / 1m lateral move / subtle handheld).
Lens/DoF: Focal length (mm), DoF (shallow/medium/deep), focus target.
Lighting & grade: Keep consistent; call out highlight/shadow emphasis.
Sound/atmos (optional): One line (wind, city hum, footsteps, metal creak) to support editing rhythm.

Hard requirements:
Must include: 1 environment-establishing wide, 1 intimate close-up, 1 extreme detail ECU, and 1 power-angle shot (low or high).
Ensure edit-motivated continuity between shots (eyeline match, action continuation, consistent screen direction / axis).
Commercial master-level gate: Before finalizing, review - Does the story have ONE clear emotional core (not a vague mood)? Does every frame justify its existence (if you can cut it without losing coherence, it is redundant - replace or remove it)? Does each keyframe have compositional intentionality (not default center-framing or generic coverage)? Is visual quality consistent with the reference image fidelity and style?

If the reference image lacks sufficient narrative elements, output a shorter sequence (minimum 4 keyframes covering the 4-beat arc), state what additional context would enable expansion, do NOT fabricate subjects or props. Quality standard remains unchanged in fallback mode.

You MUST additionally output ONE single master image: a Cinematic Contact Sheet / Storyboard Grid containing ALL keyframes in one large image.
Grid Layout: Default 3x3. If more than 9 keyframes, use 4x3 or 5x3 so every keyframe fits into ONE image.
Content: The single master image must include every keyframe as a separate panel (one shot per cell) for easy selection.
Labeling: Each panel must be clearly labeled: KF number + shot type + suggested duration (labels placed in safe margins, never covering the subject).
Continuity: Strict continuity across ALL panels: same subjects, same wardrobe/appearance, same environment, same lighting & same cinematic color grade; only action/expression/blocking/framing/movement changes.
Realism: DoF shifts realistically: shallow in close-ups, deeper in wides; photoreal textures and consistent grading.
Style match: The grid overall visual quality, color treatment, and texture must closely match the reference image.
Follow-up: After the master grid image, output the full text breakdown for each KF in order so the user can regenerate any single frame at higher quality.

Output in this order:
A) Scene Breakdown
B) Theme & Story
C) Cinematic Approach
D) Keyframes (KF# list)
E) ONE Master Contact Sheet Image (All KFs in one grid)

分镜上不要有文字
分镜图片风格要与原图保持一致

用中文输出""",
}

PROMPT_CATEGORIES["🎬 分鏡導演（給語言模型，非 H3 提示詞）"] = STORYBOARD_DIRECTOR


# Companion brief, kept verbatim: take the storyboard panels back to a language model and get one H3
# prompt per shot, with the shots locked to one timeline, one identity and one space.
STORYBOARD_DIRECTOR["多圖分鏡 → 連貫多段影片提示詞（例：四宮格 30 秒）"] = """# 🎬 MiniMax H3 图生视频自动提示词工程（升级版：多分镜连贯系统）

---

# 🧠 一、核心升级能力（新增）

本系统新增支持：

## ✅ 多图片分镜生成（重点）

适用于：

* 四宫格
* 多张序列图
* 分镜草图
* 连续动作拆图

---

## 🎯 核心原则（非常重要）

> ❗多个分镜不是多个视频，而是一个“完整故事的不同时间切片”

---

### 👉 必须满足：

* 所有分镜共同构成一个完整视频（如30秒）
* 每个分镜是同一故事的连续片段
* 镜头之间必须具备：

  * 时间连续性
  * 动作连续性
  * 空间一致性
  * 人物一致性

---

# 📥 二、用户输入结构（升级）

用户可能输入：

### 1️⃣ 多张图片（分镜）

例如：

* @图片1（分镜1）
* @图片2（分镜2）
* @图片3（分镜3）
* @图片4（分镜4）

---

### 2️⃣ 总时长

例如：

* 30秒

---

### 3️⃣ 可选信息

* 每个分镜时长（如 0-7s / 7-15s）
* 或统一平均分配
* 或每张图一个场景主题

---

### 4️⃣ 可选主题

* 用户提供：直接使用
* 用户未提供：自动从所有分镜图推导“统一主线剧情”

---

# ⚙️ 三、系统自动处理逻辑（核心）

---

## 🧩 Step 1：建立“全局故事线”

如果用户没有主题：

👉 自动生成：

```text
【全局故事线】
基于所有分镜图生成一个连续叙事：人物在同一空间/同一事件中的时间推进过程
```

---

## 🧩 Step 2：分镜绑定时间轴

示例（30秒四宫格）：

| 分镜 | 时间     |
| -- | ------ |
| 图1 | 0-7s   |
| 图2 | 7-15s  |
| 图3 | 15-22s |
| 图4 | 22-30s |

---

## 🧩 Step 3：统一一致性锁定（关键）

```text
所有分镜必须保持：
- 同一人物身份（脸/体型/服装）
- 同一空间逻辑（或合理空间推进）
- 同一视觉风格
- 同一叙事事件
```

---

# 🎬 四、分镜提示词生成规则（核心输出）

---

## 📦 输出结构（必须严格）

系统会输出：

```text
视频一（@图片1）
视频二（@图片2）
视频三（@图片3）
视频四（@图片4）
```

---

# 🎥 每个分镜视频标准结构

---

## 🧱 结构固定为：

### 1️⃣ 参考素材说明

### 2️⃣ 核心创意（局部剧情）

### 3️⃣ 画面过程（该段时间）

---

# 🎬 五、标准生成模板（工业级）

---

## 🎥 视频N（@图片N）

---

### 【参考素材说明】

```text
@图片N：分镜参考图，锁定当前时间节点的角色状态、构图与场景关系
```

---

### 🔒 一致性约束（自动补充）

```text
必须保持与前后分镜同一人物一致性（脸部/体型/服装）
必须保持空间连续性（同一地点或逻辑延续）
禁止出现额外角色或风格突变
```

---

### 🎯 【核心创意】

```text
{该分镜时间段}，电影感写实风格视频。

基于整体剧情中第N阶段事件：
人物在当前状态下继续推进故事动作，
镜头风格与前后分镜保持连续性。
```

---

### 🎬 【画面过程说明】

```text
0-3秒：
中景，基于@图片N画面结构，人物处于当前分镜状态，镜头轻微推进

3-6秒：
人物发生关键动作变化（根据分镜图内容延续上一分镜动作）

6-结束：
动作完成或过渡至下一分镜状态，镜头自然收束
```

---

# 🔗 六、多分镜“强连贯规则”（重点）

---

## ❗这是整个系统最关键部分

### 1️⃣ 动作连续性

```text
上一镜头的动作必须“未完成”，下一镜头必须“接着完成”
```

---

### 2️⃣ 空间连续性

```text
镜头之间不能“瞬移换场”，除非剧情明确发生转场
```

---

### 3️⃣ 时间连续性

```text
所有分镜必须严格组成完整时间线（如0-30秒）
```

---

### 4️⃣ 镜头衔接规则

* 可以：

  * 走 → 跑 → 停
  * 转头 → 行走 → 回头

* 不可以：

  * 突然换衣服
  * 人物消失
  * 场景跳跃无逻辑

---

# 🧪 七、完整示例（四宫格 30秒）

---

## 🎯 用户输入：

* 图片：4张（四宫格）
* 总时长：30秒
* 主题：男人在城市中寻找失踪的人

---

## ✅ 输出：

---

# 🎥 视频一（@图片1）

```text
【参考素材说明】
@图片1：锁定人物初始状态（站立于街头，情绪不安）

必须保持人物一致性，不得更换身份或风格

【核心创意】
0-7秒，电影感写实风格。
人物站在城市街头，似乎在寻找某人，情绪紧张。

【画面过程说明】
0-3秒：
中景，人物（@图片1）站在街头，环顾四周，镜头缓慢推进

3-7秒：
人物开始迈步前行，进入搜索状态，镜头跟随移动
```

---

# 🎥 视频二（@图片2）

```text
【参考素材说明】
@图片2：人物进入城市巷道搜索状态

必须保持与视频一连续性

【核心创意】
7-15秒，人物进入城市巷道继续寻找目标

【画面过程说明】
7-10秒：
中近景，人物进入巷道，脚步加快

10-15秒：
人物停下观察环境细节，镜头轻微摇动
```

---

# 🎥 视频三（@图片3）

```text
15-22秒，人物发现线索，情绪变化，开始加速行动
```

---

# 🎥 视频四（@图片4）

```text
22-30秒，人物接近目标位置，情绪达到高潮，画面收束
```

---

# 🚀 八、最终升级总结（系统本质）

---

## 👉 这个系统本质是：

### ❗把 H3 从“视频生成工具”升级为：

> 🎬 “分镜级导演自动生成系统”

---

## ✔ 它具备三层能力：

### 1️⃣ 单图 → 动态视频

### 2️⃣ 多图 → 连续叙事

### 3️⃣ 时间轴 → 完整影片

---

# 🧠 一句话终极定义：

👉 **H3 多图模式 = 用图片做“电影分镜脚本”，AI负责补拍摄过程**"""
