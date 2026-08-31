export default function WorkspaceTabs({
  tabs = [],
  activeTab,
  onChange,
  disabled = false,
}) {
  const handleKeyDown = (event, currentIndex) => {
    if (disabled || !tabs.length) return;

    let nextIndex = currentIndex;
    if (event.key === "ArrowRight") {
      nextIndex = (currentIndex + 1) % tabs.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = tabs.length - 1;
    } else {
      return;
    }

    event.preventDefault();
    onChange?.(tabs[nextIndex].id);
    const tabList = event.currentTarget.parentElement;
    tabList?.children[nextIndex]?.focus();
  };

  return (
    <nav
      className="griffin-workspace-tabs"
      aria-label="Analysis sections"
    >
      <div
        className="griffin-workspace-tabs-inner"
        role="tablist"
      >
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              type="button"
              className={`griffin-workspace-tab ${
                isActive ? "is-active" : ""
              }`}
              onClick={() => onChange?.(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              disabled={disabled}
              aria-selected={isActive}
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