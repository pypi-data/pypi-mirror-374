from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from loguru import logger


@dataclass
class DenylistConfig:
    denylist: List[str] = field(default_factory=list, metadata={"help": "Comma-separated forbidden terms/phrases"})
    mode: str = field(default="mask", metadata={"help": "mask|synonym"})
    mask_token: str = field(default="***", metadata={"help": "Replacement when mode=mask or synonym missing"})
    whole_words_only: bool = field(default=True, metadata={"help": "Match only whole words/phrases"})
    case_insensitive: bool = field(default=True, metadata={"help": "Case-insensitive matching"})
    preserve_case: bool = field(default=True, metadata={"help": "Shape replacement case to matched token"})
    pairs: List[str] = field(
        default_factory=list,
        metadata={"help": "Synonym rules like bad=>good1|good2; first is used"},
    )


class DenylistMutation:
    name = "denylist"
    description = "Replace forbidden words/phrases by masking or deterministic synonyms."

    def __init__(self, config: Optional[DenylistConfig] = None):
        self.cfg = config or DenylistConfig()
        self._syn = self._parse_pairs(self.cfg.pairs)

    def mutate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            logger.warning("DenylistMutation received non-string input: {}", type(prompt).__name__)
            return str(prompt)

        terms = [t for t in self.cfg.denylist if t]
        if not terms:
            return prompt

        terms = sorted(terms, key=len, reverse=True)
        flags = re.UNICODE | (re.IGNORECASE if self.cfg.case_insensitive else 0)
        patterns = [self._term_pattern(t, self.cfg.whole_words_only) for t in terms]
        pattern = re.compile("|".join(patterns), flags)

        def choose_synonym(key: str) -> str:
            entry = self._syn.get(key.lower())
            return entry[0] if entry else self.cfg.mask_token

        def shape_case(src: str, repl: str) -> str:
            if not self.cfg.preserve_case:
                return repl
            if src.isupper():
                return repl.upper()
            if src.istitle():
                return repl[:1].upper() + repl[1:].lower()
            if src.islower():
                return repl.lower()
            return repl.upper()

        def repl_fn(m: re.Match) -> str:
            text = m.group(0)
            key = text.lower() if self.cfg.case_insensitive else text
            if self.cfg.mode == "mask":
                return self.cfg.mask_token
            rep = choose_synonym(key)
            return shape_case(text, rep)

        return pattern.sub(repl_fn, prompt)

    @staticmethod
    def _parse_pairs(pairs: List[str]) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for p in pairs:
            if "=>" not in p:
                continue
            k, v = p.split("=>", 1)
            k = k.strip()
            opts = [x.strip() for x in v.split("|") if x.strip()]
            if k and opts:
                out[k.lower()] = opts
        return out

    @staticmethod
    def _term_pattern(term: str, whole: bool) -> str:
        esc = re.escape(term)
        if whole:
            # whole token OR suffix-at-token-end (matches 'handgun' but not 'gunslinger')
            return rf"(?<!\w){esc}(?!\w)|\w+{esc}(?!\w)"
        return esc
