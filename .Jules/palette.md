## 2025-05-18 - Accessible Roving TabIndex for Navigation Tabs
**Learning:** Standard tab navigation controls require `role="tablist"` on container, roving `tabIndex` (`0` for active, `-1` for inactive), and keyboard handlers (`ArrowRight`, `ArrowLeft`, `Home`, `End`) to meet WAI-ARIA standards and ensure smooth screen reader/keyboard UX.
**Action:** Always link tabs with `aria-controls` to panels (`role="tabpanel"`) and manage focus explicitly when arrow keys cycle through options.
