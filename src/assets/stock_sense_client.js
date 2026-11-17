// Stock Sense ERP - Client-side keyboard shortcuts (Ctrl+K, Ctrl+B, ESC)
(function () {
  document.addEventListener("keydown", function (e) {
    // Ctrl+K or Cmd+K -> open Quick Search trigger button
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      var btn = document.getElementById("btn-open-quick-search");
      if (btn) btn.click();
    }
    // Ctrl+B or Cmd+B -> toggle Sidebar collapse
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
      e.preventDefault();
      var toggleBtn = document.getElementById("sidebarToggleBtn");
      if (toggleBtn) toggleBtn.click();
    }
    // ESC -> close visible modals / drawers
    if (e.key === "Escape") {
      [
        "btn-close-quick-search",
        "btn-close-m1-drawer",
        "btn-close-m2-drawer",
        "btn-close-snooze-modal",
        "btn-close-m2-threshold",
        "btn-close-m3-tag-modal",
        "btn-close-m3-campaign-modal",
        "btn-close-po-preview",
        "btn-close-m4-supplier-drawer",
        "btn-close-m4-lifecycle-modal",
        "btn-close-m5-cycle-modal",
      ].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.click();
      });
    }
  });
})();
