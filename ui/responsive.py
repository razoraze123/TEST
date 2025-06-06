"""Simple responsive helper and mixin for Qt widgets."""

class ResponsiveMixin:
    """Mixin adjusting layout metrics on window resize."""

    # width breakpoints -> settings
    BREAKPOINTS = [
        # mobile phones
        (0, {"margin": 6, "spacing": 4, "font": 11, "collapse": True}),
        (480, {"margin": 10, "spacing": 8, "font": 12, "collapse": True}),
        # tablets
        (768, {"margin": 20, "spacing": 12, "font": 14, "collapse": False}),
        # small desktop
        (1024, {"margin": 30, "spacing": 16, "font": 15, "collapse": False}),
        # large desktop
        (1440, {"margin": 40, "spacing": 20, "font": 16, "collapse": False}),
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
