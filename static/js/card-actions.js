(function () {
  var store = window.ImpressStore;
  if (!store) return;

  function itemFrom(button) {
    return {
      slug: button.getAttribute("data-slug"),
      name: button.getAttribute("data-name"),
      image: button.getAttribute("data-image"),
      url: button.getAttribute("data-url"),
      category: button.getAttribute("data-category") || "",
      qty: 1
    };
  }

  function sync() {
    document.querySelectorAll("[data-toggle-wish]").forEach(function (button) {
      var saved = store.isWishlisted(button.getAttribute("data-slug"));
      button.classList.toggle("is-active", saved);
      var icon = button.querySelector("i");
      if (icon) icon.className = saved ? "fa-solid fa-heart" : "fa-regular fa-heart";
    });
  }

  document.addEventListener("click", function (event) {
    var wish = event.target.closest("[data-toggle-wish]");
    var cart = event.target.closest("[data-add-cart]");
    if (wish) {
      event.preventDefault();
      store.toggleWishlist(itemFrom(wish));
      sync();
    } else if (cart && !cart.disabled) {
      event.preventDefault();
      store.addToCart(itemFrom(cart));
    }
  });
  document.addEventListener("DOMContentLoaded", sync);
  window.addEventListener("impress-store-change", sync);
})();
