"""Flask web UI for the Leben in Deutschland trainer."""

import json
import random
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, request, send_from_directory

from lid_trainer.questions import STATES, QuestionBank

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Leben in Deutschland Trainer</title>
<style>
  :root { --bg: #1a1a2e; --card: #16213e; --accent: #0f3460;
          --green: #4ecca3; --red: #e74c3c; --text: #eee;
          --dim: #888; --selected: #1a3a5c; --yellow: #f39c12; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: var(--bg);
         color: var(--text); min-height: 100vh;
         display: flex; flex-direction: column; align-items: center; }
  .container { max-width: 700px; width: 100%; padding: 20px; }
  h1 { text-align: center; margin: 20px 0; font-size: 1.5em; }
  .subtitle { text-align: center; color: var(--dim);
              margin-bottom: 20px; }
  .card { background: var(--card); border-radius: 12px;
          padding: 24px; margin: 16px 0; }
  .question-text { font-size: 1.1em; line-height: 1.5;
                    margin-bottom: 20px; }
  .option { display: block; width: 100%; padding: 14px 18px;
            margin: 8px 0; background: var(--accent);
            border: 2px solid transparent; border-radius: 8px;
            color: var(--text); font-size: 1em; cursor: pointer;
            text-align: left; transition: all 0.2s; }
  .option:hover:not(:disabled) { border-color: var(--green); }
  .option.selected { border-color: var(--green);
                      background: var(--selected); }
  .option:disabled { cursor: default; }
  .btn { padding: 12px 24px; border: none; border-radius: 8px;
         font-size: 1em; cursor: pointer; margin: 8px 4px;
         transition: all 0.2s; }
  .btn-primary { background: var(--green); color: #111; }
  .btn-primary:hover { opacity: 0.9; }
  .btn-primary:disabled { opacity: 0.4; cursor: default; }
  .btn-secondary { background: var(--accent); color: var(--text); }
  .btn-warn { background: var(--yellow); color: #111; }
  .progress-bar { height: 6px; background: var(--accent);
                   border-radius: 3px; margin: 10px 0; }
  .progress-fill { height: 100%; background: var(--green);
                    border-radius: 3px; transition: width 0.3s; }
  .score { text-align: center; font-size: 1.3em; margin: 10px 0; }
  .counter { color: var(--dim); font-size: 0.9em; }
  .image-note { color: var(--dim); font-style: italic;
                 font-size: 0.9em; margin-bottom: 10px; }
  .q-image { width: 100%; max-width: 500px; border-radius: 8px;
             margin: 0 auto 16px; display: block; }
  select { padding: 10px; border-radius: 8px;
           background: var(--accent); color: var(--text);
           border: 1px solid #333; font-size: 1em;
           width: 100%; margin: 8px 0; }
  .flex { display: flex; gap: 10px; justify-content: center;
          flex-wrap: wrap; }
  .result-card { text-align: center; padding: 40px; }
  .result-card .emoji { font-size: 3em; }
  .hidden { display: none; }
  .review-item { padding: 16px; margin: 8px 0; border-radius: 8px;
                  border-left: 4px solid; }
  .review-correct { border-color: var(--green);
                     background: rgba(78,204,163,0.08); }
  .review-wrong { border-color: var(--red);
                   background: rgba(231,76,60,0.08); }
  .review-q { font-weight: 600; margin-bottom: 8px; }
  .review-answer { font-size: 0.95em; margin: 4px 0; }
  .review-answer.yours-correct { color: var(--green); }
  .review-answer.yours-wrong { color: var(--red); }
  .review-answer.correct-was { color: var(--green); }
  .option.correct { background: #1b5e20; border-color: var(--green); }
  .option.wrong { background: #7f1d1d; border-color: var(--red); }
  .translation { background: var(--accent); border-radius: 8px;
    padding: 14px 18px; margin-top: 12px; font-size: 0.92em;
    color: var(--dim); line-height: 1.6; }
  .translation strong { color: var(--text); }
  .review-header { display: flex; justify-content: space-between;
                    align-items: center; margin-bottom: 16px; }
  .review-filter { display: flex; gap: 8px; }
  .review-filter button { padding: 6px 14px; border-radius: 6px;
    border: 1px solid #333; background: var(--accent);
    color: var(--text); cursor: pointer; font-size: 0.85em; }
  .review-filter button.active { background: var(--green);
    color: #111; border-color: var(--green); }
  .timer-warning { color: var(--yellow); }
  .timer-critical { color: var(--red); animation: pulse 1s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
  .time-info { color: var(--dim); font-size: 0.95em;
               margin-top: 8px; }
  .round-banner { text-align: center; padding: 12px;
    background: var(--accent); border-radius: 8px;
    margin-bottom: 12px; font-weight: 600; }
  .menu-grid { display: grid; gap: 10px;
    grid-template-columns: 1fr 1fr; margin-top: 16px; }
  .menu-grid .btn { width: 100%; }
  @media (max-width: 500px) {
    .menu-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">
  <h1>🇩🇪 Leben in Deutschland Trainer</h1>

  <!-- Setup Screen -->
  <div id="setup" class="card">
    <p class="subtitle">Wähle dein Bundesland und Modus</p>
    <label>Bundesland:</label>
    <select id="stateSelect"></select>
    <div class="menu-grid">
      <button class="btn btn-primary"
        onclick="startTimed('exam')">🎓 Exam (33)</button>
      <button class="btn btn-primary"
        onclick="startTimed('quick')">⚡ Quick 10</button>
      <button class="btn btn-warn"
        onclick="startLearn('general')">📖 Learn All General</button>
      <button class="btn btn-warn"
        onclick="startLearn('state')">📖 Learn State</button>
      <button class="btn btn-secondary" id="mistakesBtn"
        onclick="startLearn('mistakes')">🔁 Review Mistakes
        <span id="mistakeCount"></span></button>
      <button class="btn btn-secondary"
        onclick="clearMistakes()"
        style="font-size:0.85em">🗑 Clear Mistake Bank</button>
    </div>
  </div>

  <!-- Quiz Screen (timed exam / quick) -->
  <div id="quiz" class="hidden">
    <div class="counter">
      <span id="qCounter"></span>
      <span id="timerDisplay"
        style="float:right; font-weight:bold;">⏱ 60:00</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" id="progressBar"></div>
    </div>
    <div class="card">
      <div class="question-text" id="questionText"></div>
      <img id="questionImage" class="q-image hidden" alt="">
      <div id="optionsContainer"></div>
    </div>
    <div class="flex">
      <button class="btn btn-secondary"
        onclick="finishTimedQuiz()">Finish</button>
    </div>
  </div>

  <!-- Learn Screen (repeat wrong answers) -->
  <div id="learn" class="hidden">
    <div id="roundBanner" class="round-banner"></div>
    <div class="counter">
      <span id="learnCounter"></span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" id="learnProgress"></div>
    </div>
    <div class="card">
      <div class="question-text" id="learnQuestionText"></div>
      <img id="learnQuestionImage" class="q-image hidden" alt="">
      <div id="learnOptions"></div>
      <div id="learnFeedback" class="hidden"></div>
      <div id="learnTranslation" class="translation hidden"></div>
    </div>
    <div class="flex">
      <button class="btn btn-primary" id="learnSubmitBtn"
        onclick="learnSubmit()" disabled>Submit</button>
      <button class="btn btn-primary hidden" id="learnNextBtn"
        onclick="learnNext()">Next →</button>
      <button class="btn btn-secondary"
        onclick="finishLearn()">Stop Learning</button>
    </div>
  </div>

  <!-- Result Screen -->
  <div id="result" class="hidden">
    <div class="card result-card">
      <div class="emoji" id="resultEmoji"></div>
      <div class="score" id="resultScore"></div>
      <p id="resultText"
        style="margin:10px 0; color:var(--dim);"></p>
      <div class="flex" style="margin-top: 16px;">
        <button class="btn btn-primary"
          onclick="showSetup()">Back to Menu</button>
      </div>
    </div>
    <div class="review-header">
      <strong>Review</strong>
      <div class="review-filter">
        <button id="filterAll" class="active"
          onclick="filterReview('all')">All</button>
        <button id="filterWrong"
          onclick="filterReview('wrong')">Wrong only</button>
      </div>
    </div>
    <div id="reviewContainer"></div>
  </div>
</div>
"""

HTML_SCRIPT = """
<script>
const STATES = %STATES%;
const EXAM_SECONDS = 3600;
const EXAM_QUESTIONS = 33;

/* ── shared state ── */
let allResults = [];  // [{question, chosen, correct_answer}]

/* ── timed quiz state ── */
let questions = [];
let currentIdx = 0;
let userAnswers = [];
let timerInterval = null;
let timeRemaining = 0;
let totalTimeLimit = 0;

/* ── learn mode state ── */
let learnQueue = [];
let learnIdx = 0;
let learnSelectedIdx = -1;
let learnRound = 0;
let learnTotalOriginal = 0;
let learnWrongThisRound = [];
let learnResultsThisRound = [];
let learnSubmitted = false;
let learnCurrentMode = '';  // 'general', 'state', or 'mistakes'

/* ── populate state dropdown ── */
const sel = document.getElementById('stateSelect');
STATES.forEach(s => {
  const opt = document.createElement('option');
  opt.value = s; opt.textContent = s;
  if (s === '%DEFAULT_STATE%') opt.selected = true;
  sel.appendChild(opt);
});

/* ── helpers ── */
function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}
function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
function hideAll() {
  ['setup','quiz','learn','result'].forEach(
    id => document.getElementById(id).classList.add('hidden'));
}
function showSetup() {
  stopTimer();
  hideAll();
  document.getElementById('setup').classList.remove('hidden');
  updateMistakeCountUI();
}

/* ════════════════════════════════════════════
   MISTAKE BANK (localStorage)
   Bank format: { "state:id": correctStreak }
   correctStreak starts at 0 when added (wrong answer).
   Each correct answer in learn mode increments it.
   Removed when correctStreak reaches 3.
   ════════════════════════════════════════════ */
const BANK_KEY = 'lid_mistake_bank';

function getMistakeBank() {
  try {
    return JSON.parse(localStorage.getItem(BANK_KEY)) || {};
  } catch { return {}; }
}

function saveMistakeBank(bank) {
  localStorage.setItem(BANK_KEY, JSON.stringify(bank));
}

function mistakeKey(q) {
  return (q.state || '') + ':' + q.id;
}

function recordMistake(q) {
  const bank = getMistakeBank();
  const key = mistakeKey(q);
  // Reset streak to 0 on any wrong answer
  bank[key] = 0;
  saveMistakeBank(bank);
}

function recordCorrectInBank(q) {
  const bank = getMistakeBank();
  const key = mistakeKey(q);
  if (key in bank) {
    bank[key] = (bank[key] || 0) + 1;
    if (bank[key] >= 3) {
      delete bank[key];
    }
    saveMistakeBank(bank);
  }
}

function getMistakeKeys() {
  return Object.keys(getMistakeBank());
}

function clearMistakes() {
  if (confirm('Clear all saved mistakes? This cannot be undone.')) {
    localStorage.removeItem(BANK_KEY);
    updateMistakeCountUI();
  }
}

function updateMistakeCountUI() {
  const keys = getMistakeKeys();
  const el = document.getElementById('mistakeCount');
  const btn = document.getElementById('mistakesBtn');
  if (keys.length > 0) {
    el.textContent = '(' + keys.length + ')';
    btn.disabled = false;
  } else {
    el.textContent = '(0)';
    btn.disabled = true;
  }
}

// Update count on page load
updateMistakeCountUI();

/* ════════════════════════════════════════════
   TIMED QUIZ (Exam / Quick 10)
   ════════════════════════════════════════════ */
function startTimer(seconds) {
  timeRemaining = seconds; totalTimeLimit = seconds;
  updateTimerDisplay();
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeRemaining--;
    updateTimerDisplay();
    if (timeRemaining <= 0) {
      clearInterval(timerInterval); timerInterval = null;
      finishTimedQuiz();
    }
  }, 1000);
}
function stopTimer() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}
function updateTimerDisplay() {
  const el = document.getElementById('timerDisplay');
  el.textContent = '⏱ ' + formatTime(Math.max(0, timeRemaining));
  el.className = '';
  if (timeRemaining <= 60) el.className = 'timer-critical';
  else if (timeRemaining <= 300) el.className = 'timer-warning';
}

async function startTimed(mode) {
  const state = document.getElementById('stateSelect').value;
  const resp = await fetch(
    '/api/questions?mode=' + mode +
    '&state=' + encodeURIComponent(state));
  questions = await resp.json();
  currentIdx = 0;
  userAnswers = new Array(questions.length).fill(-1);
  allResults = [];
  hideAll();
  document.getElementById('quiz').classList.remove('hidden');
  const perQ = EXAM_SECONDS / EXAM_QUESTIONS;
  startTimer(Math.round(perQ * questions.length));
  showTimedQuestion();
}

function showTimedQuestion() {
  if (currentIdx >= questions.length) { finishTimedQuiz(); return; }
  const q = questions[currentIdx];
  document.getElementById('qCounter').textContent =
    'Question ' + (currentIdx+1) + ' / ' + questions.length;
  document.getElementById('progressBar').style.width =
    ((currentIdx / questions.length) * 100) + '%';
  document.getElementById('questionText').textContent = q.question;
  const qImg = document.getElementById('questionImage');
  if (q.image) {
    qImg.src = '/images/' + q.image;
    qImg.classList.remove('hidden');
  } else {
    qImg.classList.add('hidden');
  }
  const c = document.getElementById('optionsContainer');
  c.innerHTML = '';
  q.options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'option';
    btn.textContent = (i+1) + '. ' + opt;
    btn.onclick = () => timedSelect(i);
    c.appendChild(btn);
  });
}

function timedSelect(idx) {
  // Record answer and immediately advance
  userAnswers[currentIdx] = idx;
  // Brief highlight then move on
  const btns = document.querySelectorAll('#optionsContainer .option');
  btns.forEach(b => b.classList.remove('selected'));
  btns[idx].classList.add('selected');
  btns.forEach(b => { b.disabled = true; });
  setTimeout(() => { currentIdx++; showTimedQuestion(); }, 200);
}

function submitAndNext() {
  // Not used in timed mode anymore, kept for safety
  currentIdx++; showTimedQuestion();
}

function finishTimedQuiz() {
  stopTimer();
  allResults = [];
  for (let i = 0; i < questions.length; i++) {
    if (userAnswers[i] !== -1) {
      allResults.push({
        question: questions[i],
        chosen: userAnswers[i],
        correct_answer: questions[i].correct_answer
      });
    }
  }
  const timeUsed = totalTimeLimit - Math.max(0, timeRemaining);
  showResults(
    'Time: ' + formatTime(timeUsed) +
    ' / ' + formatTime(totalTimeLimit));
}

/* ════════════════════════════════════════════
   LEARN MODE (repeat wrong answers)
   ════════════════════════════════════════════ */
async function startLearn(mode) {
  const state = document.getElementById('stateSelect').value;
  let data;
  if (mode === 'mistakes') {
    const keys = getMistakeKeys();
    if (keys.length === 0) {
      alert('No mistakes saved yet. Practice some questions first!');
      return;
    }
    const resp = await fetch('/api/questions?mode=mistakes&keys=' +
      encodeURIComponent(JSON.stringify(keys)));
    data = await resp.json();
  } else {
    const resp = await fetch(
      '/api/questions?mode=' + mode +
      '&state=' + encodeURIComponent(state));
    data = await resp.json();
  }
  if (!data.length) {
    alert('No questions available for this selection.');
    return;
  }
  learnCurrentMode = mode;
  learnQueue = shuffle(data);
  learnIdx = 0; learnSelectedIdx = -1;
  learnRound = 1;
  learnTotalOriginal = learnQueue.length;
  learnWrongThisRound = [];
  learnResultsThisRound = [];
  allResults = [];
  hideAll();
  document.getElementById('learn').classList.remove('hidden');
  updateRoundBanner();
  showLearnQuestion();
}

function updateRoundBanner() {
  document.getElementById('roundBanner').textContent =
    'Round ' + learnRound + ' — ' + learnQueue.length +
    ' question' + (learnQueue.length !== 1 ? 's' : '') +
    ' (of ' + learnTotalOriginal + ' total)';
}

function showLearnQuestion() {
  if (learnIdx >= learnQueue.length) {
    endLearnRound(); return;
  }
  const q = learnQueue[learnIdx];
  learnSelectedIdx = -1;
  learnSubmitted = false;
  document.getElementById('learnSubmitBtn').disabled = true;
  document.getElementById('learnSubmitBtn').classList.remove('hidden');
  document.getElementById('learnNextBtn').classList.add('hidden');
  document.getElementById('learnFeedback').classList.add('hidden');
  document.getElementById('learnTranslation').classList.add('hidden');
  document.getElementById('learnCounter').textContent =
    'Question ' + (learnIdx+1) + ' / ' + learnQueue.length;
  document.getElementById('learnProgress').style.width =
    ((learnIdx / learnQueue.length) * 100) + '%';
  document.getElementById('learnQuestionText').textContent =
    q.question;
  const lImg = document.getElementById('learnQuestionImage');
  if (q.image) {
    lImg.src = '/images/' + q.image;
    lImg.classList.remove('hidden');
  } else {
    lImg.classList.add('hidden');
  }
  const c = document.getElementById('learnOptions');
  c.innerHTML = '';
  q.options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'option';
    btn.textContent = (i+1) + '. ' + opt;
    btn.onclick = () => {
      if (learnSubmitted) return;
      document.querySelectorAll('#learnOptions .option')
        .forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      learnSelectedIdx = i;
      document.getElementById('learnSubmitBtn').disabled = false;
    };
    c.appendChild(btn);
  });
}

function learnSubmit() {
  if (learnSelectedIdx === -1 || learnSubmitted) return;
  learnSubmitted = true;
  const q = learnQueue[learnIdx];
  const chosen = learnSelectedIdx;
  const correct = q.correct_answer;
  const isCorrect = chosen === correct;

  // Show correct/wrong on options
  const btns = document.querySelectorAll('#learnOptions .option');
  btns.forEach((btn, i) => {
    btn.disabled = true;
    if (i === correct) btn.classList.add('correct');
    if (i === chosen && !isCorrect) btn.classList.add('wrong');
  });

  // Show feedback text
  const fb = document.getElementById('learnFeedback');
  fb.innerHTML = isCorrect
    ? '<span style="color:var(--green);font-weight:600;">✓ Correct!</span>'
    : '<span style="color:var(--red);font-weight:600;">✗ Wrong</span>';
  fb.classList.remove('hidden');

  // Show English translation
  const tr = document.getElementById('learnTranslation');
  const opts_en = q.options_en || q.options;
  let html = '<strong>🇬🇧 ' + (q.question_en || q.question) + '</strong><br>';
  q.options.forEach((opt, i) => {
    const en = opts_en[i] || opt;
    const marker = i === correct ? ' ✓' : '';
    const style = i === correct
      ? 'color:var(--green)'
      : (i === chosen && !isCorrect ? 'color:var(--red)' : '');
    html += '<span style="' + style + '">' +
      (i+1) + '. ' + en + marker + '</span><br>';
  });
  tr.innerHTML = html;
  tr.classList.remove('hidden');

  // Record
  learnResultsThisRound.push({
    question: q, chosen, correct_answer: correct });
  allResults.push({
    question: q, chosen, correct_answer: correct });
  if (!isCorrect) {
    learnWrongThisRound.push(q);
    // Any learn mode: wrong answer goes into mistake bank
    recordMistake(q);
  } else if (learnCurrentMode === 'mistakes') {
    // Only in Review Mistakes mode: correct answers count toward removal
    recordCorrectInBank(q);
  }

  // Swap buttons
  document.getElementById('learnSubmitBtn').classList.add('hidden');
  document.getElementById('learnNextBtn').classList.remove('hidden');
}

function learnNext() {
  learnIdx++;
  showLearnQuestion();
}

function learnSubmitAndNext() { learnSubmit(); }

function endLearnRound() {
  const wrong = learnWrongThisRound;
  const total = learnResultsThisRound.length;
  const correct = total - wrong.length;

  if (wrong.length === 0) {
    // All correct this round — done!
    showResults('All questions mastered after ' +
      learnRound + ' round' + (learnRound !== 1 ? 's' : '') + '!');
    return;
  }

  // Show round summary, then start next round
  const msg = 'Round ' + learnRound + ': ' + correct + '/' + total +
    ' correct. ' + wrong.length + ' wrong — repeating them now.';
  document.getElementById('roundBanner').textContent = msg;

  // Brief pause then start next round
  learnRound++;
  learnQueue = shuffle([...wrong]);
  learnIdx = 0;
  learnWrongThisRound = [];
  learnResultsThisRound = [];
  updateRoundBanner();
  showLearnQuestion();
}

function finishLearn() {
  showResults('Stopped after round ' + learnRound);
}

/* ════════════════════════════════════════════
   RESULTS & REVIEW
   ════════════════════════════════════════════ */
function showResults(extraInfo) {
  hideAll();
  document.getElementById('result').classList.remove('hidden');
  updateMistakeCountUI();

  // Deduplicate: for learn mode a question can appear multiple times.
  // Show the LAST attempt for each question in the review.
  const seen = new Map();
  for (const r of allResults) {
    const key = (r.question.state || '') + ':' + r.question.id;
    seen.set(key, r);
  }
  const dedupedResults = [...seen.values()];

  let correctCount = 0;
  for (const r of dedupedResults) {
    if (r.chosen === r.correct_answer) correctCount++;
  }
  const total = dedupedResults.length;
  const pct = total > 0 ? Math.round((correctCount/total)*100) : 0;
  const passed = pct >= 50;

  document.getElementById('resultEmoji').textContent =
    passed ? '🎉' : '📚';
  document.getElementById('resultScore').textContent =
    correctCount + ' / ' + total + ' (' + pct + '%)';
  let msg = passed
    ? 'Bestanden! Gut gemacht!'
    : 'Noch nicht bestanden. Weiter üben!';
  if (extraInfo) {
    msg += '<div class="time-info">' + extraInfo + '</div>';
  }
  document.getElementById('resultText').innerHTML = msg;

  // Store for review filtering
  window._reviewResults = dedupedResults;
  buildReview('all');
}

function buildReview(filter) {
  const results = window._reviewResults || [];
  const container = document.getElementById('reviewContainer');
  container.innerHTML = '';

  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    const q = r.question;
    const chosen = r.chosen;
    const isCorrect = chosen === r.correct_answer;
    if (filter === 'wrong' && isCorrect) continue;

    const div = document.createElement('div');
    div.className = 'review-item ' +
      (isCorrect ? 'review-correct' : 'review-wrong');
    const icon = isCorrect ? '✓' : '✗';
    const tag = q.state ? ' (' + q.state + ')' : '';
    let html = '<div class="review-q">' + icon + ' Q' +
      q.id + tag + ': ' + q.question + '</div>';
    if (q.image) {
      html += '<img class="q-image" src="/images/' +
        q.image + '" alt="">';
    }
    if (isCorrect) {
      html += '<div class="review-answer yours-correct">' +
        'Your answer: ' + q.options[chosen] + '</div>';
    } else {
      html += '<div class="review-answer yours-wrong">' +
        'Your answer: ' + q.options[chosen] + '</div>';
      html += '<div class="review-answer correct-was">' +
        'Correct: ' + q.options[r.correct_answer] + '</div>';
    }
    div.innerHTML = html;
    container.appendChild(div);
  }
  if (container.children.length === 0) {
    container.innerHTML =
      '<div class="card" style="text-align:center;' +
      'color:var(--green);">All answers correct! 🎉</div>';
  }
}

function filterReview(filter) {
  document.getElementById('filterAll').classList.toggle(
    'active', filter === 'all');
  document.getElementById('filterWrong').classList.toggle(
    'active', filter === 'wrong');
  buildReview(filter);
}
</script>
</body></html>
"""


def create_app(bank: QuestionBank, default_state: str = "Berlin") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = "lid-trainer-secret"

    images_dir = Path(__file__).parent / "data" / "images"

    @app.route("/")
    def index() -> str:
        """Serve the main page."""
        html = HTML_TEMPLATE + HTML_SCRIPT
        html = html.replace("%STATES%", json.dumps(STATES))
        html = html.replace("%DEFAULT_STATE%", default_state)
        return html

    @app.route("/images/<path:filename>")
    def serve_image(filename: str) -> tuple:
        """Serve question images."""
        return send_from_directory(str(images_dir), filename)

    @app.route("/api/questions")
    def api_questions() -> tuple:
        """Return questions based on mode and state."""
        mode = request.args.get("mode", "exam")
        state = request.args.get("state", default_state)

        if mode == "exam":
            qs = bank.exam_simulation(state)
        elif mode == "general":
            qs = bank.general_questions()
            random.shuffle(qs)
        elif mode == "state":
            qs = bank.state_questions(state)
        elif mode == "quick":
            all_qs = bank.general_questions()
            all_qs += bank.state_questions(state)
            qs = random.sample(all_qs, min(10, len(all_qs)))
        elif mode == "mistakes":
            keys_raw = request.args.get("keys", "[]")
            try:
                keys = json.loads(keys_raw)
            except (json.JSONDecodeError, TypeError):
                keys = []
            key_set = set(keys)
            qs = [q for q in bank.all_questions if ((q.state or "") + ":" + str(q.id)) in key_set]
        else:
            qs = []

        data = [
            {
                "id": q.id,
                "question": q.question,
                "question_en": q.question_en,
                "options": q.options,
                "options_en": q.options_en or q.options,
                "correct_answer": q.correct_answer,
                "has_image": q.has_image,
                "image": q.image,
                "state": q.state,
            }
            for q in qs
        ]
        return jsonify(data)

    return app


def run_web(bank: QuestionBank, state: str, port: int = 5050) -> None:
    """Start the web server and open browser."""
    app = create_app(bank, default_state=state)
    url = f"http://127.0.0.1:{port}"
    Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"\n  🌐 Web UI running at {url}")
    print("  Press Ctrl+C to stop\n")
    app.run(host="127.0.0.1", port=port, debug=False)
