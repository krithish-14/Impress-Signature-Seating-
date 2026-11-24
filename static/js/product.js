(function () {
  var cfg = window.IMPRESS_PDP;
  var store = window.ImpressStore;
  if (!cfg || !store) return;
  var qty = document.getElementById("pdp-qty");
  var cartBtn = document.getElementById("pdpCartBtn");
  var wishBtn = document.getElementById("pdpWishBtn");
  var enquireBtn = document.getElementById("pdpEnquireBtn");

  function current() {
    return { slug: cfg.slug, name: cfg.name, image: cfg.image, url: cfg.url, category: cfg.category, qty: qty ? qty.value : 1 };
  }
  function syncWish() {
    var saved = store.isWishlisted(cfg.slug);
    wishBtn.innerHTML = saved ? '<i class="fa-solid fa-heart"></i> Saved to wishlist' : '<i class="fa-regular fa-heart"></i> Add to wishlist';
  }
  function syncLinks() {
    var amount = qty && qty.value ? qty.value : "1";
    if (enquireBtn) enquireBtn.href = "/contact/?slug=" + encodeURIComponent(cfg.slug) + "&product=" + encodeURIComponent(cfg.name) + "&qty=" + encodeURIComponent(amount);
  }
  if (qty) {
    qty.addEventListener("input", function () {
      qty.value = qty.value.replace(/\D/g, "");
      syncLinks();
    });
    qty.addEventListener("blur", function () {
      var next = Math.max(1, Number(qty.value) || 1);
      var limit = Number(qty.getAttribute("data-max") || 0);
      if (limit) next = Math.min(limit, next);
      qty.value = String(next);
      syncLinks();
    });
  }
  document.querySelectorAll("[data-qty-step]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!qty || qty.disabled) return;
      var next = Math.max(1, (Number(qty.value) || 1) + Number(button.getAttribute("data-qty-step")));
      var limit = Number(qty.getAttribute("data-max") || 0);
      if (limit) next = Math.min(limit, next);
      qty.value = String(next);
      syncLinks();
    });
  });
  syncLinks();
  syncWish();
  if (cartBtn) cartBtn.addEventListener("click", function () {
    store.addToCart(current());
    cartBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added to cart';
    window.setTimeout(function () { cartBtn.innerHTML = '<i class="fa-solid fa-bag-shopping"></i> Add to cart'; }, 1400);
  });
  if (wishBtn) wishBtn.addEventListener("click", function () { store.toggleWishlist(current()); syncWish(); });
  var related = document.getElementById("pdpRelated");
  document.querySelectorAll("[data-related-dir]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!related) return;
      var card = related.querySelector(".product-card");
      var step = card ? card.getBoundingClientRect().width + 12 : 220;
      related.scrollBy({ left: Number(button.getAttribute("data-related-dir")) * step, behavior: "smooth" });
    });
  });
})();
