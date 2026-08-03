import json

import joblib
from sklearn.model_selection import train_test_split

from signalroom.config import Settings
from signalroom.data import FEATURES, generate_accounts
from signalroom.modeling import evaluate, fit_models, reason_codes, score_frame

SHOWCASE_NAMES = [
    "Acme Operations",
    "Fjord Analytics",
    "Northline Cloud",
    "Linear Works",
    "Brightway Logistics",
    "Summit Systems",
    "Atlas Commerce",
    "Cedar Labs",
    "Evergreen Mobility",
    "Harbor Health",
    "Juniper Data",
    "Keystone Works",
]


def _account_names(count: int) -> list[str]:
    prefixes = [
        "Aster",
        "Beacon",
        "Cobalt",
        "Delta",
        "Elm",
        "Falcon",
        "Granite",
        "Helix",
        "Indigo",
        "Juno",
        "Kite",
        "Lumen",
        "Meridian",
        "Nova",
        "Oak",
        "Pioneer",
        "Quartz",
        "River",
        "Solstice",
        "Tandem",
        "Union",
        "Vertex",
        "Willow",
        "Xeno",
        "Yellowfin",
        "Zenith",
        "Arc",
        "Boreal",
        "Crown",
        "Dune",
    ]
    suffixes = [
        "Analytics",
        "Cloud",
        "Commerce",
        "Data",
        "Digital",
        "Energy",
        "Finance",
        "Health",
        "Industries",
        "Labs",
        "Logistics",
        "Mobility",
        "Networks",
        "Operations",
        "Partners",
        "Retail",
        "Systems",
        "Technology",
        "Ventures",
        "Works",
    ]
    generated = [f"{prefix} {suffix}" for suffix in suffixes for prefix in prefixes]
    return [
        SHOWCASE_NAMES[index] if index < len(SHOWCASE_NAMES) else generated[index]
        for index in range(count)
    ]


def train_and_persist(settings: Settings, force: bool = False) -> dict:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    if (
        not force
        and settings.model_path.exists()
        and settings.metrics_path.exists()
        and settings.accounts_path.exists()
    ):
        return json.loads(settings.metrics_path.read_text(encoding="utf-8"))

    data = generate_accounts(settings.account_count, settings.random_seed)
    train, test = train_test_split(
        data,
        test_size=0.25,
        random_state=settings.random_seed,
        stratify=data["churned"],
    )
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    bundle = fit_models(train)
    metrics = evaluate(bundle, train, test)

    scored = score_frame(bundle, test[FEATURES])
    scored["churned"] = test["churned"].to_numpy()
    scored = scored.sort_values(["risk", "expected_net_value"], ascending=False).reset_index(
        drop=True
    )
    scored.insert(0, "account_id", [f"acct-{index + 1:04d}" for index in range(len(scored))])
    scored.insert(1, "account_name", _account_names(len(scored)))
    scored["drivers"] = scored.apply(lambda row: json.dumps(reason_codes(row)), axis=1)

    joblib.dump(bundle, settings.model_path)
    settings.metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    scored.to_csv(settings.accounts_path, index=False)
    if not settings.policy_path.exists():
        settings.policy_path.write_text(
            json.dumps({"threshold": 0.55, "capacity": 50}, indent=2), encoding="utf-8"
        )
    return metrics


if __name__ == "__main__":
    from signalroom.config import settings

    result = train_and_persist(settings, force=True)
    print(json.dumps(result, indent=2))
