export default function WorkspaceTabs({
  tabs = [],
  activeTab,
  onChange,
  disabled = false,
}) {
  const handleKeyDown = (event, index) => {
    if (disabled || !tabs.length) return;

    let nextIndex = index;
    if (event.key === "ArrowRight") {
      event.preventDefault();
      nextIndex = (index + 1) % tabs.length;
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      nextIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      event.preventDefault();
      nextIndex = 0;
    } else if (event.key === "End") {
      event.preventDefault();
      nextIndex = tabs.length - 1;
    } else {
      return;
    }

    const nextTab = tabs[nextIndex];
    if (nextTab) {
      onChange?.(nextTab.id);
      const buttons = event.currentTarget.parentElement?.querySelectorAll('[role="tab"]');
      if (buttons && buttons[nextIndex]) {
        buttons[nextIndex].focus();
      }
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
              id={`workspace-tab-${tab.id}`}
              type="button"
              className={`griffin-workspace-tab ${
                isActive ? "is-active" : ""
              }`}
              onClick={() => onChange?.(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              disabled={disabled}
              aria-selected={isActive}
              aria-controls={`workspace-panel-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              role="tab"
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}