/**
 * Bedtime Story Generator — frontend
 * Landing → form → API → chunked reader with read-aloud word highlighting
 */

const RANDOM_OBJECTS = [
  "a red balloon", "a friendly owl", "a warm blanket", "a shiny star",
  "a little boat", "a magic key", "a soft teddy bear", "a rainbow kite",
  "a glowing lantern", "a garden snail", "a wooden flute", "a blue marble",
  "a cozy scarf", "a paper airplane", "a sleepy puppy", "a golden acorn",
  "a music box", "a feather pillow", "a tiny castle", "a bubble wand",
];

const SENTENCES_PER_CHUNK = 2;

const landingView = document.getElementById("landing-view");
const setupView = document.getElementById("setup-view");
const loadingView = document.getElementById("loading-view");
const readerView = document.getElementById("reader-view");
const storyForm = document.getElementById("story-form");
const formError = document.getElementById("form-error");
const ageSlider = document.getElementById("age");
const ageValue = document.getElementById("age-value");
const randomBtn = document.getElementById("random-btn");
const createBtn = document.getElementById("create-btn");
const setupBackBtn = document.getElementById("setup-back-btn");
const sampleCardsEl = document.getElementById("sample-cards");
const backBtn = document.getElementById("back-btn");
const storyChunkEl = document.getElementById("story-chunk");
const prevChunkBtn = document.getElementById("prev-chunk");
const nextChunkBtn = document.getElementById("next-chunk");
const playBtn = document.getElementById("play-btn");
const chunkIndicator = document.getElementById("chunk-indicator");
const judgeBadge = document.getElementById("judge-badge");

const allViews = [landingView, setupView, loadingView, readerView];

let chunks = [];
let currentChunkIndex = 0;
let speechUtterance = null;
let isPlaying = false;
let readerReturnView = landingView;
let sampleStories = [];

// --- Views ---

function showView(view) {
  allViews.forEach((el) => {
    el.classList.toggle("active", el === view);
    el.hidden = el !== view;
  });
}

// --- Landing & samples ---

async function loadSampleStories() {
  try {
    const res = await fetch("/static/data/sample_stories.json");
    sampleStories = await res.json();
    renderSampleCards();
  } catch {
    sampleCardsEl.innerHTML =
      '<p class="samples-intro">Sample stories could not be loaded.</p>';
  }
}

function renderSampleCards() {
  sampleCardsEl.innerHTML = "";

  sampleStories.forEach((sample) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sample-card";
    btn.innerHTML = `
      <p class="sample-card-title">${escapeHtml(sample.title)}</p>
      <p class="sample-card-teaser">${escapeHtml(sample.teaser)}</p>
      <div class="sample-card-meta">
        <span class="sample-tag">Age ${sample.age}</span>
        <span class="sample-tag">${escapeHtml(sample.length)}</span>
        <span class="sample-tag">Sample</span>
      </div>
    `;
    btn.addEventListener("click", () => openSampleStory(sample));
    sampleCardsEl.appendChild(btn);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function openSampleStory(sample) {
  readerReturnView = landingView;
  openReader(sample.story, { isSample: true, title: sample.title });
}

createBtn.addEventListener("click", () => showView(setupView));
setupBackBtn.addEventListener("click", () => showView(landingView));

loadSampleStories();

// --- Form helpers ---

ageSlider.addEventListener("input", () => {
  ageValue.textContent = ageSlider.value;
});

function pickRandomObjects(count = 3) {
  const pool = [...RANDOM_OBJECTS];
  const picked = [];
  for (let i = 0; i < count && pool.length; i++) {
    const idx = Math.floor(Math.random() * pool.length);
    picked.push(pool.splice(idx, 1)[0]);
  }
  return picked;
}

randomBtn.addEventListener("click", () => {
  const [a, b, c] = pickRandomObjects();
  document.getElementById("object1").value = a;
  document.getElementById("object2").value = b;
  document.getElementById("object3").value = c;
});

function showError(msg) {
  formError.textContent = msg;
  formError.hidden = !msg;
}

// --- Story parsing ---

function splitIntoSentences(text) {
  const cleaned = text.trim().replace(/\n+/g, " ");
  const parts = cleaned.match(/[^.!?]+[.!?]+|[^.!?]+$/g);
  return parts ? parts.map((s) => s.trim()).filter(Boolean) : [cleaned];
}

function groupSentences(sentences, perChunk = SENTENCES_PER_CHUNK) {
  const groups = [];
  for (let i = 0; i < sentences.length; i += perChunk) {
    groups.push(sentences.slice(i, i + perChunk).join(" "));
  }
  return groups;
}

function tokenizeWords(text) {
  const tokens = [];
  const regex = /\S+/g;
  let match;
  while ((match = regex.exec(text)) !== null) {
    tokens.push({
      word: match[0],
      start: match.index,
      end: match.index + match[0].length,
    });
  }
  return tokens;
}

function renderChunkWords(text) {
  storyChunkEl.innerHTML = "";
  const tokens = tokenizeWords(text);
  tokens.forEach((t, i) => {
    const span = document.createElement("span");
    span.className = "word";
    span.dataset.index = String(i);
    span.textContent = t.word;
    storyChunkEl.appendChild(span);
    if (i < tokens.length - 1) {
      storyChunkEl.appendChild(document.createTextNode(" "));
    }
  });
  return tokens;
}

// --- Speech + highlighting ---

function stopSpeech() {
  window.speechSynthesis.cancel();
  speechUtterance = null;
  isPlaying = false;
  playBtn.classList.remove("playing");
  playBtn.querySelector(".play-icon").textContent = "▶";
  playBtn.querySelector(".play-label").textContent = "Read aloud";
  storyChunkEl.querySelectorAll(".word").forEach((w) => {
    w.classList.remove("active", "read");
  });
}

function highlightWordAtCharIndex(charIndex, tokens) {
  const wordEls = storyChunkEl.querySelectorAll(".word");
  wordEls.forEach((el) => el.classList.remove("active"));

  let activeIdx = 0;
  for (let i = 0; i < tokens.length; i++) {
    if (charIndex >= tokens[i].start) activeIdx = i;
  }

  wordEls.forEach((el, i) => {
    if (i < activeIdx) el.classList.add("read");
    else el.classList.remove("read");
  });

  const active = wordEls[activeIdx];
  if (active) {
    active.classList.add("active");
    active.classList.remove("read");
  }
}

function speakCurrentChunk() {
  if (!chunks.length) return;

  const text = chunks[currentChunkIndex];
  const tokens = tokenizeWords(text);

  stopSpeech();
  renderChunkWords(text);

  if (!window.speechSynthesis) {
    return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.88;
  utterance.pitch = 1.05;

  utterance.onboundary = (event) => {
    if (event.name === "word") {
      highlightWordAtCharIndex(event.charIndex, tokens);
    }
  };

  utterance.onend = () => {
    storyChunkEl.querySelectorAll(".word").forEach((w) => {
      w.classList.remove("active");
      w.classList.add("read");
    });
    isPlaying = false;
    playBtn.classList.remove("playing");
    playBtn.querySelector(".play-icon").textContent = "▶";
    playBtn.querySelector(".play-label").textContent = "Read again";
  };

  utterance.onerror = () => stopSpeech();

  speechUtterance = utterance;
  isPlaying = true;
  playBtn.classList.add("playing");
  playBtn.querySelector(".play-icon").textContent = "⏸";
  playBtn.querySelector(".play-label").textContent = "Pause";

  window.speechSynthesis.speak(utterance);
}

playBtn.addEventListener("click", () => {
  if (isPlaying) {
    stopSpeech();
  } else {
    speakCurrentChunk();
  }
});

// --- Chunk navigation ---

function updateChunkUI() {
  if (!chunks.length) return;

  stopSpeech();
  renderChunkWords(chunks[currentChunkIndex]);

  prevChunkBtn.disabled = currentChunkIndex === 0;
  nextChunkBtn.disabled = currentChunkIndex >= chunks.length - 1;

  chunkIndicator.textContent = `Passage ${currentChunkIndex + 1} of ${chunks.length}`;
}

prevChunkBtn.addEventListener("click", () => {
  if (currentChunkIndex > 0) {
    currentChunkIndex--;
    updateChunkUI();
  }
});

nextChunkBtn.addEventListener("click", () => {
  if (currentChunkIndex < chunks.length - 1) {
    currentChunkIndex++;
    updateChunkUI();
  }
});

// --- Load story into reader ---

function openReader(storyText, meta = {}) {
  const sentences = splitIntoSentences(storyText);
  chunks = groupSentences(sentences, SENTENCES_PER_CHUNK);
  currentChunkIndex = 0;

  if (meta.isSample) {
    judgeBadge.textContent = "Sample story";
    judgeBadge.className = "judge-badge sample";
  } else if (meta.passed) {
    judgeBadge.textContent = "✓ Approved for bedtime";
    judgeBadge.className = "judge-badge passed";
  } else {
    judgeBadge.textContent = "Draft (review with a parent)";
    judgeBadge.className = "judge-badge failed";
  }
  judgeBadge.hidden = false;

  updateChunkUI();
  showView(readerView);
}

backBtn.addEventListener("click", () => {
  stopSpeech();
  showView(readerReturnView);
});

// --- API ---

storyForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  showError("");

  const payload = {
    object1: document.getElementById("object1").value,
    object2: document.getElementById("object2").value,
    object3: document.getElementById("object3").value,
    age: parseInt(ageSlider.value, 10),
    length: document.querySelector('input[name="length"]:checked').value,
  };

  showView(loadingView);

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showView(setupView);
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    readerReturnView = setupView;
    openReader(data.story, { passed: data.passed, attempts: data.attempts });
  } catch {
    showView(setupView);
    showError("Could not reach the server. Is the app running?");
  }
});

window.addEventListener("beforeunload", stopSpeech);
