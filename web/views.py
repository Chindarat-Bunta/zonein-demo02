from django.shortcuts import render


def profile_view(request):
    """
    Personal profile page (My Profile) showing user avatar, name,
    review history, and personal wishlist.
    """
    user = request.user

    # Dynamic user details (uses authenticated user if logged in, or realistic defaults)
    if user.is_authenticated:
        display_name = user.first_name if user.first_name else user.username
        username = user.username
        email = user.email if user.email else f"{username}@zonein.app"
        join_date = user.date_joined.strftime("%b %Y") if hasattr(user, "date_joined") and user.date_joined else "ก.ย. 2026"
    else:
        display_name = "คุณภัทรพล วงศ์สว่าง"
        username = "patraphon_traveler"
        email = "patraphon.w@zonein.app"
        join_date = "ก.ย. 2026"

    # Sample review history data for display
    reviews = [
        {
            "id": 1,
            "place_name": "Skyline Rooftop Cafe & Bistro",
            "category": "คาเฟ่ & บิสโทร",
            "rating": 5,
            "stars": [1, 2, 3, 4, 5],
            "date": "2 กันยายน 2026",
            "comment": "บรรยากาศดีมาก ลมเย็นสบาย เหมาะกับการมานั่งทำงานหรือชมพระอาทิตย์ตกดิน เครื่องดื่ม Dirty Coffee และ Basque Cheesecake อร่อยเข้มข้นมาก พนักงานบริการสุภาพ แนะนำให้มาช่วง 17:00 น. ครับ",
            "likes_count": 28,
            "images_count": 3,
            "badge_color": "#FF9D9D",
        },
        {
            "id": 2,
            "place_name": "Green Haven Camping & Glamping",
            "category": "ที่พัก & แคมป์ปิ้งธรรมชาติ",
            "rating": 4,
            "stars": [1, 2, 3, 4],
            "date": "25 สิงหาคม 2026",
            "comment": "ที่พักเงียบสงบโอบล้อมด้วยภูเขา อากาศตอนกลางคืนเย็นสบายมาก ห้องพักสไตล์โดมสะอาด มีสิ่งอำนวยความสะดวกครบ มีบริการเซ็ตหมูกระทะยามเย็นสุดฟิน ประทับใจมาก จะกลับมาซ้ำแน่นอน",
            "likes_count": 19,
            "images_count": 2,
            "badge_color": "#48BB78",
        },
        {
            "id": 3,
            "place_name": "Old Town Artisan Craft Coffee",
            "category": "สเปเชียลตี้คอฟฟี่",
            "rating": 5,
            "stars": [1, 2, 3, 4, 5],
            "date": "14 สิงหาคม 2026",
            "comment": "ร้านตกแต่งสไตล์วินเทจร่วมสมัย เมล็ดกาแฟมีให้เลือกหลากหลายจากดอยช้างและเอธิโอเปีย บาริสต้าให้คำแนะนำดีมาก เหมาะกับสายกาแฟตัวจริง",
            "likes_count": 34,
            "images_count": 4,
            "badge_color": "#ED8936",
        },
    ]

    # Sample wishlist items for display
    wishlist = [
        {
            "id": 1,
            "place_name": "Misty Mountain Valley Resort",
            "category": "รีสอร์ท & วิวทะเลหมอก",
            "location": "เขาค้อ, เพชรบูรณ์",
            "rating": 4.9,
            "reviews_count": 310,
            "gradient": "linear-gradient(135deg, #FFE5D9 0%, #FFCAD4 100%)",
            "tags": ["วิวภูเขา", "อาหารเช้าฟรี", "ใกล้จุดชมวิว"],
        },
        {
            "id": 2,
            "place_name": "The Secret Garden Riverhouse",
            "category": "พูลวิลล่าริมสายน้ำ",
            "location": "สวนผึ้ง, ราชบุรี",
            "rating": 4.8,
            "reviews_count": 184,
            "gradient": "linear-gradient(135deg, #D8E2DC 0%, #FFE5D9 100%)",
            "tags": ["ริมน้ำ", "เงียบสงบ", "เหมาะกับครอบครัว"],
        },
        {
            "id": 3,
            "place_name": "Hideaway Slow Bar & Gallery",
            "category": "คาเฟ่ลับ & แกลเลอรีศิลปะ",
            "location": "อารีย์, กรุงเทพฯ",
            "rating": 4.7,
            "reviews_count": 96,
            "gradient": "linear-gradient(135deg, #E8E8E4 0%, #BEE3F8 100%)",
            "tags": ["งานศิลปะ", "กาแฟดริป", "มุมถ่ายรูปสวย"],
        },
        {
            "id": 4,
            "place_name": "Blue Horizon Seafront Cabin",
            "category": "บ้านพักติดหาดส่วนตัว",
            "location": "ปราณบุรี, ประจวบคีรีขันธ์",
            "rating": 4.9,
            "reviews_count": 242,
            "gradient": "linear-gradient(135deg, #C6F6D5 0%, #BEE3F8 100%)",
            "tags": ["ติดทะเล", "ปิ้งย่างได้", "พายเรือคายัค"],
        },
    ]

    context = {
        "display_name": display_name,
        "username": username,
        "email": email,
        "join_date": join_date,
        "reviews": reviews,
        "wishlist": wishlist,
        "reviews_count": len(reviews),
        "wishlist_count": len(wishlist),
    }

    return render(request, "profile.html", context)
