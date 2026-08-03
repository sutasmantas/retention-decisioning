# SignalRoom depth execution checkpoint

Date: 2026-08-03

Status: **SLICE 6 COMPLETE — ALL REQUIRED GATES PASS**

## Restart point

- Repository: `portfolio_demos/retention_decisioning`
- Assigned worktree: `portfolio_demos/worktrees/signalroom_real_data`
- Completed branch: `agent/signalroom-real-data`
- Base: `580137a66a414916ade2e70ec038fbce1ff517e1`
- Admission/reuse decision: `57e25b4`
- Functional implementation: `f9051cf`
- Frozen evidence result: `bdeb56f`
- Reproduction control: `699dbdd`
- Local `main`: fast-forwarded through `699dbdd`; not pushed
- State at handoff: both the branch worktree and local main were clean before
  this checkpoint-only commit.

## Gate evidence

| Gate | Status | Evidence |
| --- | --- | --- |
| Real reusable input | PASS | GitHub file pinned to `TerraBaseAI/campaign-decisioning-engine@c44ae9a`; 64,000 x 12; SHA-256 `0e589332...291aece` |
| Target/split/leakage/action contract | PASS | `docs/REAL_DATA_ADMISSION.md`; Mens email vs control, two-week visit, pre-treatment allowlist, joint-stratified 80/20, positive top-20% capacity |
| Repository GitHub comparison | PASS | Six pinned repositories compared before implementation; Criteo, Online Retail, and RetailHero alternatives explicitly rejected |
| Component/source audit | PASS | Loader/validation/split/Qini/uplift/IPW/bootstrap/model decisions recorded as refit/retain/reject before code |
| No integration-heavy reinvention | PASS | Bounded patterns refit from `uplift-bench` and the RCT analysis repository; the seven-model stack and stale scikit-uplift runtime dependency were not imported |
| Experiment health | PASS | binary-arm SRM `p=0.9961`; maximum absolute covariate SMD `0.0164` against `0.10` |
| Frozen held-out run | PASS | 34,090 train / 8,523 holdout; 500 seeded bootstrap samples; committed JSON and Markdown artifacts |
| Promotion discipline | PASS | `PROMOTE_AVERAGE_EFFECT_ONLY`; no feature/model/arm/split/threshold change after targeting failed two gates |
| Existing product regression | PASS | 15 total tests including retained API/policy suite; Ruff, Node syntax, Docker Compose config |
| Package/clean checkout | PASS | detached install with benchmark constraints, training, 15 tests at 91.43% coverage, full CLI, wheel/sdist, and Twine |
| UI/polish stop | PASS | no HTML, CSS, JavaScript, screenshot, API route, or synthetic product behavior changed |

## Result and claim boundary

- Average visit effect: `+0.0767`, bootstrap 95% interval
  `[0.0634, 0.0920]`.
- Top-20% realized uplift: `0.1167`, interval `[0.0733, 0.1512]`.
- Normalized Qini: `0.0144`, interval `[-0.0166, 0.0457]` — gate failed.
- IPW equal-capacity policy gain: `+0.0060`, interval
  `[-0.0019, 0.0128]` — gate failed.
- `scikit-uplift==0.5.1` cross-check agreed within metric convention rounding.

The real randomized experiment supports an average short-horizon email effect.
It does not support a claim that these features improve individualized
targeting at 20% capacity. It does not validate SaaS churn reduction, revenue,
temporal generalization, long-term retention, or production deployment.

## Verification commands

```powershell
pip install -c requirements-benchmark.txt -e ".[dev]"
python -m signalroom.training
python -m ruff check .
python -m pytest --cov=signalroom --cov-fail-under=85
node --check app.js
docker compose config -q
python -m signalroom.real_benchmark --bootstrap 500
python -m build
python -m twine check "dist/*"
```

Detached Windows verification produced one upstream FastAPI/httpx deprecation
warning and no functional failures. Regenerated artifact Git filtered hashes
matched the committed index hashes; raw worktree bytes used CRLF because global
`core.autocrlf=true`.

## Remaining limitations

- The dataset is a public historical benchmark with no timestamps.
- Visit is a two-week re-engagement outcome, not churn, retention, or revenue.
- Conversion is sparse and spend is heavy-tailed; neither is promoted here.
- Harm outcomes such as unsubscribe and complaints are absent.
- The existing UI remains a deterministic synthetic SaaS demonstration.
- No remote push, deployment, client data, or live production result exists.

## Exact next action

Stop implementation. The ranked queue has no automatically admitted next
slice: Atlas depth requires a representative retrieval failure or matching live
job, and general visual polish remains rejected. Use the completed expertise
card in qualified proposals and let proposal/interview evidence or a live job
admit the next smallest consequential experiment. Do not reopen ContextSidecar.
