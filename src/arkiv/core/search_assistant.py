"""LLM-assisted query rewriting for memory-style search."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

from arkiv.core.classifier import DEFAULT_CATEGORIES
from arkiv.core.config import ArkivConfig, LLMConfig
from arkiv.core.llm import completion

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """\
You help users find documents in a private local archive.

Task:
- read the user's vague search request
- generate 2 to 5 concrete search rewrites
- extract only cautious filter hints that are actually implied
- keep the output short and useful for retrieval

Allowed category values:
{category_list}

Return ONLY JSON with this shape:
{{
  "rewrites": ["..."],
  "filters": {{
    "category": ["..."],
    "organizations": ["..."],
    "date_hints": ["..."],
    "topics": ["..."]
  }},
  "notes": "one short sentence"
}}

Rules:
- Do not invent documents that may not exist.
- Do not add exact dates unless the user implied them.
- Keep rewrites short and retrieval-friendly.
- Keep the user's language when possible.
- If you are unsure, return fewer filters instead of guessing.

User query:
---
{query}
---
"""


@dataclass(frozen=True)
class QueryAssist:
    """Structured query-assist output for memory search."""

    rewrites: list[str]
    filters: dict[str, list[str]]
    notes: str
    raw: str = ""

    def queries(self, original_query: str) -> list[str]:
        """Return the deduplicated query list to send into retrieval."""
        ordered = [original_query.strip(), *self.rewrites]
        seen: set[str] = set()
        result: list[str] = []
        for query in ordered:
            cleaned = " ".join(query.split())
            key = cleaned.casefold()
            if not cleaned or key in seen:
                continue
            seen.add(key)
            result.append(cleaned)
        return result

    @classmethod
    def empty(cls) -> QueryAssist:
        return cls(rewrites=[], filters={}, notes="", raw="")


def _build_prompt(categories: dict[str, str], query: str) -> str:
    category_list = ", ".join(sorted(categories))
    return _PROMPT_TEMPLATE.format(category_list=category_list, query=query)


def _build_model_id(config: LLMConfig) -> str:
    """Map provider config to the model id expected by llm.completion()."""
    if config.provider == "ollama":
        return f"ollama_chat/{config.model}"
    if config.provider == "openai":
        return config.model
    return f"{config.provider}/{config.model}"


def _clean_list(values: object, limit: int = 5) -> list[str]:
    if not isinstance(values, list):
        return []

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        cleaned = " ".join(value.split()).strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def _parse_response(raw: str) -> QueryAssist:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Search-assist output must be a JSON object")

    raw_filters = data.get("filters", {})
    filters: dict[str, list[str]] = {}
    if isinstance(raw_filters, dict):
        for key, value in raw_filters.items():
            cleaned_values = _clean_list(value)
            if cleaned_values:
                filters[str(key)] = cleaned_values

    return QueryAssist(
        rewrites=_clean_list(data.get("rewrites", [])),
        filters=filters,
        notes=" ".join(str(data.get("notes", "")).split()),
        raw=raw,
    )


class QueryAssistant:
    """Generate retrieval-friendly search rewrites via the configured LLM."""

    def __init__(self, config: LLMConfig, arkiv_config: ArkivConfig | None = None) -> None:
        self.config = config
        self._model_id = _build_model_id(config)
        self._retries = arkiv_config.classifier_retries if arkiv_config is not None else 2
        self._timeout = arkiv_config.classifier_timeout if arkiv_config is not None else 20
        merged_categories = dict(DEFAULT_CATEGORIES)
        if arkiv_config is not None and arkiv_config.categories:
            merged_categories.update(arkiv_config.categories)
        self._categories = merged_categories

    def assist(self, query: str) -> QueryAssist:
        """Generate search rewrites and conservative filter hints."""
        if not query.strip():
            return QueryAssist.empty()

        prompt = _build_prompt(self._categories, query.strip())
        last_exc: Exception = Exception("no attempts made")

        for attempt in range(self._retries):
            try:
                response = completion(
                    model=self._model_id,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=min(self.config.temperature, 0.2),
                    max_tokens=min(self.config.max_tokens, 400),
                    timeout=self._timeout,
                    api_base=self.config.base_url,
                    api_key=self.config.api_key,
                )
                raw = response.choices[0].message.content or ""
                assist = _parse_response(raw)
                if not assist.rewrites and not assist.filters and not assist.notes:
                    return QueryAssist.empty()
                return assist
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("Search assist returned invalid JSON: %s", exc)
                return QueryAssist.empty()
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "Search assist failed (attempt %d/%d): %s",
                    attempt + 1,
                    self._retries,
                    exc,
                )
                if attempt < self._retries - 1:
                    time.sleep(2**attempt)

        logger.debug("Search assist fallback after failure: %s", last_exc)
        return QueryAssist.empty()
