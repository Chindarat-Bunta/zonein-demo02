from django.core.management.base import BaseCommand
from web.models import Place


class Command(BaseCommand):
    help = "Seeds demo categories, locations, and places in Sisaket (ศรีสะเกษ) for ZoneIn review app"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[*] Resetting & Seeding Sisaket (ศรีสะเกษ) places data..."))

        # Places in Sisaket
        places_data = [
            {
                "name": "ผามออีแดง (อุทยานแห่งชาติเขาพระวิหาร)",
                "slug": "pha-mo-e-dang",
                "category": "travel",
                "price_level": 1,
                "address": "อุทยานแห่งชาติเขาพระวิหาร ต.เสาธงชัย อ.กันทรลักษ์ จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=80",
                "description": "จุดชมวิวหน้าผาสูงตระหง่านบริเวณชายแดนไทย-กัมพูชา ชมทะเลหมอกและพระอาทิตย์ขึ้นสุดอลังการ พร้อมภาพแกะสลักนูนต่ำหินทรายโบราณอายุกว่า 1,500 ปี และทัศนียภาพปราสาทเขาพระวิหาร",
                "tags": "ทะเลหมอก, พระอาทิตย์ขึ้น, จุดชมวิว, เขาพระวิหาร, ธรรมชาติ, Unseen ศรีสะเกษ, กันทรลักษ์",
                "is_featured": True,
            },
            {
                "name": "ปราสาทหินสระกำแพงใหญ่",
                "slug": "prasat-sa-kamphaeng-yai",
                "category": "culture",
                "price_level": 1,
                "address": "วัดสระกำแพงใหญ่ ต.สระกำแพงใหญ่ อ.อุทุมพรพิสัย จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80",
                "description": "ปราสาทขอมโบราณที่สมบูรณ์และงดงามที่สุดแห่งหนึ่งในอีสานใต้ สร้างขึ้นในพุทธศตวรรษที่ 16 ศิลปะแบบบาปวนและเกลียง โดดเด่นด้วยทับหลังศิลาทรายแกะสลักอย่างประณีต",
                "tags": "ปราสาทขอม, โบราณสถาน, อุทุมพรพิสัย, ประวัติศาสตร์, ศิลปะขอม, ไหว้พระ",
                "is_featured": True,
            },
            {
                "name": "วัดป่ามหาเจดีย์แก้ว (วัดล้านขวด)",
                "slug": "wat-lan-khuat-khunhan",
                "category": "culture",
                "price_level": 1,
                "address": "บ้านดอน ต.สิ อ.ขุนหาญ จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=800&auto=format&fit=crop&q=80",
                "description": "มหัศจรรย์สถาปัตยกรรมระดับโลกที่สร้างสรรค์จากขวดแก้วรีไซเคิลกว่า 1.5 ล้านขวด ทั้งพระอุโบสถ เจดีย์แก้ว ศาลากลางน้ำ และกุฏิ สะท้อนแสงอาทิตย์ระยิบระยับสวยงาม",
                "tags": "วัดล้านขวด, สถาปัตยกรรมแปลกตา, ไหว้พระ, ขุนหาญ, ถ่ายรูปสวย, Unseen Thailand",
                "is_featured": True,
            },
            {
                "name": "วัดพระธาตุสุพรรณหงส์",
                "slug": "wat-phra-that-suphannahong",
                "category": "culture",
                "price_level": 1,
                "address": "บ้านหว้าน ต.น้ำคำ อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1609766857041-ed402ea8069a?w=800&auto=format&fit=crop&q=80",
                "description": "พระอุโบสถบนเรือสุพรรณหงส์จำลองสีทองอร่ามกลางสระน้ำขนาดใหญ่ ตกแต่งลวดลายวิจิตรงดงาม มีสะพานไม้ทอดยาวข้ามบึงบัว และตลาดโบราณวิถีชุมชนให้เดินชิมช้อป",
                "tags": "เรือสุพรรณหงส์, บึงบัว, ไหว้พระเมืองศรีสะเกษ, ตลาดโบราณ, ถ่ายรูปสวย",
                "is_featured": True,
            },
            {
                "name": "สวนสมเด็จพระศรีนครินทร์ ศรีสะเกษ (สวนดงลำดวน)",
                "slug": "somdet-park-dong-lamduan",
                "category": "travel",
                "price_level": 1,
                "address": "ภายในวิทยาลัยเกษตรและเทคโนโลยีศรีสะเกษ ต.หนองครก อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&auto=format&fit=crop&q=80",
                "description": "สวนสมเด็จพระศรีนครินทร์แห่งแรกในประเทศไทย อุดมด้วยต้นลำดวนธรรมชาติกว่า 50,000 ต้น ส่งกลิ่นหอมกรุ่นทั่วสวน มีสวนสัตว์ขนาดเล็ก สะพานแขวน และลานพักผ่อนริมน้ำ",
                "tags": "ดอกลำดวน, สวนสาธารณะ, สวนสัตว์, ธรรมชาติ, ปิกนิก, เมืองศรีสะเกษ",
                "is_featured": False,
            },
            {
                "name": "เกาะกลางน้ำห้วยน้ำคำ & หอศรีลำดวนเกียรติยศ",
                "slug": "huai-nam-kham-island-tower",
                "category": "travel",
                "price_level": 1,
                "address": "ถนนเลี่ยงเมือง ต.หนองครก อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=800&auto=format&fit=crop&q=80",
                "description": "แลนด์มาร์กสำคัญใจกลางเมืองศรีสะเกษ สวนสาธารณะขนาดใหญ่บนเกาะกลางน้ำ พร้อมหอชมเมืองศรีลำดวนเกียรติยศ และอควาเรียมแสดงพันธุ์ปลาแม่น้ำมูล",
                "tags": "หอชมเมือง, ห้วยน้ำคำ, แลนด์มาร์ก, อควาเรียม, จุดชมวิว, วิ่งออกกำลังกาย",
                "is_featured": True,
            },
            {
                "name": "น้ำตกสำโรงเกียรติ",
                "slug": "samrong-kiat-waterfall",
                "category": "travel",
                "price_level": 1,
                "address": "เขตรักษาพันธุ์สัตว์ป่าพนมดงรัก ต.บักดอง อ.ขุนหาญ จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=800&auto=format&fit=crop&q=80",
                "description": "น้ำตกภูเขาไฟขนาดกลางในเขตรักษาพันธุ์สัตว์ป่าพนมดงรัก สายน้ำไหลตกลงมาจากหน้าผาหินสูง 8 เมตร ท่ามกลางป่าดิบชื้นร่มรื่น เหมาะแก่การแช่น้ำคลายร้อนและปิกนิก",
                "tags": "น้ำตก, เล่นน้ำ, ป่าพนมดงรัก, ธรรมชาติ, ขุนหาญ, ปิกนิก",
                "is_featured": False,
            },
            {
                "name": "น้ำตกห้วยจันทร์ (น้ำตกหลูปู)",
                "slug": "huai-chan-waterfall",
                "category": "travel",
                "price_level": 1,
                "address": "ต.ห้วยจันทร์ อ.ขุนหาญ จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80",
                "description": "น้ำตกธรรมชาติที่ไหลลดหลั่นตามโขดหินแก่งหิน บรรยากาศร่มรื่น มีต้นไม้ใหญ่ล้อมรอบ น้ำใสเย็นสบาย เดินทางสะดวก เหมาะสำหรับครอบครัว",
                "tags": "น้ำตกห้วยจันทร์, เล่นน้ำ, ธรรมชาติ, ขุนหาญ, จุดกางเต็นท์",
                "is_featured": False,
            },
            {
                "name": "ไก่ย่างไม้มะดัน ห้วยทับทัน (ร้านต้นตำรับไม้มะดัน)",
                "slug": "kai-yang-mai-madan-huai-thap-than",
                "category": "restaurant",
                "price_level": 1,
                "address": "ริมทางหลวง 226 ต.ห้วยทับทัน อ.ห้วยทับทัน จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&auto=format&fit=crop&q=80",
                "description": "สุดยอดของอร่อยประจำจังหวัดศรีสะเกษ ไก่ย่างหมักสมุนไพรสูตรพิเศษ หนีบด้วยไม้มะดันสดแล้วย่างบนเตาถ่านจนหนังกรอบหอม รสเปรี้ยวกลมกล่อมจากไม้มะดัน ทานคู่ส้มตำปลาร้าและข้าวเหนียว",
                "tags": "ไก่ย่างไม้มะดัน, อาหารอีสาน, ส้มตำแซ่บ, ของดีศรีสะเกษ, ของฝาก, ห้วยทับทัน",
                "is_featured": True,
            },
            {
                "name": "บ้านไม้ขาว คาเฟ่ (Baan Mai Khao Cafe)",
                "slug": "baan-mai-khao-cafe",
                "category": "cafe",
                "price_level": 2,
                "address": "ถนนหลักเมือง ต.เมืองเหนือ อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&auto=format&fit=crop&q=80",
                "description": "คาเฟ่สไตล์มินิมอลเจแปนนีสในบ้านไม้สีขาวแสนอบอุ่น โดดเด่นด้วยเมนูมัทฉะพรีเมียม กาแฟดริป และครัวซองต์เนยสดฝรั่งเศส กลิ่นหอมละมุน",
                "tags": "มินิมอล, มัทฉะ, คาเฟ่ถ่ายรูป, ครัวซองต์, กาแฟดริป, เมืองศรีสะเกษ",
                "is_featured": False,
            },
            {
                "name": "ปราสาทปรางค์กู่",
                "slug": "prasat-prang-ku",
                "category": "culture",
                "price_level": 1,
                "address": "บ้านกู่ ต.กู่ อ.ปรางค์กู่ จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?w=800&auto=format&fit=crop&q=80",
                "description": "ปราสาทหินและศิลาแลงโบราณอายุกว่า 800 ปี ศิลปะขอมแบบบาปวน ผังปรางค์ 3 องค์เรียงกันบนฐานศิลาแลงเดียวกัน ร่มรื่นด้วยต้นไม้ใหญ่และสระน้ำโบราณ",
                "tags": "ปราสาทขอม, ศิลาแลง, ประวัติศาสตร์, ปรางค์กู่, โบราณคดี, ถ่ายรูปคลาสสิก",
                "is_featured": False,
            },
            {
                "name": "จุดชมวิวสันเขื่อนราษีไศล",
                "slug": "rasi-salai-dam-viewpoint",
                "category": "travel",
                "price_level": 1,
                "address": "เขื่อนราษีไศล ต.หนองแค อ.ราษีไศล จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
                "description": "จุดชมวิวพระอาทิตย์ตกดินอันงดงามริมแม่น้ำมูล ลมพัดเย็นสบายตลอดทั้งวัน มีถนนเลียบสันเขื่อนสำหรับเดินเล่น ปั่นจักรยาน และมีร้านปลาแม่น้ำเผาสดๆ รสเด็ด",
                "tags": "เขื่อนราษีไศล, พระอาทิตย์ตก, แม่น้ำมูล, ปั่นจักรยาน, ชมวิว, อาหารปลาแม่น้ำ",
                "is_featured": False,
            },
            {
                "name": "ศรีพฤทเธศวร รีสอร์ต & สปา (Sri Pruetthesawan Resort)",
                "slug": "sri-pruetthesawan-resort",
                "category": "hotel",
                "price_level": 3,
                "address": "299 หมู่ 8 ถนนศรีสะเกษ-อุบล ต.โพธิ์ อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
                "description": "รีสอร์ตบูทีคหรูท่ามกลางสวนสวยร่มรื่น ผสมผสานสถาปัตยกรรมอีสานร่วมสมัย ห้องพักกว้างขวาง สระว่ายน้ำกลางแจ้ง สปาผ่อนคลาย และอาหารเช้าเลิศรส",
                "tags": "รีสอร์ต, ที่พักศรีสะเกษ, สระว่ายน้ำ, พักผ่อน, โรงแรมบูทีค, สปา",
                "is_featured": True,
            },
            {
                "name": "โรงแรมเกษสิริ ศรีสะเกษ (Kessiri Hotel)",
                "slug": "kessiri-hotel-sisaket",
                "category": "hotel",
                "price_level": 2,
                "address": "1102-05 ถนนขุขันธ์ ต.เมืองใต้ อ.เมือง จ.ศรีสะเกษ",
                "cover_image_url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
                "description": "โรงแรมใจกลางเมืองศรีสะเกษ เดินทางสะดวกสบาย ใกล้สถานีรถไฟ ตลาดโต้รุ่ง และแหล่งช้อปปิ้ง ห้องพักสะอาด สิ่งอำนวยความสะดวกครบครัน พร้อมที่จอดรถกว้างขวาง",
                "tags": "โรงแรมในเมือง, ที่พักราคาประหยัด, ใกล้สถานีรถไฟ, เมืองศรีสะเกษ, เดินทางสะดวก",
                "is_featured": False,
            },
        ]

        valid_fields = {f.name for f in Place._meta.get_fields()}
        for p in places_data:
            model_data = {k: v for k, v in p.items() if k in valid_fields}
            Place.objects.update_or_create(
                slug=p["slug"],
                defaults=model_data,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] Successfully seeded Sisaket places: {Place.objects.count()} places!"
            )
        )
