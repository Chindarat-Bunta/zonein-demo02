from django.test import TestCase, Client
from django.urls import reverse
from web.models import Category, Location, Place


class SearchFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_travel = Category.objects.create(
            name="สถานที่ท่องเที่ยว & ธรรมชาติ", slug="travel", icon="fa-mountain-sun", color="#10b981"
        )
        self.cat_culture = Category.objects.create(
            name="โบราณสถาน & วัดวาอาราม", slug="culture", icon="fa-landmark-dome", color="#8b5cf6"
        )
        self.cat_cafe = Category.objects.create(
            name="คาเฟ่", slug="cafe", icon="fa-mug-hot", color="#f97316"
        )

        self.loc_kantharalak = Location.objects.create(
            city="ศรีสะเกษ", zone="อ.กันทรลักษ์", slug="ssk-kantharalak"
        )
        self.loc_muang = Location.objects.create(
            city="ศรีสะเกษ", zone="อ.เมืองศรีสะเกษ", slug="ssk-muang"
        )

        self.place1 = Place.objects.create(
            name="ผามออีแดง ชายแดนไทย",
            slug="pha-mo-e-dang",
            category=self.cat_travel,
            location=self.loc_kantharalak,
            rating=4.9,
            review_count=890,
            price_level=1,
            address="อุทยานแห่งชาติเขาพระวิหาร ต.เสาธงชัย อ.กันทรลักษ์ จ.ศรีสะเกษ",
            description="จุดชมวิวหน้าผาสูงตระหง่าน ชมทะเลหมอกและพระอาทิตย์ขึ้นสุดอลังการ",
            tags="ทะเลหมอก, พระอาทิตย์ขึ้น, จุดชมวิว, เขาพระวิหาร, ธรรมชาติ",
        )

        self.place2 = Place.objects.create(
            name="วัดพระธาตุสุพรรณหงส์",
            slug="wat-phra-that-suphannahong",
            category=self.cat_culture,
            location=self.loc_muang,
            rating=4.8,
            review_count=510,
            price_level=1,
            address="บ้านหว้าน ต.น้ำคำ อ.เมือง จ.ศรีสะเกษ",
            description="พระอุโบสถบนเรือสุพรรณหงส์จำลองสีทองอร่ามกลางสระน้ำขนาดใหญ่",
            tags="เรือสุพรรณหงส์, บึงบัว, ไหว้พระเมืองศรีสะเกษ",
        )

    def test_index_view_renders(self):
        response = self.client.get(reverse("web:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ค้นหา")
        self.assertContains(response, "แผนที่")
        self.assertContains(response, "ทำเล/อำเภอ")
        self.assertContains(response, "หมวดหมู่")
        self.assertContains(response, "ล้างตัวกรอง")

    def test_keyword_search(self):
        response = self.client.get(reverse("web:index"), {"q": "ทะเลหมอก"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_count"], 1)
        self.assertEqual(response.context["places"][0].name, "ผามออีแดง ชายแดนไทย")

    def test_category_filter(self):
        response = self.client.get(reverse("web:index"), {"category": "culture"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_count"], 1)
        self.assertEqual(response.context["places"][0].name, "วัดพระธาตุสุพรรณหงส์")

    def test_location_filter(self):
        response = self.client.get(reverse("web:index"), {"location": "ssk-kantharalak"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_count"], 1)
        self.assertEqual(response.context["places"][0].name, "ผามออีแดง ชายแดนไทย")

    def test_combined_filter_empty_result(self):
        response = self.client.get(
            reverse("web:index"), {"q": "คำค้นหาที่ไม่มีในฐานข้อมูลxyz123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_count"], 0)

    def test_api_places_endpoint(self):
        response = self.client.get(reverse("web:api_places"), {"q": "ผามออีแดง"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["places"][0]["slug"], "pha-mo-e-dang")
        self.assertEqual(data["places"][0]["category"]["slug"], "travel")
