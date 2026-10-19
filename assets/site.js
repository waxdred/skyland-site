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

// motion: reveals on scroll (Apple), windows popping in and sliding (Hyprland), the hero
// shot straightening as it scrolls, and the tiling demo laid out by the scroll position
(() => {
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.addEventListener("DOMContentLoaded", () => {
    const mark = (selector, cls, stagger) => {
      document.querySelectorAll(selector).forEach((el, i) => {
        el.classList.add("reveal");
        if (cls) el.classList.add(typeof cls === "function" ? cls(i) : cls);
        if (stagger) el.style.setProperty("--i", String(i % stagger));
      });
    };
    mark("main section h2, main section .sub, .tiling .head");
    mark(".grid .feature", "pop", 4);                       // a row of windows opening
    mark(".gallery figure", (i) => (i % 2 ? "from-right" : "from-left"), 2);
    mark(".split > img", null);
    mark(".docs article .card", null);
    const seen = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); seen.unobserve(e.target); }
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach((el) => seen.observe(el));

    // the hero shot: tilted back, straightens as it comes up (scroll-linked)
    const shot = document.querySelector(".hero .shot");
    if (shot && !still) shot.classList.add("tilt");

    // tiling demo: dwindle from 1 to 5 windows, then the master layout
    const demo = document.querySelector(".tiling");
    const wins = demo ? [...demo.querySelectorAll(".win")] : [];
    const caption = demo?.querySelector(".caption");
    const dots = demo ? [...demo.querySelectorAll(".bar .ws")] : [];
    const D = (x, y, w, h) => ({ x, y, w, h });
    const steps = [
      { text: "<kbd>alt-t</kbd> a terminal fills the workspace", focus: 0, ws: 0, rects: [D(0, 0, 100, 100)] },
      { text: "dwindle: the next one splits the focused window", focus: 1, ws: 0, rects: [D(0, 0, 50, 100), D(50, 0, 50, 100)] },
      { text: "along its longest side, toward the cursor", focus: 2, ws: 0, rects: [D(0, 0, 50, 100), D(50, 0, 50, 50), D(50, 50, 50, 50)] },
      { text: "and again: smart_split", focus: 3, ws: 0, rects: [D(0, 0, 50, 100), D(50, 0, 50, 50), D(50, 50, 25, 50), D(75, 50, 25, 50)] },
      { text: "five windows, no mouse", focus: 4, ws: 0, rects: [D(0, 0, 50, 100), D(50, 0, 50, 50), D(50, 50, 25, 50), D(75, 50, 25, 25), D(75, 75, 25, 25)] },
      { text: "<kbd>alt-shift-t</kbd> master layout: one big window, a stack", focus: 0, ws: 0, rects: [D(0, 0, 60, 100), D(60, 0, 40, 25), D(60, 25, 40, 25), D(60, 50, 40, 25), D(60, 75, 40, 25)] },
      { text: "<kbd>cmd-2</kbd> workspaces slide, Hyprland's slidevert", focus: 5, ws: 1, rects: [], next: [D(0, 0, 100, 100)] },
    ];
    let current = -1;
    const gap = 6; // px, Hyprland gaps_in
    const place = (win, r) => {
      win.style.left = `calc(${r.x}% + ${gap / 2}px)`;
      win.style.top = `calc(${r.y}% + ${gap / 2}px)`;
      win.style.width = `calc(${r.w}% - ${gap}px)`;
      win.style.height = `calc(${r.h}% - ${gap}px)`;
    };
    const apply = (n) => {
      if (n === current) return;
      current = n;
      const step = steps[n];
      caption.innerHTML = step.text;
      dots.forEach((d, i) => d.classList.toggle("on", i === step.ws));
      wins.forEach((win, i) => {
        const onNext = i === wins.length - 1; // the window of workspace 2
        const r = onNext ? step.next?.[0] : step.rects[i];
        win.classList.toggle("focused", i === step.focus);
        if (r) {
          if (!win.classList.contains("shown")) place(win, step.ws ? D(r.x, r.y + 100, r.w, r.h) : r); // slides in from below
          requestAnimationFrame(() => { place(win, r); win.classList.add("shown"); });
        } else if (step.ws && !onNext && win.classList.contains("shown")) {
          const was = steps[5].rects[i]; // slides out above
          place(win, D(was.x, was.y - 100, was.w, was.h));
        } else {
          win.classList.remove("shown");
        }
        if (!step.ws && onNext) win.classList.remove("shown");
      });
    };

    let ticking = false;
    const onScroll = () => {
      ticking = false;
      if (shot && !still) {
        const r = shot.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, 1 - (r.top - innerHeight * 0.15) / (innerHeight * 0.75)));
        shot.style.transform = `perspective(1400px) rotateX(${(1 - p) * 16}deg) scale(${0.9 + p * 0.1})`;
        shot.style.opacity = String(0.6 + p * 0.4);
      }
      if (demo) {
        const r = demo.getBoundingClientRect();
        const p = Math.min(0.999, Math.max(0, -r.top / (r.height - innerHeight)));
        apply(still ? 4 : Math.floor(p * steps.length));
      }
    };
    addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    addEventListener("resize", onScroll);
    onScroll();
  });
})();
