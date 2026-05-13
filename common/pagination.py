from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import math


@dataclass
class PageResult:
    items: List[Any] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    def __post_init__(self):
        if self.total_pages == 0 and self.page_size > 0:
            self.total_pages = math.ceil(self.total / self.page_size) if self.total > 0 else 0

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


def paginate(items: list, page: int = 1, page_size: int = 20) -> PageResult:
    total = len(items)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return PageResult(
        items=items[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
