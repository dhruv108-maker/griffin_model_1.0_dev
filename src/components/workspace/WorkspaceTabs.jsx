export default function WorkspaceTabs({
  tabs = [],
  activeTab,
  onChange,
  disabled = false,
}) {
  const handleKeyDown = (event, currentIndex) => {
    if (disabled || !tabs.length) return;

    let targetIndex = null;

    if (event.key === "ArrowRight") {
      targetIndex = (currentIndex + 1) % tabs.length;
    } else if (event.key === "ArrowLeft") {
      targetIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      targetIndex = 0;
    } else if (event.key === "End") {
      targetIndex = tabs.length - 1;
    }

    if (targetIndex !== null) {
      event.preventDefault();
      const targetTab = tabs[targetIndex];
      onChange?.(targetTab.id);
      const targetEl = event.currentTarget.parentElement?.children[targetIndex];
      targetEl?.focus();
    }
  };

  return (
    <nav
      className="griffin-workspace-tabs"
      aria-label="Analysis sections"
    >
      <div className="griffin-workspace-tabs-inner" role="tablist">
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              type="button"
              className={`griffin-workspace-tab ${
                isActive ? "is-active" : ""
              }`}
              onClick={() => onChange?.(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              disabled={disabled}
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
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