# SignalRoom systematic dossier checkpoint

Date: 2026-08-05

Status: **DOSSIER COMPLETE — ALL ELEVEN SYSTEMATIC GATES PASS; EXPERIMENTS NOT STARTED**

## Restart point

- Repository: `portfolio_demos/retention_decisioning`
- Assigned worktree:
  `portfolio_demos/worktrees/signalroom_technique_dossier`
- Branch: `agent/signalroom-technique-dossier`
- Base: `ecbf00988053de5347d2a47ac245057a64e156a2`
- Dossier commit: `6cbebe11d3680a52be22220f9a030ab2cdfbe3ce`
- Checkpoint commit: this checkpoint-only commit
- State before checkpoint edit: dossier commit clean; no application,
  dependency, UI, dataset, model or experiment change.
- ContextSidecar: completed by another agent and out of scope; not inspected or
  used as a dependency.

## Required artifacts

| Artifact | Status | Evidence |
| --- | --- | --- |
| Technique taxonomy | PASS | `TECHNIQUE_TAXONOMY.md`; eleven decisions, workloads, metrics, search protocol and saturation log |
| Evidence matrix | PASS | `EVIDENCE_MATRIX.csv`; 45 unique, complete evidence rows |
| GitHub implementation audit | PASS | `GITHUB_IMPLEMENTATION_AUDIT.md`; twelve pinned repositories and adopt/refit/custom decisions |
| Benchmark design | PASS | `BENCHMARK_DESIGN.md`; frozen S0–S7 queue with data, metrics, budget, routing and stop rules |
| Research decision | PASS | `RESEARCH_DECISION.md`; candidate dispositions, reuse boundary, claims and all gates |
| Expertise notes | PASS | `docs/EXPERTISE_NOTES.md`; six notes, each with an explicit central-index disposition |

## Systematic gate evidence

| Gate | Status | Evidence |
| --- | --- | --- |
| Problem decomposition | PASS | risk, ATE, CATE, identification, nuisance, ranking, calibration, policy, economics, safety and transport separated |
| Search protocol | PASS | search date/window, primary-source hierarchy, query groups, admission/exclusion and stop rules recorded |
| Survey coverage | PASS | uplift review, systematic cross-stream benchmark, meta/orthogonal/forest sources and recent practical guide |
| Benchmark coverage | PASS | Hillstrom, corrected Criteo, IHDP, ACIC, Jobs, controlled DGPs, DGP/leak criticism and UpliftBench |
| Existing-answer search | PASS | each material question has external-answer, confidence and local-work disposition |
| Technique-family saturation | PASS | two consecutive breadth expansions added variants/different contracts but no immediate family |
| Candidate comparison | PASS | assumptions, objective, regime, resources, integration and failure routes compared |
| Contrary evidence | PASS | no universal winner, Qini variance/objective mismatch, metric dispute, benchmark bias, weak overlap and shift included |
| Implementation evidence | PASS | GitHub pins, activity/release evidence, environment/download hazards, duplication and custom-logic limits |
| Portfolio fit | PASS | distinct risk-versus-effect and value/capacity evidence with proposal-safe boundaries |
| Review status | PASS | findings labelled established, provisional, contested or unknown; no experimental result inferred |

## Research decision

- Preserve the current Hillstrom ATE and T-learner as frozen controls; the
  stronger targeting claim remains rejected.
- Later compare matched S/T/X, R/DR, one EconML causal forest and one CausalML
  direct uplift forest under repeated outer evaluation.
- Use UpliftBench commit `604cf7c` as the first isolated harness candidate in
  Python 3.12, while treating its 2026-08-02 findings as provisional.
- Require overlap/nuisance diagnostics, effect calibration, multiple ranking
  metrics, and IPW/SNIPS/DR value against equal-capacity policies.
- Route by non-dominated regime/objective/cost/capacity behavior, not a pooled
  leaderboard.
- Keep no-harm, fairness, observational sensitivity, transport, multi-arm and
  dynamic profiles conditional on their missing data/estimand contracts.
- Do not write estimators, forests, calibration, policy evaluation, dataset
  loaders or benchmark orchestration from scratch.
- License was not researched or used as a repository decision signal.

## Baseline verification

Constrained environment used the repository's frozen numerical versions:
`pandas==2.2.3`, `numpy==2.2.4`, `scikit-learn==1.8.0`, and
`scipy==1.16.3`.

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
node --check app.js
docker compose config -q
```

Observed 2026-08-05:

- Ruff: PASS.
- Pytest: PASS, 15 tests in 1.12 seconds on the final rerun.
- JavaScript syntax: PASS.
- Docker Compose config: PASS.
- Dossier artifact validator: PASS, six artifacts, 45 CSV rows, unique IDs,
  complete cells/statuses, all eleven gates, and six expertise dispositions.
- Changed-path audit before the dossier commit: PASS; exactly the six required
  dossier artifacts.

An earlier uncontrolled run using global `pandas==3.0.5` failed one
real-benchmark test because `_balance_table()` treated the string-like
categorical `history_segment` as numeric and attempted to parse
`"2) $100 - $200"`. This is a real compatibility limitation. The project
declares `pandas<3`, and its frozen pandas 2.2.3 environment passes; no source
fix was authorized or made in the dossier.

## Remaining limitations

- No new estimator, metric, calibrator, policy learner or sensitivity method
  was run.
- No data, model, repository or large artifact was downloaded into the project.
- UpliftBench is extremely recent, single-author and under review; its design is
  reusable but its numerical findings remain provisional.
- Qini, pROCini and balanced-ranking sufficiency is contested; no bespoke
  metric was admitted without a reproducible parity route.
- Real randomized data does not reveal individual counterfactual truth; PEHE is
  limited to known-effect workloads.
- Hillstrom has no timestamp, churn/retention/revenue target, harm outcome or
  target-client population.
- Current Hillstrom evidence supports the average two-week visit effect only;
  individualized targeting, no-harm, transport and production value remain
  unsupported.
- Global pandas 3 compatibility is unresolved outside the pinned environment.
- No merge, push, deployment, polish or new-project work occurred.

## Exact next action

Stop. The systematic dossier phase is complete, but all project experiments
remain unstarted/partial. The first SignalRoom experiment, if a later
authoritative checkpoint admits it, is **S0 only**: reconcile the current
source, numerical constraints, synthetic/Hillstrom artifacts, split lineage,
feature allowlist, metric conventions, 15 tests and service configuration at
base `ecbf009`, with no download and no estimator/UI change. Do not start S1 or
any model comparison before S0 is separately authorized and passes.
