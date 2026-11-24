(function (window) {
  var CART_KEY = "impress_cart";
  var WISH_KEY = "impress_wishlist";

  function read(key) {
    try {
      var parsed = JSON.parse(window.localStorage.getItem(key) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) {
      return [];
    }
  }

  function write(key, items) {
    window.localStorage.setItem(key, JSON.stringify(items));
    updateCounts();
    window.dispatchEvent(new CustomEvent("impress-store-change"));
  }

  function updateCounts() {
    var cartCount = read(CART_KEY).reduce(function (sum, item) { return sum + (Number(item.qty) || 1); }, 0);
    var wishCount = read(WISH_KEY).length;
    document.querySelectorAll('[data-count="cart"]').forEach(function (el) {
      el.textContent = String(cartCount);
      el.hidden = cartCount === 0;
    });
    document.querySelectorAll('[data-count="wishlist"]').forEach(function (el) {
      el.textContent = String(wishCount);
      el.hidden = wishCount === 0;
    });
  }

  function addToCart(item) {
    var items = read(CART_KEY);
    var existing = items.find(function (entry) { return entry.slug === item.slug; });
    var qty = Math.max(1, Number(item.qty) || 1);
    if (existing) existing.qty = (Number(existing.qty) || 1) + qty;
    else items.push({ slug: item.slug, name: item.name, image: item.image, url: item.url, category: item.category || "", qty: qty });
    write(CART_KEY, items);
  }

  function toggleWishlist(item) {
    var items = read(WISH_KEY);
    var saved = items.some(function (entry) { return entry.slug === item.slug; });
    items = saved ? items.filter(function (entry) { return entry.slug !== item.slug; }) : items.concat([{ slug: item.slug, name: item.name, image: item.image, url: item.url, category: item.category || "" }]);
    write(WISH_KEY, items);
    return !saved;
  }

  window.ImpressStore = {
    cart: function () { return read(CART_KEY); },
    wishlist: function () { return read(WISH_KEY); },
    addToCart: addToCart,
    setCartQty: function (slug, qty) {
      write(CART_KEY, read(CART_KEY).map(function (item) {
        if (item.slug === slug) item.qty = Math.max(1, Number(qty) || 1);
        return item;
      }));
    },
    clearCart: function () { write(CART_KEY, []); },
    removeFromCart: function (slug) { write(CART_KEY, read(CART_KEY).filter(function (item) { return item.slug !== slug; })); },
    isWishlisted: function (slug) { return read(WISH_KEY).some(function (item) { return item.slug === slug; }); },
    toggleWishlist: toggleWishlist,
    removeWishlist: function (slug) { write(WISH_KEY, read(WISH_KEY).filter(function (item) { return item.slug !== slug; })); },
    updateCounts: updateCounts
  };

  document.addEventListener("DOMContentLoaded", updateCounts);
})(window);
