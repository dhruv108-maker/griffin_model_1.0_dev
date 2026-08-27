import { useRef } from "react";

export default function WorkspaceTabs({
  tabs = [],
  activeTab,
  onChange,
  disabled = false,
}) {
  const tabRefs = useRef({});

  const handleKeyDown = (event, currentIndex) => {
    if (disabled || !tabs.length) return;

    let targetIndex = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      targetIndex = (currentIndex + 1) % tabs.length;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      targetIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      event.preventDefault();
      targetIndex = 0;
    } else if (event.key === "End") {
      event.preventDefault();
      targetIndex = tabs.length - 1;
    }

    if (targetIndex !== null) {
      const targetTab = tabs[targetIndex];
      onChange?.(targetTab.id);
      tabRefs.current[targetTab.id]?.focus();
    }
  };

  return (
    <nav
      className="griffin-workspace-tabs"
      aria-label="Analysis sections"
    >
      <div
        className="griffin-workspace-tabs-inner"
        role="tablist"
        aria-label="Analysis sections"
      >
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              ref={(element) => {
                if (element) {
                  tabRefs.current[tab.id] = element;
                }
              }}
              id={`tab-${tab.id}`}
              type="button"
              className={`griffin-workspace-tab ${
                isActive ? "is-active" : ""
              }`}
              onClick={() => onChange?.(tab.id)}
              onKeyDown={(event) => handleKeyDown(event, index)}
              disabled={disabled}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}