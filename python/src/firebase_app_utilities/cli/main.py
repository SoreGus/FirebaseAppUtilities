from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
from typing import Any

from ..core.project import FirebaseProject


def _json_default(
    value: Any,
) -> str:
    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    return str(value)


def _print_json(
    value: Any,
) -> None:
    print(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=_json_default,
        )
    )


def _add_config_argument(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument(
        "--config",
        default="firebase_app_utilities.local.toml",
        help="Path to project TOML configuration.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firebase-app-utils",
        description="FirebaseAppUtilities project tooling",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    status = subparsers.add_parser(
        "status",
        help="Show connected project configuration",
    )
    _add_config_argument(status)

    collections = subparsers.add_parser(
        "collections",
        help="List Firestore collections",
    )
    _add_config_argument(collections)

    documents = subparsers.add_parser(
        "documents",
        help="List documents from a collection",
    )
    documents.add_argument(
        "collection"
    )
    documents.add_argument(
        "--limit",
        type=int,
        default=50,
    )
    _add_config_argument(documents)

    analytics = subparsers.add_parser(
        "analytics",
        help="Query custom analytics events",
    )
    analytics.add_argument(
        "--event"
    )
    analytics.add_argument(
        "--limit",
        type=int,
        default=100,
    )
    analytics.add_argument(
        "--counts",
        action="store_true",
    )
    analytics.add_argument(
        "--days",
        type=int,
    )
    _add_config_argument(analytics)

    function = subparsers.add_parser(
        "function",
        help="Call an HTTP function endpoint",
    )
    function.add_argument(
        "name"
    )
    function.add_argument(
        "--method",
        default="POST",
    )
    function.add_argument(
        "--json",
        dest="json_payload",
    )
    _add_config_argument(function)

    gui = subparsers.add_parser(
        "gui",
        help="Open the reusable local GUI",
    )
    _add_config_argument(gui)

    return parser


def _load_project(
    path: str,
) -> FirebaseProject:
    config_path = (
        Path(path)
        .expanduser()
    )

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration not found: {config_path}"
        )

    return FirebaseProject.from_toml(
        config_path
    )


def main(
    argv: list[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "gui":
            from ..gui import FirebaseUtilitiesApp

            config_path = (
                Path(args.config)
                .expanduser()
            )

            if config_path.exists():
                FirebaseUtilitiesApp.from_toml(
                    config_path
                ).run()
            else:
                FirebaseUtilitiesApp().run()

            return 0

        project = _load_project(
            args.config
        )

        if args.command == "status":
            _print_json(
                project.status()
            )
            return 0

        if args.command == "collections":
            _print_json(
                project.firestore.list_collections()
            )
            return 0

        if args.command == "documents":
            _print_json(
                project.firestore.list_documents(
                    args.collection,
                    limit=args.limit,
                )
            )
            return 0

        if args.command == "analytics":
            if args.counts:
                _print_json(
                    project.analytics.count_by_name(
                        days=args.days,
                        limit=args.limit,
                    )
                )
            else:
                _print_json(
                    project.analytics.list_events(
                        event_name=args.event,
                        days=args.days,
                        limit=args.limit,
                    )
                )
            return 0

        if args.command == "function":
            payload = (
                json.loads(
                    args.json_payload
                )
                if args.json_payload
                else None
            )

            response = (
                project.functions.request(
                    args.name,
                    method=args.method,
                    json=payload,
                )
            )

            try:
                _print_json(
                    response.json()
                )
            except ValueError:
                print(response.text)

            return 0

    except Exception as error:
        parser.exit(
            1,
            f"error: {error}\n",
        )

    return 0
