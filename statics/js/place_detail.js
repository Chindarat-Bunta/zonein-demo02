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
            if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
                showDetailToast('กรุณาเข้าสู่ระบบก่อนเขียนรีวิว ✍️');
                setTimeout(() => {
                    window.location.href = `/signin/?next=${encodeURIComponent(window.location.pathname + window.location.hash)}`;
                }, 800);
                return;
            }
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
        btnLike.addEventListener('click', async () => {
            if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
                showDetailToast('กรุณาเข้าสู่ระบบเพื่อกดถูกใจสถานที่นี้ ❤️');
                return;
            }
            const placeId = btnLike.getAttribute('data-place-id');
            if (!placeId) return;

            btnLike.disabled = true;
            try {
                const res = await fetch(`/api/places/${placeId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });
                const data = await res.json();
                if (data.success) {
                    btnLike.classList.toggle('active', data.is_liked);
                    const svg = btnLike.querySelector('svg');
                    if (svg) {
                        svg.setAttribute('fill', data.is_liked ? '#ef4444' : 'none');
                    }
                    if (likeCountSpan && typeof data.total_likes !== 'undefined') {
                        likeCountSpan.textContent = data.total_likes;
                    }
                    showDetailToast(data.is_liked ? 'ถูกใจสถานที่นี้แล้ว ❤️' : 'ยกเลิกการถูกใจแล้ว');
                } else {
                    showDetailToast(data.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง');
                }
            } catch (err) {
                console.error('Like error:', err);
                showDetailToast('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
            } finally {
                btnLike.disabled = false;
            }
        });
    }

    const btnWishlist = document.getElementById('btnPlaceWishlist');
    const wishlistBtnText = document.getElementById('wishlistBtnText');
    if (btnWishlist) {
        btnWishlist.addEventListener('click', async () => {
            if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
                showDetailToast('กรุณาเข้าสู่ระบบเพื่อบันทึกรายการโปรด 🔖');
                return;
            }
            const placeId = btnWishlist.getAttribute('data-place-id');
            if (!placeId) return;

            btnWishlist.disabled = true;
            try {
                const res = await fetch('/api/wishlist/toggle/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({ place_id: placeId })
                });
                const data = await res.json();
                if (data.status === 'success' || data.success) {
                    const isSaved = (typeof data.is_wishlisted !== 'undefined') ? data.is_wishlisted : data.is_saved;
                    btnWishlist.classList.toggle('active', isSaved);
                    if (wishlistBtnText) {
                        wishlistBtnText.textContent = isSaved ? 'บันทึกแล้วในรายการโปรด' : 'บันทึกสถานที่';
                    }
                    const svg = btnWishlist.querySelector('svg');
                    if (svg) {
                        svg.setAttribute('fill', isSaved ? '#e05d5d' : 'none');
                    }
                    btnWishlist.setAttribute('title', isSaved ? 'นำออกจากรายการโปรด' : 'บันทึกในรายการโปรด');
                    showDetailToast(isSaved ? 'บันทึกในรายการโปรดเรียบร้อยแล้ว ❤️' : 'นำออกจากรายการโปรดแล้ว');
                } else {
                    showDetailToast(data.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง');
                }
            } catch (err) {
                console.error('Wishlist error:', err);
                showDetailToast('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
            } finally {
                btnWishlist.disabled = false;
            }
        });
    }

    // 6. Share Button → Open Share Modal
    const btnShare = document.getElementById('btnPlaceShare');
    if (btnShare) {
        btnShare.addEventListener('click', () => {
            const url = window.location.href;
            const placeName = document.querySelector('.place-main-title')?.innerText
                || document.title.split('—')[0].trim();
            const placeDesc = document.querySelector('.place-location-snippet')?.innerText
                || 'สถานที่ท่องเที่ยวบน ZoneIn';
            const coverImg = document.getElementById('sharePreviewImg')?.src
                || document.querySelector('.gallery-main-photo img')?.src
                || '';

            currentSharePayload = {
                title: `${placeName} — ZoneIn สถานที่ท่องเที่ยว`,
                text: placeDesc,
                url: url,
                imageUrl: coverImg,
                placeName: placeName
            };
            openShareModal(currentSharePayload);
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

    // Close share modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeShareModal();
    });
});

// ===================================================
// Modern Multi-Platform Sharing System
// ===================================================
let currentSharePayload = {
    title: 'ZoneIn - สถานที่ท่องเที่ยว',
    text: 'ดูสถานที่ท่องเที่ยวนี้บน ZoneIn!',
    url: window.location.href,
    imageUrl: '',
    placeName: ''
};

function openShareModal(data) {
    const modal = document.getElementById('shareModalOverlay');
    if (!modal) return;

    const titleEl = document.getElementById('sharePreviewTitle');
    const descEl = document.getElementById('sharePreviewDesc');
    const urlTextEl = document.getElementById('sharePreviewUrlText');
    const imgWrap = document.getElementById('sharePreviewImgWrap');
    const inputEl = document.getElementById('shareUrlInput');
    const hintEl = document.getElementById('shareModalHint');

    if (titleEl) titleEl.innerText = data.placeName || data.title;
    if (descEl) descEl.innerText = data.text;
    if (inputEl) inputEl.value = data.url;
    if (urlTextEl) {
        try {
            const parsedUrl = new URL(data.url);
            urlTextEl.innerText = parsedUrl.host + (parsedUrl.pathname !== '/' ? parsedUrl.pathname : '');
        } catch { urlTextEl.innerText = data.url; }
    }
    if (hintEl) { hintEl.style.display = 'none'; hintEl.innerText = ''; }

    resetCopyShareButton();

    if (imgWrap) {
        if (data.imageUrl) {
            imgWrap.innerHTML = `<img id="sharePreviewImg" src="${data.imageUrl}" alt="พรีวิว" style="width:100%;height:100%;object-fit:cover;">`;
        } else {
            imgWrap.innerHTML = '<span style="font-size: 1.4rem;">📍</span>';
        }
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeShareModal(event) {
    if (event && event.target && event.target.closest('.share-modal-card')) return;
    const modal = document.getElementById('shareModalOverlay');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

function resetCopyShareButton() {
    const btn = document.getElementById('btnCopyShareLink');
    const text = document.getElementById('copyShareText');
    const icon = document.getElementById('copyShareIcon');
    if (!btn || !text) return;
    btn.classList.remove('copied');
    text.innerText = 'คัดลอกลิงก์';
    if (icon) {
        icon.innerHTML = '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>';
    }
}

function copyShareLink() {
    const url = currentSharePayload.url || window.location.href;
    const btn = document.getElementById('btnCopyShareLink');
    const text = document.getElementById('copyShareText');
    const icon = document.getElementById('copyShareIcon');

    const markCopied = () => {
        if (btn && text) {
            btn.classList.add('copied');
            text.innerText = 'คัดลอกแล้ว! ✓';
            if (icon) { icon.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>'; }
            setTimeout(() => resetCopyShareButton(), 2500);
        }
        showDetailToast('คัดลอกลิงก์เรียบร้อยแล้ว 🔗');
    };

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(markCopied).catch(() => { fallbackCopy(url); markCopied(); });
    } else {
        fallbackCopy(url);
        markCopied();
    }
}

function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try { document.execCommand('copy'); } catch (e) { console.error('Fallback copy failed', e); }
    document.body.removeChild(textArea);
}

function shareToPlatform(platform) {
    const { title, text, url, placeName } = currentSharePayload;
    const encodedUrl = encodeURIComponent(url);
    const shareHeading = placeName ? `${placeName} — ZoneIn` : title;
    const encodedTitle = encodeURIComponent(`${shareHeading}: ${text}`);
    const popupOpts = 'width=620,height=560,toolbar=no,menubar=no,location=no,status=no';

    switch (platform) {
        case 'facebook': {
            const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedTitle}`;
            window.open(fbUrl, '_blank', popupOpts);
            break;
        }
        case 'instagram': {
            copyShareLink();
            const hintEl = document.getElementById('shareModalHint');
            if (hintEl) {
                hintEl.innerHTML = '📸 คัดลอกลิงก์เรียบร้อยแล้ว! กำลังเปิด Instagram เพื่อแชร์ในสตอรี่หรือแชท...';
                hintEl.style.display = 'block';
            }
            showDetailToast('คัดลอกลิงก์แล้ว! เปิด Instagram เพื่อแชร์ได้เลย 📸');
            setTimeout(() => window.open('https://www.instagram.com/', '_blank'), 500);
            break;
        }
        case 'line': {
            const lineUrl = `https://social-plugins.line.me/lineit/share?url=${encodedUrl}&text=${encodedTitle}`;
            window.open(lineUrl, '_blank', popupOpts);
            break;
        }
        case 'x': {
            const xUrl = `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`;
            window.open(xUrl, '_blank', popupOpts);
            break;
        }
        case 'whatsapp': {
            const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareHeading + '\n' + text + '\n' + url)}`;
            window.open(waUrl, '_blank', popupOpts);
            break;
        }
        case 'native': {
            if (navigator.share) {
                navigator.share({ title: shareHeading, text, url }).catch(() => {});
            } else {
                copyShareLink();
            }
            break;
        }
        default:
            copyShareLink();
    }
}
