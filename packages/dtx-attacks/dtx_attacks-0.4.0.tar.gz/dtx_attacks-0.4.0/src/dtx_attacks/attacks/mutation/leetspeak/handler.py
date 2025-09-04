from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Pattern, Tuple
from loguru import logger


@dataclass
class LeetspeakConfig:
    deterministic: bool = field(default=True, metadata={"help": "Use first substitution per char if True; else random"})
    custom_substitutions: Optional[Dict[str, List[str]]] = field(default=None, metadata={"help": "Override default leet map"})
    indices: Optional[List[int]] = field(default=None, metadata={"help": "0-based indices of words to convert"})
    keywords: Optional[List[str]] = field(default=None, metadata={"help": "Select words containing any keyword"})
    proportion: Optional[float] = field(default=None, metadata={"help": "Proportion [0.0-1.0] of words to convert"})
    regex: Optional[str] = field(default=None, metadata={"help": "Regex pattern (case-insensitive) to select words"})


class LeetspeakMutation:
    name = "leetspeak"
    description = "Convert selected words to 1337 substitutions; preserves original spacing and punctuation."

    def __init__(self, config: Optional[LeetspeakConfig] = None):
        self.cfg = config or LeetspeakConfig()
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
        self._subs: Dict[str, List[str]] = self.cfg.custom_substitutions or {
            "a": ["4", "@", "/\\", "@", "^", "/-\\"],
            "b": ["8", "6", "13", "|3", "/3", "!3"],
            "c": ["(", "[", "<", "{"],
            "e": ["3"],
            "g": ["9"],
            "i": ["1", "!"],
            "l": ["1", "|"],
            "o": ["0"],
            "s": ["5", "$"],
            "t": ["7"],
            "z": ["2"],
        }

    def mutate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            logger.warning("LeetspeakMutation received non-string input: {}", type(prompt).__name__)
            prompt = str(prompt)

        parts = self._split_keep_seps(prompt)
        word_positions = [i for i, tok in enumerate(parts) if i % 2 == 0]
        words = [parts[i] for i in word_positions]
        n = len(words)

        if self._idx_set is not None:
            sel_idx = set(i for i in range(n) if i in self._idx_set)
        elif self._kw_lower is not None:
            sel_idx = set(i for i, w in enumerate(words) if any(k in w.lower() for k in self._kw_lower))
        elif self._regex is not None:
            sel_idx = set(i for i, w in enumerate(words) if self._regex.search(w))
        elif isinstance(self.cfg.proportion, float):
            k = 0 if self.cfg.proportion <= 0 else (n if self.cfg.proportion >= 1 else math.ceil(self.cfg.proportion * n))
            sel_idx = set(range(k))
        else:
            sel_idx = set(range(n))

        out_parts: List[str] = []
        wi = 0
        for j, tok in enumerate(parts):
            if j % 2 == 1:
                out_parts.append(tok)
                continue
            if wi in sel_idx:
                out_parts.append(self._convert_word(tok))
            else:
                out_parts.append(tok)
            wi += 1

        return "".join(out_parts)

    def _convert_word(self, word: str) -> str:
        if self.cfg.deterministic:
            return "".join(self._subs.get(ch.lower(), [ch])[0] if ch.lower() in self._subs else ch for ch in word)
        out = []
        for ch in word:
            low = ch.lower()
            if low in self._subs:
                lst = self._subs[low]
                out.append(lst[0] if len(lst) == 1 else random.choice(lst))
            else:
                out.append(ch)
        return "".join(out)

    def _split_keep_seps(self, s: str) -> List[str]:
        if not s:
            return []
        tokens = re.split(r"(\s+)", s, flags=re.UNICODE)
        if tokens and tokens[-1] == "":
            tokens = tokens[:-1]
        return tokens
