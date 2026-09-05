from django.core.management.base import BaseCommand
from web.models import Category, Location, Place


class Command(BaseCommand):
    help = "Seeds demo categories, locations, and places for ZoneIn review app"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[*] Seeding ZoneIn places review data..."))

        # 1. Categories
        categories_data = [
            {"name": "คาเฟ่ & กาแฟ", "slug": "cafe", "icon": "fa-mug-hot", "color": "#f97316"},
            {"name": "ร้านอาหาร & สตรีทฟู้ด", "slug": "restaurant", "icon": "fa-utensils", "color": "#ef4444"},
            {"name": "ที่พัก & โรงแรม", "slug": "hotel", "icon": "fa-bed", "color": "#3b82f6"},
            {"name": "สถานที่ท่องเที่ยว", "slug": "travel", "icon": "fa-mountain-sun", "color": "#10b981"},
            {"name": "บาร์ & ไนท์ไลฟ์", "slug": "bar", "icon": "fa-martini-glass-citrus", "color": "#8b5cf6"},
        ]

        cat_objs = {}
        for c in categories_data:
            obj, _ = Category.objects.get_or_create(
                slug=c["slug"],
                defaults={"name": c["name"], "icon": c["icon"], "color": c["color"]},
            )
            cat_objs[c["slug"]] = obj

        # 2. Locations
        locations_data = [
            {"city": "กรุงเทพมหานคร", "zone": "อารีย์ - พหลโยธิน", "slug": "bkk-ari"},
            {"city": "กรุงเทพมหานคร", "zone": "ทองหล่อ - เอกมัย", "slug": "bkk-thonglor"},
            {"city": "กรุงเทพมหานคร", "zone": "สยาม - ปทุมวัน", "slug": "bkk-siam"},
            {"city": "กรุงเทพมหานคร", "zone": "เยาวราช - ตลาดน้อย", "slug": "bkk-yaowarat"},
            {"city": "เชียงใหม่", "zone": "นิมมานเหมินท์", "slug": "cnx-nimman"},
            {"city": "เชียงใหม่", "zone": "แม่ริม - ภูเขา", "slug": "cnx-maerim"},
            {"city": "ชลบุรี", "zone": "บางแสน - ชายหาด", "slug": "cbi-bangsaen"},
            {"city": "ภูเก็ต", "zone": "ย่านเมืองเก่า (Old Town)", "slug": "pkt-oldtown"},
        ]

        loc_objs = {}
        for l in locations_data:
            obj, _ = Location.objects.get_or_create(
                slug=l["slug"],
                defaults={"city": l["city"], "zone": l["zone"]},
            )
            loc_objs[l["slug"]] = obj

        # 3. Places
        places_data = [
            {
                "name": "Factory Coffee - Specialty BKK",
                "slug": "factory-coffee-specialty",
                "category": cat_objs["cafe"],
                "location": loc_objs["bkk-ari"],
                "rating": 4.9,
                "review_count": 348,
                "price_level": 2,
                "address": "49 ถนนพญาไท แขวงถนนพญาไท เขตราชเทวี กรุงเทพฯ",
                "image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&auto=format&fit=crop&q=80",
                "description": "ร้านกาแฟระดับแชมป์การันตีรางวัลมากมาย โดดเด่นด้วย Specialty Coffee เมนู Signature หลากหลาย นั่งชิลล์คุยงานสบาย พร้อมบาริสต้ามืออาชีพแนะนำเมล็ด",
                "tags": "Specialty Coffee, กาแฟดริป, แชมป์บาริสต้า, มีที่จอดรถ, อารีย์",
                "is_featured": True,
            },
            {
                "name": "Nana Coffee Roasters Ari",
                "slug": "nana-coffee-roasters-ari",
                "category": cat_objs["cafe"],
                "location": loc_objs["bkk-ari"],
                "rating": 4.8,
                "review_count": 215,
                "price_level": 2,
                "address": "ซอยอารีย์ 4 ฝั่งเหนือ แขวงพญาไท เขตพญาไท กรุงเทพฯ",
                "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&auto=format&fit=crop&q=80",
                "description": "คาเฟ่บรรยากาศสวนทรอปิคอลใจกลางอารีย์ มุมถ่ายรูปเพียบ มีเบเกอรี่และกาแฟ House Blend หลากหลายเมล็ด เหมาะกับคนชอบถ่ายรูปและนั่งพักผ่อน",
                "tags": "ถ่ายรูปสวย, สวนสวย, ขนมเค้ก, คาเฟ่อารีย์, Co-working",
                "is_featured": True,
            },
            {
                "name": "เจ๊โอว ข้าวต้มเป็ด (Jeh O Chula)",
                "slug": "jeh-o-chula",
                "category": cat_objs["restaurant"],
                "location": loc_objs["bkk-siam"],
                "rating": 4.7,
                "review_count": 920,
                "price_level": 2,
                "address": "113 ซอยจุฬาลงกรณ์ 22 แขวงรองเมือง เขตปทุมวัน กรุงเทพฯ",
                "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&auto=format&fit=crop&q=80",
                "description": "ตำนานมาม่าต้มยำหม้อไฟรอบดึกระดับมิชลินไกด์ หมูกรอบยำแซ่บ ยำกุ้งเต้น และเป็ดพะโล้เนื้อนุ่ม รสชาติจัดจ้านถึงใจสไตล์สตรีทฟู้ดกรุงเทพฯ",
                "tags": "มิชลินไกด์, มาม่าโอ้โห, อาหารรอบดึก, สยาม, สตรีทฟู้ด",
                "is_featured": True,
            },
            {
                "name": "theCOMMONS Thonglor",
                "slug": "thecommons-thonglor",
                "category": cat_objs["bar"],
                "location": loc_objs["bkk-thonglor"],
                "rating": 4.6,
                "review_count": 480,
                "price_level": 3,
                "address": "335 ซอยทองหล่อ 17 แขวงคลองตันเหนือ เขตวัฒนา กรุงเทพฯ",
                "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80",
                "description": "คอมมูนิตี้มอลล์สุดชิคสไตล์ Open-air แหล่งรวมร้านอาหาร บาร์ คราฟต์เบียร์ และกิจกรรมไลฟ์สไตล์ใจกลางทองหล่อ เป็นมิตรกับสัตว์เลี้ยง",
                "tags": "บาร์, ดนตรีสด, Pet-friendly, ทองหล่อ, นั่งชิลล์",
                "is_featured": False,
            },
            {
                "name": "Graph Contemporary Chiang Mai",
                "slug": "graph-contemporary-cnx",
                "category": cat_objs["cafe"],
                "location": loc_objs["cnx-nimman"],
                "rating": 4.8,
                "review_count": 180,
                "price_level": 2,
                "address": "ถนนเจริญเมือง ต.วัดเกต อ.เมือง เชียงใหม่",
                "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&auto=format&fit=crop&q=80",
                "description": "คาเฟ่สไตล์วินเทจคลาสสิก ผสมผสานศิลปะและกาแฟ Specialty เมนู Nitro และ Mocktail รสสัมผัสแปลกใหม่ กลิ่นอายเมืองเหนือสุดอบอุ่น",
                "tags": "เชียงใหม่, นิมมาน, กาแฟ Specialty, มู้ดวินเทจ, ศิลปะ",
                "is_featured": True,
            },
            {
                "name": "Onsen At Moncham Resort",
                "slug": "onsen-at-moncham-resort",
                "category": cat_objs["hotel"],
                "location": loc_objs["cnx-maerim"],
                "rating": 4.9,
                "review_count": 270,
                "price_level": 4,
                "address": "293 หมู่ 2 ต.โป่งแยง อ.แม่ริม เชียงใหม่",
                "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
                "description": "ที่พักออนเซ็นสไตล์เรียวกังญี่ปุ่นท่ามกลางหุบเขาแม่ริม อากาศเย็นสบายตลอดปี มีบ่อน้ำแร่ธรรมชาติ วิวทะเลหมอกยามเช้า และอาหารไคเซกิ",
                "tags": "ออนเซ็น, วิวภูเขา, ทะเลหมอก, ญี่ปุ่น, ที่พักเชียงใหม่, แม่ริม",
                "is_featured": True,
            },
            {
                "name": "Torry's Ice Cream Phuket Old Town",
                "slug": "torrys-ice-cream-phuket",
                "category": cat_objs["cafe"],
                "location": loc_objs["pkt-oldtown"],
                "rating": 4.7,
                "review_count": 510,
                "price_level": 2,
                "address": "16 ซอยรมณีย์ ต.ตลาดเหนือ อ.เมือง ภูเก็ต",
                "image_url": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=800&auto=format&fit=crop&q=80",
                "description": "ร้านไอศกรีมพรีเมียมในตึกเก่าชิโนโปรตุกีส เสิร์ฟไอศกรีมรสชาติขนมพื้นเมืองภูเก็ต เช่น บีโกหมอย และโอ้เอ๋ว รสชาติเป็นเอกลักษณ์",
                "tags": "ไอศกรีมโฮมเมด, ภูเก็ตโอลด์ทาวน์, ขนมพื้นเมือง, ถ่ายรูปชิคๆ",
                "is_featured": False,
            },
            {
                "name": "Chariot Bangsaen Beachfront",
                "slug": "chariot-bangsaen-beachfront",
                "category": cat_objs["restaurant"],
                "location": loc_objs["cbi-bangsaen"],
                "rating": 4.6,
                "review_count": 390,
                "price_level": 3,
                "address": "ถนนรอบเขาสามมุข ต.แสนสุข อ.เมือง ชลบุรี",
                "image_url": "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=800&auto=format&fit=crop&q=80",
                "description": "ร้านอาหารริมทะเลเขาสามมุข วิวพระอาทิตย์ตกดินสุดโรแมนติก อาหารทะเลสดๆ ปลากะพงทอดน้ำปลา กุ้งแม่น้ำเผา นั่งรับลมทะเลสบายๆ",
                "tags": "อาหารทะเล, ริมทะเล, พระอาทิตย์ตก, บางแสน, เขาสามมุข",
                "is_featured": False,
            },
            {
                "name": "Ba Hao Tian Mi 八號甜蜜 (เยาวราช)",
                "slug": "ba-hao-tian-mi-yaowarat",
                "category": cat_objs["cafe"],
                "location": loc_objs["bkk-yaowarat"],
                "rating": 4.5,
                "review_count": 320,
                "price_level": 1,
                "address": "8 ถนนผดุงด้าว แขวงสัมพันธวงศ์ เขตสัมพันธวงศ์ กรุงเทพฯ",
                "image_url": "https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=800&auto=format&fit=crop&q=80",
                "description": "คาเฟ่พุดดิ้งสไตล์โมเดิร์นไชนิสชื่อดังแห่งเยาวราช พุดดิ้งงาดำ พุดดิ้งชานมไข่มุก และโทสต์ฉ่ำเนย ทานง่าย หวานกำลังดี",
                "tags": "พุดดิ้ง, เยาวราช, ขนมหวาน, สไตล์จีน, ของกินกลางคืน",
                "is_featured": False,
            },
            {
                "name": "The Slate Phuket Resort & Spa",
                "slug": "the-slate-phuket-resort",
                "category": cat_objs["hotel"],
                "location": loc_objs["pkt-oldtown"],
                "rating": 4.9,
                "review_count": 420,
                "price_level": 4,
                "address": "116 หมู่ 1 หาดในยาง ต.สาคู อ.ถลาง ภูเก็ต",
                "image_url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
                "description": "รีสอร์ตหรูดีไซน์ Industrial Chic ที่ได้รับแรงบันดาลใจจากประวัติศาสตร์เหมืองแร่ดีบุกภูเก็ต สระว่ายน้ำ 3 สระ สปาระดับโลก ติดหาดในยาง",
                "tags": "รีสอร์ตหรู, ภูเก็ต, สปา, ติดทะเล, พูลวิลล่า, ถ่ายรูปสวย",
                "is_featured": True,
            },
            {
                "name": "เขาช่องลม นครนายก",
                "slug": "khao-chong-lom-nakhorn-nayok",
                "category": cat_objs["travel"],
                "location": loc_objs["cnx-maerim"], # or general travel
                "rating": 4.6,
                "review_count": 650,
                "price_level": 1,
                "address": "เขื่อนขุนด่านปราการชล ต.หินตั้ง อ.เมือง นครนายก",
                "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80",
                "description": "กรีนแลนด์เมืองไทย นั่งเรือหางยาวเข้าไปชมทุ่งหญ้าเขียวขจีและลำธารใสเย็นกลางหุบเขา เหมาะแก่การเดินป่าเบาๆ ถ่ายภาพธรรมชาติ",
                "tags": "ธรรมชาติ, เดินป่า, ภูเขา, น้ำตก, ถ่ายรูปธรรมชาติ, Unseen Thailand",
                "is_featured": False,
            }
        ]

        for p_data in places_data:
            Place.objects.update_or_create(
                slug=p_data["slug"],
                defaults=p_data,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] Successfully seeded {Category.objects.count()} categories, {Location.objects.count()} locations, and {Place.objects.count()} places!"
            )
        )
