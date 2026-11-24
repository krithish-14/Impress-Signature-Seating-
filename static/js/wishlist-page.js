(function () {
  var store = window.ImpressStore;
  var emptyEl = document.getElementById("wishEmpty");
  var listEl = document.getElementById("wishList");
  if (!store || !emptyEl || !listEl) return;
  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function render() {
    var items = store.wishlist();
    var empty = items.length === 0;
    emptyEl.hidden = !empty;
    listEl.hidden = empty;
    if (empty) { listEl.innerHTML = ""; return; }
    listEl.innerHTML = items.map(function (item) {
      return '<article class="bag-item"><a href="' + esc(item.url) + '"><img src="' + esc(item.image) + '" alt="' + esc(item.name) + '"></a><div class="bag-info"><p class="bag-cat">' + esc(item.category) + '</p><a href="' + esc(item.url) + '"><h3>' + esc(item.name) + '</h3></a><button class="bag-add" type="button" data-cart="' + esc(item.slug) + '">Add to cart</button></div><button class="bag-remove" type="button" data-remove="' + esc(item.slug) + '" aria-label="Remove">×</button></article>';
    }).join("");
  }
  listEl.addEventListener("click", function (event) {
    var removeBtn = event.target.closest("[data-remove]");
    var cartBtn = event.target.closest("[data-cart]");
    if (removeBtn) { store.removeWishlist(removeBtn.getAttribute("data-remove")); render(); return; }
    if (cartBtn) {
      var slug = cartBtn.getAttribute("data-cart");
      var item = store.wishlist().find(function (entry) { return entry.slug === slug; });
      if (item) store.addToCart({ slug: item.slug, name: item.name, image: item.image, url: item.url, category: item.category, qty: 1 });
    }
  });
  render();
})();
