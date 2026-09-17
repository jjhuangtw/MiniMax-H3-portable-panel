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

LONG_VIDEO_EXAMPLES = {
    "🏛 建築（長片範例）": _ARCH,
    "🛋 室內（長片範例）": _INTERIOR,
    "🧍 人物（長片範例）": _PEOPLE,
}
