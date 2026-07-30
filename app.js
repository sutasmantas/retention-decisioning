const viewNames = {
  overview: "Retention overview",
  accounts: "Scored accounts",
  policy: "Decision policy",
  monitoring: "Model monitoring"
};

const state = {
  summary: null,
  accounts: [],
  monitoring: null,
  curve: [],
  activeAccount: null
};

const byId = id => document.getElementById(id);
const pages = [...document.querySelectorAll(".page")];
const navItems = [...document.querySelectorAll(".nav-item[data-view]")];
const drawer = byId("account-drawer");
const drawerBackdrop = byId("drawer-backdrop");
const modal = byId("score-modal");
const modalBackdrop = byId("modal-backdrop");
const toast = byId("toast");
const slider = byId("threshold-slider");
const capacitySlider = byId("capacity-slider");

const escapeHtml = value => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const percentage = value => `${Math.round(Number(value) * 100)}%`;
const signedPercentage = value => {
  const number = Math.round(Number(value) * 100);
  return `${number > 0 ? "+" : ""}${number}%`;
};
const decimal = value => Number(value).toFixed(2);
const money = value => {
  const number = Number(value);
  if (Math.abs(number) >= 1_000_000) return `€${(number / 1_000_000).toFixed(2)}M`;
  if (Math.abs(number) >= 1_000) return `€${Math.round(number / 1_000)}K`;
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  }).format(number);
};

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

function showView(name) {
  pages.forEach(page => page.classList.toggle("active", page.id === `view-${name}`));
  navItems.forEach(item => item.classList.toggle("active", item.dataset.view === name));
  byId("page-title").textContent = viewNames[name];
  if (window.location.hash !== `#${name}`) {
    window.history.replaceState(null, "", `#${name}`);
  }
  window.scrollTo(0, 0);
}

function openDrawer() {
  drawer.classList.add("open");
  drawerBackdrop.classList.add("open");
}

function closeDrawer() {
  drawer.classList.remove("open");
  drawerBackdrop.classList.remove("open");
}

function openModal() {
  modal.classList.add("open");
  modalBackdrop.classList.add("open");
  byId("score-result").classList.remove("visible");
}

function closeModal() {
  modal.classList.remove("open");
  modalBackdrop.classList.remove("open");
}

function showToast(title, copy, isError = false) {
  byId("toast-title").textContent = title;
  byId("toast-copy").textContent = copy;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

function riskClass(risk) {
  if (risk >= 0.75) return "high";
  if (risk >= 0.55) return "medium";
  return "low";
}

function overviewRow(account) {
  return `<button class="account-row" data-account-id="${escapeHtml(account.account_id)}">
    <span class="account-name"><i class="account-logo coral">${escapeHtml(account.account_name[0])}</i><span><b>${escapeHtml(account.account_name)}</b><small>${escapeHtml(account.segment)} · ${money(account.mrr)} MRR</small></span></span>
    <span><b class="uplift-value">${signedPercentage(account.uplift)}</b><small>estimated uplift</small></span>
    <span><b>${money(account.expected_net_value)}</b><small>expected net value</small></span>
    <span><b>${escapeHtml(account.action)}</b><small>${escapeHtml(account.top_signal)}</small></span>
    <span><b>${account.days_to_renewal}d</b><small>to renewal</small></span>
    <span class="row-arrow">↗</span>
  </button>`;
}

function accountRow(account) {
  return `<button class="account-row" data-account-id="${escapeHtml(account.account_id)}">
    <span class="account-name"><i class="account-logo coral">${escapeHtml(account.account_name[0])}</i><span><b>${escapeHtml(account.account_name)}</b><small>${escapeHtml(account.segment)}</small></span></span>
    <span><b class="risk-score ${riskClass(account.risk)}">${percentage(account.risk)}</b></span>
    <span><b class="uplift-value">${signedPercentage(account.uplift)}</b></span>
    <span><b>${money(account.expected_net_value)}</b></span>
    <span>${account.days_to_renewal} days</span>
    <span>${escapeHtml(account.action)}</span>
    <span class="action-link">Inspect ↗</span>
  </button>`;
}

function renderAccountTables() {
  const overviewHeader = `<div class="table-head"><span>ACCOUNT</span><span>UPLIFT</span><span>NET VALUE</span><span>RECOMMENDED PLAY</span><span>RENEWAL</span><span></span></div>`;
  byId("overview-accounts").innerHTML = overviewHeader
    + state.summary.priority_accounts.slice(0, 5).map(overviewRow).join("");
  renderFilteredAccounts();
}

function renderFilteredAccounts() {
  const query = byId("account-search").value.trim().toLowerCase();
  const filtered = state.accounts.filter(account =>
    `${account.account_name} ${account.segment} ${account.action}`
      .toLowerCase()
      .includes(query)
  ).slice(0, 40);
  const header = `<div class="table-head"><span>ACCOUNT</span><span>RISK</span><span>UPLIFT</span><span>NET VALUE</span><span>RENEWAL</span><span>RECOMMENDED PLAY</span><span></span></div>`;
  byId("all-accounts").innerHTML = header + filtered.map(accountRow).join("");
}

function renderCover() {
  const { outcome } = state.summary;
  byId("cover-at-risk").textContent = money(outcome.at_risk_mrr);
  byId("cover-protected").textContent = money(outcome.expected_mrr_protected);
  byId("cover-capacity").textContent = percentage(outcome.capacity_used);
  byId("cover-queued").textContent = `${outcome.queued_accounts} accounts prioritized`;
  byId("cover-priority-total").textContent = `${outcome.queued_accounts} total`;
  byId("cover-threshold").textContent = percentage(state.summary.policy.threshold);
  byId("cover-priority-list").innerHTML = state.summary.priority_accounts.slice(0, 3)
    .map((account, index) => `<article class="${index === 0 ? "critical-account" : ""}">
      <div class="account-risk ${index === 1 ? "amber" : index === 2 ? "gold" : ""}">${Math.round(account.risk * 100)}<small>%</small></div>
      <div><b>${escapeHtml(account.account_name)}</b><small>${money(account.mrr)} MRR · renews in ${account.days_to_renewal} days</small><em>${escapeHtml(account.action)}</em></div>
    </article>`).join("");
}

function renderSummary() {
  const { model, outcome, policy, total_accounts: total } = state.summary;
  const threshold = percentage(policy.threshold);
  byId("account-count").textContent = total;
  byId("model-version").textContent = model.version;
  byId("sidebar-health").textContent = model.status;
  byId("sidebar-auc").textContent = decimal(model.roc_auc);
  byId("active-policy-pill").innerHTML = `<span class="health-dot"></span>Active policy · ${threshold} threshold`;
  byId("at-risk-mrr").textContent = money(outcome.at_risk_mrr);
  byId("priority-count").textContent = outcome.queued_accounts;
  byId("capacity-summary").innerHTML = `${percentage(outcome.capacity_used)} <span>of ${policy.capacity}-account capacity</span>`;
  byId("protected-mrr").textContent = money(outcome.expected_mrr_protected);
  byId("baseline-lift").textContent = state.summary.risk_only_baseline.net_value_gap >= 0
    ? `${money(state.summary.risk_only_baseline.net_value_gap)} more net value than risk-only ranking`
    : `${money(Math.abs(state.summary.risk_only_baseline.net_value_gap))} below the risk-only baseline`;
  byId("model-health").textContent = model.status;
  byId("model-quality-summary").innerHTML = `ROC-AUC ${decimal(model.roc_auc)} <span>· Brier ${decimal(model.brier_score)}</span>`;
  byId("impact-protected").textContent = money(outcome.expected_mrr_protected);
  byId("impact-threshold").textContent = threshold;
  byId("impact-queued").textContent = outcome.queued_accounts;
  byId("impact-capacity").textContent = `${percentage(outcome.capacity_used)} capacity`;
  byId("impact-capacity-bar").style.width = `${Math.min(outcome.capacity_used * 100, 100)}%`;
  byId("account-threshold").textContent = `Risk ≥ ${threshold}`;
  byId("account-table-note").textContent = `${total} held-out accounts · reproducible synthetic dataset`;
  byId("matrix-risk-gate").textContent = `Score ≥ ${threshold}`;
  slider.value = Math.round(policy.threshold * 100);
  capacitySlider.value = policy.capacity;
  byId("capacity-number").textContent = policy.capacity;
  byId("cover-policy-label").textContent = outcome.capacity_used >= 0.95
    ? "Capacity-fit policy"
    : "Focused policy";
  renderCover();
  renderAccountTables();
}

function renderImpactCurve() {
  const maximum = Math.max(
    ...state.curve.flatMap(row => [
      row.expected_net_value,
      row.risk_only_expected_net_value
    ]),
    1
  );
  const points = state.curve.map((row, index) => {
    const x = 4 + index * 92 / (state.curve.length - 1);
    const y = 88 - row.expected_net_value / maximum * 68;
    return { x, y, threshold: row.threshold };
  });
  const baselinePoints = state.curve.map((row, index) => {
    const x = 4 + index * 92 / (state.curve.length - 1);
    const y = 88 - Math.max(row.risk_only_expected_net_value, 0) / maximum * 68;
    return { x, y };
  });
  byId("impact-line").setAttribute(
    "points",
    points.map(point => `${point.x},${point.y}`).join(" ")
  );
  byId("impact-area").setAttribute(
    "d",
    `M ${points[0].x},90 L ${points.map(point => `${point.x},${point.y}`).join(" L ")} L ${points.at(-1).x},90 Z`
  );
  byId("impact-baseline").setAttribute(
    "points",
    baselinePoints.map(point => `${point.x},${point.y}`).join(" ")
  );
  const activeThreshold = state.summary.policy.threshold;
  const marker = points.reduce((best, point) =>
    Math.abs(point.threshold - activeThreshold) < Math.abs(best.threshold - activeThreshold)
      ? point
      : best
  );
  byId("impact-marker").setAttribute("cx", marker.x);
  byId("impact-marker").setAttribute("cy", marker.y);
  byId("impact-threshold").style.left = `${marker.x}%`;
  byId("impact-threshold").style.top = `${marker.y}%`;
}

function nearestCurve(threshold) {
  return state.curve.find(row => Math.round(row.threshold * 100) === Number(threshold))
    || state.curve.reduce((best, row) =>
      Math.abs(row.threshold * 100 - threshold) < Math.abs(best.threshold * 100 - threshold)
        ? row
        : best
    );
}

function renderPolicy(threshold) {
  const outcome = nearestCurve(Number(threshold));
  const thresholdNumber = Math.round(outcome.threshold * 100);
  byId("threshold-number").textContent = thresholdNumber;
  byId("queued-value").textContent = outcome.queued_accounts;
  byId("capacity-value").textContent = `${percentage(outcome.capacity_used)} of capacity`;
  byId("protected-value").textContent = money(outcome.expected_mrr_protected);
  byId("recall-value").textContent = percentage(outcome.recall);
  byId("precision-value").textContent = percentage(outcome.precision);
  byId("chart-value").textContent = money(outcome.expected_net_value);
  byId("baseline-value").textContent = outcome.net_value_gain_vs_risk_only >= 0
    ? `${money(outcome.net_value_gain_vs_risk_only)} above risk-only queue`
    : `${money(Math.abs(outcome.net_value_gain_vs_risk_only))} below risk-only queue`;
  byId("capacity-number").textContent = capacitySlider.value;
  byId("policy-note-title").textContent = `At ${thresholdNumber}% risk`;
  byId("policy-note-copy").textContent = outcome.eligible_accounts > outcome.capacity
    ? `${outcome.eligible_accounts} accounts qualify; the ${outcome.capacity} highest expected-value accounts are selected.`
    : `${outcome.queued_accounts} accounts qualify and use ${percentage(outcome.capacity_used)} of available outreach capacity.`;
  document.querySelectorAll(".preset-row button").forEach(button => {
    button.classList.toggle("active", Number(button.dataset.threshold) === thresholdNumber);
  });
  const samples = state.curve.filter((_, index) => index % 7 === 0).slice(0, 6);
  const maximum = Math.max(...samples.map(row => row.expected_net_value), 1);
  const selectedSample = samples.reduce((best, row) =>
    Math.abs(row.threshold - outcome.threshold) < Math.abs(best.threshold - outcome.threshold)
      ? row
      : best
  );
  document.querySelectorAll(".cost-bars i").forEach((bar, index) => {
    const row = samples[index];
    if (!row) return;
    bar.style.height = `${Math.max(12, row.expected_net_value / maximum * 88)}%`;
    bar.classList.toggle("selected", row.threshold === selectedSample.threshold);
  });
}

async function updateCapacity(value) {
  byId("capacity-number").textContent = value;
  const response = await requestJson(`/api/policy/curve?capacity=${Number(value)}`);
  state.curve = response.curve;
  renderPolicy(slider.value);
  renderImpactCurve();
}

function labelForFeature(feature) {
  return {
    weekly_active_ratio: "Weekly active ratio",
    feature_adoption: "Feature adoption",
    priority_tickets: "Priority tickets",
    days_to_renewal: "Days to renewal"
  }[feature] || feature;
}

function renderMonitoring() {
  const metrics = state.monitoring;
  const maxPsi = Math.max(...metrics.feature_stability.map(item => item.psi));
  byId("monitor-status").innerHTML = `<span class="health-dot"></span>${escapeHtml(metrics.status)} · synthetic holdout`;
  byId("holdout-note").textContent = `Latest holdout · ${metrics.holdout_accounts} accounts`;
  byId("quality-badge").textContent = metrics.status.toUpperCase();
  byId("monitor-pr-auc").textContent = decimal(metrics.pr_auc);
  byId("monitor-roc-auc").textContent = decimal(metrics.roc_auc);
  byId("monitor-brier").textContent = decimal(metrics.brier_score);
  byId("max-psi").textContent = decimal(maxPsi);
  byId("calibration-rows").innerHTML = `<div class="calibration-title"><b>Calibration by risk band</b><span>Predicted vs observed</span></div>`
    + metrics.calibration.map(row => `<div class="cal-row"><span>${escapeHtml(row.band)}</span><i><b style="width:${Math.round(row.predicted * 100)}%"></b></i><em>${percentage(row.observed)}</em></div>`).join("");
  byId("stability-rows").innerHTML = metrics.feature_stability
    .map(item => `<div><span>${escapeHtml(labelForFeature(item.feature))}</span><i><b style="width:${Math.max(item.psi * 400, 4)}%"></b></i><em>${decimal(item.psi)}</em></div>`)
    .join("");
  byId("segment-rows").innerHTML = `<div><span>SEGMENT</span><span>ACCOUNTS</span><span>PR-AUC</span><span>BRIER SCORE</span><span>STATUS</span></div>`
    + metrics.segments.map(segment => `<div><b>${escapeHtml(segment.segment)}</b><span>${segment.accounts}</span><span>${decimal(segment.pr_auc)}</span><span>${decimal(segment.brier_score)}</span><em class="${segment.brier_score <= 0.2 ? "ok" : "watch"}">${segment.brier_score <= 0.2 ? "Healthy" : "Watch"}</em></div>`).join("");
}

async function showAccount(accountId) {
  const account = await requestJson(`/api/accounts/${encodeURIComponent(accountId)}`);
  state.activeAccount = account;
  byId("drawer-logo").textContent = account.account_name[0];
  byId("drawer-name").textContent = account.account_name;
  byId("drawer-meta").textContent = `${account.segment} · Renewal in ${account.days_to_renewal} days`;
  byId("drawer-risk").textContent = Math.round(account.risk * 100);
  byId("drawer-tier").textContent = `${account.risk_tier} risk`;
  byId("drawer-uplift").textContent = `${percentage(account.uplift)} estimated incremental retention effect.`;
  byId("drawer-drivers").innerHTML = account.drivers.map((driver, index) => `<div class="driver">
    <span><i class="driver-icon ${index === 0 ? "down" : index === 1 ? "alert" : "time"}">${index === 0 ? "↓" : index === 1 ? "!" : "◷"}</i><b>${escapeHtml(driver.label)}</b><small>${escapeHtml(driver.evidence)}</small></span>
    <strong>+${Number(driver.impact_points).toFixed(0)} pts</strong>
  </div>`).join("");
  byId("drawer-action").textContent = account.action;
  byId("drawer-action-copy").textContent = account.action_description;
  byId("drawer-policy-tier").textContent = `${account.segment} · ${account.risk_tier}`;
  byId("drawer-action-uplift").textContent = percentage(account.uplift);
  byId("drawer-mrr").textContent = `${money(account.mrr)} MRR`;
  byId("drawer-net-value").textContent = money(account.expected_net_value);
  byId("drawer-model").textContent = `Score generated by ${account.model_version}`;
  openDrawer();
}

async function runScore() {
  const button = byId("run-score");
  const payload = {
    account_name: byId("score-name").value,
    segment: byId("score-segment").value,
    mrr: Number(byId("score-mrr").value),
    seat_change_pct: Number(byId("score-seats").value),
    weekly_active_ratio: Number(byId("score-active").value),
    priority_tickets: Number(byId("score-tickets").value),
    days_to_renewal: Number(byId("score-renewal").value),
    feature_adoption: Number(byId("score-adoption").value),
    tenure_months: Number(byId("score-tenure").value),
    nps: Number(byId("score-nps").value),
    resolution_hours: Number(byId("score-resolution").value)
  };
  button.textContent = "Scoring…";
  button.disabled = true;
  try {
    const result = await requestJson("/api/score", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    byId("result-risk").textContent = Math.round(result.risk * 100);
    byId("result-tier").textContent = `${result.risk_tier} risk`;
    byId("result-action").textContent = result.action;
    byId("result-copy").textContent = `${result.action_description} Estimated uplift: ${percentage(result.uplift)}.`;
    byId("score-result").classList.add("visible");
  } catch (error) {
    showToast("Scoring failed", error.message, true);
  } finally {
    button.textContent = "Run model";
    button.disabled = false;
  }
}

async function applyPolicy() {
  const button = byId("apply-policy");
  button.disabled = true;
  button.textContent = "Saving…";
  try {
    await requestJson("/api/policy", {
      method: "PUT",
      body: JSON.stringify({
        threshold: Number(slider.value) / 100,
        capacity: Number(capacitySlider.value)
      })
    });
    await loadCore();
    renderPolicy(slider.value);
    showToast(
      "Policy saved",
      `${slider.value}% risk threshold · ${capacitySlider.value}-account capacity.`
    );
  } catch (error) {
    showToast("Policy not saved", error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "Apply policy";
  }
}

async function copyActionPlan() {
  if (!state.activeAccount) return;
  const account = state.activeAccount;
  const text = `${account.account_name}: ${account.action}. ${account.action_description} Risk ${percentage(account.risk)}; estimated uplift ${percentage(account.uplift)}.`;
  try {
    await navigator.clipboard.writeText(text);
    showToast("Action plan copied", "The model decision is ready to paste into your workflow.");
  } catch {
    showToast("Copy unavailable", "Clipboard access was blocked by the browser.", true);
  }
}

async function loadCore() {
  const [summary, accounts, monitoring] = await Promise.all([
    requestJson("/api/summary"),
    requestJson("/api/accounts?limit=100"),
    requestJson("/api/monitoring")
  ]);
  const curve = await requestJson(`/api/policy/curve?capacity=${summary.policy.capacity}`);
  state.summary = summary;
  state.accounts = accounts.accounts;
  state.monitoring = monitoring;
  state.curve = curve.curve;
  renderSummary();
  renderMonitoring();
  renderPolicy(Math.round(summary.policy.threshold * 100));
  renderImpactCurve();
}

navItems.forEach(item => item.addEventListener("click", () => showView(item.dataset.view)));
document.querySelectorAll("[data-view-link]").forEach(item =>
  item.addEventListener("click", () => showView(item.dataset.viewLink))
);
document.addEventListener("click", event => {
  const row = event.target.closest("[data-account-id]");
  if (row) showAccount(row.dataset.accountId).catch(error =>
    showToast("Account unavailable", error.message, true)
  );
});
byId("close-drawer").addEventListener("click", closeDrawer);
drawerBackdrop.addEventListener("click", closeDrawer);
byId("score-account").addEventListener("click", openModal);
byId("close-modal").addEventListener("click", closeModal);
byId("cancel-score").addEventListener("click", closeModal);
modalBackdrop.addEventListener("click", closeModal);
byId("run-score").addEventListener("click", runScore);
byId("create-task").addEventListener("click", copyActionPlan);
byId("account-search").addEventListener("input", renderFilteredAccounts);
slider.addEventListener("input", event => renderPolicy(event.target.value));
let capacityPreviewTimer;
capacitySlider.addEventListener("input", event => {
  byId("capacity-number").textContent = event.target.value;
  window.clearTimeout(capacityPreviewTimer);
  capacityPreviewTimer = window.setTimeout(() => {
    updateCapacity(event.target.value).catch(error =>
      showToast("Capacity preview unavailable", error.message, true)
    );
  }, 120);
});
document.querySelectorAll(".preset-row button").forEach(button =>
  button.addEventListener("click", () => {
    slider.value = button.dataset.threshold;
    renderPolicy(button.dataset.threshold);
  })
);
byId("apply-policy").addEventListener("click", applyPolicy);

const params = new URLSearchParams(window.location.search);
const shot = params.get("shot");
const initialView = window.location.hash.slice(1);
if (viewNames[initialView]) showView(initialView);
window.addEventListener("hashchange", () => {
  const nextView = window.location.hash.slice(1);
  if (viewNames[nextView]) showView(nextView);
});
if (shot === "cover") document.body.classList.add("cover-mode");
if (shot === "account") document.body.classList.add("image-shot", "shot-account");
if (shot === "policy") {
  document.body.classList.add("image-shot", "shot-policy");
  byId("shot-kicker").textContent = "DECISION POLICY";
  byId("shot-title").textContent = "Tune the intervention threshold around value and team capacity.";
  showView("policy");
}

loadCore()
  .then(() => {
    if (shot === "account" && state.summary.priority_accounts.length) {
      return showAccount(state.summary.priority_accounts[0].account_id);
    }
    return null;
  })
  .catch(error => showToast("Application unavailable", error.message, true));
