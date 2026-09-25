from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    project_id: str
    environment: str = "development"
    credentials: Path | None = None


@dataclass(frozen=True, slots=True)
class AnalyticsConfig:
    collection: str = "analytics_events"


@dataclass(frozen=True, slots=True)
class FunctionsConfig:
    base_url: str | None = None


@dataclass(frozen=True, slots=True)
class UtilitiesConfig:
    project: ProjectConfig
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    functions: FunctionsConfig = field(default_factory=FunctionsConfig)

    @classmethod
    def from_toml(cls, path: str | Path) -> "UtilitiesConfig":
        config_path = Path(path).expanduser().resolve()
        with config_path.open("rb") as handle:
            raw = tomllib.load(handle)

        project_raw = raw.get("project", {})
        project_id = str(project_raw.get("project_id", "")).strip()
        if not project_id:
            raise ValueError("[project].project_id is required")

        credentials_raw = project_raw.get("credentials")
        credentials = None
        if credentials_raw:
            candidate = Path(str(credentials_raw)).expanduser()
            if not candidate.is_absolute():
                candidate = (config_path.parent / candidate).resolve()
            credentials = candidate

        analytics_raw = raw.get("analytics", {})
        functions_raw = raw.get("functions", {})

        return cls(
            project=ProjectConfig(
                project_id=project_id,
                environment=str(project_raw.get("environment", "development")),
                credentials=credentials,
            ),
            analytics=AnalyticsConfig(
                collection=str(analytics_raw.get("collection", "analytics_events"))
            ),
            functions=FunctionsConfig(
                base_url=(
                    str(functions_raw["base_url"]).rstrip("/")
                    if functions_raw.get("base_url")
                    else None
                )
            ),
        )
