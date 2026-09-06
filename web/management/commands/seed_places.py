from django.core.management.base import BaseCommand
from web.models import Category, Location, Place


class Command(BaseCommand):
    help = "Seeds demo categories, locations, and places in Sisaket for ZoneIn"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[*] Seeding Sisaket places review data..."))

        # 1. Categories
        categories_data = [
            {"name": "สถานที่ท่องเที่ยว & ธรรมชาติ", "slug": "travel", "icon": "fa-mountain-sun", "color": "#10b981"},
            {"name": "โบราณสถาน & วัดวาอาราม", "slug": "culture", "icon": "fa-landmark-dome", "color": "#8b5cf6"},
            {"name": "คาเฟ่ & กาแฟ", "slug": "cafe", "icon": "fa-mug-hot", "color": "#f97316"},
            {"name": "ร้านอาหาร & สตรีทฟู้ด", "slug": "restaurant", "icon": "fa-utensils", "color": "#ef4444"},
            {"name": "ที่พัก & รีสอร์ต", "slug": "hotel", "icon": "fa-bed", "color": "#3b82f6"},
        ]

        cat_objs = {}
        for c in categories_data:
            obj, _ = Category.objects.update_or_create(
                slug=c["slug"],
                defaults={"name": c["name"], "icon": c["icon"], "color": c["color"]},
            )
            cat_objs[c["slug"]] = obj

        # Clear old non-Sisaket locations
        Location.objects.exclude(city="ศรีสะเกษ").delete()

        # 2. Sisaket Locations
        locations_data = [
            {"city": "ศรีสะเกษ", "zone": "อ.เมืองศรีสะเกษ", "slug": "ssk-muang"},
            {"city": "ศรีสะเกษ", "zone": "อ.กันทรลักษ์", "slug": "ssk-kantharalak"},
            {"city": "ศรีสะเกษ", "zone": "อ.อุทุมพรพิสัย", "slug": "ssk-uthumphon"},
            {"city": "ศรีสะเกษ", "zone": "อ.ขุนหาญ", "slug": "ssk-khunhan"},
            {"city": "ศรีสะเกษ", "zone": "อ.ราษีไศล", "slug": "ssk-rasisalai"},
            {"city": "ศรีสะเกษ", "zone": "อ.ขุขันธ์", "slug": "ssk-khukhan"},
            {"city": "ศรีสะเกษ", "zone": "อ.ห้วยทับทัน", "slug": "ssk-huaitapthan"},
            {"city": "ศรีสะเกษ", "zone": "อ.ไพรบึง", "slug": "ssk-phraibueng"},
        ]

        loc_objs = {}
        for l in locations_data:
            obj, _ = Location.objects.update_or_create(
                slug=l["slug"],
                defaults={"city": l["city"], "zone": l["zone"]},
            )
            loc_objs[l["slug"]] = obj

        # 3. Sisaket Places
        places_data = [
            {
                "name": "ผามออีแดง ชายแดนไทย",
                "slug": "pha-mo-e-dang",
                "category": cat_objs["travel"],
                "location": loc_objs["ssk-kantharalak"],
                "rating": 4.9,
                "review_count": 890,
                "price_level": 1,
                "address": "อุทยานแห่งชาติเขาพระวิหาร ต.เสาธงชัย อ.กันทรลักษ์ จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=80",
                "description": "จุดชมวิวหน้าผาสูงตระหง่าน ชมทะเลหมอกและพระอาทิตย์ขึ้นสุดอลังการ มองเห็นผืนป่ากัมพูชาและภาพสลักนูนต่ำอายุกว่าพันปี",
                "tags": "ทะเลหมอก, พระอาทิตย์ขึ้น, จุดชมวิว, เขาพระวิหาร, ธรรมชาติ",
                "is_featured": True,
            },
            {
                "name": "วัดพระธาตุสุพรรณหงส์",
                "slug": "wat-phra-that-suphannahong",
                "category": cat_objs["culture"],
                "location": loc_objs["ssk-muang"],
                "rating": 4.8,
                "review_count": 510,
                "price_level": 1,
                "address": "บ้านหว้าน ต.น้ำคำ อ.เมือง จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1528181304800-259b08848526?w=800&auto=format&fit=crop&q=80",
                "description": "พระอุโบสถบนเรือสุพรรณหงส์จำลองสีทองอร่ามกลางสระน้ำขนาดใหญ่ ตกแต่งวิจิตรงดงาม พร้อมตลาดโบราณและสะพานไม้ชมบัว",
                "tags": "เรือสุพรรณหงส์, บึงบัว, ไหว้พระ, ถ่ายรูปสวย, วัฒนธรรม",
                "is_featured": True,
            },
            {
                "name": "ปราสาทสระกำแพงใหญ่",
                "slug": "prasat-sa-kamphaeng-yai",
                "category": cat_objs["culture"],
                "location": loc_objs["ssk-uthumphon"],
                "rating": 4.7,
                "review_count": 420,
                "price_level": 1,
                "address": "วัดสระกำแพงใหญ่ ต.สระกำแพงใหญ่ อ.อุทุมพรพิสัย จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80",
                "description": "ปราสาทขอมโบราณที่สมบูรณ์และใหญ่ที่สุดในจังหวัดศรีสะเกษ สร้างด้วยหินทรายและศิลาแลง ศิลปะแบบบาปวนอายุกว่า 1,000 ปี",
                "tags": "ปราสาทขอม, โบราณสถาน, ประวัติศาสตร์, หินทราย, ศรีสะเกษ",
                "is_featured": True,
            },
            {
                "name": "วัดล้านขวด (วัดป่ามหาเจดีย์แก้ว)",
                "slug": "wat-lan-khuat",
                "category": cat_objs["culture"],
                "location": loc_objs["ssk-khunhan"],
                "rating": 4.8,
                "review_count": 630,
                "price_level": 1,
                "address": "ต.สิ อ.ขุนหาญ จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=800&auto=format&fit=crop&q=80",
                "description": "มหาเจดีย์และอุโบสถกลางน้ำที่สร้างขึ้นจากขวดแก้วรีไซเคิลกว่า 1.5 ล้านขวด สะท้อนแสงแดดระยิบระยับสวยงาม แปลกตาและมีเอกลักษณ์ระดับโลก",
                "tags": "วัดล้านขวด, Unseen Thailand, ขุนหาญ, สถาปัตยกรรม, ถ่ายรูป",
                "is_featured": True,
            },
            {
                "name": "สวนสมเด็จพระศรีนครินทร์ ศรีสะเกษ",
                "slug": "somdej-park-sisaket",
                "category": cat_objs["travel"],
                "location": loc_objs["ssk-muang"],
                "rating": 4.6,
                "review_count": 350,
                "price_level": 1,
                "address": "วิทยาลัยเกษตรและเทคโนโลยี ต.หนองครก อ.เมือง จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&auto=format&fit=crop&q=80",
                "description": "สวนสมเด็จฯ แห่งแรกของประเทศไทย แหล่งรวมต้นลำดวนกว่า 40,000 ต้น พร้อมสวนสัตว์ สวนน้ำ และเส้นทางปั่นจักรยานพักผ่อนใจกลางเมือง",
                "tags": "ดงลำดวน, สวนสาธารณะ, พักผ่อน, สวนสัตว์, ดอกลำดวน",
                "is_featured": False,
            },
            {
                "name": "น้ำตกสำโรงเกียรติ",
                "slug": "samrong-kiat-waterfall",
                "category": cat_objs["travel"],
                "location": loc_objs["ssk-khunhan"],
                "rating": 4.7,
                "review_count": 280,
                "price_level": 1,
                "address": "เขตรักษาพันธุ์สัตว์ป่าพนมดงรัก ต.บักดอง อ.ขุนหาญ จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=800&auto=format&fit=crop&q=80",
                "description": "น้ำตกหินทรายขนาดใหญ่สูงกว่า 8 เมตร ไหลผ่านหน้าผาสู่แอ่งน้ำใส ร่มรื่นด้วยพรรณไม้นานาพันธุ์ เหมาะแก่การปิคนิคและเล่นน้ำคลายร้อน",
                "tags": "น้ำตก, เล่นน้ำ, ธรรมชาติ, ป่าไม้, ขุนหาญ",
                "is_featured": False,
            },
            {
                "name": "เขื่อนราษีไศล & สะพานข้ามแม่น้ำมูล",
                "slug": "rasi-salai-dam",
                "category": cat_objs["travel"],
                "location": loc_objs["ssk-rasisalai"],
                "rating": 4.6,
                "review_count": 210,
                "price_level": 1,
                "address": "ต.หนองแค อ.ราษีไศล จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
                "description": "จุดชมวิวแม่น้ำมูลสุดกว้างขวาง พระอาทิตย์ตกดินสะท้อนผิวน้ำงดงาม ลมพัดเย็นสบาย พร้อมร้านอาหารปลาเผาริมเขื่อน",
                "tags": "เขื่อน, แม่น้ำมูล, ชมพระอาทิตย์ตก, จุดชมวิว, ราษีไศล",
                "is_featured": False,
            },
            {
                "name": "ไก่ย่างไม้มะดัน ห้วยทับทัน",
                "slug": "huai-thap-than-grilled-chicken",
                "category": cat_objs["restaurant"],
                "location": loc_objs["ssk-huaitapthan"],
                "rating": 4.9,
                "review_count": 750,
                "price_level": 1,
                "address": "ริมทางหลวง 226 ต.ห้วยทับทัน อ.ห้วยทับทัน จ.ศรีสะเกษ",
                "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&auto=format&fit=crop&q=80",
                "description": "ของดีเมืองศรีสะเกษ ไก่บ้านหมักเครื่องเทศย่างด้วยไม้มะดันสด หอมกลิ่นควันไม้และสมุนไพรเฉพาะตัว หนังกรอบเนื้อนุ่ม จิ้มแจ่วรสเด็ด",
                "tags": "ของดีศรีสะเกษ, ไก่ย่างไม้มะดัน, อาหารอีสาน, ส้มตำ, อร่อยบอกต่อ",
                "is_featured": True,
            },
        ]

        for p in places_data:
            Place.objects.update_or_create(
                slug=p["slug"],
                defaults=p,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Successfully seeded {len(places_data)} Sisaket places!"))
