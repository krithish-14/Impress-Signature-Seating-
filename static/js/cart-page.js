(function () {
  var store = window.ImpressStore;
  var emptyEl = document.getElementById("cartEmpty");
  var listEl = document.getElementById("cartList");
  var footerEl = document.getElementById("cartFooter");
  var totalEl = document.getElementById("cartTotal");
  if (!store || !emptyEl || !listEl) return;

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
      return '<article class="bag-item"><a href="' + esc(item.url) + '"><img src="' + esc(item.image) + '" alt="' + esc(item.name) + '"></a><div class="bag-info"><p class="bag-cat">' + esc(item.category) + '</p><a href="' + esc(item.url) + '"><h3>' + esc(item.name) + '</h3></a><label>Qty <input type="number" min="1" value="' + esc(item.qty) + '" data-qty="' + esc(item.slug) + '"></label></div><button class="bag-remove" type="button" data-remove="' + esc(item.slug) + '" aria-label="Remove">×</button></article>';
    }).join("");
    totalEl.textContent = String(items.reduce(function (sum, item) { return sum + (Number(item.qty) || 1); }, 0));
  }
  listEl.addEventListener("change", function (event) {
    var slug = event.target.getAttribute("data-qty");
    if (slug) { store.setCartQty(slug, event.target.value); render(); }
  });
  listEl.addEventListener("click", function (event) {
    var button = event.target.closest("[data-remove]");
    if (button) { store.removeFromCart(button.getAttribute("data-remove")); render(); }
  });
  render();
})();
