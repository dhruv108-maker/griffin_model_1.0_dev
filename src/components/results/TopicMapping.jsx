import { useMemo, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  CircleDashed,
  Search,
  XCircle,
} from "lucide-react";

function normalizeStatus(topic) {
  const raw = String(
    topic?.status ||
      topic?.coverage_status ||
      topic?.match_status ||
      ""
  ).toLowerCase();

  if (
    raw.includes("partial") ||
    raw.includes("weak")
  ) {
    return "partial";
  }

  if (
    raw.includes("missing") ||
    raw.includes("uncovered") ||
    raw.includes("not_covered")
  ) {
    return "missing";
  }

  if (
    raw.includes("covered") ||
    raw.includes("matched") ||
    raw === "match"
  ) {
    return "covered";
  }

  if (topic?.covered === true || topic?.matched === true) {
    return "covered";
  }

  if (
    topic?.covered === false ||
    topic?.matched === false
  ) {
    return "missing";
  }

  return "unknown";
}

function normalizeTopics(mapping) {
  if (!mapping) return [];

  if (Array.isArray(mapping)) {
    return mapping;
  }

  if (Array.isArray(mapping.topics)) {
    return mapping.topics;
  }

  if (Array.isArray(mapping.topic_mapping)) {
    return mapping.topic_mapping;
  }

  if (Array.isArray(mapping.items)) {
    return mapping.items;
  }

  /*
   * Some Griffin result structures may group topics
   * under units. Preserve the actual topic objects
   * while attaching the unit label for display.
   */
  if (Array.isArray(mapping.units)) {
    return mapping.units.flatMap((unit) => {
      if (!Array.isArray(unit?.topics)) {
        return [];
      }

      return unit.topics.map((topic) => ({
        ...topic,
        unit_name:
          topic?.unit_name ||
          unit?.unit_name ||
          unit?.name ||
          unit?.title,
      }));
    });
  }

  return [];
}

function StatusIcon({ status }) {
  if (status === "covered") {
    return (
      <CheckCircle2
        size={16}
        className="griffin-topic-status-icon is-covered"
      />
    );
  }

  if (status === "partial") {
    return (
      <CircleDashed
        size={16}
        className="griffin-topic-status-icon is-partial"
      />
    );
  }

  if (status === "missing") {
    return (
      <XCircle
        size={16}
        className="griffin-topic-status-icon is-missing"
      />
    );
  }

  return (
    <AlertCircle
      size={16}
      className="griffin-topic-status-icon is-unknown"
    />
  );
}

function StatusLabel({ status }) {
  const labels = {
    covered: "Covered",
    partial: "Partially covered",
    missing: "Missing",
    unknown: "Unknown",
  };

  return (
    <span
      className={`griffin-topic-status is-${status}`}
    >
      <StatusIcon status={status} />
      {labels[status]}
    </span>
  );
}

function TopicRow({ topic }) {
  const [expanded, setExpanded] = useState(false);

  const status = normalizeStatus(topic);

  const name =
    topic?.topic_name ||
    topic?.topic ||
    topic?.name ||
    topic?.title ||
    topic?.topic_id ||
    "Untitled topic";

  const unit =
    topic?.unit_name ||
    topic?.unit ||
    topic?.unit_title ||
    topic?.unit_id ||
    "—";

  const pages =
    topic?.supporting_pages ||
    topic?.pages ||
    topic?.page_numbers ||
    [];

  const evidence =
    topic?.evidence ||
    topic?.evidence_text ||
    topic?.supporting_evidence ||
    null;

  const confidence =
    topic?.confidence ??
    topic?.confidence_score ??
    topic?.similarity_score ??
    null;

  const hasDetails =
    Boolean(evidence) ||
    pages?.length > 0 ||
    confidence !== null;

  return (
    <div
      className={`griffin-topic-row is-${status}`}
    >
      <div className="griffin-topic-main">
        <div className="griffin-topic-status-cell">
          <StatusIcon status={status} />
        </div>

        <div className="griffin-topic-name">
          <strong>{name}</strong>

          <span>{unit}</span>
        </div>

        <div className="griffin-topic-status-cell-label">
          <StatusLabel status={status} />
        </div>

        <div className="griffin-topic-pages">
          {pages?.length > 0
            ? pages.map((page) => (
                <span key={page}>
                  p.{page}
                </span>
              ))
            : "—"}
        </div>

        <div className="griffin-topic-confidence">
          {confidence !== null &&
          Number.isFinite(Number(confidence))
            ? Number(confidence).toFixed(3)
            : "—"}
        </div>

        {hasDetails && (
          <button
            type="button"
            className="griffin-topic-expand"
            onClick={() =>
              setExpanded((value) => !value)
            }
            aria-label={
              expanded
                ? "Collapse topic"
                : "Expand topic"
            }
            aria-expanded={expanded}
          >
            <ChevronDown
              size={16}
              className={
                expanded ? "is-expanded" : ""
              }
            />
          </button>
        )}
      </div>

      {expanded && (
        <div className="griffin-topic-details">
          {evidence && (
            <div className="griffin-topic-detail-block">
              <span>Supporting evidence</span>
              <p>{evidence}</p>
            </div>
          )}

          {pages?.length > 0 && (
            <div className="griffin-topic-detail-block">
              <span>Supporting pages</span>
              <p>
                {pages
                  .map((page) => `Page ${page}`)
                  .join(", ")}
              </p>
            </div>
          )}

          {confidence !== null && (
            <div className="griffin-topic-detail-block">
              <span>Confidence / similarity</span>
              <p>
                {Number.isFinite(Number(confidence))
                  ? Number(confidence).toFixed(4)
                  : String(confidence)}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function TopicMapping({
  result,
  mapping,
}) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");

  const topics = useMemo(
    () =>
      normalizeTopics(
        mapping ||
          result?.topic_mapping
      ),
    [mapping, result]
  );

  const filteredTopics = useMemo(() => {
    const normalizedQuery =
      query.trim().toLowerCase();

    return topics.filter((topic) => {
      const status = normalizeStatus(topic);

      const matchesStatus =
        filter === "all" ||
        status === filter;

      if (!matchesStatus) {
        return false;
      }

      if (!normalizedQuery) {
        return true;
      }

      const searchable = [
        topic?.topic_name,
        topic?.topic,
        topic?.name,
        topic?.title,
        topic?.topic_id,
        topic?.unit_name,
        topic?.unit,
        topic?.unit_id,
        topic?.evidence,
        topic?.evidence_text,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchable.includes(
        normalizedQuery
      );
    });
  }, [topics, query, filter]);

  const counts = useMemo(() => {
    return topics.reduce(
      (accumulator, topic) => {
        const status = normalizeStatus(topic);

        accumulator[status] =
          (accumulator[status] || 0) + 1;

        return accumulator;
      },
      {
        covered: 0,
        partial: 0,
        missing: 0,
        unknown: 0,
      }
    );
  }, [topics]);

  return (
    <section className="griffin-result-section griffin-topic-mapping">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            TOPIC MAPPING
          </span>

          <h2>Topic-level alignment</h2>

          <p>
            Search and inspect the topic mappings
            returned by Griffin.
          </p>
        </div>

        <div className="griffin-topic-total">
          <strong>{topics.length}</strong>
          <span>topics</span>
        </div>
      </div>

      <div className="griffin-topic-toolbar">
        <div className="griffin-topic-search">
          <Search size={16} />

          <input
            type="search"
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            placeholder="Search topics, units, or evidence…"
            aria-label="Search topic mappings"
          />
        </div>

        <div className="griffin-topic-filters">
          <button
            type="button"
            className={
              filter === "all"
                ? "is-active"
                : ""
            }
            onClick={() => setFilter("all")}
          >
            All
            <span>{topics.length}</span>
          </button>

          <button
            type="button"
            className={
              filter === "covered"
                ? "is-active"
                : ""
            }
            onClick={() => setFilter("covered")}
          >
            Covered
            <span>{counts.covered}</span>
          </button>

          <button
            type="button"
            className={
              filter === "partial"
                ? "is-active"
                : ""
            }
            onClick={() => setFilter("partial")}
          >
            Partial
            <span>{counts.partial}</span>
          </button>

          <button
            type="button"
            className={
              filter === "missing"
                ? "is-active"
                : ""
            }
            onClick={() => setFilter("missing")}
          >
            Missing
            <span>{counts.missing}</span>
          </button>
        </div>
      </div>

      <div className="griffin-topic-table">
        <div className="griffin-topic-table-header">
          <span>Status</span>
          <span>Topic</span>
          <span>Classification</span>
          <span>Pages</span>
          <span>Confidence</span>
          <span />
        </div>

        {filteredTopics.length === 0 ? (
          <div className="griffin-topic-empty">
            <AlertCircle size={20} />

            <div>
              <strong>
                {topics.length === 0
                  ? "No topic mappings available"
                  : "No matching topics"}
              </strong>

              <span>
                {topics.length === 0
                  ? "The evaluation result did not contain a topic mapping collection."
                  : "Try a different search term or filter."}
              </span>
            </div>
          </div>
        ) : (
          <div className="griffin-topic-table-body">
            {filteredTopics.map(
              (topic, index) => (
                <TopicRow
                  key={
                    topic?.topic_id ||
                    topic?.id ||
                    `${topic?.topic_name || "topic"}-${index}`
                  }
                  topic={topic}
                />
              )
            )}
          </div>
        )}
      </div>
    </section>
  );
}