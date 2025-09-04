from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Optional
from loguru import logger


@dataclass
class FlipConfig:
    """
    Configuration for FlipMutation.

    - preserve_lines: reverse each line independently (keeps line order).
    - preserve_words: reverse characters inside each word but keep word order/spaces.
      (If both flags are False, reverse the entire string.)
    """
    preserve_lines: bool = field(default=False, metadata={"help": "Reverse each line independently"})
    preserve_words: bool = field(default=False, metadata={"help": "Reverse characters per word; keep word order"})


class FlipMutation:
    """
    Simple prompt converter: reverses text.

    Examples
    --------
    >>> FlipMutation(FlipConfig()).mutate("hello me")
    'em olleh'
    >>> FlipMutation(FlipConfig(preserve_words=True)).mutate("hello me")
    'olleh em'
    """

    name = "flip"
    description = "Reverse the text (optionally per-line or per-word)."

    def __init__(self, config: Optional[FlipConfig] = None):
        self.cfg = config or FlipConfig()

    def mutate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            logger.warning("FlipMutation received non-string input: {}", type(prompt).__name__)
            return str(prompt)

        if self.cfg.preserve_lines:
            return self._reverse_per_line(prompt)

        if self.cfg.preserve_words:
            return self._reverse_per_word(prompt)

        # Default: reverse entire string
        return prompt[::-1]

    @staticmethod
    def _reverse_per_line(text: str) -> str:
        # keep newline characters with their original line
        out_lines = []
        for line in re.split(r"(\r?\n)", text):
            if line in ("\n", "\r\n"):
                out_lines.append(line)
            else:
                out_lines.append(line[::-1])
        return "".join(out_lines)

    @staticmethod
    def _reverse_per_word(text: str) -> str:
        # split into tokens while preserving whitespace
        tokens = re.split(r"(\s+)", text)
        flipped = [
            tok if tok.isspace() else tok[::-1]
            for tok in tokens
        ]
        return "".join(flipped)
