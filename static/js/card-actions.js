(function () {
  var store = window.ImpressStore;
  if (!store) return;

  function cardInput(button) {
    var card = button.closest(".product-card");
    return card ? card.querySelector("[data-card-qty]") : null;
  }

  function typedQty(input) {
    var value = Math.max(1, Number(input && input.value) || 1);
    return value;
  }

  function itemFrom(button) {
    return {
      slug: button.getAttribute("data-slug"),
      name: button.getAttribute("data-name"),
      image: button.getAttribute("data-image"),
      url: button.getAttribute("data-url"),
      category: button.getAttribute("data-category") || "",
      qty: typedQty(cardInput(button))
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
    var step = event.target.closest("[data-card-step]");
    if (step && !step.disabled) {
      event.preventDefault();
      var input = step.parentElement.querySelector("[data-card-qty]");
      if (!input || input.disabled) return;
      var next = Math.max(1, (Number(input.value) || 1) + Number(step.getAttribute("data-card-step")));
      input.value = String(next);
      return;
    }
    var wish = event.target.closest("[data-toggle-wish]");
    var cart = event.target.closest("[data-add-cart]");
    if (wish) {
      event.preventDefault();
      store.toggleWishlist(itemFrom(wish));
      sync();
    } else if (cart && !cart.disabled) {
      event.preventDefault();
      store.addToCart(itemFrom(cart));
      var label = cart.textContent;
      cart.textContent = "Added";
      window.setTimeout(function () { cart.textContent = label; }, 1200);
    }
  });
  document.addEventListener("input", function (event) {
    if (!event.target.matches("[data-card-qty]")) return;
    event.target.value = event.target.value.replace(/\D/g, "");
  });
  document.addEventListener("focusout", function (event) {
    if (!event.target.matches("[data-card-qty]")) return;
    event.target.value = String(Math.max(1, Number(event.target.value) || 1));
  });
  document.addEventListener("DOMContentLoaded", sync);
  window.addEventListener("impress-store-change", sync);
})();
