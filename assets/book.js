(function () {
  var root = document.documentElement;

  // Theme: follow the system unless the reader picks one (remembered on this device).
  var KEY = "aih-theme";
  try {
    var saved = localStorage.getItem(KEY);
    if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  } catch (e) { /* storage unavailable: keep system theme */ }

  var btn = document.querySelector(".theme-btn");
  function currentIsDark() {
    var forced = root.getAttribute("data-theme");
    if (forced) return forced === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function paintBtn() {
    if (btn) btn.textContent = currentIsDark() ? "Light" : "Dark";
  }
  if (btn) {
    paintBtn();
    btn.addEventListener("click", function () {
      var next = currentIsDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
      paintBtn();
    });
  }

  // Reading progress bar.
  var bar = document.querySelector(".progress");
  function onScroll() {
    if (!bar) return;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? (window.scrollY / h) * 100 : 0;
    bar.style.width = Math.min(100, Math.max(0, p)) + "%";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Copy buttons on code blocks.
  document.querySelectorAll("pre").forEach(function (pre) {
    var b = document.createElement("button");
    b.className = "copy-btn";
    b.type = "button";
    b.textContent = "Copy";
    b.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = code ? code.innerText : pre.innerText;
      var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1400); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta); done();
      }
    });
    pre.appendChild(b);
  });
})();
