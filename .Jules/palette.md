## 2025-08-27 - Accessible ARIA Tablist Pattern for Navigation Tabs
**Learning:** Workspace tabs in Griffin Console required WAI-ARIA 1.2 tablist roving tabindex and arrow key navigation (`ArrowLeft`, `ArrowRight`, `Home`, `End`) to satisfy accessibility standards and allow screen reader & keyboard users to navigate panels smoothly.
**Action:** When creating or editing tabbed interfaces, ensure `role="tablist"` wraps `role="tab"` buttons with roving `tabIndex={isActive ? 0 : -1}`, `aria-controls`, and `onKeyDown` handlers linking to the active `role="tabpanel"`.
