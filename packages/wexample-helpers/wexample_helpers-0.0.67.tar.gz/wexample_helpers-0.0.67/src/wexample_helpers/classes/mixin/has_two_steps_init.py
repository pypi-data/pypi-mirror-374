from __future__ import annotations


class HasTwoStepInit:
    is_setup: bool = False

    def setup(self) -> HasTwoStepInit:
        self.is_setup = True
        return self
