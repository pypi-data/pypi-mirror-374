from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import List, Optional, Pattern, Tuple
from loguru import logger


@dataclass
class FirstLetterConfig:
    letter_separator: str = field(default=" ", metadata={"help": "Separator used to join the extracted first letters"})
    indices: Optional[List[int]] = field(default=None, metadata={"help": "0-based indices of words to convert"})
    keywords: Optional[List[str]] = field(default=None, metadata={"help": "Select words containing any keyword"})
    proportion: Optional[float] = field(default=None, metadata={"help": "Proportion [0.0-1.0] of words to convert"})
    regex: Optional[str] = field(default=None, metadata={"help": "Regex pattern (case-insensitive) to select words"})


class FirstLetterMutation:
    name = "first_letter"
    description = "Replace each selected word with its first letter/digit; join results with a separator."

    def __init__(self, config: Optional[FirstLetterConfig] = None):
        self.cfg = config or FirstLetterConfig()
        provided = [
            name for name, val in [
                ("indices", self.cfg.indices),
                ("keywords", self.cfg.keywords),
                ("proportion", self.cfg.proportion),
                ("regex", self.cfg.regex),
            ] if val not in (None, [])
        ]
        if len(provided) > 1:
            raise ValueError(f"Only one of indices/keywords/proportion/regex may be set (got: {provided})")
        self._regex: Optional[Pattern[str]] = re.compile(self.cfg.regex, re.IGNORECASE | re.UNICODE) if self.cfg.regex else None
        self._kw_lower: Optional[List[str]] = [k.lower() for k in (self.cfg.keywords or []) if k] or None
        self._idx_set = set(int(i) for i in (self.cfg.indices or [])) if self.cfg.indices else None

    def mutate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            logger.warning("FirstLetterMutation received non-string input: {}", type(prompt).__name__)
            prompt = str(prompt)

        words = self._split_words(prompt)

        if self._idx_set is not None:
            selected = [tok for tok, i in words if i in self._idx_set]
        elif self._kw_lower is not None:
            selected = [tok for tok, _ in words if any(k in tok.lower() for k in self._kw_lower)]
        elif self._regex is not None:
            selected = [tok for tok, _ in words if self._regex.search(tok)]
        elif isinstance(self.cfg.proportion, float):
            n = len(words)
            k = 0 if self.cfg.proportion <= 0 else (n if self.cfg.proportion >= 1 else math.ceil(self.cfg.proportion * n))
            selected = [tok for tok, i in words if i < k]
        else:
            selected = [tok for tok, _ in words]

        letters: List[str] = []
        for tok in selected:
            stripped = "".join(ch for ch in tok if ch.isalnum())
            if stripped:
                letters.append(stripped[0])

        return self.cfg.letter_separator.join(letters)

    def _split_words(self, s: str) -> List[Tuple[str, int]]:
        if not s:
            return []
        parts = re.split(r"\s+", s.strip(), flags=re.UNICODE)
        out: List[Tuple[str, int]] = []
        for i, tok in enumerate(parts):
            t = tok.strip()
            if t:
                out.append((t, i))
        return out
