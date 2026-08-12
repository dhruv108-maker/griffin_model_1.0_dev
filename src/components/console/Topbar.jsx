import {
  Activity,
  Bell,
  ChevronDown,
} from "lucide-react";

export default function Topbar({
  workspaceName = "Griffin Console",
  context = "Analysis Workspace",
  backendOnline = true,
}) {
  return (
    <header className="griffin-topbar">
      <div className="griffin-topbar-context">
        <div className="griffin-context-indicator">
          <span
            className={`griffin-status-dot ${
              backendOnline
                ? "is-online"
                : "is-offline"
            }`}
          />

          <span>{workspaceName}</span>
        </div>

        <span className="griffin-context-separator">
          /
        </span>

        <span className="griffin-context-muted">
          {context}
        </span>
      </div>

      <div className="griffin-topbar-actions">
        <button
          type="button"
          className="griffin-icon-button"
          title={
            backendOnline
              ? "Backend connected"
              : "Backend unavailable"
          }
          aria-label="Backend status"
        >
          <Activity size={17} />
        </button>

        <button
          type="button"
          className="griffin-icon-button"
          title="Notifications"
          aria-label="Notifications"
        >
          <Bell size={17} />
        </button>

        <button
          type="button"
          className="griffin-profile-button"
          aria-label="Open profile menu"
        >
          <span className="griffin-avatar">
            G
          </span>

          <span className="griffin-profile-name">
            User
          </span>

          <ChevronDown size={15} />
        </button>
      </div>
    </header>
  );
}