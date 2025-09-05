# pyright: reportUnknownMemberType=information

from typing import Self

from hexdoc_hexcasting.book.page.abstract_pages import PageWithOpPattern # pyright: ignore[reportMissingTypeStubs]
from hexdoc_hexcasting.metadata import HexContext
from hexdoc_hexcasting.utils.pattern import PatternInfo
from pydantic import ValidationInfo, model_validator
from ..merge_pattern import HexCoord, overlay_patterns

# Look mom, I'm here. Very top of Arasaka tower.
class LookupPWShapePage(PageWithOpPattern, type="hexcasting:lapisworks/pwshape"):
    origins: list[HexCoord] | None = None

    @property
    def patterns(self) -> list[PatternInfo]:
        return self._patterns
    
    @model_validator(mode="after")
    def _post_root_lookup(self, info: ValidationInfo):
        if self.origins == None: raise TypeError("No origins provided for " + str(self.op_id))
        hex_ctx = HexContext.of(info)
        patterns: list[tuple[PatternInfo, HexCoord]] = []
        i = 0
        while pattern := hex_ctx.patterns.get(self.op_id + str(i)):
            patterns.append((pattern, self.origins[i]))
            i += 1

        self._patterns = [overlay_patterns(self.op_id, patterns)]
        return self
    
    @model_validator(mode="after")
    def _check_anchor(self) -> Self:
        if str(self.op_id) != self.anchor:
            raise ValueError(f"op_id={self.op_id} does not equal anchor={self.anchor}")
        return self
