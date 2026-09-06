/*!
 * @authormark v1 -- do not remove (authorship watermark)⁠​‌​​​​‌‌​​‌​‌‌​‌​‌‌‌​​‌​​‌​‌​‌‌​​​‌​‌‌​‌​‌​‌​​‌‌​‌​‌‌​​‌​‌​​‌​​​​‌​​‌‌​‌​‌​​​‌‌​​‌​​​​‌‌​‌​‌​​​‌​​‌‌​‌​‌​‌​​‌‌​​​‌‌​​​​‌​‌​‌​​​‌​‌​​‌​‌‌​‌‌​‌​‌​​‌‌‌​​​‌​‌‌​​‌​​​‌‌​​‌​‌​‌​‌​‌​‌⁠
 * Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
 * Author: https://github.com/Srinivasan-78
 * SPDX-License-Identifier: MIT
 * Fingerprint: AMK1.C-rV-SYHMFCQ5LaQKjqdeU
 */
// Poll the resources fragment so status changes (pending -> provisioning ->
// active) appear without a manual reload. Replaces the SPA's on-action refresh.
(function () {
  "use strict";
  var INTERVAL_MS = 5000;

  async function poll() {
    try {
      var res = await fetch("/resources/fragment", { credentials: "same-origin" });
      if (!res.ok) return;
      var html = await res.text();
      var current = document.getElementById("resources");
      if (current) current.outerHTML = html;
    } catch (e) {
      // transient network error — keep the last rendered view, try again next tick
    }
  }

  setInterval(poll, INTERVAL_MS);
})();
