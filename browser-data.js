(() => {
  const details = (account, signals = ["Weekly active usage", "Renewal proximity", "Seat contraction"]) => ({
    ...account,
    drivers: signals.map((label, index) => ({ label, impact_points: [27, 14, 10][index], evidence: ["Usage declined 31%", `${account.days_to_renewal} days to renewal`, "Seats down 15%"][index] })),
    action_description: account.action === "Executive service recovery"
      ? "Resolve open service issues, assign an executive owner and agree a recovery date."
      : "Run a focused enablement session around the unadopted workflows with the highest expected value.",
    features: {}, model_version: "churn-logit-1.0",
  });
  const account = (id, name, segment, mrr, risk, uplift, days, action, signal) => details({
    account_id: id, account_name: name, segment, mrr, risk,
    risk_tier: risk >= 0.8 ? "Critical" : risk >= 0.55 ? "Elevated" : "Moderate",
    uplift, expected_mrr_protected: Math.max(0, Math.round(mrr * uplift)),
    expected_net_value: Math.max(-950, Math.round(mrr * uplift - (segment === "Enterprise" ? 950 : 420))),
    days_to_renewal: days, action, top_signal: signal,
  });
  const accounts = [
    account("acct-0014", "Nova Analytics", "Business", 50019, 0.7374, 0.2144, 146, "Adoption enablement plan", "Weekly active usage"),
    account("acct-0020", "Tandem Analytics", "Business", 50606, 0.7025, 0.1730, 67, "Adoption enablement plan", "Weekly active usage"),
    account("acct-0053", "Willow Cloud", "Business", 19100, 0.5860, 0.4, 31, "Executive service recovery", "Priority support load"),
    account("acct-0067", "Granite Commerce", "Business", 21891, 0.5588, 0.2598, 107, "Adoption enablement plan", "Feature adoption"),
    account("acct-0001", "Acme Operations", "Business", 14382, 0.8561, 0.1425, 5, "Executive service recovery", "Priority support load"),
    account("acct-0003", "Northline Cloud", "Enterprise", 27203, 0.8407, -0.0931, 32, "Adoption enablement plan", "Seat contraction"),
    account("acct-0005", "Brightway Logistics", "Growth", 7951, 0.8003, 0.1608, 92, "Executive service recovery", "Weekly active usage"),
    account("acct-0006", "Summit Systems", "Enterprise", 59391, 0.7975, -0.0731, 33, "Executive service recovery", "Seat contraction"),
  ];
  const row = (threshold, eligible, queued, protected, net, precision, recall) => ({
    threshold, capacity: 50, eligible_accounts: eligible, queued_accounts: queued,
    capacity_used: queued / 50, at_risk_mrr: Math.round(protected * 12.7),
    expected_mrr_protected: protected, expected_net_value: net, precision, recall,
    risk_only_expected_net_value: 61989,
    net_value_gain_vs_risk_only: net - 61989,
  });
  let curve = [
    row(0.45, 88, 50, 189074, 165274, 0.583, 0.411), row(0.50, 68, 50, 163691, 141621, 0.644, 0.356),
    row(0.55, 50, 50, 130669, 110039, 0.69, 0.301), row(0.60, 33, 33, 86682, 73102, 0.714, 0.215),
    row(0.65, 21, 21, 55274, 46834, 0.812, 0.16), row(0.70, 12, 12, 37983, 32843, 0.81, 0.104),
    row(0.75, 5, 5, 8161, 6011, 0.917, 0.067), row(0.80, 3, 3, 4037, 3017, 0.8, 0.025),
  ];
  let summary = {
    policy: { threshold: 0.55, capacity: 50 },
    outcome: { ...curve[2], at_risk_mrr: 1654392 },
    risk_only_baseline: { eligible_accounts: 71, queued_accounts: 50, expected_mrr_protected: 88349, expected_net_value: 61989, negative_uplift_accounts: 15, negative_value_accounts: 16, net_value_gap: 48050 },
    model: { status: "Healthy", version: "churn-logit-1.0", holdout_accounts: 600, roc_auc: 0.7627, brier_score: 0.1615 },
    total_accounts: 600, priority_accounts: accounts.slice(0, 5),
  };
  const monitoring = {
    holdout_accounts: 600, prevalence: 0.2717, roc_auc: 0.7627, pr_auc: 0.5727, brier_score: 0.1615, uplift_rmse: 0.084,
    calibration: [{ band: "0–20%", predicted: 0.114, observed: 0.113, count: 266 }, { band: "20–40%", predicted: 0.287, observed: 0.286, count: 189 }, { band: "40–60%", predicted: 0.49, observed: 0.458, count: 96 }, { band: "60–80%", predicted: 0.68, observed: 0.705, count: 44 }],
    segments: [{ segment: "Business", accounts: 277, pr_auc: 0.52, brier_score: 0.16 }, { segment: "Enterprise", accounts: 127, pr_auc: 0.629, brier_score: 0.171 }, { segment: "Growth", accounts: 196, pr_auc: 0.613, brier_score: 0.158 }],
    feature_stability: [{ feature: "weekly_active_ratio", psi: 0.0238 }, { feature: "feature_adoption", psi: 0.0092 }, { feature: "priority_tickets", psi: 0.0055 }, { feature: "days_to_renewal", psi: 0.0158 }],
    status: "Healthy", model_version: "churn-logit-1.0", data_note: "Metrics use a deterministic synthetic holdout set.",
  };
  const clone = (value) => structuredClone(value);
  window.SIGNALROOM_BROWSER_API = async (url, options = {}) => {
    await new Promise((resolve) => setTimeout(resolve, 70));
    if (url === "/api/summary") return clone(summary);
    if (url.startsWith("/api/accounts?")) return { accounts: clone(accounts), total: 600 };
    if (url === "/api/monitoring") return clone(monitoring);
    if (url.startsWith("/api/policy/curve")) {
      const capacity = Number(new URL(url, location.href).searchParams.get("capacity") || 50);
      return { curve: curve.map((item) => ({ ...item, capacity, queued_accounts: Math.min(item.eligible_accounts, capacity), capacity_used: Math.min(item.eligible_accounts, capacity) / capacity })) };
    }
    if (url === "/api/policy" && options.method === "PUT") {
      const policy = JSON.parse(options.body || "{}");
      summary.policy = policy;
      const nearest = curve.reduce((best, item) => Math.abs(item.threshold - policy.threshold) < Math.abs(best.threshold - policy.threshold) ? item : best);
      summary.outcome = { ...nearest, capacity: policy.capacity, queued_accounts: Math.min(nearest.eligible_accounts, policy.capacity), capacity_used: Math.min(nearest.eligible_accounts, policy.capacity) / policy.capacity };
      return clone(summary.policy);
    }
    if (url === "/api/score" && options.method === "POST") {
      const input = JSON.parse(options.body || "{}");
      const risk = Math.min(0.96, Math.max(0.08, 0.34 + input.priority_tickets * 0.055 + (1 - input.weekly_active_ratio) * 0.38 + Math.max(0, -input.seat_change_pct) * 0.008));
      return details({ account_name: input.account_name, risk, risk_tier: risk >= 0.75 ? "High" : risk >= 0.55 ? "Elevated" : "Moderate", uplift: risk >= 0.55 ? 0.18 : 0.08, action: risk >= 0.75 ? "Executive service recovery" : "Adoption enablement plan", action_description: risk >= 0.75 ? "Resolve the service issue and assign an executive owner." : "Focus outreach on the workflows with the highest adoption gap." });
    }
    const match = url.match(/^\/api\/accounts\/(.+)$/);
    if (match) return clone(accounts.find((item) => item.account_id === decodeURIComponent(match[1])));
    if (url === "/api/health") return { status: "ok", model_status: "Healthy", model_version: "churn-logit-1.0" };
    throw new Error(`Unknown browser-workspace route: ${url}`);
  };
})();
