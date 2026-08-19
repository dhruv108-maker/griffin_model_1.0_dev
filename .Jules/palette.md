## 2025-05-18 - ARIA Semantics for Interactive Lists and Tab Containers

**Learning:** Collapsible list items (such as expandable unit/topic cards) require explicit `aria-expanded` attributes on toggle buttons to communicate collapse/expand states to screen readers. Similarly, child tab items with `role="tab"` fail accessibility standards if their parent container lacks `role="tablist"`.
**Action:** Always verify parent container roles (`role="tablist"`) when defining tab controls and ensure collapsible header trigger elements include `aria-expanded={isExpanded}`.
