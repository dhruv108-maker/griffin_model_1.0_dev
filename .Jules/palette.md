## 2025-08-20 - WAI-ARIA Tablist Keyboard Navigation and Roving TabIndex

**Learning:** Buttons with `role="tab"` without a parent `role="tablist"` violate WAI-ARIA accessibility semantics. Screen readers rely on `role="tablist"` parent containers and roving `tabIndex` (`0` for active tab, `-1` for inactive tabs) alongside keyboard arrow key navigation (`ArrowLeft`/`ArrowRight`/`Home`/`End`) to allow efficient navigation across tabbed workspace sections.

**Action:** Whenever creating tab navigation controls, always wrap tabs in a `role="tablist"` container, apply roving `tabIndex`, add `id`/`aria-controls` links, and attach arrow key event handlers for seamless keyboard accessibility.
