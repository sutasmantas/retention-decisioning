from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    data_dir: Path = Path("data/runtime")
    random_seed: int = 42
    account_count: int = 2400

    model_config = SettingsConfigDict(env_prefix="SIGNALROOM_", env_file=".env")

    @property
    def model_path(self) -> Path:
        return self.data_dir / "models.joblib"

    @property
    def metrics_path(self) -> Path:
        return self.data_dir / "metrics.json"

    @property
    def accounts_path(self) -> Path:
        return self.data_dir / "accounts.csv"

    @property
    def policy_path(self) -> Path:
        return self.data_dir / "policy.json"


settings = Settings()
