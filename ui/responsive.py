"""Simple responsive helper and mixin for Qt widgets."""

class ResponsiveMixin:
    """Mixin adjusting layout metrics on window resize."""

    # width breakpoints -> settings
    BREAKPOINTS = [
        (0, {"margin": 10, "spacing": 8, "font": 12, "collapse": True}),
        (700, {"margin": 20, "spacing": 15, "font": 14, "collapse": False}),
        (1100, {"margin": 30, "spacing": 20, "font": 16, "collapse": False}),
    ]

    def _responsive_values(self, width):
        values = {}
        for w, vals in self.BREAKPOINTS:
            if width >= w:
                values = vals
            else:
                break
        return values

    def resizeEvent(self, event):
        super().resizeEvent(event)
        vals = self._responsive_values(self.width())
        self.apply_responsive(vals)

    # ------------------------------------------------------------------
    def apply_responsive(self, values):
        """Override in subclasses to consume responsive metrics."""
        pass
