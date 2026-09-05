from django.test import TestCase, Client
from django.urls import reverse
from web.models import Category, Location, Place


class SearchFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_cafe = Category.objects.create(
            name="คาเฟ่", slug="cafe", icon="fa-mug-hot", color="#f97316"
        )
        self.cat_hotel = Category.objects.create(
            name="ที่พัก", slug="hotel", icon="fa-bed", color="#3b82f6"
        )

        self.loc_ari = Location.objects.create(
            city="กรุงเทพมหานคร", zone="อารีย์", slug="bkk-ari"
        )
        self.loc_cnx = Location.objects.create(
            city="เชียงใหม่", zone="นิมมาน", slug="cnx-nimman"
        )

        self.place1 = Place.objects.create(
            name="Specialty Coffee Ari",
            slug="specialty-coffee-ari",
            category=self.cat_cafe,
            location=self.loc_ari,
            rating=4.9,
            review_count=100,
            price_level=2,
            address="ซอยอารีย์ พญาไท กทม.",
            description="กาแฟดริปชั้นยอด เมล็ดนำเข้า นั่งทำงานชิลล์",
            tags="Specialty Coffee, กาแฟ, อารีย์",
        )

        self.place2 = Place.objects.create(
            name="Nimman Boutique Hotel",
            slug="nimman-boutique-hotel",
            category=self.cat_hotel,
            location=self.loc_cnx,
            rating=4.5,
            review_count=50,
            price_level=3,
            address="ถนนนิมมานเหมินท์ เชียงใหม่",
            description="โรงแรมบูทีคดีไซน์สวยกลางนิมมาน พร้อมสระว่ายน้ำ",
            tags="ที่พัก, สระว่ายน้ำ, เชียงใหม่",
        )

    def test_index_view_renders(self):
        response = self.client.get(reverse("web:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Specialty Coffee Ari")
        self.assertContains(response, "Nimman Boutique Hotel")
        self.assertContains(response, "หมวดหมู่")
        self.assertContains(response, "ทำเล/ย่าน")
        self.assertContains(response, "ล้างตัวกรอง")

    def test_keyword_search(self):
        response = self.client.get(reverse("web:index"), {"q": "กาแฟ"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Specialty Coffee Ari")
        self.assertNotContains(response, "Nimman Boutique Hotel")

    def test_category_filter(self):
        response = self.client.get(reverse("web:index"), {"category": "hotel"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nimman Boutique Hotel")
        self.assertNotContains(response, "Specialty Coffee Ari")

    def test_location_filter(self):
        response = self.client.get(reverse("web:index"), {"location": "bkk-ari"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Specialty Coffee Ari")
        self.assertNotContains(response, "Nimman Boutique Hotel")

    def test_combined_filter_empty_result(self):
        response = self.client.get(
            reverse("web:index"), {"q": "คำค้นหาที่ไม่มีในฐานข้อมูลxyz123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_count"], 0)
        self.assertContains(response, "ไม่พบสถานที่ที่ตรงกับเงื่อนไข")

    def test_api_places_endpoint(self):
        response = self.client.get(reverse("web:api_places"), {"q": "Ari"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["places"][0]["slug"], "specialty-coffee-ari")
        self.assertEqual(data["places"][0]["category"]["slug"], "cafe")


class WishlistTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="คาเฟ่", slug="cafe", icon="fa-mug-hot")
        self.loc = Location.objects.create(
            city="กรุงเทพมหานคร", zone="อารีย์", slug="bkk-ari"
        )
        self.place = Place.objects.create(
            name="Nana Coffee Roasters",
            slug="nana-coffee-roasters",
            category=self.cat,
            location=self.loc,
            rating=4.8,
            review_count=50,
            address="อารีย์ ซอย 4",
            description="คาเฟ่สวย กาแฟดี",
        )

    def test_wishlist_page_renders_empty_state(self):
        response = self.client.get(reverse("web:wishlist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "รายการสถานที่โปรด (My Wishlist)")
        self.assertContains(response, "ยังไม่มีสถานที่ในรายการโปรด")

    def test_api_wishlist_toggle_add_and_remove(self):
        # 1. Add to wishlist
        response = self.client.post(
            reverse("web:api_wishlist_toggle"),
            data={"place_id": self.place.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "added")
        self.assertTrue(data["is_wishlisted"])
        self.assertEqual(data["total_count"], 1)

        # Verify in wishlist page
        wishlist_page_res = self.client.get(reverse("web:wishlist"))
        self.assertEqual(wishlist_page_res.status_code, 200)
        self.assertContains(wishlist_page_res, "Nana Coffee Roasters")

        # 2. Remove from wishlist (toggle again)
        response2 = self.client.post(
            reverse("web:api_wishlist_toggle"),
            data={"place_id": self.place.id},
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2["status"], "success")
        self.assertEqual(data2["action"], "removed")
        self.assertFalse(data2["is_wishlisted"])
        self.assertEqual(data2["total_count"], 0)

    def test_api_wishlist_list_endpoint(self):
        # Toggle add
        self.client.post(
            reverse("web:api_wishlist_toggle"),
            data={"place_id": self.place.id},
            content_type="application/json",
        )

        response = self.client.get(reverse("web:api_wishlist_list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn(self.place.id, data["place_ids"])
        self.assertEqual(len(data["places"]), 1)
        self.assertEqual(data["places"][0]["name"], "Nana Coffee Roasters")
