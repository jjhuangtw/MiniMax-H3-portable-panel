# -*- coding: utf-8 -*-
"""Complete, ready-to-generate prompts written in MiniMax H3's official three-field
format (integrated_multimodal_description / overall_soundscape / non_diegetic_music),
following the official h3-prompt-writing guide. These are T2VA prompts: they need no
reference material, so they generate directly in the 文生影音 / FL2VA tabs.

Each demonstrates a different feature of the format — multi-shot cuts, camera-motion
vocabulary, speakers and dialogue, off-screen voiceover, on-screen text, diegetic sound
vs. audience-only score. All subjects are fictional; no real-person likenesses.
"""

OFFICIAL_FORMAT_EXAMPLES = {
    "清晨麵包店・獨白單鏡": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a warm medium-wide shot frames a small street bakery before sunrise as the middle-aged baker lifts the metal shutter. The camera pushes in with small amplitude at slow speed while he sets a fresh loaf on the flour-dusted wooden counter. The baker with a calm, slightly raspy voice (S1) says: <d>[English] First batch of the morning.</d> He wipes his hands on his apron and glances toward the door.

overall_soundscape: The metal shutter scrapes upward over a quiet street while trays clink softly inside. A single wall clock ticks, followed by light footsteps and the crisp crackle of the loaf's crust.

non_diegetic_music: A soft acoustic-guitar figure at a moderate tempo, joined by sparse upright-bass notes that fade gently at the end.""",

    "雨夜列車車窗・獨白": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a young woman sits beside a rain-covered train window in a dim carriage, a folded letter resting in her lap. The camera trucks right with small amplitude at slow speed as her reflection slides across the glass and the city lights blur past. The quiet, breathy young woman (S1) says: <d>[English] I get off at the next station.</d> She folds the letter along its existing crease and lowers her gaze.

overall_soundscape: The train wheels keep a steady metallic rhythm beneath a low ventilation hum. Rain ticks against the window while paper rustles softly in her hands.

non_diegetic_music: Sustained cello at a slow tempo with widely spaced piano tones, gradually decreasing in volume.""",

    "咖啡師拉花・特寫無台詞": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a tight overhead close-up frames a barista's hands pouring steamed milk into a dark espresso. The camera holds a static shot as a white rosetta blooms across the crema and the cup fills to the rim. The barista taps the pitcher down and slides the finished cup a few centimeters forward.

overall_soundscape: The steam wand hisses briefly before settling, followed by the soft swirl of milk against ceramic and the light clink of the pitcher on the counter. Low café room tone continues underneath.

non_diegetic_music: A relaxed jazz trio at a moderate tempo — brushed drums, walking bass, and soft piano chords held at a steady, even volume.""",

    "山頂日出・自然環境音": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a wide shot looks out from a rocky mountain ridge as the first sunlight spills across a sea of low clouds. The camera pedestals up with large amplitude at slow speed, revealing distant peaks catching the warm light while thin mist drifts through the foreground. A lone hiker stands motionless at the edge of the frame, facing the horizon.

overall_soundscape: A steady high-altitude wind moves across the ridge, carrying the faint calls of distant birds and the occasional shift of loose gravel underfoot.

non_diegetic_music: Sustained low strings at a slow tempo, joined by a single high sustained note that gradually swells in volume as the light spreads.""",

    "霓虹街頭・角色回眸（3D 動畫）": """integrated_multimodal_description: [Shot 1] Polished 3D CG animation, a stylish young woman in a long coat stands on a rain-slick neon street at night, her back to the camera. The camera arcs around her with medium amplitude at slow speed as she turns her head over her shoulder toward the lens, blue and magenta reflections sliding across the wet pavement and her hair.

overall_soundscape: Light rain patters on the pavement and a distant car passes through a puddle. A faint electric hum rises from the neon signs overhead.

non_diegetic_music: A restrained synthwave pulse at a moderate tempo with a soft arpeggiated line and a low sustained bass that holds steady throughout.""",

    "天橋雙人對話・雙鏡切換": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot frames two friends leaning on a pedestrian-bridge railing above evening traffic. The tall man in a grey jacket (S1) turns to the woman beside him and says: <d>[English] You really booked the tickets?</d> [Shot 2] At 00:03.000, the camera cuts to a closer shot of the woman with a bright, warm voice (S2), who smiles and replies: <d>[English] Both of them. We leave Friday.</d> She holds up two paper tickets between her fingers.

overall_soundscape: A steady flow of traffic passes below the bridge with the occasional distant horn. A light breeze moves fabric and paper as footsteps approach faintly from behind.

non_diegetic_music: A bright acoustic-guitar pattern at a moderate tempo with light hand-percussion, rising slightly in volume after the second line.""",

    "實驗室科學家・旁白（voiceover）": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a researcher in a white coat stands at a lab bench, lit by the cool glow of an instrument display. The camera pushes in with small amplitude at slow speed toward her focused expression. The composed female researcher (S1) says in an off-screen voiceover: <d>[English] We ran it forty times before it held.</d> while her lips remain completely closed. She adjusts a dial and watches a readout climb.

overall_soundscape: A low ventilation hum fills the room beneath the soft electronic beeps of the instrument. A dial clicks between settings and a faint fan spins up.

non_diegetic_music: Sparse electronic tones at a slow tempo over a quiet sustained pad that gradually increases in intensity.""",

    "廚房煎牛排・純現場音（無配樂）": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a close shot frames a cast-iron pan on a stovetop as a chef lowers a seasoned steak into shimmering oil. The camera pushes in with small amplitude at slow speed while butter foams and the chef spoons it over the surface. He tilts the pan and the flame briefly licks the edge.

overall_soundscape: The steak sears with a loud, sustained sizzle the moment it touches the pan, followed by the crackle of foaming butter and the soft scrape of a metal spoon against iron.

non_diegetic_music: N/A""",

    "街頭藝人・彈唱（diegetic）": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a busker sits on a wooden stool in a sunlit plaza, an acoustic guitar across his knee. The camera holds a static shot as he strums an opening chord and the warm-voiced young man (S1) sings: <d>[English] Slow down, the evening's ours tonight.</d> A small crowd gathers at the edge of the frame, and a coin drops into the open guitar case.

overall_soundscape: The plaza carries a soft crowd murmur and occasional footsteps on stone. A coin lands and rattles inside the guitar case, and a light breeze moves through nearby leaves.

non_diegetic_music: N/A""",

    "太空艙艙門・科幻登場": """integrated_multimodal_description: [Shot 1] Cinematic 3D CG animation, a low-angle medium shot frames a spacesuited explorer as a curved airlock door slides open ahead, cold blue light pouring out. The camera pushes in with small amplitude at slow speed while she steps forward and raises her gaze toward the lens; a soft indicator light pulses on her chest plate and the metal surface shows faint scuffs of use.

overall_soundscape: A pressurized hiss escapes the opening door, followed by the heavy magnetic steps of her boots on the deck and the low mechanical whir of the suit's servos.

non_diegetic_music: A low electronic drone at a slow tempo with a single rising synth note that swells as the door finishes opening.""",

    "雨夜店面・招牌文字（on-screen text）": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium shot frames the glass front of a small corner diner on a rainy night, warm light spilling onto the wet sidewalk. A red neon sign in the window reads "OPEN" and glows steadily above the door. The camera trucks left with small amplitude at slow speed as raindrops streak the glass and a silhouetted customer steps inside.

overall_soundscape: Steady rain falls on the awning and the pavement while distant traffic hisses over the wet road. The door's small bell rings once as it opens and closes.

non_diegetic_music: A mellow electric-piano line at a slow tempo with a soft brushed-snare rhythm held quietly underneath.""",

    "舞者旋轉・練舞室": """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a full shot frames a dancer in a soft flowing costume standing at the center of a bright studio. The camera arcs around her with medium amplitude at slow speed as she extends both arms and completes a single slow turn, the skirt lifting and settling naturally around her.

overall_soundscape: Soft footsteps pivot against the wooden floor while the costume's fabric rustles through the turn. A quiet room tone continues beneath, with a faint squeak of a shoe at the finish.

non_diegetic_music: A gentle solo piano at a slow tempo with sustained pedal tones that rise slightly in volume as the turn completes.""",
}
