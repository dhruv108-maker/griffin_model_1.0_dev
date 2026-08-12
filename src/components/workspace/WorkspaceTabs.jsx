export default function WorkspaceTabs({
  tabs = [],
  activeTab,
  onChange,
  disabled = false,
}) {
  return (
    <nav
      className="griffin-workspace-tabs"
      aria-label="Analysis sections"
    >
      <div className="griffin-workspace-tabs-inner">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              type="button"
              className={`griffin-workspace-tab ${
                isActive ? "is-active" : ""
              }`}
              onClick={() => onChange?.(tab.id)}
              disabled={disabled}
              aria-selected={isActive}
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