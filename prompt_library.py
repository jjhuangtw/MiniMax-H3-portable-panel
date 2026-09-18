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
