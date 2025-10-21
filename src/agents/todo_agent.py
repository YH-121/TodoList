"""
NLP による自然言語 → タスク抽出のダミー実装。

本実装では単純に改行または句読点で分割し、
空でないフレーズをタイトルとして返すのみ。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ExtractedTask:
    title: str
    due: Optional[datetime] = None


def extract_tasks(text: str) -> List[ExtractedTask]:
    candidates = [s.strip() for s in text.replace("\n", ",").split(",")]
    return [ExtractedTask(title=c) for c in candidates if c]

