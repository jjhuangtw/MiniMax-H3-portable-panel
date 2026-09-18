# -*- coding: utf-8 -*-
"""Ready-to-use LONG-VIDEO segment prompts (30 s - 2 min) for the 📼 長片 tab, for
learning. Each example is several segments separated by a line of `---`; the panel
snaps one segment to each ~10 s window and continues the previous segment's latents.

Segments are written with MiniMax H3's official prompt techniques: a style + shot
opening (`[Shot 1] Live-action, cinematic, ...`), camera-motion vocabulary
(Push In / Truck / Arc / Pedestal / Tilt with amplitude + speed), diegetic sound
folded into the description, on-screen text in "double quotes", `<Picture 1>` for a
carried character reference, and speaker IDs `(S1)` with `<d>[Language] ...</d>`.

Categories: 建築 / 室內 / 人物. Assumes the default 10 s per segment.
"""

# --- 建築 Architecture: camera-led tours, rich ambience, little or no dialogue ---
_ARCH = {
    "濱海玻璃宅・環繞導覽（約 30 秒／3 段）": """[Shot 1] Live-action, cinematic, a wide shot of a modern glass villa on a cliff at golden hour, the sea shimmering beyond a reflecting pool. The camera pushes in with small amplitude at slow speed toward the open entrance as light glints along the clean horizontal lines.
---
Live-action, cinematic, the view continues along the reflecting pool beside the villa. The camera trucks right with medium amplitude at slow speed, revealing floor-to-ceiling glass that mirrors the moving clouds while thin ripples cross the water.
---
Live-action, cinematic, the tour arrives at the seaward terrace. The camera pedestals up with large amplitude at slow speed, opening onto the infinity pool meeting the bright sea line as the last warm light spreads across the deck.""",

    "現代美術館・清晨巡禮（約 60 秒／6 段）": """[Shot 1] Live-action, cinematic, a minimalist museum atrium at dawn, pale light falling through a high skylight onto smooth concrete. The camera pushes in with small amplitude at slow speed toward a wide corridor lined with white walls.
---
Live-action, cinematic, the walk continues down the white corridor past evenly spaced abstract sculptures. The camera tracks forward at slow speed, holding the vanishing lines straight as soft light grazes each pedestal.
---
Live-action, cinematic, the corridor opens into a tall gallery. The camera tilts up with medium amplitude at slow speed, revealing a suspended installation of thin metal rods catching the skylight.
---
Live-action, cinematic, a curved ramp descends to a lower hall. The camera arcs around the ramp with medium amplitude at slow speed, keeping the concrete curve smooth against the bright wall behind it.
---
Live-action, cinematic, the lower hall frames a single large canvas on a far wall. The camera pushes in with small amplitude at slow speed, letting the texture of the brushwork gradually resolve.
---
Live-action, cinematic, the tour ends at a floor-to-ceiling window overlooking a quiet courtyard. The camera pulls out with medium amplitude at slow speed as morning light fills the room and a lone visitor steps into the frame.""",
}

# --- 室內 Interior: mood, changing light, materials, a calm human presence ---
_INTERIOR = {
    "北歐公寓・晨光流轉（約 60 秒／6 段）": """[Shot 1] Live-action, cinematic, a bright Scandinavian living room, pale oak floor and a linen sofa, sheer curtains drifting in a light breeze. The camera trucks left with small amplitude at slow speed across the room as morning light warms the wall.
---
Live-action, cinematic, the view settles on a low coffee table with a ceramic cup releasing thin steam. The camera pushes in with small amplitude at slow speed as the steam curls upward in the soft light.
---
Live-action, cinematic, sunlight shifts across a shelf of books and a small potted plant. The camera pans right with small amplitude at slow speed, following the moving band of light along the spines.
---
Live-action, cinematic, a window seat with a folded wool blanket comes into view. The camera pedestals down with small amplitude at slow speed to frame the light pooling on the cushion.
---
Live-action, cinematic, the kitchen counter beyond the room holds a glass of water catching the light. The camera pushes in with small amplitude at slow speed as bright refractions tremble on the countertop.
---
Live-action, cinematic, the room returns to the sofa, now fully lit. The camera pulls out with medium amplitude at slow speed, the curtains lifting once more as the space glows evenly.""",

    "侘寂茶室・一盞茶的時間（約 90 秒／9 段）": """[Shot 1] Live-action, cinematic, a wabi-sabi tea room with rough plaster walls and a low wooden table, warm side light on a handmade ceramic cup. The camera pushes in with small amplitude at slow speed toward the table.
---
Live-action, cinematic, a hand lifts an iron kettle over the cup. The camera holds a static shot as a slow ribbon of hot water fills it and steam rises.
---
Live-action, cinematic, the tea deepens in color inside the cup. The camera pushes in with small amplitude at slow speed until the surface reflects the window light.
---
Live-action, cinematic, a dried branch in a narrow vase stands beside the table. The camera trucks right with small amplitude at slow speed to include the vase and its long shadow.
---
Live-action, cinematic, light moves slowly across the plaster wall. The camera pans left with small amplitude at slow speed, tracing the faint texture of the surface.
---
Live-action, cinematic, the cup is raised gently from the table. The camera tilts up with small amplitude at slow speed following the cup toward soft light.
---
Live-action, cinematic, steam drifts across the frame in front of the window. The camera holds a static shot as the vapor thins and disappears.
---
Live-action, cinematic, the empty table remains with the cup set back down. The camera pulls out with small amplitude at slow speed, revealing the quiet room around it.
---
Live-action, cinematic, the room dims slightly as a cloud passes. The camera holds a static shot while the warm light softens across the whole space.""",
}

# --- 人物 People: a character (use <Picture 1>), actions, dialogue, continuity ---
_PEOPLE = {
    "海邊旅人的一天（約 60 秒／6 段，用 <Picture 1>）": """[Shot 1] Live-action, cinematic, the traveler shown in <Picture 1> stands on a quiet beach at sunrise, wearing a light shirt, facing the sea. The camera pushes in with small amplitude at slow speed as a gentle breeze lifts the hem of the shirt.
---
Live-action, cinematic, the same traveler from <Picture 1> begins to walk along the wet sand near the waterline. The camera tracks alongside at slow speed, keeping their appearance and clothing consistent while footprints form behind them.
---
Live-action, cinematic, the traveler stops to pick up a small shell. The camera pushes in with small amplitude at slow speed to their hands as they turn the shell over in the light.
---
Live-action, cinematic, the traveler looks out toward the horizon and takes a slow breath. The camera arcs around them with small amplitude at slow speed, the sea sparkling behind.
---
Live-action, cinematic, the traveler sits on a low rock and rests their arms on their knees. The camera holds a static shot as small waves roll in and out at their feet.
---
Live-action, cinematic, the traveler rises and continues down the beach as the light grows brighter. The camera pulls out with medium amplitude at slow speed, leaving them small against the wide shoreline.""",

    "咖啡館的邂逅・雙人對話（約 120 秒／12 段，用 <Picture 1>、(S1)(S2) 台詞）": """[Shot 1] Live-action, cinematic, a warm corner café in the afternoon; the young woman shown in <Picture 1> sits by the window with a book, preserving her appearance and clothing. The camera pushes in with small amplitude at slow speed as she turns a page.
---
Live-action, cinematic, the woman from <Picture 1> glances up as the café door opens. The camera holds a static shot while soft light falls across her table.
---
Live-action, cinematic, a young man steps in and pauses near the counter, looking around. The camera trucks right with small amplitude at slow speed to follow him toward her table.
---
Live-action, cinematic, the man stops beside the table. The clear, friendly young man (S1) says: <d>[English] Is this seat taken?</d> He gestures at the empty chair.
---
Live-action, cinematic, the woman from <Picture 1> smiles and closes her book. The warm-voiced young woman (S2) replies: <d>[English] It's all yours.</d> She moves her cup aside.
---
Live-action, cinematic, the man sits down across from her. The camera pushes in with small amplitude at slow speed to a two-shot as they settle into the seats.
---
Live-action, cinematic, a barista sets two cups on the table. The camera holds a static shot as steam rises and the two exchange a small nod of thanks.
---
Live-action, cinematic, the woman from <Picture 1> lifts her cup. The man (S1) says: <d>[English] Good book?</d> He leans forward slightly.
---
Live-action, cinematic, the woman turns the cover toward him. The woman (S2) says: <d>[English] The best one I've read this year.</d> She smiles and sets it down.
---
Live-action, cinematic, they both laugh quietly and look toward the window. The camera trucks left with small amplitude at slow speed to include the sunlit street outside.
---
Live-action, cinematic, the light warms as the afternoon turns. The camera holds a static shot on the two of them talking, cups now half empty.
---
Live-action, cinematic, the two rise to leave together. The camera pulls out with medium amplitude at slow speed, following them toward the café door and the bright street beyond.""",
}

# --- 房仲帶看 Real-estate agent property tour: one consistent agent (<Picture 1>)
# presents a property space by space, with Chinese presentation lines. Fictional agent. ---
_REALTOR = {
    "房仲帶看・接待中心＋樣品屋（約 30 秒／3 段，用 <Picture 1>）": """[Shot 1] Live-action, cinematic, the real estate agent shown in <Picture 1> stands in the bright lobby of a modern Taipei residential sales center, wearing a navy agent uniform, preserving her appearance and clothing. The camera pushes in with small amplitude at slow speed as she turns to the camera and gestures toward the space. The professional agent (S1) says: <d>[Chinese] 歡迎參觀，這是我們的接待中心。</d>
---
Live-action, cinematic, the same agent from <Picture 1> walks to a marble architectural model of the complex and presents it with an open hand. The camera trucks right with small amplitude at slow speed following her. The agent (S1) says: <d>[Chinese] 這是整個社區的規劃，中央有一座景觀中庭。</d>
---
Live-action, cinematic, the agent from <Picture 1> leads into a model-unit living room and gestures toward the floor-to-ceiling window. The camera arcs around her with small amplitude at slow speed as daylight fills the room. The agent (S1) says: <d>[Chinese] 客廳採光非常好，整面落地窗面向公園。</d>""",

    "房仲帶看・都會景觀三房（約 60 秒／6 段，用 <Picture 1>）": """[Shot 1] Live-action, cinematic, the real estate agent shown in <Picture 1> stands at the entrance of a modern residential tower at golden hour, wearing a navy uniform, preserving her appearance. The camera pedestals up with small amplitude at slow speed revealing the glass facade behind her. The professional agent (S1) says: <d>[Chinese] 這是今天要帶大家看的都會景觀三房。</d>
---
Live-action, cinematic, the same agent from <Picture 1> steps into a bright lobby with a stone reception desk and pendant lights. The camera tracks forward at slow speed following her past the seating. The agent (S1) says: <d>[Chinese] 一樓大廳有二十四小時管理櫃台。</d>
---
Live-action, cinematic, the agent from <Picture 1> enters the living room and gestures toward the open space. The camera arcs around her with small amplitude at slow speed as light pours through the window. The agent (S1) says: <d>[Chinese] 客廳挑高三米二，面向公園完全無遮蔽。</d>
---
Live-action, cinematic, the agent from <Picture 1> walks into the open-plan kitchen and rests a hand on the island. The camera trucks left with small amplitude at slow speed along the counter. The agent (S1) says: <d>[Chinese] 廚房是開放式設計，中島很適合下廚聚餐。</d>
---
Live-action, cinematic, the agent from <Picture 1> shows the main bedroom and gestures toward a walk-in closet. The camera pushes in with small amplitude at slow speed. The agent (S1) says: <d>[Chinese] 主臥有獨立更衣室和衛浴，非常隱私。</d>
---
Live-action, cinematic, the agent from <Picture 1> steps onto the balcony overlooking the city skyline at dusk. The camera pulls out with medium amplitude at slow speed to include her and the view. The agent (S1) says: <d>[Chinese] 陽台可以看到整個城市的天際線，歡迎預約賞屋。</d>""",

    "房仲帶看・豪宅公設一日（約 90 秒／9 段，用 <Picture 1>）": """[Shot 1] Live-action, cinematic, the real estate agent shown in <Picture 1> stands in the grand double-height lobby of a luxury residence, wearing a navy uniform, preserving her appearance. The camera pushes in with small amplitude at slow speed as she gestures a welcome. The professional agent (S1) says: <d>[Chinese] 今天帶大家參觀這棟豪宅的完整公設。</d>
---
Live-action, cinematic, the same agent from <Picture 1> presents the lobby's marble wall and chandelier. The camera tilts up with small amplitude at slow speed following her gesture. The agent (S1) says: <d>[Chinese] 大廳採用天然石材，燈飾是訂製的。</d>
---
Live-action, cinematic, the agent from <Picture 1> walks into the residents' lounge with soft seating and a fireplace. The camera trucks right with small amplitude at slow speed. The agent (S1) says: <d>[Chinese] 這裡是住戶交誼廳，可以接待客人。</d>
---
Live-action, cinematic, the agent from <Picture 1> shows the fitness gym with floor-to-ceiling windows. The camera tracks forward at slow speed past the equipment. The agent (S1) says: <d>[Chinese] 健身房設備齊全，採光也很好。</d>
---
Live-action, cinematic, the agent from <Picture 1> stands beside an indoor swimming pool, light rippling on the water. The camera arcs around her with small amplitude at slow speed. The agent (S1) says: <d>[Chinese] 恆溫游泳池一年四季都能使用。</d>
---
Live-action, cinematic, the agent from <Picture 1> presents a private cinema room with tiered seating. The camera pushes in with small amplitude at slow speed. The agent (S1) says: <d>[Chinese] 這是私人影廳，適合家庭聚會。</d>
---
Live-action, cinematic, the agent from <Picture 1> walks through a landscaped rooftop garden at golden hour. The camera trucks left with small amplitude at slow speed as grasses sway. The agent (S1) says: <d>[Chinese] 頂樓花園可以俯瞰整個城市。</d>
---
Live-action, cinematic, the agent from <Picture 1> enters a model unit's living room with warm light. The camera arcs around her with small amplitude at slow speed. The agent (S1) says: <d>[Chinese] 室內格局方正，每一房都有對外窗。</d>
---
Live-action, cinematic, the agent from <Picture 1> stands by the entrance and gives a warm closing gesture. The camera pulls out with medium amplitude at slow speed revealing the lobby around her. The agent (S1) says: <d>[Chinese] 感謝參觀，歡迎預約專人為您服務。</d>""",
}

LONG_VIDEO_EXAMPLES = {
    "🏛 建築（長片範例）": _ARCH,
    "🛋 室內（長片範例）": _INTERIOR,
    "🧍 人物（長片範例）": _PEOPLE,
    "🏠 房仲帶看（長片範例）": _REALTOR,
}
