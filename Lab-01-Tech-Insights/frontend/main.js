function setStatus(message, type = "info") {
  const status = document.getElementById("status");
  if (!message) {
    status.hidden = true;
    status.textContent = "";
    status.dataset.type = "";
    return;
  }

  status.hidden = false;
  status.textContent = message;
  status.dataset.type = type;
}

async function fetchText(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Fetch failed: ${res.status} ${res.statusText}`);
  }
  return await res.text();
}

async function getMarked() {
  // Prefer global UMD build if present
  if (globalThis.marked && typeof globalThis.marked.parse === "function") {
    return globalThis.marked;
  }

  throw new Error(
    "Markdown parser marked was not loaded. Check that index.html loaded ./vendor/marked.min.js."
  );
}

function parseMarkdown(markedLib, markdown) {
  const options = {
    gfm: true,
    breaks: true,
    headerIds: true,
    mangle: false,
  };

  if (markedLib && typeof markedLib.parse === "function") {
    return markedLib.parse(markdown, options);
  }
  if (typeof markedLib === "function") {
    return markedLib(markdown, options);
  }

  throw new Error("marked was loaded but did not expose parse().");
}

async function renderMarkdown(markdown) {
  const markedLib = await getMarked();
  const html = parseMarkdown(markedLib, markdown);

  const purifier = globalThis.DOMPurify;
  if (!purifier || typeof purifier.sanitize !== "function") {
    throw new Error("HTML sanitizer DOMPurify was not loaded.");
  }

  const clean = purifier.sanitize(html, {
    USE_PROFILES: { html: true },
  });

  const content = document.getElementById("content");
  content.innerHTML = clean;
}

async function loadReport(reportPath) {
  setStatus(`Loading: ${reportPath}`);

  try {
    const markdown = await fetchText(reportPath);
    await renderMarkdown(markdown);
    setStatus(`Loaded: ${reportPath}`);
  } catch (err) {
    console.error(err);
    setStatus(`Failed to load: ${reportPath}. ${err?.message || err}`, "error");

    const content = document.getElementById("content");
    content.innerHTML = "";
  }
}

function wireUi() {
  loadReport("report.md");
}

wireUi();
