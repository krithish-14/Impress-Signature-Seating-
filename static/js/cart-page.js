(function () {
  var store = window.ImpressStore;
  var emptyEl = document.getElementById("cartEmpty");
  var listEl = document.getElementById("cartList");
  var footerEl = document.getElementById("cartFooter");
  var totalEl = document.getElementById("cartTotal");
  var whatsappBtn = document.getElementById("cartWhatsappBtn");
  if (!store || !emptyEl || !listEl) return;

  function whatsappLink(items) {
    if (!whatsappBtn) return;
    var lines = items.map(function (item) {
      return "- " + (item.name || "Item") + " x " + (Number(item.qty) || 1);
    }).join("\n");
    var text = "Hi, I would like a quote for:\n" + lines;
    whatsappBtn.href = "https://wa.me/" + whatsappBtn.getAttribute("data-whatsapp") + "?text=" + encodeURIComponent(text);
  }

  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function render() {
    var items = store.cart();
    var empty = items.length === 0;
    emptyEl.hidden = !empty;
    listEl.hidden = empty;
    footerEl.hidden = empty;
    if (empty) { listEl.innerHTML = ""; return; }
    listEl.innerHTML = items.map(function (item) {
      return '<article class="bag-item"><a href="' + esc(item.url) + '"><img src="' + esc(item.image) + '" alt="' + esc(item.name) + '"></a><div class="bag-info"><p class="bag-cat">' + esc(item.category) + '</p><a href="' + esc(item.url) + '"><h3>' + esc(item.name) + '</h3></a><div class="qty-stepper"><button type="button" data-step="-1" data-slug="' + esc(item.slug) + '" aria-label="Decrease quantity">−</button><span>' + esc(item.qty) + '</span><button type="button" data-step="1" data-slug="' + esc(item.slug) + '" aria-label="Increase quantity">+</button></div></div><button class="bag-remove" type="button" data-remove="' + esc(item.slug) + '" aria-label="Remove">×</button></article>';
    }).join("");
    totalEl.textContent = String(items.reduce(function (sum, item) { return sum + (Number(item.qty) || 1); }, 0));
    whatsappLink(items);
  }
  listEl.addEventListener("click", function (event) {
    var stepBtn = event.target.closest("[data-step]");
    if (stepBtn) {
      var slug = stepBtn.getAttribute("data-slug");
      var item = store.cart().find(function (entry) { return entry.slug === slug; });
      if (!item) return;
      var next = (Number(item.qty) || 1) + Number(stepBtn.getAttribute("data-step"));
      if (next < 1) store.removeFromCart(slug);
      else store.setCartQty(slug, next);
      return;
    }
    var button = event.target.closest("[data-remove]");
    if (button) store.removeFromCart(button.getAttribute("data-remove"));
  });
  window.addEventListener("impress-store-change", render);
  render();
})();
