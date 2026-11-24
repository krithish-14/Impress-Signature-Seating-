(function () {
  var form = document.getElementById("contactForm");
  if (!form) return;
  var successEl = document.getElementById("contactSuccess");
  var errorEl = document.getElementById("contactError");
  var submitBtn = document.getElementById("contactSubmit");
  var messageInput = document.getElementById("message");
  var preview = document.getElementById("quotePreview");

  function showFieldError(name, message) {
    var input = form.querySelector('[name="' + name + '"]');
    var msg = form.querySelector('[data-for="' + name + '"]');
    if (input) input.classList.toggle("invalid", Boolean(message));
    if (msg) {
      msg.textContent = message || "";
      msg.style.display = message ? "block" : "none";
    }
  }

  function collectQuoteItems() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("slug") || params.get("product")) {
      return { source: "product", items: [{ slug: params.get("slug") || "", name: params.get("product") || "", qty: Number(params.get("qty") || 1) || 1 }] };
    }
    var cart = window.ImpressStore ? window.ImpressStore.cart() : [];
    if (cart.length) {
      return { source: "cart", items: cart.map(function (item) { return { slug: item.slug || "", name: item.name || "", qty: Number(item.qty) || 1 }; }) };
    }
    return { source: "general", items: [] };
  }

  function showPreview() {
    var collected = collectQuoteItems();
    if (!collected.items.length) { preview.hidden = true; return; }
    preview.hidden = false;
    preview.innerHTML = "<strong>This enquiry includes</strong><ul class='mb-0'>" + collected.items.map(function (item) {
      return "<li>" + String(item.name).replace(/[&<>]/g, function (ch) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]; }) + " × " + item.qty + "</li>";
    }).join("") + "</ul>";
    if (!messageInput.value && collected.source === "cart") {
      messageInput.value = "I would like a quote for " + collected.items.map(function (item) { return item.name + " x" + item.qty; }).join(", ") + ".";
    }
  }

  showPreview();
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    ["name", "email", "phone", "message"].forEach(function (name) { showFieldError(name, ""); });
    successEl.hidden = true;
    errorEl.hidden = true;
    successEl.style.display = "none";
    errorEl.style.display = "none";
    var collected = collectQuoteItems();
    document.getElementById("quoteItems").value = JSON.stringify(collected.items);
    submitBtn.disabled = true;
    fetch(form.action, { method: "POST", headers: { "X-Requested-With": "XMLHttpRequest" }, body: new FormData(form) })
      .then(function (response) { return response.json().then(function (data) { return { ok: response.ok, data: data }; }); })
      .then(function (result) {
        if (result.ok && result.data.success) {
          successEl.textContent = result.data.message;
          successEl.hidden = false;
          successEl.style.display = "block";
          form.reset();
          if (collected.source === "cart" && window.ImpressStore) window.ImpressStore.clearCart();
          showPreview();
        } else {
          Object.keys(result.data.errors || {}).forEach(function (key) { showFieldError(key, result.data.errors[key]); });
          errorEl.textContent = result.data.message || "Unable to send your message. Please try again later.";
          errorEl.hidden = false;
          errorEl.style.display = "block";
        }
      })
      .catch(function () {
        errorEl.textContent = "Unable to send your message. Please try again later.";
        errorEl.hidden = false;
        errorEl.style.display = "block";
      })
      .finally(function () { submitBtn.disabled = false; });
  });
})();
