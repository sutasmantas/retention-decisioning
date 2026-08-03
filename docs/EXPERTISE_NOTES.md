# Expertise notes

## When real randomized data supports an intervention but not necessarily targeting

### Client trigger

- Job wording or deliverable that makes this relevant: churn prevention,
  campaign targeting, uplift modeling, treatment/control evaluation, or a
  capacity-constrained intervention queue.
- How often it appeared in the measured corpus or proposal log: predictive ML
  represented 127 of 4,908 measured requirement tags (2.6%); this is a bounded
  credibility gap rather than a general portfolio expansion.
- Existing project/component that can be reused: SignalRoom's T-learner and
  capacity policy; the real-data evaluation components selected in
  `docs/REAL_DATA_ADMISSION.md`.

### Failure symptom or unanswered choice

Synthetic data can prove that the software runs, but it cannot establish that
customer features contain enough real treatment-effect signal to justify an
individual targeting policy.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Broad treatment | The randomized experiment may show a positive average email effect | Ignores a real capacity constraint and may contact low/negative-effect customers |
| Random 20% policy | Honest capacity-matched baseline that needs no model | Leaves any learnable heterogeneity unused |
| T-learner top 20% | Uses treated/control outcome models to rank incremental response | Can overfit weak heterogeneity and look useful without beating the capacity-matched baseline |

### Controlled comparison

- Representative cases or fixtures: pinned 64,000-row Hillstrom GitHub mirror;
  42,613-row Mens-email versus no-email randomized contrast.
- Frozen development/held-out split, when relevant: deterministic joint
  treatment/outcome 80/20 split, seed 42.
- Metrics and decision thresholds chosen before the run: ATE with 95%
  bootstrap interval; normalized Qini with lower bound greater than zero;
  top-20% uplift above ATE; 20%-capacity IPW value gain over random with lower
  bound greater than zero.
- Runtime, hardware, model/provider version, cost assumptions, and date:
  local Windows CPU; Python/sklearn versions captured in the output; no model
  provider or token cost; run date captured by the command.
- What is deliberately outside the comparison: SaaS churn, temporal drift,
  conversion/spend optimization, long-run harms, UI/API changes, and model
  shopping.

### Result

The checksum-pinned run used 42,613 customers, with 34,090 training rows and
8,523 held-out rows. Randomization health passed: the binary-arm SRM check was
`p=0.9961`, and maximum absolute covariate SMD was `0.0164` against the `0.10`
limit.

- Average two-week visit effect: `+0.0767`, bootstrap 95% interval
  `[0.0634, 0.0920]`.
- Top-20% realized uplift: `0.1167`, interval `[0.0733, 0.1512]`.
- Normalized Qini: `0.0144`, interval `[-0.0166, 0.0457]`.
- Learned 20%-capacity policy value: `0.1274`; random equal-capacity policy:
  `0.1214`.
- IPW policy-value gain: `+0.0060`, interval `[-0.0019, 0.0128]`.

The average intervention effect passed. Individual targeting failed two of
three pre-registered gates because both Qini and policy-gain intervals crossed
zero. No model, feature, arm, split, or threshold was changed after the run.

The local Qini (`0.0144495`) and uplift-at-20% (`0.1167296`) were independently
cross-checked against `scikit-uplift==0.5.1` (`0.0144346` and `0.1165697`). The
minor differences are consistent with implementation-specific curve/tie
conventions and do not change either decision gate.

### Decision rule

Promote learned targeting only when it beats a random policy at the same
capacity with a positive bootstrap lower bound and passes the two ranking
gates. This run therefore retains the experiment-level email effect and
rejects individualized targeting for the available features. At a fixed 20%
capacity, use an explicit non-model allocation rule and keep a randomized
control until richer pre-treatment features can be tested under the same gate.

### Delivery control

Require an explicit randomized control arm, pre-treatment feature allowlist,
checksum-pinned input, held-out policy evaluation, and a capacity-matched
baseline before a learned intervention queue is described as beneficial.

### Reuse boundary

- Reusable without client data: loader contract, leakage checks, joint split,
  Qini/uplift-at-k, IPW capacity evaluation, bootstrap report, and promotion
  rule.
- Requires client data, credentials, environment, or acceptance criteria:
  treatment definition, action cost/capacity, outcome horizon, harm
  guardrails, and a representative randomized experiment.
- Unsupported claim that must not appear in a proposal: that SignalRoom's
  synthetic SaaS lift or this retail email benchmark proves production churn
  reduction or client revenue.

### Proposal-safe insight

I built a checksum-pinned evaluation path around a real randomized email
experiment and separated average intervention lift from targeting value. The
experiment showed a clear average visit increase, but the model's equal-budget
advantage crossed zero, so the deployment gate correctly rejected a stronger
personalized-targeting claim.

### Evidence

- Code: `signalroom/real_data.py`, `signalroom/real_metrics.py`, and
  `signalroom/real_benchmark.py`.
- Tests: real-data, metric, promotion, report, existing API, and policy suites;
  15 passing with 91% aggregate coverage in the local verification run.
- Raw comparison artifacts: `artifacts/real_data/benchmark.json` and
  `artifacts/real_data/benchmark.md`.
- Human review, if used: none.
- Reproduction commands: `pip install -c requirements-benchmark.txt -e
  ".[dev]"`, then `python -m signalroom.real_benchmark --bootstrap 500`.

### Interview follow-up

- Likely technical question: Why is ordinary response prediction not enough?
- Short answer: it ranks likely visitors, including people who would visit
  without email; uplift ranking estimates the difference between treated and
  untreated potential outcomes and must be evaluated against randomized
  treatment assignments.
- Deeper evidence to open if challenged: the pinned contract, held-out Qini,
  top-capacity uplift, and IPW policy-value comparison.
