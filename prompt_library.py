"""Original, editable short-video prompts: scene, movement, camera and sound."""

ARCHITECTURE = [
    ("現代極簡別墅", "寫實建築攝影，白色幾何量體的現代別墅，大片玻璃與淺灰石材，入口水池映出立面，清晨樹影微微晃動。", "廣角鏡頭沿步道緩慢推向入口，保持建築垂直線筆直。", "微風、樹葉沙沙聲、輕微水聲。"),
    ("清水模住宅", "清水模住宅庭院，細緻模板紋理與深色金屬窗框，午後斜陽在混凝土牆上形成明暗分界，庭院小樹隨風輕搖。", "低速橫移，展現牆面厚度與空間層次。", "遠處鳥鳴、葉片摩擦聲、安靜庭院環境音。"),
    ("日式庭院與緣側", "日式木造住宅緣側面向枯山水庭院，白砂、苔蘚、石燈籠與楓樹，竹簾輕輕擺動，光線柔和。", "由木廊緩慢推向庭院，單一連續鏡頭。", "竹葉聲、風鈴輕響、遠處流水聲。"),
    ("北歐客廳", "明亮北歐風客廳，淺橡木地板、米白布沙發與簡潔家具，柔和日光透過薄紗窗簾，窗簾隨風微動。", "從客廳一角平穩橫移，維持自然透視。", "輕柔室內空氣聲、窗外鳥鳴。"),
    ("侘寂茶室", "侘寂風茶室，粗糙灰泥牆、原木矮桌、手工陶杯與乾燥花枝，溫暖側光照出自然材質，熱茶蒸氣緩慢上升。", "由桌邊中景緩慢推近茶杯，背景保留空間輪廓。", "細微倒茶聲、安靜室內環境音。"),
    ("工業風 Loft", "挑高工業風閣樓，紅磚牆、黑色鋼梁與大面積格窗，皮革沙發與木桌，午後光束中可見細微浮塵。", "廣角緩慢向前移動，展現挑高與鋼構比例。", "遠處城市低鳴、輕微室內回音。"),
    ("豪宅挑高大廳", "精品住宅挑高大廳，天然大理石、弧形樓梯與垂吊燈飾，暖色間接照明映在石材表面，空間整潔。", "從入口緩慢推進並輕微仰拍，樓梯結構保持穩定。", "柔和空調聲、寬敞空間回音。"),
    ("精品飯店大堂", "精品飯店大堂，深木色接待櫃台、黃銅細節、藝術擺件與暖色座椅，窗外車燈緩慢掠過玻璃。", "沿座椅旁平滑橫移，最後停在接待櫃台構圖。", "低聲交談的模糊環境音、輕柔鋼琴。"),
    ("玻璃帷幕辦公樓", "現代玻璃帷幕辦公大樓，整齊立面反射藍天與緩慢移動的雲，前方植栽與廣場具有真實尺度。", "街道視角緩慢仰拍，立面格線連續、不扭曲。", "遠處交通聲、都市微風。"),
    ("摩天樓空拍", "黃金時刻的城市摩天樓群，玻璃與金屬立面反射夕陽，街道車流緩慢移動，遠景帶有自然空氣透視。", "穩定空拍沿天際線平緩側移，不快速旋轉。", "高空風聲、低沉城市環境音。"),
    ("海景度假別墅", "面向海洋的度假別墅，木質露台與無邊際泳池連接藍色海平面，白色遮陽簾輕晃，池水泛起波紋。", "沿泳池邊緩慢向海景推進。", "海浪、海風、泳池細微水聲。"),
    ("山林木屋", "松林中的木造山屋，斜屋頂與石砌基座，清晨薄霧飄過林間，室內透出溫暖燈光，枝葉輕微擺動。", "沿林間小徑平穩接近木屋。", "林間鳥鳴、微風、腳踩碎石聲。"),
    ("中式四合院", "傳統中式四合院，灰瓦屋頂、木格窗與石板庭院，中央樹木投下斑駁光影，落葉沿地面輕輕滑動。", "由月洞門緩慢推入庭院，保持對稱構圖。", "樹葉聲、遠處鳥鳴、庭院空間回音。"),
    ("歐式古典建築", "歐式古典石造建築，柱廊、拱窗與雕花簷口細節清晰，暖色夕陽掠過立面，前景噴泉持續流動。", "低角度沿柱廊緩慢橫移，比例自然。", "噴泉流水、廣場腳步的遠處回音。"),
    ("哥德式教堂", "哥德式教堂內部，高聳尖拱與彩繪玻璃，彩色日光落在石板地面，空氣中浮塵緩慢移動，莊嚴寧靜。", "沿中央走道緩慢向前，略微仰拍拱頂。", "寬闊室內殘響、低音管風琴氛圍。"),
    ("未來曲線展館", "未來感公共展館，流線型白色屋頂、連續曲面與大面積玻璃，周圍淺水池反射建築，雲影緩慢移動。", "平穩繞行建築一小段弧線，結構形狀保持一致。", "水面輕響、廣場微風、柔和電子氛圍音。"),
    ("街角咖啡館", "溫暖的街角咖啡館，木框玻璃門、磚牆與戶外小桌，室內暖光透出，門口盆栽隨風輕動，無可辨識招牌。", "從街道側面緩慢靠近窗邊。", "咖啡機蒸氣、杯盤輕響、遠處街道聲。"),
    ("圖書館閱讀空間", "現代圖書館，層層木質書架、整齊閱讀桌與高窗，柔和自然光照亮書脊，空間安靜而有秩序。", "沿書架通道低速前進，保持透視線穩定。", "遠處翻頁聲、輕微腳步、室內環境音。"),
    ("美術館白盒子", "極簡美術館，潔白牆面、淺灰地板與幾何雕塑，天窗灑下均勻柔光，材質和陰影乾淨自然。", "緩慢側移經過雕塑，利用前後景展現空間深度。", "輕微鞋底聲、空曠展廳回音。"),
    ("雨夜建築立面", "雨夜的現代商業建築，暖色窗光與立面洗牆燈映在濕潤路面，細雨持續落下，雨水沿排水溝流動。", "街道低角度緩慢推近，反射隨視角自然變化。", "細雨、路面積水聲、遠處車流。"),
]

PEOPLE = [
    ("自然人像微笑", "寫實人像，一名成年女性站在窗邊柔光中，穿米色襯衫，自然眨眼並露出輕微微笑，皮膚保留真實紋理。", "眼平中近景緩慢推近，五官與髮型保持一致。", "細微呼吸、安靜室內環境音。"),
    ("男性商務形象", "一名成年男性穿合身深色西裝站在明亮辦公室，輕輕整理袖口後抬眼看向鏡頭，神情沉穩自然。", "胸部以上中近景，鏡頭穩定。", "衣料摩擦、柔和辦公室環境音。"),
    ("街頭時尚走拍", "一名成年時尚模特穿長版外套沿城市人行道自然步行，衣襬隨步伐擺動，背景行人柔焦，午後光線自然。", "與人物同速平穩後退跟拍，保持全身構圖。", "清晰腳步、遠處車流、輕微衣料聲。"),
    ("棚拍時裝展示", "一名成年模特站在純灰攝影棚，穿剪裁俐落的服裝，緩慢側轉四分之一圈後停下，服裝材質細節清楚。", "固定全身鏡頭，柔和主光與輪廓光。", "輕微腳步與衣料摩擦、簡潔節奏配樂。"),
    ("咖啡館閱讀", "一名成年女性坐在咖啡館窗邊閱讀，輕輕翻過一頁，手邊熱咖啡升起蒸氣，暖色日光照在桌面。", "側面中景緩慢推近，手部動作自然。", "翻頁、杯盤輕響、遠處咖啡機聲。"),
    ("城市通勤", "一名成年上班族提著公事包走過清晨街道，步伐從容，看到前方路口後稍微放慢速度，背景車流自然。", "腰部高度側面跟拍，動作連續。", "腳步、城市交通聲、衣料摩擦。"),
    ("公園慢跑", "一名成年跑者穿運動服在公園步道慢跑，呼吸與擺臂配合節奏，清晨陽光穿過樹葉，神情專注。", "側前方穩定跟拍，保持人物比例自然。", "規律腳步、呼吸、鳥鳴。"),
    ("健身啞鈴訓練", "一名成年健身者在整潔健身房做一次緩慢啞鈴彎舉，手肘穩定，肌肉隨動作自然收縮，姿勢受控。", "固定腰部以上中景，清晰呈現雙臂動作。", "呼吸、器材輕响、低沉室內環境音。"),
    ("舞者緩慢轉身", "一名成年舞者穿柔軟舞衣站在明亮練舞室，舒展雙臂並完成一次緩慢轉身，衣裙自然擺動，動作優雅。", "穩定全身鏡頭，人物始終完整入鏡。", "輕柔腳步、衣裙摩擦、舒緩鋼琴。"),
    ("鋼琴演奏", "一名成年鋼琴家在小型音樂廳專注演奏，雙手自然移動於琴鍵上，身體隨節奏輕微擺動，暖色舞台光。", "側面中景，人物與琴鍵同時入鏡。", "與演奏動作相配的柔和鋼琴、音樂廳殘響。"),
    ("廚師料理", "一名成年廚師在乾淨廚房中緩慢攪拌鍋內食材，熱氣自然上升，神情專注，金屬鍋具反光柔和。", "側前方中景輕微推近，保留手部與鍋具。", "食材滋滋聲、鍋鏟碰鍋聲、抽風環境音。"),
    ("職人工坊", "一名成年木工在工坊中用砂紙打磨木板，動作緩慢有力，木紋清晰，側窗光照亮細小木屑。", "由半身中景緩慢推向工作中的雙手。", "砂紙摩擦木材、工坊低沉環境音。"),
    ("陶藝拉坯", "一名成年陶藝師坐在拉坯機前，以沾水雙手扶住旋轉的陶土，陶坯輪廓逐漸變得平順，工作室光線溫暖。", "手部與陶坯中近景，固定鏡頭。", "轉盤低鳴、濕陶土摩擦聲、細微水聲。"),
    ("醫師親切形象", "一名成年醫師穿乾淨白袍站在明亮診間，收起手中資料後輕輕點頭微笑，背景整潔，無可辨識個人資料。", "眼平半身鏡頭，柔和自然光。", "紙張輕響、安靜診間環境音。"),
    ("旅人海邊漫步", "一名成年旅人沿海邊沙灘慢慢步行，穿輕便襯衫，海風吹動髮絲與衣角，夕陽映出柔和輪廓光。", "側後方中遠景穩定跟拍。", "海浪、踩沙腳步、海風。"),
    ("山林健行", "一名成年健行者背著背包沿森林小徑前進，跨過一小段樹根，動作自然穩定，晨霧與斑駁陽光穿過樹林。", "後側方平穩跟拍，人物全身入鏡。", "鞋底踩落葉、背包摩擦、林間鳥鳴。"),
    ("雨夜情緒特寫", "一名成年女性站在雨夜屋簷下，凝望街道後緩慢轉頭，表情從沉思變得平靜，髮絲帶著細小水珠。", "眼平近景緩慢推近，臉部身份與膚色穩定。", "雨聲、遠處車輪水聲、細微呼吸。"),
    ("銀髮長者肖像", "一名銀髮長者坐在庭院木椅上，溫和地望向鏡頭並微笑，皺紋與皮膚紋理自然，樹葉光影輕輕晃動。", "眼平中近景，緩慢而克制的推鏡。", "鳥鳴、樹葉聲、平靜呼吸。"),
    ("古風人物漫步", "一名成年人物穿素雅傳統長袍在竹林石徑緩步前行，衣袖隨風輕動，神情平和，清晨薄霧層次自然。", "側面中遠景跟拍，衣服與五官保持一致。", "石徑腳步、竹葉摩擦、淡淡笛聲。"),
    ("科幻角色登場", "一名成年科幻探險者穿細緻太空裝站在飛船艙門前，緩慢抬頭望向前方，胸前指示燈柔和閃爍，金屬表面有使用痕跡。", "低角度半身鏡頭緩慢推近，造型與身體結構穩定。", "艙內低鳴、呼吸、裝備細微機械聲。"),
]


GLAMOUR_ANIMATION = [
    ("黑色晚禮服・紅毯回眸", "精緻 3D 時尚動畫，一名 28 歲成年女性穿黑色合身晚禮服與高跟鞋，在紅毯上走兩步後優雅回眸，裙襬輕擺，神情自信迷人，暖色閃光勾勒輪廓。", "全身中遠景緩慢跟拍，停在四分之三側身構圖，保留服裝完整造型。", "高跟鞋腳步、遠處快門、低調弦樂。"),
    ("緞面洋裝・城市天台", "電影級 3D 動畫，一名 30 歲成年女性穿酒紅色不透明緞面細肩帶洋裝，站在城市天台欄杆旁輕輕轉身，晚風吹動長髮，霓虹在布料上形成柔和反光。", "眼平半身鏡頭緩慢繞行小段弧線，焦點停留在表情與髮絲。", "都市低鳴、微風、柔和爵士樂。"),
    ("成熟旗袍・雨巷漫步", "細膩三渲二動畫，一名 29 歲成年女性穿剪裁合身的墨綠刺繡旗袍，撐傘走過雨後石板巷，步伐從容，耳飾輕晃，眼神溫柔而自信。", "中遠景側面跟拍，呈現旗袍線條與雨巷景深。", "雨滴落傘、石板腳步、遠處古箏。"),
    ("露肩禮服・月光舞會", "浪漫 3D 動畫，一名 27 歲成年女性穿珍珠白露肩長禮服，在月光與暖燈交織的舞廳緩慢轉半圈，裙襬自然展開，微笑含蓄。", "固定全身鏡頭略微推近，旋轉時保持五官與服裝一致。", "裙襬摩擦、輕柔華爾滋、舞廳回音。"),
    ("皮衣女騎士・霓虹街頭", "寫實風格 3D 動畫，一名 30 歲成年女性穿短版皮衣、合身上衣與長褲，站在重型機車旁摘下墨鏡，俐落短髮與自信笑容映著藍紫霓虹。", "腰部以上中景緩慢推近，展現皮革材質與表情。", "機車低沉怠速、遠處車流、節制電子節奏。"),
    ("海灘泳裝・夕陽廣告", "高品質 3D 度假廣告動畫，一名 28 歲成年女性穿典雅連身泳裝與輕薄披肩，在海邊自然散步，海風吹動披肩，夕陽照亮健康膚色與自信笑容。", "全身中遠景平穩側拍，畫面以人物、海浪與夕陽共同構圖。", "海浪、踩沙腳步、輕快度假配樂。"),
    ("泳池畔・夏日時尚", "明亮 3D 時尚動畫，一名 26 歲成年女性穿簡潔比基尼泳裝並搭配繫好的沙灘罩裙，在泳池邊扶正寬簷帽，抬眼微笑，水面反光自然閃動。", "眼平中遠景緩慢橫移，呈現完整時尚造型與泳池環境。", "池水輕響、棕櫚葉聲、輕柔熱帶節奏。"),
    ("探戈舞者・紅裙轉身", "電影感三渲二動畫，一名 32 歲成年女性穿紅色舞裙與舞鞋，在木地板舞台完成一個俐落的轉身收步，姿態挺拔，表情沉著而有魅力。", "穩定全身鏡頭，清楚呈現步伐與裙襬動態。", "舞鞋落地、手風琴、簡潔探戈節拍。"),
    ("爵士歌姬・聚光舞台", "精緻 3D 音樂動畫，一名 35 歲成年女性穿深藍亮片長禮服，站在復古麥克風前輕哼旋律，隨節拍微微擺動，暖色聚光燈映出優雅輪廓。", "眼平半身鏡頭緩慢推近，注重自然表情與口型。", "輕柔無詞哼唱、爵士鋼琴、低音提琴。"),
    ("絲巾女郎・敞篷海岸", "復古 3D 廣告動畫，一名 30 歲成年女性穿合身襯衫與高腰長褲，倚在停靠海岸的敞篷車旁，伸手按住被風吹起的絲巾，露出灑脫笑容。", "中景緩慢側移，保留海岸線與車身作為背景。", "海風、絲巾輕響、復古輕爵士。"),
    ("成熟御姐・都會西裝", "精緻日系動畫，一名 32 歲成年女性穿俐落白色西裝外套、合身內搭與長褲，走進玻璃大廳後輕輕整理領口，眼神堅定，姿態從容。", "全身跟拍逐漸收至半身，保持比例自然。", "高跟鞋聲、衣料摩擦、沉穩都市配樂。"),
    ("哥德女王・玫瑰長廊", "暗色奇幻 3D 動畫，一名 30 歲成年女性穿黑色蕾絲覆面料長裙，服裝內襯不透明，沿玫瑰長廊緩步前行，手持一朵深紅玫瑰，神情神秘優雅。", "半身鏡頭平穩後退，燭光與背景散景柔和變化。", "裙襬聲、輕微腳步、低沉弦樂。"),
    ("精靈女王・月色森林", "高品質奇幻 3D 動畫，一名外貌約 30 歲的成年精靈女性穿銀綠色露肩長禮服與精緻冠飾，在月色森林中抬起手接住飄落花瓣，神情沉靜迷人。", "眼平中景緩慢繞行，髮絲、衣料與五官保持連續。", "樹葉聲、夜間蟲鳴、空靈豎琴。"),
    ("科幻女特工・艙門登場", "電影級 3D 科幻動畫，一名 28 歲成年女性穿完整覆蓋身體的合身科技戰鬥服，走出亮著冷光的艙門，停步後抬眼看向前方，造型俐落自信。", "低幅度仰拍全身構圖，緩慢推至中景。", "艙門氣壓声、靴子腳步、低頻電子氛圍。"),
    ("珠寶廣告・優雅側顏", "精品 3D 廣告動畫，一名 30 歲成年女性穿黑色露肩禮服，佩戴細緻耳環與項鍊，緩慢轉頭讓珠寶捕捉光線，表情自然，皮膚細節柔和。", "肩部以上人像特寫，焦點由耳環平滑移至眼睛。", "細微珠寶輕響、柔和鋼琴、安靜棚拍環境。"),
    ("香水廣告・花園回眸", "柔美 3D 動畫，一名 27 歲成年女性穿淡金色細肩帶長裙，漫步開滿白花的花園後回眸微笑，花瓣隨微風飄落，逆光勾勒長髮。", "中景平穩跟拍，以小幅推鏡捕捉回眸表情。", "鳥鳴、花葉輕響、清透弦樂。"),
    ("拉丁舞者・陽光露台", "鮮明三渲二動畫，一名 29 歲成年女性穿色彩明亮的舞蹈短上衣與高腰流蘇裙，在露台完成兩步輕快舞步，笑容明亮，流蘇隨動作自然擺動。", "固定全身中遠景，保持四肢與步伐清晰。", "鞋底節拍、康加鼓、輕快拉丁音樂。"),
    ("復古佳人・酒廊燈影", "復古電影風格 3D 動畫，一名 34 歲成年女性穿酒紅絲絨長裙與長手套，坐在酒廊圓桌旁輕輕放下無酒精飲品，抬頭微笑，暖光照出布料光澤。", "眼平半身鏡頭緩慢側移，以表情與服裝質感為主。", "玻璃杯輕響、遠處低聲交談、柔和薩克斯風。"),
    ("東方舞者・絲帶旋舞", "華麗 3D 舞台動畫，一名 28 歲成年女性穿寶石色專業舞蹈服與長裙，手持絲帶完成一個舒展的側轉，姿態優雅，金色飾片反射舞台光。", "全身固定鏡頭，絲帶運動軌跡與四肢保持清楚。", "絲帶劃過空氣、鈴飾輕響、柔和打擊樂。"),
    ("海風長裙・時尚封面", "高端 3D 時尚動畫，一名 31 歲成年女性穿剪裁俐落的白色露背長禮服，站在海景露台輕微側轉並回眸，背部衣料邊緣與裙襬自然隨風擺動，氣質成熟自信。", "全身四分之三側後方構圖，緩慢橫移，保留完整服裝與海景。", "海風、遠處浪聲、極簡鋼琴。"),
]


def build_templates(entries):
    return {
        name: f"{scene}\n\n鏡頭：{camera}\n\n聲音：{sound}\n\n單一連續鏡頭，動作自然連貫，光影一致。不要文字、字幕、標誌或浮水印。"
        for name, scene, camera, sound in entries
    }


PROMPT_CATEGORIES = {
    "建築（20 組）": build_templates(ARCHITECTURE),
    "人物（20 組）": build_templates(PEOPLE),
    "成年女性・性感動畫（20 組）": build_templates(GLAMOUR_ANIMATION),
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
