// copy buttons on code blocks, light / dark toggle (remembered), anchors on doc headings
(() => {
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem("theme");
    if (saved) root.dataset.theme = saved;
  } catch {}
  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", () => {
        const next = root.dataset.theme === "light" ? "dark" : "light";
        root.dataset.theme = next;
        try { localStorage.setItem("theme", next); } catch {}
      });
    }
    for (const pre of document.querySelectorAll("pre")) {
      const button = document.createElement("button");
      button.className = "copy";
      button.type = "button";
      button.textContent = "copy";
      button.addEventListener("click", async () => {
        const text = pre.querySelector("code")?.innerText ?? pre.innerText;
        try {
          await navigator.clipboard.writeText(text.replace(/\n$/, ""));
          button.textContent = "copied";
        } catch {
          button.textContent = "select it";
        }
        setTimeout(() => (button.textContent = "copy"), 1400);
      });
      pre.appendChild(button);
    }
    for (const heading of document.querySelectorAll(".docs article h2[id], .docs article h3[id]")) {
      const a = document.createElement("a");
      a.className = "anchor";
      a.href = "#" + heading.id;
      a.textContent = "#";
      a.setAttribute("aria-label", "Link to this section");
      heading.appendChild(a);
    }
    const filter = document.querySelector("#command-filter");
    if (filter) {
      filter.addEventListener("input", () => {
        const q = filter.value.trim().toLowerCase();
        for (const cmd of document.querySelectorAll(".cmd")) {
          cmd.hidden = q && !cmd.textContent.toLowerCase().includes(q);
        }
      });
    }
  });
})();
