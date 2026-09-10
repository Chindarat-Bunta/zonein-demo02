from django.http import JsonResponse
from django.contrib.auth.models import User
from web.models import Place, Review, Notification
from .views import parse_json_body


def place_reviews_list_create(request, place_id):
    """
    Endpoint: /api/places/<place_id>/reviews/
    - GET: List all reviews for the specified place
    - POST: Create a new review (rating 1-5, comment)
    """
    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({"success": False, "error": "ไม่พบสถานที่นี้ในระบบ"}, status=404)

    if request.method == "GET":
        reviews = place.reviews.select_related("user", "user__profile").all()
        data = []
        for r in reviews:
            profile = getattr(r.user, "profile", None)
            data.append({
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "nickname": profile.nickname if profile else r.user.username,
                    "avatar_url": profile.avatar_url if profile else "",
                },
                "created_at": r.created_at.isoformat(),
            })

        return JsonResponse({
            "success": True,
            "place_id": place.id,
            "place_name": place.name,
            "average_rating": place.average_rating,
            "review_count": len(data),
            "reviews": data,
        })

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse(
                {"success": False, "error": "unauthorized", "message": "กรุณาเข้าสู่ระบบก่อนเขียนรีวิว"},
                status=401,
            )

        payload = parse_json_body(request)
        if payload is None:
            payload = request.POST.dict()

        try:
            rating = int(payload.get("rating", 0))
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "คะแนนเรตติ้งต้องเป็นตัวเลข"}, status=400)

        if not (1 <= rating <= 5):
            return JsonResponse({"success": False, "error": "คะแนนเรตติ้งต้องอยู่ระหว่าง 1 ถึง 5 ดาว"}, status=400)

        comment = payload.get("comment", "").strip()
        if not comment:
            return JsonResponse({"success": False, "error": "กรุณากรอกข้อความรีวิว"}, status=400)

        user = request.user

        # Handle review photo upload to Cloudinary
        image_url = payload.get("image_url", "").strip()
        image_file = request.FILES.get("image") or request.FILES.get("photo")
        if image_file:
            from web.services import upload_image
            upload_res = upload_image(image_file, folder="zonein/reviews")
            if upload_res.get("success"):
                image_url = upload_res.get("url")

        review = Review.objects.create(
            place=place,
            user=user,
            rating=rating,
            comment=comment,
            image_url=image_url
        )

        # Build reviewer info to return to the frontend
        profile = getattr(user, "profile", None)
        display_name = (
            profile.get_display_name() if profile else user.username
        )
        avatar_url = profile.avatar_url if profile else ""

        # Trigger notification to place author if not self
        if place.author and place.author != user:
            actor_tag = f"{display_name} (@{user.username})" if display_name and display_name != user.username else f"@{user.username}"
            Notification.objects.create(
                actor=user,
                recipient=place.author,
                action_type="comment",
                post=place,
                message=f"{actor_tag} ได้แสดงความคิดเห็นบนโพสต์ '{place.name}'",
            )

        return JsonResponse({
            "success": True,
            "message": "บันทึกรีวิวเรียบร้อยแล้ว",
            "review": {
                "id": review.id,
                "place_id": place.id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
                # Extra fields for the JS card builder
                "user_name": display_name,
                "username": user.username,
                "avatar_url": avatar_url,
            },
            "new_average_rating": place.average_rating,
            "total_reviews": place.review_count,
        }, status=201)

    return JsonResponse({"success": False, "error": f"Method {request.method} not allowed"}, status=405)

