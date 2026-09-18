# -*- coding: utf-8 -*-
"""Themed, ready-to-generate T2VA prompts in MiniMax H3's official three-field format
(integrated_multimodal_description / overall_soundscape / non_diegetic_music), written
with the official h3-prompt-writing techniques: [Shot 1] style opening, camera-motion
vocabulary (Push In / Truck / Arc / Tilt / Pedestal + amplitude + speed), diegetic sound
folded into the description, and audience-only score kept separate. All subjects fictional.

Themes: 美食料理 / 動物寵物 / 自然風景 / 產品・廣告, plus 室內・景觀 (merged into 建築).
"""


def _p(desc, soundscape, music="N/A"):
    return (f"integrated_multimodal_description: {desc}\n\n"
            f"overall_soundscape: {soundscape}\n\n"
            f"non_diegetic_music: {music}")


FOOD = {
    "煎牛排・鑄鐵鍋特寫": _p(
        "[Shot 1] Live-action, cinematic, a tight close-up of a cast-iron pan on a stovetop as a chef lowers a seasoned steak into shimmering oil. The camera pushes in with small amplitude at slow speed while butter foams and the chef spoons it over the surface.",
        "The steak sears with a loud sustained sizzle the moment it touches the pan, followed by the crackle of foaming butter and the soft scrape of a metal spoon against iron."),
    "拉麵・熱氣上升": _p(
        "[Shot 1] Live-action, cinematic, an overhead close-up of a steaming bowl of ramen, chopsticks lifting a tangle of noodles above the broth. The camera pulls out with small amplitude at slow speed as thin steam curls upward and drops fall back into the soup.",
        "Broth bubbles faintly while noodles slip and drip back into the bowl; distant kitchen clatter and a low room tone continue underneath.",
        "A gentle koto melody at a slow tempo with sparse plucked notes held at an even volume."),
    "手沖咖啡・注水": _p(
        "[Shot 1] Live-action, cinematic, a macro shot of a gooseneck kettle pouring a thin stream of hot water in slow spirals over fresh coffee grounds in a dripper. The camera holds a static shot as the grounds bloom and swell.",
        "A steady thin pour of water patters over the grounds, with the faint hiss of releasing gas and soft drips falling into the glass carafe below."),
    "握壽司・擺盤": _p(
        "[Shot 1] Live-action, cinematic, a close-up of a chef's hands pressing a piece of nigiri sushi and setting it precisely on a dark ceramic plate. The camera trucks right with small amplitude at slow speed to reveal a row of finished pieces glistening under soft light.",
        "The soft press of rice, a light brush of soy glaze, and the gentle tap of the plate on the counter, over a quiet restaurant room tone.",
        "A minimal solo shamisen at a slow tempo with restrained, evenly spaced notes."),
    "小籠包・蒸籠掀蓋": _p(
        "[Shot 1] Live-action, cinematic, a close-up of a bamboo steamer on a table; two hands lift the lid and a burst of steam rises to reveal plump soup dumplings. The camera pushes in with small amplitude at slow speed as the steam thins.",
        "The wooden lid scrapes softly as it lifts, releasing a rush of steam, followed by quiet bubbling and distant teahouse murmur."),
    "舒芙蕾鬆餅・翻面": _p(
        "[Shot 1] Live-action, cinematic, a close-up of a skillet where a tall fluffy souffle pancake is flipped by a spatula, its golden surface wobbling as it settles. The camera holds a static shot as a light dusting of powder falls over it.",
        "The soft sizzle of batter, the gentle slide and tap of the spatula, and the faint jiggle of the pancake settling, over a warm kitchen ambience.",
        "A light acoustic-ukulele pattern at a moderate tempo with a bright, even feel."),
    "調酒・注入雞尾酒": _p(
        "[Shot 1] Live-action, cinematic, a macro shot of a coupe glass as a bartender strains a pale cocktail into it, a twist of citrus peel resting on the rim. The camera pushes in with small amplitude at slow speed as the liquid settles and a single drop rolls down the stem.",
        "The clink of ice in the shaker, a smooth strained pour, and the soft ring of glass, over a low lounge room tone.",
        "A relaxed jazz brush-drum and upright-bass groove at a moderate tempo, held quietly."),
    "巧克力淋醬・蛋糕": _p(
        "[Shot 1] Live-action, cinematic, a macro shot of glossy chocolate ganache being poured over a round cake, flowing evenly down the sides. The camera arcs around the cake with small amplitude at slow speed as the surface turns mirror-smooth.",
        "A thick smooth pour of ganache, the faint drip at the cake's edge, and a soft spatula scrape, over a quiet kitchen ambience."),
}

ANIMALS = {
    "窗邊的貓": _p(
        "[Shot 1] Live-action, cinematic, a fluffy tabby cat sits on a windowsill in soft morning light, tail flicking slowly as it watches something outside. The camera pushes in with small amplitude at slow speed as the cat blinks and turns its head.",
        "A soft purr and the faint rustle of fur, with gentle birdsong and a light breeze coming through the open window."),
    "草地奔跑的狗": _p(
        "[Shot 1] Live-action, cinematic, a golden retriever bounds across a sunlit meadow toward the camera, ears flopping and tongue out. The camera tracks backward at fast speed keeping the dog centered as grass blurs past.",
        "Rhythmic paws thudding on soft ground, happy panting, and the swish of grass, over a light open-field breeze.",
        "A bright acoustic-guitar pattern at a lively tempo with light hand percussion."),
    "幼犬玩耍": _p(
        "[Shot 1] Live-action, cinematic, a small puppy tumbles after a rolling ball on a wooden floor, paws sliding as it pounces. The camera holds a low static shot at floor level as the puppy shakes the ball and looks up.",
        "Tiny scrabbling paws on wood, playful yips, and the light roll of the ball, over a quiet indoor room tone.",
        "A playful pizzicato-strings tune at a moderate tempo with a light bounce."),
    "草原上的馬": _p(
        "[Shot 1] Live-action, cinematic, a chestnut horse grazes on a wide grassland at golden hour, mane lifting in the wind. The camera arcs around the horse with medium amplitude at slow speed as it raises its head toward the light.",
        "Soft chewing of grass, an occasional snort and tail swish, and a steady low wind moving across the open plain."),
    "枝頭小鳥": _p(
        "[Shot 1] Live-action, cinematic, a small robin perches on a mossy branch in a green forest, tilting its head. The camera holds a static macro shot as the bird hops once and ruffles its feathers.",
        "Bright layered birdsong, the faint flutter of wings, and rustling leaves in a gentle breeze."),
    "水族箱魚群": _p(
        "[Shot 1] Live-action, cinematic, a shoal of small silver fish drifts through a planted aquarium, catching shafts of blue light. The camera trucks left with small amplitude at slow speed following the shimmering group past swaying plants.",
        "A soft continuous bubbling of the filter and the muffled underwater hum of moving water.",
        "A calm ambient synth pad at a slow tempo, sustained and gently evolving."),
    "兔子吃紅蘿蔔": _p(
        "[Shot 1] Live-action, cinematic, a white rabbit nibbles a carrot held between its paws on a straw-covered floor, nose twitching. The camera pushes in with small amplitude at slow speed to a close-up of its mouth and whiskers.",
        "Quick soft crunching of the carrot, tiny sniffing sounds, and the faint rustle of straw in a quiet barn."),
    "打呵欠的小貓": _p(
        "[Shot 1] Live-action, cinematic, a sleepy kitten curled on a knitted blanket opens its mouth in a wide slow yawn, then settles back down. The camera holds a static close-up as its eyes blink shut.",
        "A tiny high-pitched yawn and soft breathing, over a warm quiet indoor room tone.",
        "A tender music-box melody at a slow tempo with sparse delicate notes."),
}

NATURE = {
    "山頂日出": _p(
        "[Shot 1] Live-action, cinematic, a wide shot from a rocky ridge as the first sunlight spills across a sea of low clouds. The camera pedestals up with large amplitude at slow speed revealing distant peaks catching the warm light while thin mist drifts through the foreground.",
        "A steady high-altitude wind moves across the ridge, carrying faint distant birdcalls and the occasional shift of loose gravel.",
        "Sustained low strings at a slow tempo joined by a single high note that swells as the light spreads."),
    "晨霧森林": _p(
        "[Shot 1] Live-action, cinematic, tall pines rise through thick morning mist, shafts of pale light cutting between the trunks. The camera tracks forward at slow speed as the fog slowly parts to reveal a soft green clearing.",
        "Dripping condensation from branches, distant muffled birdsong, and a hushed still-air ambience."),
    "海浪拍岸": _p(
        "[Shot 1] Live-action, cinematic, waves roll in and break across dark rocks at a rugged coastline under an overcast sky. The camera holds a static wide shot as spray bursts upward and foam slides back over the stones.",
        "Powerful waves crash and recede over rock, with hissing foam, scattered spray, and a steady coastal wind."),
    "瀑布": _p(
        "[Shot 1] Live-action, cinematic, a tall waterfall plunges into a misty green pool surrounded by wet ferns. The camera tilts down with medium amplitude at slow speed following the falling water into the churning basin.",
        "A continuous roar of falling water, the hiss of rising mist, and echoing splashes in the rock basin."),
    "秋葉飄落": _p(
        "[Shot 1] Live-action, cinematic, golden and red maple leaves drift down through a quiet autumn forest, settling on a leaf-covered path. The camera pushes in with small amplitude at slow speed following one spiraling leaf to the ground.",
        "A soft rustle of leaves in a light breeze, the faint patter of leaves landing, and distant birdsong.",
        "A gentle solo piano at a slow tempo with widely spaced, wistful notes."),
    "落雪": _p(
        "[Shot 1] Live-action, cinematic, large snowflakes fall slowly over a silent evergreen forest at dusk, dusting the branches white. The camera holds a static wide shot as the snow thickens and settles.",
        "A muffled hush of falling snow, the faint creak of a laden branch, and a soft cold wind.",
        "Sparse sustained synth pads at a very slow tempo, soft and unhurried."),
    "沙漠沙丘": _p(
        "[Shot 1] Live-action, cinematic, wind-sculpted sand dunes stretch to the horizon under a low golden sun, thin streams of sand blowing off the crests. The camera trucks right with medium amplitude at slow speed along a razor-sharp ridge line.",
        "A dry gusting wind hisses over the sand, lifting fine grains that rattle softly across the dune surface."),
    "湖面倒影": _p(
        "[Shot 1] Live-action, cinematic, a still alpine lake mirrors snow-capped peaks and a pink dawn sky, faint ripples spreading from the shore. The camera pulls out with small amplitude at slow speed revealing the reflection stretching across the glassy water.",
        "Very gentle lapping at the shoreline, a distant loon call, and a calm mountain-air ambience.",
        "A soft sustained cello note at a slow tempo, warm and barely rising."),
}

PRODUCT = {
    "智慧型手機・登場": _p(
        "[Shot 1] 3D CG, product commercial, a sleek black smartphone floats and rotates slowly in a dark studio, edge light tracing its polished aluminum frame. The camera arcs around it with medium amplitude at slow speed as the screen lights up with a soft glow.",
        "A clean low electronic hum and a subtle rising tone as the screen activates, in an otherwise silent studio.",
        "A minimal electronic pulse at a moderate tempo with a single bright synth accent."),
    "球鞋・旋轉": _p(
        "[Shot 1] 3D CG, product commercial, a modern running sneaker rotates on a seamless white pedestal under crisp studio light, revealing its mesh texture and layered sole. The camera pushes in with small amplitude at slow speed toward the heel detail.",
        "A crisp studio silence with a faint airy whoosh as the shoe turns.",
        "An upbeat electronic beat at a moderate tempo with a punchy, even rhythm."),
    "香水瓶・光影": _p(
        "[Shot 1] Live-action, cinematic product shot, a faceted glass perfume bottle sits on a reflective black surface as a slow beam of light sweeps across it, refracting into soft rainbow glints. The camera trucks left with small amplitude at slow speed following the moving highlight.",
        "A near-silent studio ambience with a faint glassy shimmer as the light passes.",
        "A slow elegant piano arpeggio with sustained strings held softly beneath."),
    "手錶・微距": _p(
        "[Shot 1] Live-action, macro product shot, an automatic wristwatch rests at an angle, its second hand sweeping smoothly across a textured dial. The camera pushes in with small amplitude at slow speed until the ticking hand fills the frame.",
        "The delicate rhythmic tick of the movement and a faint metallic resonance, in a quiet studio.",
        "A refined minimal piano motif at a slow, precise tempo."),
    "汽車・車燈細節": _p(
        "[Shot 1] 3D CG, automotive commercial, a low-angle macro along the front of a sleek dark sports car as its LED headlight sequentially illuminates. The camera trucks right with medium amplitude at slow speed across the sculpted bodywork and grille.",
        "A deep resonant power-on hum and a subtle electric click as the lights energize, in a dark studio.",
        "A cinematic synth swell at a moderate tempo with a low driving pulse."),
    "耳機・懸浮旋轉": _p(
        "[Shot 1] 3D CG, product commercial, a pair of matte over-ear headphones floats and rotates slowly in a soft gradient studio, ear cushions catching gentle light. The camera arcs around them with medium amplitude at slow speed.",
        "A clean studio silence with a soft airy tone as the headphones turn.",
        "A smooth downtempo electronic groove at a moderate tempo with a mellow bassline."),
    "保養品瓶罐": _p(
        "[Shot 1] Live-action, cinematic product shot, a frosted-glass cosmetic jar sits among smooth stones and a single water droplet rolls down its side. The camera pushes in with small amplitude at slow speed as soft light glows through the frosted surface.",
        "A serene near-silent ambience with the faint sound of a single droplet and a soft water trickle.",
        "A calm ambient pad at a slow tempo, airy and evenly sustained."),
    "飲料罐・凝水": _p(
        "[Shot 1] Live-action, macro product shot, a chilled aluminum beverage can beaded with condensation stands on a dark surface as a droplet slides down and light catches the wet metal. The camera arcs around it with small amplitude at slow speed.",
        "The faint crackle of condensation and a soft fizz from inside the can, in a cool quiet studio.",
        "A fresh upbeat electronic pop groove at a moderate tempo with a crisp clap."),
}

# Merged into the 建築 category (interiors + designed landscapes).
INTERIOR_LANDSCAPE = {
    "飯店大堂・暖光巡覽": _p(
        "[Shot 1] Live-action, cinematic, a grand hotel lobby with a dark wood reception desk, brass details and hanging pendant lights, warm indirect lighting glowing on stone. The camera trucks left with small amplitude at slow speed past low seating toward the desk.",
        "A soft blurred murmur of distant conversation, gentle footsteps on stone, and a quiet spacious room tone.",
        "A restrained solo piano at a slow tempo with warm, evenly spaced notes."),
    "閱讀角落": _p(
        "[Shot 1] Live-action, cinematic, a cozy window reading nook with a folded wool blanket and a small stack of books, warm afternoon light pooling on the cushion. The camera pushes in with small amplitude at slow speed as dust motes drift in the light.",
        "A very quiet indoor room tone with the faint tick of a wall clock and a soft breeze at the window."),
    "屋頂花園": _p(
        "[Shot 1] Live-action, cinematic, a modern rooftop garden with timber decking, tall grasses and lounge chairs overlooking a hazy city skyline at golden hour. The camera pedestals up with medium amplitude at slow speed revealing the planted terrace and the view beyond.",
        "A gentle rooftop breeze rustling grasses and leaves, with a faint distant hum of the city below.",
        "A warm acoustic-guitar pattern at a relaxed tempo, soft and even."),
    "禪意庭院": _p(
        "[Shot 1] Live-action, cinematic, a Japanese zen courtyard with raked white gravel, moss, a stone lantern and a single maple, soft light filtering through leaves. The camera arcs around the lantern with small amplitude at slow speed.",
        "Rustling maple leaves, a distant wind chime, and the faint trickle of a small water basin in a serene garden.",
        "A minimal koto motif at a slow tempo with sparse resonant notes."),
    "現代廚房": _p(
        "[Shot 1] Live-action, cinematic, a bright minimalist kitchen with pale stone counters, matte cabinetry and a glass of water catching sunlight. The camera trucks right with small amplitude at slow speed across the clean surfaces as light refractions tremble on the countertop.",
        "A calm indoor ambience with the faint hum of a refrigerator and soft light footsteps on tile."),
    "美術館展廳": _p(
        "[Shot 1] Live-action, cinematic, a tall white gallery hall with a single large canvas on the far wall, even skylight washing the concrete floor. The camera tracks forward at slow speed down the corridor keeping the vanishing lines straight.",
        "A hushed spacious reverberation, the faint echo of distant footsteps, and a quiet indoor room tone."),
    "泳池露台": _p(
        "[Shot 1] Live-action, cinematic, an infinity pool on a terrace meets a bright sea horizon, white loungers and a sheer canopy drifting in the breeze, water rippling gently. The camera pushes in with small amplitude at slow speed toward the pool's edge.",
        "Soft lapping of pool water, a light sea breeze moving fabric, and distant gentle waves.",
        "A mellow downtempo groove at a relaxed tempo with a soft, even pulse."),
    "挑高樓梯中庭": _p(
        "[Shot 1] Live-action, cinematic, a soaring atrium with a sculptural curved staircase, pale stone and a glass roof letting daylight fall across the steps. The camera tilts up with medium amplitude at slow speed following the spiral toward the skylight.",
        "A wide airy reverberation, the faint sound of a distant door and soft footsteps echoing through the atrium."),
}

THEME_CATEGORIES = {
    "美食料理（8 組）": FOOD,
    "動物寵物（8 組）": ANIMALS,
    "自然風景（8 組）": NATURE,
    "產品・廣告（8 組）": PRODUCT,
}
