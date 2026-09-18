# -*- coding: utf-8 -*-
"""Existing 建築 / 人物 / 成年女性動畫 templates rewritten to conform to MiniMax H3's
official prompt spec (h3-prompt-writing skill): English three-field T2VA format with a
[Shot 1] style opening, official camera-motion vocabulary, diegetic sound folded into the
description, overall_soundscape, and non_diegetic_music. Names are kept; content rewritten.
"""


def _p(desc, soundscape, music="N/A"):
    return (f"integrated_multimodal_description: {desc}\n\n"
            f"overall_soundscape: {soundscape}\n\n"
            f"non_diegetic_music: {music}")


ARCHITECTURE_H3 = {
    "現代極簡別墅": _p(
        "[Shot 1] Live-action, cinematic, a wide eye-level shot of a modern minimalist villa of white geometric volumes with large glass and light-grey stone, an entrance reflecting pool mirroring the facade at dawn. The camera pushes in with small amplitude at slow speed along the path toward the entrance, keeping the vertical lines straight while faint tree shadows shift on the wall.",
        "A light breeze moves through the trees with a soft rustle of leaves and the faint trickle of water in the reflecting pool."),
    "清水模住宅": _p(
        "[Shot 1] Live-action, cinematic, a fair-faced concrete house courtyard with fine formwork texture and dark metal window frames, afternoon oblique sun drawing a sharp light-and-shadow line across the wall as a small tree sways. The camera trucks right with small amplitude at slow speed revealing the wall's depth and the layered space.",
        "Distant birdsong, the soft friction of swaying leaves, and a quiet enclosed-courtyard ambience."),
    "日式庭院與緣側": _p(
        "[Shot 1] Live-action, cinematic, a Japanese wooden engawa facing a dry-landscape garden of white gravel, moss, a stone lantern and a maple, a bamboo blind swaying gently in soft light. The camera pushes in with small amplitude at slow speed from the wooden corridor toward the garden in a single continuous move.",
        "Rustling bamboo leaves, the light ring of a wind chime, and the faint trickle of distant water.",
        "A minimal koto motif at a slow tempo with sparse resonant notes."),
    "北歐客廳": _p(
        "[Shot 1] Live-action, cinematic, a bright Scandinavian living room with a pale oak floor, a beige linen sofa and simple furniture, sheer curtains drifting as soft daylight fills the room. The camera trucks left with small amplitude at slow speed across the room keeping a natural perspective.",
        "A gentle indoor air ambience with the curtains softly stirring and faint birdsong from outside the window."),
    "侘寂茶室": _p(
        "[Shot 1] Live-action, cinematic, a wabi-sabi tea room with rough plaster walls, a low wood table and a handmade ceramic cup, warm side light bringing out the natural materials as tea steam rises slowly. The camera pushes in with small amplitude at slow speed from a mid shot toward the cup while the background keeps its spatial outline.",
        "The faint sound of tea being poured and a quiet still indoor ambience."),
    "工業風 Loft": _p(
        "[Shot 1] Live-action, cinematic, a high-ceilinged industrial loft with red brick walls, black steel beams and large grid windows, a leather sofa and wooden table, fine dust drifting in an afternoon light beam. The camera tracks forward at slow speed showing the height and the steel-frame proportions.",
        "A distant low city rumble and a faint indoor reverberation."),
    "豪宅挑高大廳": _p(
        "[Shot 1] Live-action, cinematic, a double-height luxury residential lobby with natural marble, a curved staircase and hanging light fixtures, warm indirect lighting glowing on the stone. The camera pushes in with small amplitude at slow speed with a slight tilt up while the staircase structure stays stable.",
        "A soft air-conditioning hum and the spacious echo of a wide interior."),
    "精品飯店大堂": _p(
        "[Shot 1] Live-action, cinematic, a boutique hotel lobby with a dark-wood reception desk, brass details, art objects and warm seating, headlights sweeping slowly across the glass outside. The camera trucks left with small amplitude at slow speed past the seating to settle on the reception desk.",
        "A soft blurred murmur of distant conversation over a quiet room tone.",
        "A gentle piano at a slow tempo, warm and evenly spaced."),
    "玻璃帷幕辦公樓": _p(
        "[Shot 1] Live-action, cinematic, a modern glass-curtain-wall office tower, its clean facade reflecting blue sky and slowly moving clouds, planting and a plaza giving real scale in the foreground. The camera tilts up with small amplitude at slow speed from street level, keeping the facade grid continuous and undistorted.",
        "Distant traffic and a light urban breeze."),
    "摩天樓空拍": _p(
        "[Shot 1] Live-action, cinematic, a cluster of golden-hour city skyscrapers with glass and metal facades reflecting the sunset, slow traffic below and natural aerial haze in the distance. The camera trucks right with medium amplitude at slow speed gliding steadily along the skyline without rapid rotation.",
        "A high-altitude wind and a low continuous city hum."),
    "海景度假別墅": _p(
        "[Shot 1] Live-action, cinematic, an oceanfront resort villa where a wood deck and an infinity pool meet the blue sea horizon, a white sun shade swaying as the pool surface ripples. The camera pushes in with small amplitude at slow speed toward the sea view along the pool's edge.",
        "Ocean waves, a sea breeze, and the faint lap of pool water."),
    "山林木屋": _p(
        "[Shot 1] Live-action, cinematic, a timber cabin in a pine forest with a sloped roof and stone base, thin morning mist drifting between the trees, warm interior light glowing as branches sway. The camera tracks forward at slow speed approaching the cabin along a forest path.",
        "Forest birdsong, a light breeze, and the crunch of gravel underfoot."),
    "中式四合院": _p(
        "[Shot 1] Live-action, cinematic, a traditional Chinese courtyard house with grey tile roofs, wooden lattice windows and a stone-paved yard, dappled light under a central tree as fallen leaves slide across the ground. The camera pushes in with small amplitude at slow speed through the moon gate into the courtyard, holding a symmetrical composition.",
        "Rustling leaves, distant birdsong, and the soft echo of the enclosed courtyard."),
    "歐式古典建築": _p(
        "[Shot 1] Live-action, cinematic, a European classical stone building with a colonnade, arched windows and carved cornices, warm sunset grazing the facade as a fountain runs in the foreground. The camera trucks right with small amplitude at slow speed at a low angle along the colonnade with natural proportions.",
        "Running fountain water and the distant echo of footsteps across the plaza."),
    "哥德式教堂": _p(
        "[Shot 1] Live-action, cinematic, the interior of a Gothic cathedral with soaring pointed arches and stained glass, colored daylight falling on the stone floor as dust motes drift, solemn and quiet. The camera pushes in with small amplitude at slow speed along the central aisle with a slight tilt up toward the vaults.",
        "A wide interior reverberation over a low ambient organ drone.",
        "A low sustained organ tone at a very slow tempo, soft and even."),
    "未來曲線展館": _p(
        "[Shot 1] Live-action, cinematic, a futuristic public pavilion with a streamlined white roof, continuous curved surfaces and large glass, a shallow reflecting pool mirroring the building as cloud shadows move slowly. The camera arcs around the building with medium amplitude at slow speed keeping the form consistent.",
        "The soft response of water, a light plaza breeze, and a faint airy ambience.",
        "A soft ambient electronic pad at a slow tempo, evenly sustained."),
    "街角咖啡館": _p(
        "[Shot 1] Live-action, cinematic, a warm corner cafe with a wood-framed glass door, brick walls and small outdoor tables, warm interior light spilling out as a doorway planter stirs in the breeze, no readable signage. The camera pushes in with small amplitude at slow speed approaching the window from the street.",
        "The hiss of a coffee machine, the light clink of cups and saucers, and a distant street ambience."),
    "圖書館閱讀空間": _p(
        "[Shot 1] Live-action, cinematic, a modern library with layered wooden bookshelves, orderly reading tables and tall windows, soft daylight lighting the spines in a calm, orderly space. The camera tracks forward at slow speed down a shelf aisle keeping the perspective lines stable.",
        "Distant page turns, faint footsteps, and a quiet indoor room tone."),
    "美術館白盒子": _p(
        "[Shot 1] Live-action, cinematic, a minimalist white-box museum with clean white walls, a pale grey floor and geometric sculptures, a skylight casting even soft light with clean materials and shadows. The camera trucks left with small amplitude at slow speed past the sculptures, using foreground and background to show spatial depth.",
        "Light footsteps and the open echo of an empty gallery."),
    "雨夜建築立面": _p(
        "[Shot 1] Live-action, cinematic, the facade of a modern commercial building on a rainy night, warm window light and wall-wash lighting reflected on the wet pavement as fine rain falls and water runs along the gutter. The camera pushes in with small amplitude at slow speed at a low angle so the reflections shift naturally with the view.",
        "Steady fine rain, the sound of water on the pavement, and distant traffic."),
}

PEOPLE_H3 = {
    "自然人像微笑": _p(
        "[Shot 1] Live-action, cinematic, an eye-level medium-close shot of an adult woman standing by a window in soft light, wearing a beige shirt, blinking naturally and giving a slight smile while her skin keeps its real texture. The camera pushes in with small amplitude at slow speed keeping her features and hair consistent.",
        "Faint breathing and a quiet indoor room tone."),
    "男性商務形象": _p(
        "[Shot 1] Live-action, cinematic, a chest-up medium-close shot of an adult man in a fitted dark suit in a bright office, adjusting his cuff before lifting his eyes toward the camera with a calm expression. The camera holds a static shot.",
        "The soft friction of fabric and a gentle office room tone."),
    "街頭時尚走拍": _p(
        "[Shot 1] Live-action, cinematic, an adult fashion model in a long coat walks naturally along a city sidewalk, the coat swaying with each step as blurred pedestrians pass in soft afternoon light. The camera tracks backward at the same pace keeping a full-body composition.",
        "Clear footsteps, distant traffic, and the light rustle of fabric."),
    "棚拍時裝展示": _p(
        "[Shot 1] Live-action, cinematic, an adult model stands in a plain grey studio in a sharply tailored outfit, slowly turning a quarter and stopping as the fabric detail catches soft key and rim light. The camera holds a static full-body shot.",
        "Light footsteps and the soft friction of fabric.",
        "A simple rhythmic score at a moderate tempo, restrained and even."),
    "咖啡館閱讀": _p(
        "[Shot 1] Live-action, cinematic, an adult woman sits reading by a cafe window and turns a page, a hot coffee beside her releasing thin steam in warm daylight. The camera pushes in with small amplitude at slow speed from the side as her hands move naturally.",
        "A page turning, the light clink of cups, and a distant coffee machine over a soft cafe ambience."),
    "城市通勤": _p(
        "[Shot 1] Live-action, cinematic, an adult office worker carries a briefcase along a morning street, walking calmly and slowing slightly as an intersection approaches with natural traffic behind. The camera tracks from the side at waist height in a continuous move.",
        "Footsteps, city traffic, and the soft friction of clothing."),
    "公園慢跑": _p(
        "[Shot 1] Live-action, cinematic, an adult runner in sportswear jogs along a park path, breath and arm swing matching the rhythm as morning sun filters through the leaves, expression focused. The camera tracks from the front-side at slow speed keeping natural proportions.",
        "Regular footsteps, steady breathing, and birdsong."),
    "健身啞鈴訓練": _p(
        "[Shot 1] Live-action, cinematic, a fitness person in a tidy gym performs one slow dumbbell curl, elbow steady and the muscle contracting naturally under control. The camera holds a static waist-up medium shot clearly showing the arm.",
        "Breathing, the light clink of equipment, and a low indoor room tone."),
    "舞者緩慢轉身": _p(
        "[Shot 1] Live-action, cinematic, an adult dancer in a soft flowing costume stands in a bright studio, extends both arms and completes a single slow turn, the skirt swaying naturally. The camera holds a stable full-body shot with the dancer fully in frame.",
        "Soft footsteps and the rustle of the costume through the turn.",
        "A soothing solo piano at a slow tempo with sustained pedal tones."),
    "鋼琴演奏": _p(
        "[Shot 1] Live-action, cinematic, an adult pianist plays intently in a small concert hall, hands moving naturally across the keys as the body sways gently to the rhythm under warm stage light. The camera holds a side medium shot framing the pianist and the keys.",
        "The hall's soft reverberation beneath the performance.",
        "A gentle piano at a moderate tempo, matched to the player's movements."),
    "廚師料理": _p(
        "[Shot 1] Live-action, cinematic, an adult chef slowly stirs ingredients in a pot in a clean kitchen, steam rising naturally, his expression focused as soft light reflects off the metal pans. The camera pushes in with small amplitude at slow speed from the front-side keeping the hands and pan in frame.",
        "The sizzle of ingredients, the tap of a ladle against the pot, and a low exhaust-fan ambience."),
    "職人工坊": _p(
        "[Shot 1] Live-action, cinematic, an adult woodworker sands a board in a workshop with slow, firm strokes, the grain clear as side-window light catches fine sawdust. The camera pushes in with small amplitude at slow speed from a half-body shot toward the working hands.",
        "Sandpaper rubbing against wood and a low workshop room tone."),
    "陶藝拉坯": _p(
        "[Shot 1] Live-action, cinematic, an adult potter sits at a wheel, wet hands cradling the spinning clay as the form gradually smooths, the studio light warm. The camera holds a static medium-close shot of the hands and the clay.",
        "The low hum of the wheel, the friction of wet clay, and the faint sound of water."),
    "醫師親切形象": _p(
        "[Shot 1] Live-action, cinematic, an adult doctor in a clean white coat stands in a bright clinic, gathering papers before giving a small nod and a warm smile, the tidy background carrying no readable personal data. The camera holds an eye-level half-body shot in soft natural light.",
        "The light rustle of paper and a quiet clinic room tone."),
    "旅人海邊漫步": _p(
        "[Shot 1] Live-action, cinematic, an adult traveler walks slowly along a beach in a light shirt, the sea wind lifting the hair and clothing as sunset rim light traces the silhouette. The camera tracks steadily from the side-rear at a medium-far distance.",
        "Ocean waves, footsteps in the sand, and a steady sea wind."),
    "山林健行": _p(
        "[Shot 1] Live-action, cinematic, an adult hiker with a backpack moves along a forest trail and steps over a root, motion natural and steady as morning mist and dappled sun fall through the trees. The camera tracks from the rear-side at a steady pace with the full body in frame.",
        "Boots pressing on fallen leaves, the friction of the backpack, and forest birdsong."),
    "雨夜情緒特寫": _p(
        "[Shot 1] Live-action, cinematic, an adult woman stands under the eaves on a rainy night, gazing at the street before slowly turning her head as her expression shifts from thoughtful to calm, fine droplets in her hair. The camera pushes in with small amplitude at slow speed at eye level keeping her identity and skin tone stable.",
        "Rain, the distant hiss of tires on wet road, and faint breathing."),
    "銀髮長者肖像": _p(
        "[Shot 1] Live-action, cinematic, a silver-haired elder sits on a garden wooden chair, looking gently toward the camera with a warm smile, natural wrinkles and skin texture as leaf shadows sway. The camera pushes in with small amplitude at slow speed at eye level, restrained and unhurried.",
        "Birdsong, rustling leaves, and calm breathing."),
    "古風人物漫步": _p(
        "[Shot 1] Live-action, cinematic, a figure in a plain traditional robe walks slowly along a bamboo-lined stone path, the sleeves stirring in the breeze with a calm expression as morning mist layers naturally. The camera tracks from the side at a medium-far distance keeping the clothing and features consistent.",
        "Footsteps on stone, the friction of bamboo leaves, and a faint distant flute."),
    "科幻角色登場": _p(
        "[Shot 1] Cinematic 3D CG animation, a low-angle half-body shot of a sci-fi explorer in a detailed spacesuit at a ship's hatch, slowly raising the gaze ahead as a chest indicator light softly pulses on the used, scuffed metal. The camera pushes in with small amplitude at slow speed keeping the costume and body structure stable.",
        "A low cabin hum, steady breathing, and the faint mechanical sound of the suit's servos.",
        "A low electronic drone at a slow tempo with a single rising synth note."),
}

GLAMOUR_H3 = {
    "黑色晚禮服・紅毯回眸": _p(
        "[Shot 1] Polished 3D CG animation, a fashionable 28-year-old woman in a fitted black evening gown and heels takes two steps along a red carpet, then glances back elegantly as the hem sways, her expression confident, warm flashes tracing her silhouette. The camera tracks with medium amplitude at slow speed, settling on a three-quarter framing that keeps the full outfit.",
        "Heels on the carpet, distant camera shutters, and a low string ambience.",
        "A restrained low-string bed at a slow tempo, warm and even."),
    "緞面洋裝・城市天台": _p(
        "[Shot 1] Cinematic 3D CG animation, a 30-year-old woman in an opaque wine-red satin slip dress stands by a rooftop railing and turns gently as the night wind lifts her long hair, neon forming soft reflections on the fabric. The camera arcs a short curve with small amplitude at slow speed, focusing on her expression and hair.",
        "A low urban hum and a light breeze.",
        "A soft jazz mood at a moderate tempo with brushed drums held quietly."),
    "成熟旗袍・雨巷漫步": _p(
        "[Shot 1] 2.5D cel-shaded animation, a 29-year-old woman in a well-fitted dark-green embroidered qipao walks with an umbrella through a rain-wet stone alley, her pace composed and earrings swaying gently. The camera tracks from the side at a medium-far distance showing the qipao's lines and the alley's depth.",
        "Rain tapping the umbrella, footsteps on stone, and a distant guzheng.",
        "A sparse guzheng melody at a slow tempo, soft and unhurried."),
    "露肩禮服・月光舞會": _p(
        "[Shot 1] Romantic 3D CG animation, a 27-year-old woman in a pearl-white off-shoulder gown makes a slow half-turn in a ballroom lit by moonlight and warm lamps, the skirt opening naturally with a subtle smile. The camera holds a fixed full-body shot with a slight push in, keeping her features and dress consistent through the turn.",
        "The friction of the skirt and the soft echo of the ballroom.",
        "A gentle waltz at a moderate tempo with light strings."),
    "皮衣女騎士・霓虹街頭": _p(
        "[Shot 1] Photorealistic 3D CG animation, a 30-year-old woman in a cropped jacket, fitted top and trousers stands beside a heavy motorcycle and lifts off her sunglasses, her sharp short hair and confident smile catching blue-and-purple neon. The camera pushes in with small amplitude at slow speed on a waist-up framing showing the leather texture and her expression.",
        "The low idle of the motorcycle, distant traffic, and a restrained electronic pulse.",
        "A restrained electronic beat at a moderate tempo, low and even."),
    "海灘泳裝・夕陽廣告": _p(
        "[Shot 1] High-quality 3D CG resort commercial animation, a 28-year-old woman in an elegant one-piece swimsuit and a light wrap walks naturally along the shore, the sea wind lifting the wrap as the sunset warms her healthy skin and confident smile. The camera tracks steadily from the side on a full-body medium-far framing composed with the waves and the setting sun.",
        "Ocean waves, footsteps in the sand, and a sea breeze.",
        "A light, upbeat holiday score at a moderate tempo with a bright even feel."),
    "泳池畔・夏日時尚": _p(
        "[Shot 1] Bright 3D CG fashion animation, a 26-year-old woman in a simple bikini with a tied beach cover-up skirt adjusts a wide-brim hat by a pool, glancing up with a smile as the water reflections shimmer. The camera trucks with small amplitude at slow speed on an eye-level medium-far framing showing the complete styling and the pool.",
        "The soft response of pool water, rustling palm leaves, and a light tropical rhythm.",
        "A gentle tropical groove at a moderate tempo, soft and even."),
    "探戈舞者・紅裙轉身": _p(
        "[Shot 1] Cinematic 2.5D cel-shaded animation, a 32-year-old woman in a red dance dress and shoes completes a crisp turn and stop on a wooden stage, her posture upright and her expression composed and charismatic. The camera holds a stable full-body shot clearly showing the footwork and the swirl of the skirt.",
        "Dance shoes landing on the floor and the swell of an accordion.",
        "A concise tango rhythm at a moderate tempo with clear even accents."),
    "爵士歌姬・聚光舞台": _p(
        "[Shot 1] Polished 3D CG music animation, a 35-year-old woman in a deep-blue sequin gown hums a melody at a vintage microphone, swaying gently to the beat as a warm spotlight traces her elegant silhouette. The camera pushes in with small amplitude at slow speed on an eye-level half-body framing, attentive to her natural expression and lip movement.",
        "The warm reverberation of the room beneath her performance.",
        "A soft jazz piano and upright bass at a slow tempo, joined by a gentle wordless hum."),
    "絲巾女郎・敞篷海岸": _p(
        "[Shot 1] Retro 3D CG commercial animation, a 30-year-old woman in a fitted shirt and high-waist trousers leans by a convertible parked on the coast, reaching to hold a scarf lifted by the wind with an easy smile. The camera trucks with small amplitude at slow speed on a medium framing, keeping the coastline and the car body in the background.",
        "A sea wind, the light flutter of the scarf, and a soft retro-jazz mood.",
        "A light retro jazz at a moderate tempo, mellow and even."),
    "成熟御姐・都會西裝": _p(
        "[Shot 1] Refined Japanese-style 3D animation, a 32-year-old woman in a crisp white blazer, fitted top and trousers walks into a glass lobby and adjusts her collar, her gaze firm and her posture composed. The camera tracks and gradually settles from full body to half body, keeping natural proportions.",
        "Heels on the floor, the friction of fabric, and a steady urban ambience.",
        "A composed urban score at a moderate tempo, restrained and even."),
    "哥德女王・玫瑰長廊": _p(
        "[Shot 1] Dark-fantasy 3D CG animation, a 30-year-old woman in a black lace gown over an opaque lining walks slowly along a rose corridor holding a deep-red rose, her expression mysterious and elegant. The camera pulls back steadily with small amplitude at slow speed as candlelight and background bokeh shift softly.",
        "The friction of the skirt, faint footsteps, and a low string ambience.",
        "A low string bed at a slow tempo, dark and evenly sustained."),
    "精靈女王・月色森林": _p(
        "[Shot 1] High-quality fantasy 3D CG animation, an adult elf woman who appears about 30 in a silver-green off-shoulder gown and a delicate crown raises a hand to catch a falling petal in a moonlit forest, her expression serene. The camera arcs with medium amplitude at slow speed at eye level, keeping her hair, fabric and features continuous.",
        "Rustling leaves, faint night insects, and an ethereal harp.",
        "An airy solo harp at a slow tempo with widely spaced notes."),
    "科幻女特工・艙門登場": _p(
        "[Shot 1] Cinematic 3D CG sci-fi animation, a 28-year-old woman in a fully covering fitted tech combat suit steps out of a cold-lit hatch, pauses and lifts her gaze ahead, her styling sharp and confident. The camera pushes in with small amplitude at slow speed on a low-angle full-body framing settling to a medium shot.",
        "The pressurized hiss of the hatch, boot steps on the deck, and a low-frequency electronic ambience.",
        "A low electronic drone at a slow tempo with a single rising synth note."),
    "珠寶廣告・優雅側顏": _p(
        "[Shot 1] Premium 3D CG commercial animation, a 30-year-old woman in a black off-shoulder gown wearing delicate earrings and a necklace turns her head slowly to let the jewelry catch the light, her expression natural and her skin soft. The camera holds a shoulder-up portrait framing, the focus gliding smoothly from the earring to her eyes.",
        "The faint chime of jewelry over a quiet studio ambience.",
        "A soft piano at a slow tempo, gentle and evenly spaced."),
    "香水廣告・花園回眸": _p(
        "[Shot 1] Soft 3D CG animation, a 27-year-old woman in a light-gold slip dress strolls through a garden of white flowers and glances back with a smile as petals drift down, backlight tracing her long hair. The camera tracks steadily on a medium framing with a small push in to catch the glance.",
        "Birdsong, the light rustle of flowers and leaves, and a gentle breeze.",
        "A clear, airy string line at a moderate tempo, soft and rising."),
    "拉丁舞者・陽光露台": _p(
        "[Shot 1] Vivid 2.5D cel-shaded animation, a 29-year-old woman in a bright dance top and a high-waist fringe skirt performs two quick steps on a terrace with a bright smile, the fringe swaying naturally with the movement. The camera holds a fixed full-body medium-far shot keeping the limbs and footwork clear.",
        "Shoe beats, congas, and a lively latin rhythm.",
        "An upbeat latin groove at a lively tempo with congas and a clear pulse."),
    "復古佳人・酒廊燈影": _p(
        "[Shot 1] Retro-cinematic 3D CG animation, a 34-year-old woman in a wine-red velvet gown and long gloves sits at a round lounge table, gently setting down a non-alcoholic drink before looking up with a smile, warm light bringing out the fabric's sheen. The camera trucks with small amplitude at slow speed at eye level on a half-body framing focused on her expression and the texture.",
        "The light ring of a glass, distant low conversation, and a soft saxophone.",
        "A soft saxophone at a slow tempo, warm and even."),
    "東方舞者・絲帶旋舞": _p(
        "[Shot 1] Ornate 3D CG stage animation, a 28-year-old woman in a jewel-toned dance costume and a long skirt completes an expansive side turn holding a ribbon, her posture elegant as gold sequins reflect the stage light. The camera holds a fixed full-body shot keeping the ribbon's path and her limbs clear.",
        "The ribbon slicing through the air, the light chime of small bells, and soft percussion.",
        "A soft percussion pattern at a moderate tempo, gentle and even."),
    "海風長裙・時尚封面": _p(
        "[Shot 1] High-end 3D CG fashion animation, a 31-year-old woman in a sharply tailored white backless gown makes a slight turn and glances back on a sea-view terrace, the back edge of the fabric and the hem swaying in the wind, her air mature and confident. The camera trucks with small amplitude at slow speed on a full-body three-quarter rear framing, keeping the complete outfit and the sea view.",
        "A sea wind, distant waves, and a minimal ambience.",
        "A minimal solo piano at a slow tempo, spare and even."),
}

