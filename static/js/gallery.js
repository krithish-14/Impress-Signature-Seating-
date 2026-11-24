(function () {

    /* ══════════════════════════════════════
       SEARCH & FILTER LOGIC
    ══════════════════════════════════════ */
    const section        = document.querySelector('.gallery-section');
    const searchInput    = document.getElementById('gallerySearchInput');
    const searchBox      = document.getElementById('gallerySearchBox');
    const searchClear    = document.getElementById('gallerySearchClear');
    const resultsGrid    = document.getElementById('gallery-search-results');
    const noResults      = document.getElementById('gallery-no-results');
    const resultCount    = document.getElementById('gallery-result-count');
    const pills          = document.querySelectorAll('.filter-pill');

    // Build a data index from all gallery items
    const allItems = Array.from(document.querySelectorAll('.gallery-item')).map(function(el) {
        const cat = el.closest('.gallery-category') ? el.closest('.gallery-category').getAttribute('data-category') : '';
        return {
            el: el,
            caption: (el.getAttribute('data-caption') || el.querySelector('img').alt || '').toLowerCase(),
            category: cat
        };
    });

    let activeCat = 'all';

    function applySearch() {
        const rawQuery = searchInput.value.trim().toLowerCase();
        // Split into words for fuzzy matching (any word hits = match)
        const words = rawQuery.split(/\s+/).filter(function(w) { return w.length > 0; });
        const isSearching = words.length > 0 || activeCat !== 'all';

        if (!isSearching) {
            section.classList.remove('search-active');
            resultsGrid.innerHTML = '';
            noResults.style.display = 'none';
            resultCount.textContent = '';
            return;
        }

        section.classList.add('search-active');

        // Fuzzy filter: all typed words must appear somewhere in the caption
        const matched = allItems.filter(function(item) {
            const catMatch = activeCat === 'all' || item.category === activeCat;
            const textMatch = words.length === 0 || words.every(function(w) {
                return item.caption.includes(w);
            });
            return catMatch && textMatch;
        });

        resultsGrid.innerHTML = '';

        if (matched.length === 0) {
            noResults.style.display = 'flex';
            resultCount.textContent = '0 products found';
        } else {
            noResults.style.display = 'none';
            resultCount.textContent = matched.length + ' product' + (matched.length !== 1 ? 's' : '') + ' found';

            matched.forEach(function(item, i) {
                const imgEl  = item.el.querySelector('img');
                const imgSrc = item.el.getAttribute('data-src') || (imgEl ? imgEl.src : '');
                const catLabel = item.category.charAt(0).toUpperCase() + item.category.slice(1);
                const origIndex = allItems.indexOf(item);
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML =
                    '<div class="product-card-img">' +
                        '<span class="product-card-cat">' + catLabel + '</span>' +
                        '<img src="' + imgSrc + '" alt="' + item.caption + '" loading="lazy">' +
                        '<div class="product-card-view"><i class="fa-solid fa-magnifying-glass-plus"></i></div>' +
                    '</div>' +
                    '<div class="product-card-info">' +
                        '<div class="product-card-name">' + item.el.getAttribute('data-caption') + '</div>' +
                        '<div class="product-card-tag">' + catLabel + '</div>' +
                    '</div>';

                // Stagger animation
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.35s ease ' + (i * 0.05) + 's, transform 0.35s ease ' + (i * 0.05) + 's';

                card.addEventListener('click', function() { openLightbox(origIndex); });
                resultsGrid.appendChild(card);

                requestAnimationFrame(function() {
                    requestAnimationFrame(function() {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    });
                });
            });
        }
    }

    searchInput.addEventListener('input', function() {
        if (searchInput.value.length > 0) {
            searchBox.classList.add('has-value');
        } else {
            searchBox.classList.remove('has-value');
        }
        applySearch();
    });

    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchBox.classList.remove('has-value');
        applySearch();
        searchInput.focus();
    });

    pills.forEach(function(pill) {
        pill.addEventListener('click', function() {
            pills.forEach(function(p) { p.classList.remove('active'); });
            pill.classList.add('active');
            activeCat = pill.getAttribute('data-cat');
            applySearch();
        });
    });

    /* ══════════════════════════════════════
       LIGHTBOX LOGIC
    ══════════════════════════════════════ */
    const items     = Array.from(document.querySelectorAll('.gallery-categories-wrap .gallery-item'));
    const lightbox  = document.getElementById('lightbox');
    const lbImg     = document.getElementById('lbImg');
    const lbCaption = document.getElementById('lbCaption');
    const lbCounter = document.getElementById('lbCounter');
    const lbImgWrap = document.getElementById('lbImgWrap');

    let currentIndex = 0, scale = 1, panX = 0, panY = 0;
    const SCALE_STEP = 0.3, MAX_SCALE = 4, MIN_SCALE = 1;

    function applyTransform() {
        lbImg.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    }

    function openLightbox(index) {
        currentIndex = index;
        resetZoom();
        updateImage();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        resetZoom();
    }

    function updateImage() {
        const item = items[currentIndex];
        const src  = item.getAttribute('data-src') || item.querySelector('img').src;
        const cap  = item.getAttribute('data-caption') || item.querySelector('img').alt;
        lbImg.style.animation = 'none';
        lbImg.offsetHeight;
        lbImg.style.animation = '';
        lbImg.src = src;
        lbImg.alt = cap;
        lbCaption.textContent = cap;
        lbCounter.textContent = `${currentIndex + 1} / ${items.length}`;
    }

    function zoomIn(e) {
        if(e) { e.preventDefault(); e.stopPropagation(); }
        lbImg.style.transition = 'transform 0.2s ease';
        scale = Math.min(scale + SCALE_STEP, MAX_SCALE);
        applyTransform();
    }
    
    function zoomOut(e) {
        if(e) { e.preventDefault(); e.stopPropagation(); }
        lbImg.style.transition = 'transform 0.2s ease';
        scale = Math.max(scale - SCALE_STEP, MIN_SCALE);
        if (scale === MIN_SCALE) { panX = 0; panY = 0; }
        applyTransform();
    }
    
    function resetZoom() {
        lbImg.style.transition = 'transform 0.2s ease';
        scale = 1; panX = 0; panY = 0;
        applyTransform();
    }
    
    function showPrev()  { currentIndex = (currentIndex - 1 + items.length) % items.length; resetZoom(); updateImage(); }
    function showNext()  { currentIndex = (currentIndex + 1) % items.length; resetZoom(); updateImage(); }

    let isDragging = false, dragStartX = 0, dragStartY = 0, panStartX = 0, panStartY = 0;
    
    function startDrag(e) {
        if (scale <= 1) return;
        isDragging = true;
        lbImg.style.transition = 'none';
        dragStartX = e.clientX || (e.touches && e.touches[0].clientX);
        dragStartY = e.clientY || (e.touches && e.touches[0].clientY);
        panStartX = panX;
        panStartY = panY;
        lbImgWrap.classList.add('dragging');
        if (e.cancelable) e.preventDefault();
    }

    function doDrag(e) {
        if (!isDragging) return;
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);
        panX = panStartX + (clientX - dragStartX);
        panY = panStartY + (clientY - dragStartY);
        applyTransform();
        if (e.cancelable) e.preventDefault();
    }

    function endDrag() {
        isDragging = false;
        lbImgWrap.classList.remove('dragging');
    }

    lbImgWrap.addEventListener('mousedown', startDrag);
    lbImgWrap.addEventListener('touchstart', startDrag, { passive: false });
    
    document.addEventListener('mousemove', doDrag);
    document.addEventListener('touchmove', doDrag, { passive: false });
    
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);

    lightbox.addEventListener('wheel', function(e) {
        e.preventDefault();
        lbImg.style.transition = 'transform 0.1s ease';
        e.deltaY < 0 ? zoomIn() : zoomOut();
    }, { passive: false });

    let swipeStartX = 0;
    lightbox.addEventListener('touchstart', function(e) {
        swipeStartX = e.touches[0].clientX;
    }, { passive: true });
    
    lightbox.addEventListener('touchend', function(e) {
        if (scale > 1) return;
        const diff = swipeStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) {
            diff > 0 ? showNext() : showPrev();
        }
    }, { passive: true });

    document.getElementById('lbZoomIn').addEventListener('click', zoomIn);
    document.getElementById('lbZoomOut').addEventListener('click', zoomOut);
    document.getElementById('lbReset').addEventListener('click', resetZoom);
    document.getElementById('lbClose').addEventListener('click', closeLightbox);
    document.getElementById('lbPrev').addEventListener('click', showPrev);
    document.getElementById('lbNext').addEventListener('click', showNext);
    document.querySelector('.lightbox-backdrop').addEventListener('click', closeLightbox);

    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('active')) return;
        switch (e.key) {
            case 'Escape': closeLightbox(); break;
            case 'ArrowLeft': showPrev(); break;
            case 'ArrowRight': showNext(); break;
            case '+': case '=': zoomIn(); break;
            case '-': zoomOut(); break;
            case '0': resetZoom(); break;
        }
    });

    items.forEach(function(item, index) {
        item.addEventListener('click', function() { openLightbox(index); });
    });

    // Expose openLightbox for search result clones
    window.openLightbox = openLightbox;
})();
