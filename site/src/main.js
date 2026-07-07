const term = document.getElementById("termBody");
const frame = document.getElementById("frame");
const specName = document.getElementById("specName");
const specMeta = document.getElementById("specMeta");
const copyBtn = document.getElementById("copyBtn");

const installText = document.getElementById("installText");
const tabs = [...document.querySelectorAll(".tab")];

const INSTALL_COMMANDS = {
  script: "curl -LsSf https://fram.serhiifotex.dev/install.sh | sh",
  brew: "brew tap Sergio-prog/fram && brew install fram",
  uv: "uv tool install git+https://github.com/Sergio-prog/fram.git",
  skill: "npx skills add Sergio-prog/fram",
};

let activeCommand = INSTALL_COMMANDS.script;

for (const tab of tabs) {
  tab.addEventListener("click", () => {
    for (const t of tabs) {
      t.classList.toggle("active", t === tab);
      t.setAttribute("aria-selected", String(t === tab));
    }
    activeCommand = INSTALL_COMMANDS[tab.dataset.method];
    installText.textContent = activeCommand;
  });
}

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(activeCommand);
    copyBtn.textContent = "copied";
    copyBtn.classList.add("done");
    setTimeout(() => {
      copyBtn.textContent = "copy";
      copyBtn.classList.remove("done");
    }, 1600);
  } catch {
    copyBtn.textContent = "select →";
  }
});

const BASE = { w: "236px", h: "148px", imgw: "236px", fx: "none" };

const steps = [
  {
    cmd: "fram resize voyage.jpg 480x300 -o web.jpg",
    out: '<span class="ok">✓</span> web.jpg <span class="strong">480x300</span> · 96.4 KB · 0.1s',
    spec: { name: "web.jpg", meta: "480×300 · 96.4 KB", w: "188px", h: "118px", imgw: "188px" },
  },
  {
    cmd: "fram crop web.jpg 300x300 --anchor center -o square.jpg",
    out: '<span class="ok">✓</span> square.jpg <span class="strong">300x300</span> · 64.1 KB · 0.1s',
    spec: { name: "square.jpg", meta: "300×300 · 64.1 KB", w: "118px", h: "118px" },
  },
  {
    cmd: "fram grayscale square.jpg -o mono.jpg",
    out: '<span class="ok">✓</span> mono.jpg <span class="strong">300x300</span> · 58.9 KB · 0.1s',
    spec: { name: "mono.jpg", meta: "300×300 · 58.9 KB", fx: "grayscale(1) contrast(1.05)" },
  },
  {
    cmd: "fram compress-image mono.jpg --quality 80 -o final.webp",
    out: '<span class="ok">✓</span> final.webp · 58.9 KB <span class="arrow">→</span> <span class="strong">11.2 KB</span> (-81%)',
    spec: { name: "final.webp", meta: "300×300 · 11.2 KB", fx: "grayscale(1) contrast(1.05) blur(0.4px)" },
  },
  {
    cmd: "fram",
    hint: "← opens the interactive TUI",
  },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function applySpec(spec) {
  const merged = { ...spec };
  if (merged.w) frame.style.setProperty("--w", merged.w);
  if (merged.h) frame.style.setProperty("--h", merged.h);
  if (merged.imgw) frame.style.setProperty("--imgw", merged.imgw);
  if (merged.fx) frame.style.setProperty("--fx", merged.fx);
  if (merged.name) specName.textContent = merged.name;
  if (merged.meta) specMeta.textContent = merged.meta;
}

function resetSpec() {
  frame.style.setProperty("--w", BASE.w);
  frame.style.setProperty("--h", BASE.h);
  frame.style.setProperty("--imgw", BASE.imgw);
  frame.style.setProperty("--fx", BASE.fx);
  specName.textContent = "voyage.jpg";
  specMeta.textContent = "1600×1000 · 2.4 MB";
}

function line(cls = "") {
  const el = document.createElement("div");
  el.className = `t-line ${cls}`.trim();
  term.appendChild(el);
  return el;
}

function renderStatic() {
  for (const step of steps) {
    const l = line();
    l.innerHTML = `<span class="prompt">$ </span><span class="cmd">${step.cmd}</span>`;
    if (step.out) {
      const o = line("out");
      o.innerHTML = step.out;
    }
    if (step.hint) {
      const h = line("out hint");
      h.textContent = step.hint;
    }
  }
  const l = line();
  l.innerHTML = '<span class="prompt">$ </span><span class="cursor"></span>';
}

async function typeCommand(text) {
  const l = line();
  const prompt = document.createElement("span");
  prompt.className = "prompt";
  prompt.textContent = "$ ";
  const cmd = document.createElement("span");
  cmd.className = "cmd";
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  l.append(prompt, cmd, cursor);
  for (const ch of text) {
    cmd.textContent += ch;
    await sleep(ch === " " ? 46 : 24 + Math.random() * 26);
  }
  await sleep(260);
  cursor.remove();
}

async function runLoop() {
  while (true) {
    term.classList.remove("fading");
    for (const step of steps) {
      await typeCommand(step.cmd);
      await sleep(300);
      if (step.out) {
        const o = line("out");
        o.innerHTML = step.out;
      }
      if (step.hint) {
        const h = line("out hint");
        h.textContent = step.hint;
      }
      if (step.spec) applySpec(step.spec);
      await sleep(step.hint ? 2600 : 1250);
    }
    await sleep(1400);
    term.classList.add("fading");
    await sleep(500);
    term.replaceChildren();
    resetSpec();
    await sleep(900);
  }
}

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (reducedMotion) {
  renderStatic();
} else {
  runLoop();
}
