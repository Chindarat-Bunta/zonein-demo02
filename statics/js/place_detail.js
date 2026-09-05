/**
 * Zone In — Place Detail & Map Navigation Interactive Scripts
 * Handles: Star Rating Selector, Review Submission, Google Maps Navigation, Clipboard Copy, Wishlist/Like
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Toast Notification Helper
    let toastTimer = null;
    function showDetailToast(msg) {
        let toast = document.getElementById('detailToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'detailToast';
            toast.className = 'detail-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.classList.add('show');
        if (toastTimer) clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    window.showDetailToast = showDetailToast;

    // 2. Star Rating Picker in Review Box
    const starPicker = document.getElementById('starPicker');
    const selectedRatingInput = document.getElementById('selectedRatingInput');
    const starHint = document.getElementById('starPickerHint');
    const starHints = {
        1: '1 ดาว — ปรับปรุง',
        2: '2 ดาว — พอใช้',
        3: '3 ดาว — ปานกลาง',
        4: '4 ดาว — ดีมาก',
        5: '5 ดาว — ยอดเยี่ยม ประทับใจมาก'
    };

    if (starPicker) {
        const stars = starPicker.querySelectorAll('.star-picker-star');
        let currentRating = 5;

        function updateStarsDisplay(rating, isHover = false) {
            stars.forEach(star => {
                const val = parseInt(star.getAttribute('data-value'), 10);
                if (val <= rating) {
                    star.classList.add(isHover ? 'hovered' : 'selected');
                } else {
                    star.classList.remove(isHover ? 'hovered' : 'selected');
                }
            });
            if (starHint && starHints[rating]) {
                starHint.textContent = starHints[rating];
            }
        }

        // Initialize default 5 stars
        updateStarsDisplay(5, false);

        stars.forEach(star => {
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.getAttribute('data-value'), 10);
                updateStarsDisplay(val, true);
            });

            star.addEventListener('mouseleave', () => {
                stars.forEach(s => s.classList.remove('hovered'));
                updateStarsDisplay(currentRating, false);
            });

            star.addEventListener('click', () => {
                currentRating = parseInt(star.getAttribute('data-value'), 10);
                if (selectedRatingInput) {
                    selectedRatingInput.value = currentRating;
                }
                updateStarsDisplay(currentRating, false);
            });
        });
    }

    // 3. Review Submission (Optimistic UI + Event Hook for other branch integration)
    const reviewForm = document.getElementById('reviewForm');
    const reviewTextarea = document.getElementById('reviewTextarea');
    const reviewsList = document.getElementById('reviewsList');

    if (reviewForm) {
        reviewForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = reviewTextarea ? reviewTextarea.value.trim() : '';
            const rating = selectedRatingInput ? parseInt(selectedRatingInput.value, 10) : 5;

            if (!text) {
                showDetailToast('กรุณากรอกข้อความรีวิวก่อนส่งครับ');
                if (reviewTextarea) reviewTextarea.focus();
                return;
            }

            // Create optimistic review card
            const newCard = document.createElement('div');
            newCard.className = 'review-item-card';
            newCard.style.animation = 'fadeIn 0.4s ease';

            const starString = '★'.repeat(rating) + '☆'.repeat(5 - rating);

            newCard.innerHTML = `
                <div class="review-author-row">
                    <div class="author-profile-box">
                        <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop" class="author-avatar" alt="User Avatar">
                        <div class="author-meta">
                            <span class="author-name">คุณ (เพิ่งเขียนรีวิว)</span>
                            <span class="author-date">เมื่อสักครู่นี้</span>
                        </div>
                    </div>
                    <div class="review-stars-score" title="${rating} จาก 5 ดาว">${starString}</div>
                </div>
                <div class="review-body-text">${escapeHtml(text)}</div>
            `;

            if (reviewsList) {
                reviewsList.insertBefore(newCard, reviewsList.firstChild);
            }

            if (reviewTextarea) reviewTextarea.value = '';
            showDetailToast('ส่งรีวิวของคุณเรียบร้อยแล้ว ขอบคุณที่ร่วมแบ่งปันครับ! 🎉');

            // Dispatch custom event for external branch API listeners (e.g. feature/api-setup)
            const placeId = reviewsList ? reviewsList.getAttribute('data-place-id') : null;
            const eventPayload = {
                placeId: placeId,
                rating: rating,
                comment: text,
                createdAt: new Date().toISOString()
            };
            window.dispatchEvent(new CustomEvent('zonein:reviewCreated', { detail: eventPayload }));
            console.log('[Zone In]: Review created & event dispatched:', eventPayload);
        });
    }

    // 4. Copy Coordinates & Address
    window.copyCoordinates = function (coords) {
        if (!coords) return;
        navigator.clipboard.writeText(coords).then(() => {
            showDetailToast(`คัดลอกพิกัด "${coords}" เรียบร้อยแล้ว`);
        }).catch(() => {
            showDetailToast(`พิกัด: ${coords}`);
        });
    };

    window.copyAddress = function (address) {
        if (!address) return;
        navigator.clipboard.writeText(address).then(() => {
            showDetailToast('คัดลอกที่อยู่เรียบร้อยแล้ว');
        }).catch(() => {
            showDetailToast(`ที่อยู่: ${address}`);
        });
    };

    // 5. Like & Wishlist Button Toggles
    const btnLike = document.getElementById('btnPlaceLike');
    const likeCountSpan = document.getElementById('likeCount');
    if (btnLike) {
        let isLiked = false;
        btnLike.addEventListener('click', () => {
            isLiked = !isLiked;
            btnLike.classList.toggle('active', isLiked);
            if (likeCountSpan) {
                let current = parseInt(likeCountSpan.textContent, 10) || 0;
                likeCountSpan.textContent = isLiked ? current + 1 : Math.max(0, current - 1);
            }
            showDetailToast(isLiked ? 'ถูกใจสถานที่นี้แล้ว ❤️' : 'ยกเลิกการถูกใจแล้ว');
        });
    }

    const btnWishlist = document.getElementById('btnPlaceWishlist');
    if (btnWishlist) {
        let isWishlisted = false;
        btnWishlist.addEventListener('click', () => {
            isWishlisted = !isWishlisted;
            btnWishlist.classList.toggle('active', isWishlisted);
            showDetailToast(isWishlisted ? 'บันทึกในรายการโปรดเรียบร้อยแล้ว 🔖' : 'นำออกจากรายการโปรดแล้ว');
        });
    }

    // 6. Share Button
    const btnShare = document.getElementById('btnPlaceShare');
    if (btnShare) {
        btnShare.addEventListener('click', () => {
            const url = window.location.href;
            if (navigator.share) {
                navigator.share({
                    title: document.title,
                    url: url
                }).catch(() => {});
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    showDetailToast('คัดลอกลิงก์สถานที่เรียบร้อยแล้ว 🔗');
                });
            }
        });
    }

    // 7. Review Filters (All vs 5-Star)
    const filterBtns = document.querySelectorAll('.filter-btn');
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.getAttribute('data-filter');
                filterReviews(filter);
            });
        });
    }

    function filterReviews(filter) {
        const items = document.querySelectorAll('.review-item-card');
        items.forEach(item => {
            const starsText = item.querySelector('.review-stars-score')?.textContent || '';
            const starCount = (starsText.match(/★/g) || []).length;
            if (filter === 'all') {
                item.style.display = 'block';
            } else if (filter === '5star') {
                item.style.display = (starCount === 5) ? 'block' : 'none';
            } else if (filter === '4star') {
                item.style.display = (starCount === 4) ? 'block' : 'none';
            }
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
