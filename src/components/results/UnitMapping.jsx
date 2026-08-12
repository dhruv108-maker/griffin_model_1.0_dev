import { useMemo, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  CircleDashed,
  Layers3,
  Search,
  XCircle,
} from "lucide-react";

function normalizeStatus(unit) {
  const raw = String(
    unit?.status ||
      unit?.coverage_status ||
      unit?.match_status ||
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

  if (unit?.covered === true || unit?.matched === true) {
    return "covered";
  }

  if (
    unit?.covered === false ||
    unit?.matched === false
  ) {
    return "missing";
  }

  return "unknown";
}

function normalizeUnits(mapping) {
  if (!mapping) return [];

  if (Array.isArray(mapping)) {
    return mapping;
  }

  if (Array.isArray(mapping.units)) {
    return mapping.units;
  }

  if (Array.isArray(mapping.unit_mapping)) {
    return mapping.unit_mapping;
  }

  if (Array.isArray(mapping.items)) {
    return mapping.items;
  }

  /*
   * Support keyed unit objects without changing
   * the underlying Griffin data.
   */
  if (
    typeof mapping === "object" &&
    !Array.isArray(mapping)
  ) {
    const entries = Object.entries(mapping);

    const looksLikeUnits = entries.some(
      ([key, value]) =>
        typeof value === "object" &&
        value !== null &&
        (
          value.unit_name ||
          value.unit_id ||
          value.topics
        )
    );

    if (looksLikeUnits) {
      return entries.map(([key, value]) => ({
        ...value,
        unit_id:
          value.unit_id || key,
      }));
    }
  }

  return [];
}

function getTopics(unit) {
  if (Array.isArray(unit?.topics)) {
    return unit.topics;
  }

  if (Array.isArray(unit?.topic_mapping)) {
    return unit.topic_mapping;
  }

  if (Array.isArray(unit?.topic_list)) {
    return unit.topic_list;
  }

  return [];
}

function getTopicName(topic) {
  if (typeof topic === "string") {
    return topic;
  }

  return (
    topic?.topic_name ||
    topic?.topic ||
    topic?.name ||
    topic?.title ||
    topic?.topic_id ||
    "Untitled topic"
  );
}

function getTopicStatus(topic) {
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

  if (
    topic?.covered === true ||
    topic?.matched === true
  ) {
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

function StatusIcon({ status }) {
  if (status === "covered") {
    return (
      <CheckCircle2
        size={16}
        className="griffin-unit-status-icon is-covered"
      />
    );
  }

  if (status === "partial") {
    return (
      <CircleDashed
        size={16}
        className="griffin-unit-status-icon is-partial"
      />
    );
  }

  if (status === "missing") {
    return (
      <XCircle
        size={16}
        className="griffin-unit-status-icon is-missing"
      />
    );
  }

  return (
    <AlertCircle
      size={16}
      className="griffin-unit-status-icon is-unknown"
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
      className={`griffin-unit-status is-${status}`}
    >
      <StatusIcon status={status} />
      {labels[status]}
    </span>
  );
}

function TopicMiniRow({ topic }) {
  const status = getTopicStatus(topic);

  return (
    <div className="griffin-unit-topic">
      <StatusIcon status={status} />

      <span>{getTopicName(topic)}</span>
    </div>
  );
}

function UnitCard({ unit }) {
  const [expanded, setExpanded] = useState(false);

  const status = normalizeStatus(unit);
  const topics = getTopics(unit);

  const name =
    unit?.unit_name ||
    unit?.name ||
    unit?.title ||
    unit?.unit_id ||
    "Untitled unit";

  const unitId =
    unit?.unit_id ||
    unit?.id ||
    null;

  const coverage =
    unit?.coverage_percentage ??
    unit?.coverage_pct ??
    unit?.coverage;

  const coveredTopics =
    unit?.covered_topics ??
    topics.filter(
      (topic) =>
        getTopicStatus(topic) === "covered"
    ).length;

  const missingTopics =
    unit?.missing_topics ??
    topics.filter(
      (topic) =>
        getTopicStatus(topic) === "missing"
    ).length;

  const partialTopics =
    unit?.partially_covered_topics ??
    topics.filter(
      (topic) =>
        getTopicStatus(topic) === "partial"
    ).length;

  const totalTopics =
    unit?.total_topics ??
    topics.length;

  const hasTopics = topics.length > 0;

  return (
    <article
      className={`griffin-unit-card is-${status}`}
    >
      <button
        type="button"
        className="griffin-unit-card-header"
        onClick={() =>
          setExpanded((value) => !value)
        }
      >
        <div className="griffin-unit-card-status">
          <StatusIcon status={status} />
        </div>

        <div className="griffin-unit-card-title">
          <strong>{name}</strong>

          {unitId && (
            <span>{unitId}</span>
          )}
        </div>

        <StatusLabel status={status} />

        <div className="griffin-unit-coverage">
          <span>Coverage</span>

          <strong>
            {Number.isFinite(Number(coverage))
              ? `${Number(coverage).toFixed(1)}%`
              : "—"}
          </strong>
        </div>

        <div className="griffin-unit-topic-count">
          <span>Topics</span>

          <strong>
            {totalTopics}
          </strong>
        </div>

        <ChevronDown
          size={17}
          className={
            expanded ? "is-expanded" : ""
          }
        />
      </button>

      {expanded && (
        <div className="griffin-unit-card-body">
          <div className="griffin-unit-stat-grid">
            <div className="griffin-unit-stat">
              <span>Covered</span>
              <strong>{coveredTopics}</strong>
            </div>

            <div className="griffin-unit-stat">
              <span>Partial</span>
              <strong>{partialTopics}</strong>
            </div>

            <div className="griffin-unit-stat">
              <span>Missing</span>
              <strong>{missingTopics}</strong>
            </div>

            <div className="griffin-unit-stat">
              <span>Total</span>
              <strong>{totalTopics}</strong>
            </div>
          </div>

          {hasTopics ? (
            <div className="griffin-unit-topics">
              <div className="griffin-unit-topics-header">
                <span>Topics in this unit</span>
              </div>

              {topics.map((topic, index) => (
                <TopicMiniRow
                  key={
                    topic?.topic_id ||
                    topic?.id ||
                    `${name}-${index}`
                  }
                  topic={topic}
                />
              ))}
            </div>
          ) : (
            <div className="griffin-unit-no-topics">
              <AlertCircle size={15} />
              <span>
                No topic-level data returned for
                this unit.
              </span>
            </div>
          )}
        </div>
      )}
    </article>
  );
}

export default function UnitMapping({
  result,
  mapping,
}) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");

  const units = useMemo(
    () =>
      normalizeUnits(
        mapping ||
          result?.curriculum_mapping
      ),
    [mapping, result]
  );

  const counts = useMemo(() => {
    return units.reduce(
      (accumulator, unit) => {
        const status = normalizeStatus(unit);

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
  }, [units]);

  const filteredUnits = useMemo(() => {
    const normalizedQuery =
      query.trim().toLowerCase();

    return units.filter((unit) => {
      const status = normalizeStatus(unit);

      if (
        filter !== "all" &&
        status !== filter
      ) {
        return false;
      }

      if (!normalizedQuery) {
        return true;
      }

      const topics = getTopics(unit);

      const searchable = [
        unit?.unit_name,
        unit?.name,
        unit?.title,
        unit?.unit_id,
        ...topics.map(getTopicName),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchable.includes(
        normalizedQuery
      );
    });
  }, [units, query, filter]);

  return (
    <section className="griffin-result-section griffin-unit-mapping">
      <div className="griffin-result-section-header">
        <div>
          <span className="griffin-eyebrow">
            CURRICULUM MAPPING
          </span>

          <h2>Unit-level alignment</h2>

          <p>
            Inspect curriculum units and expand each
            unit to examine its topic-level coverage.
          </p>
        </div>

        <div className="griffin-unit-total">
          <Layers3 size={17} />

          <div>
            <strong>{units.length}</strong>
            <span>units</span>
          </div>
        </div>
      </div>

      <div className="griffin-unit-toolbar">
        <div className="griffin-unit-search">
          <Search size={16} />

          <input
            type="search"
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            placeholder="Search units or topics…"
            aria-label="Search curriculum units"
          />
        </div>

        <div className="griffin-unit-filters">
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
            <span>{units.length}</span>
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

      <div className="griffin-unit-list">
        {filteredUnits.length === 0 ? (
          <div className="griffin-unit-empty">
            <AlertCircle size={20} />

            <div>
              <strong>
                {units.length === 0
                  ? "No curriculum mapping available"
                  : "No matching units"}
              </strong>

              <span>
                {units.length === 0
                  ? "The evaluation result did not contain a usable curriculum unit collection."
                  : "Try a different search term or filter."}
              </span>
            </div>
          </div>
        ) : (
          filteredUnits.map((unit, index) => (
            <UnitCard
              key={
                unit?.unit_id ||
                unit?.id ||
                `${unit?.unit_name || "unit"}-${index}`
              }
              unit={unit}
            />
          ))
        )}
      </div>
    </section>
  );
}