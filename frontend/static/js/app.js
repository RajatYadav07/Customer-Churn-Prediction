// Retento.ai — Enterprise Frontend JavaScript

let gaugeChart = null;

// ── TAB NAVIGATION ──────────────────────────────────────────────
function showTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if (el) el.classList.add('active');
  if (name === 'metrics') loadMetrics();
}

// ── COLLECT FORM DATA ────────────────────────────────────────────
function getFormData() {
  const ids = [
    'tenure', 'MonthlyCharges', 'TotalCharges', 'gender',
    'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService',
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'Contract', 'PaperlessBilling', 'PaymentMethod'
  ];
  const data = {};
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) data[id] = el.value;
  });
  return data;
}

// ── PREDICT ──────────────────────────────────────────────────────
async function runPrediction() {
  const btn = document.getElementById('predict-btn');
  btn.disabled = true;
  btn.innerHTML = '<span style="opacity:0.6">⏳</span>&nbsp; Predicting...';

  const data = getFormData();

  try {
    const [predRes, recRes] = await Promise.all([
      fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }),
      fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }),
    ]);

    const pred = await predRes.json();
    const rec  = await recRes.json();

    if (pred.error) throw new Error(pred.error);
    showResults(pred, rec);

  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🔮 &nbsp;Predict Churn Risk';
  }
}

// ── SHOW RESULTS ─────────────────────────────────────────────────
function showResults(pred, rec) {
  document.getElementById('empty-state').style.display  = 'none';
  document.getElementById('result-content').style.display = 'block';

  const prob = pred.churn_probability;
  const risk = pred.risk_level;

  // Animated number
  animateNumber('prob-num', prob, '%');

  // Risk badge
  const badge = document.getElementById('risk-badge');
  badge.textContent = risk;
  badge.className = 'risk-badge ' + risk.toLowerCase();

  // Progress bar
  const bar = document.getElementById('risk-bar');
  setTimeout(() => { bar.style.width = Math.min(prob, 100) + '%'; }, 100);
  // Color the bar
  if (risk === 'High') bar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
  else if (risk === 'Medium') bar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
  else bar.style.background = 'linear-gradient(90deg, #10b981, #059669)';

  drawGauge(prob, risk);
  renderRecs(rec.recommendations || []);
}

// ── ANIMATED NUMBER ──────────────────────────────────────────────
function animateNumber(id, target, suffix = '') {
  const el = document.getElementById(id);
  const start = 0;
  const duration = 900;
  const startTime = performance.now();

  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = start + (target - start) * eased;
    el.textContent = current.toFixed(1) + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ── GAUGE CHART ──────────────────────────────────────────────────
function drawGauge(prob, risk) {
  const ctx = document.getElementById('gaugeChart').getContext('2d');
  if (gaugeChart) gaugeChart.destroy();

  const colorMap = {
    High:   ['#ff4d4d', '#e60000'], // Bright Red
    Medium: ['#f59e0b', '#d97706'], // Amber
    Low:    ['#00ff88', '#0dbd8b']  // Neon Mint
  };
  const [c1, c2] = colorMap[risk] || ['#6366f1', '#4f46e5'];
  const remaining = Math.max(0, 100 - prob);

  gaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [prob, remaining],
        backgroundColor: [c1, 'rgba(255,255,255,0.05)'],
        borderWidth: 0,
        hoverOffset: 0,
      }]
    },
    options: {
      cutout: '75%',
      rotation: -90,
      circumference: 360,
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      animation: { duration: 900, easing: 'easeOutQuart' },
    }
  });
}

// ── RECOMMENDATIONS ──────────────────────────────────────────────
const REC_ICONS = {
  discount: '💰',
  contract: '📋',
  internet: '🌐',
  security: '🔒',
  support:  '🎧',
  loyalty:  '🎁',
  reward:   '⭐',
  default:  '✨'
};

function renderRecs(recs) {
  const container = document.getElementById('recs-list');
  if (!recs.length) {
    container.innerHTML = '<p style="color:var(--text-muted); font-size:13px; padding:12px 0;">No specific recommendations.</p>';
    return;
  }
  container.innerHTML = recs.map((r, i) => `
    <div class="rec-item" style="animation-delay:${i * 0.1}s">
      <div class="rec-icon">${REC_ICONS[r.icon] || '✨'}</div>
      <div>
        <div class="rec-title">${r.title}</div>
        <div class="rec-detail">${r.detail}</div>
      </div>
    </div>
  `).join('');
}

// ── TOAST NOTIFICATION ───────────────────────────────────────────
function showToast(msg, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  t.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: ${type === 'error' ? '#ef4444' : '#10b981'};
    color: #fff; padding: 12px 20px; border-radius: 10px;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    animation: slideIn 0.3s ease;
  `;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ── METRICS ──────────────────────────────────────────────────────
async function loadMetrics() {
  const container = document.getElementById('metrics-content');
  if (container.dataset.loaded) return;

  try {
    const res = await fetch('/api/metrics');
    const data = await res.json();
    renderMetrics(data);
    container.dataset.loaded = 'true';
  } catch (e) {
    container.innerHTML = `<div class="loading-text">⚠️ Failed to load metrics. Is the server running?</div>`;
  }
}

function renderMetrics(data) {
  const results = data.model_results;
  const best    = data.best_model;
  const featImp = data.feature_importance;
  const cm      = data.confusion_matrix;
  const bestData = results[best];

  // ── STAT CHIPS ──
  const summaryHTML = `
    <div class="stat-chips">
      <div class="stat-chip primary">
        <div class="stat-chip-label">Best Model</div>
        <div class="stat-chip-val primary" style="font-size:14px; margin-top:2px">${best}</div>
      </div>
      <div class="stat-chip success">
        <div class="stat-chip-label">ROC-AUC Score</div>
        <div class="stat-chip-val success">${(bestData.roc_auc * 100).toFixed(1)}%</div>
      </div>
      <div class="stat-chip cyan">
        <div class="stat-chip-label">Accuracy</div>
        <div class="stat-chip-val cyan">${(bestData.accuracy * 100).toFixed(1)}%</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px;">
      <div class="stat-chip">
        <div class="stat-chip-label">Precision</div>
        <div class="stat-chip-val" style="font-size:20px; color:var(--text);">${(bestData.precision * 100).toFixed(1)}%</div>
      </div>
      <div class="stat-chip">
        <div class="stat-chip-label">Recall</div>
        <div class="stat-chip-val" style="font-size:20px; color:var(--text);">${(bestData.recall * 100).toFixed(1)}%</div>
      </div>
      <div class="stat-chip">
        <div class="stat-chip-label">F1 Score</div>
        <div class="stat-chip-val" style="font-size:20px; color:var(--text);">${(bestData.f1_score * 100).toFixed(1)}%</div>
      </div>
    </div>
  `;

  // ── MODEL TABLE ──
  const tableRows = Object.entries(results).map(([name, m]) => {
    const isBest = name === best;
    return `<tr class="${isBest ? 'best-row' : ''}">
      <td>${name}${isBest ? ' <span class="tag">★ Best</span>' : ''}</td>
      <td>${(m.accuracy  * 100).toFixed(2)}%</td>
      <td>${(m.roc_auc   * 100).toFixed(2)}%</td>
      <td>${(m.precision * 100).toFixed(2)}%</td>
      <td>${(m.recall    * 100).toFixed(2)}%</td>
      <td>${(m.f1_score  * 100).toFixed(2)}%</td>
    </tr>`;
  }).join('');

  const tableHTML = `
    <div class="card" style="margin-bottom:20px">
      <div class="card-title"><span class="icon">🏆</span> Model Comparison</div>
      <div style="overflow-x:auto">
        <table class="model-table">
          <thead>
            <tr>
              <th>Model</th><th>Accuracy</th><th>ROC-AUC</th>
              <th>Precision</th><th>Recall</th><th>F1</th>
            </tr>
          </thead>
          <tbody>${tableRows}</tbody>
        </table>
      </div>
    </div>
  `;

  // ── CHARTS ──
  const chartsHTML = `
    <div class="charts-row">
      <div class="card">
        <div class="card-title"><span class="icon">📈</span> Feature Importance (Top 10)</div>
        <div class="chart-wrap">
          <canvas id="featChart" role="img" aria-label="Feature importance bar chart"></canvas>
        </div>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">🔢</span> Confusion Matrix</div>
        <div class="chart-wrap">
          <canvas id="cmChart" role="img" aria-label="Confusion matrix chart"></canvas>
        </div>
      </div>
    </div>
  `;

  document.getElementById('metrics-content').innerHTML = summaryHTML + tableHTML + chartsHTML;

  // ── FEATURE IMPORTANCE CHART ──
  const top10 = Object.entries(featImp).slice(0, 10);
  const featColors = top10.map((_, i) => {
    const hue = Math.round(240 + i * 12);
    return `hsl(${hue}, 80%, 65%)`;
  });

  new Chart(document.getElementById('featChart'), {
    type: 'bar',
    data: {
      labels: top10.map(([k]) => k),
      datasets: [{
        label: 'Importance Score',
        data: top10.map(([, v]) => parseFloat(v.toFixed(4))),
        backgroundColor: '#00ff88',
        borderRadius: 5,
        borderWidth: 0,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15,21,38,0.9)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#f0f4ff',
          bodyColor: '#8892b0',
          padding: 10,
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#8892b0', font: { size: 11 } },
        },
        y: {
          grid: { display: false },
          ticks: { color: '#8892b0', font: { size: 11 } },
        }
      }
    }
  });

  // ── CONFUSION MATRIX CHART ──
  const tn = cm[0][0], fp = cm[0][1], fn = cm[1][0], tp = cm[1][1];
  new Chart(document.getElementById('cmChart'), {
    type: 'bar',
    data: {
      labels: ['True Negative', 'False Positive', 'False Negative', 'True Positive'],
      datasets: [{
        label: 'Count',
        data: [tn, fp, fn, tp],
        backgroundColor: [
          'rgba(0, 255, 136, 0.7)',
          'rgba(255, 77, 77, 0.7)',
          'rgba(245, 158, 11, 0.7)',
          'rgba(0, 210, 255, 0.7)'
        ],
        borderRadius: 6,
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15,21,38,0.9)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#f0f4ff',
          bodyColor: '#8892b0',
          padding: 10,
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#8892b0', font: { size: 11 } },
        },
        x: {
          grid: { display: false },
          ticks: { color: '#8892b0', font: { size: 11 } },
        }
      }
    }
  });
}
