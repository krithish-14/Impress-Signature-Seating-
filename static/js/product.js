(function () {
  var cfg = window.IMPRESS_PDP;
  var store = window.ImpressStore;
  if (!cfg || !store) return;
  var qty = document.getElementById("pdp-qty");
  var cartBtn = document.getElementById("pdpCartBtn");
  var wishBtn = document.getElementById("pdpWishBtn");
  var enquireBtn = document.getElementById("pdpEnquireBtn");
  var waBtn = document.getElementById("pdpWhatsappBtn");

  function current() {
    return { slug: cfg.slug, name: cfg.name, image: cfg.image, url: cfg.url, category: cfg.category, qty: qty ? qty.value : 1 };
  }
  function syncWish() {
    var saved = store.isWishlisted(cfg.slug);
    wishBtn.innerHTML = saved ? '<i class="fa-solid fa-heart"></i> Saved to wishlist' : '<i class="fa-regular fa-heart"></i> Add to wishlist';
  }
  function syncLinks() {
    var amount = qty && qty.value ? qty.value : "1";
    var text = "Hi, I would like a quote for " + cfg.name + " (quantity: " + amount + ").";
    if (waBtn) waBtn.href = "https://wa.me/" + cfg.whatsapp + "?text=" + encodeURIComponent(text);
    if (enquireBtn) enquireBtn.href = "/contact/?slug=" + encodeURIComponent(cfg.slug) + "&product=" + encodeURIComponent(cfg.name) + "&qty=" + encodeURIComponent(amount);
  }
  if (qty) qty.addEventListener("input", syncLinks);
  syncLinks();
  syncWish();
  if (cartBtn) cartBtn.addEventListener("click", function () {
    store.addToCart(current());
    cartBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added to cart';
    window.setTimeout(function () { cartBtn.innerHTML = '<i class="fa-solid fa-bag-shopping"></i> Add to cart'; }, 1400);
  });
  if (wishBtn) wishBtn.addEventListener("click", function () { store.toggleWishlist(current()); syncWish(); });
})();
