const fs = require("fs");
const path = require("path");

const ACTOR_ORDER = ["codex", "claude", "gemini"];
const ACTOR_LABELS = {
  codex: "CODX",
  claude: "CLAU",
  gemini: "GEMI",
};

const STATE_COLORS = {
  ACTIVE: 36,
  REQUESTED: 33,
  DISPATCHING: 33,
  COMPLETED: 32,
  DEGRADED: 31,
  SUPPRESSED: 90,
  IDLE: 90,
  INTEGRATING: 34,
};

function createRunId(prefix = "evcode") {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const random = Math.random().toString(16).slice(2, 8);
  return `${prefix}-${stamp}-${random}`;
}

function resolveSessionRoot({ root, artifactsRoot, runId }) {
  return path.join(artifactsRoot || root, "outputs", "runtime", "vibe-sessions", runId);
}

function loadRuntimeSummary(sessionRoot) {
  const summaryPath = path.join(sessionRoot, "runtime-summary.json");
  if (!fs.existsSync(summaryPath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(summaryPath, "utf8"));
}

function loadRuntimeEvents(eventsPath) {
  if (!eventsPath || !fs.existsSync(eventsPath)) {
    return [];
  }
  return fs.readFileSync(eventsPath, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function synthesizeEventsFromSummary(summary) {
  if (!summary || !summary.specialist_routing) {
    return [];
  }
  const events = [];
  let seq = 0;
  const push = (event) => events.push({ seq: ++seq, ts: "", phase: "plan_execute", ...event });
  const route = summary.specialist_routing;
  push({
    actor: "route",
    state: "CLASSIFIED",
    message: `task classified as ${route.classification?.domain || "unknown"} (route=${route.route_kind || "unknown"}, final_executor=${route.final_executor || "codex"})`,
    content_kind: "route",
  });
  push({ actor: "codex", state: "ACTIVE", message: "codex-led governed execution authority is active", content_kind: "status" });
  for (const item of route.requested_delegates || []) {
    push({ actor: item.assistant_name, state: "REQUESTED", message: item.purpose || "specialist requested", content_kind: "status", content: item.reason || "" });
  }
  for (const item of route.suppressed_delegates || []) {
    push({ actor: item.assistant_name, state: "SUPPRESSED", message: item.reason || "specialist suppressed", content_kind: "status" });
  }
  for (const item of route.degraded_delegates || []) {
    push({ actor: item.assistant_name, state: "DEGRADED", message: item.status || "specialist degraded", content_kind: "warning", content: item.reason || "" });
  }
  if (summary.warnings?.length) {
    for (const warning of summary.warnings) {
      push({ actor: warning.assistant_name || "system", state: "DEGRADED", message: warning.message || "specialist warning", content_kind: "warning", content: warning.reason || "" });
    }
  }
  push({ actor: "codex", state: "COMPLETED", message: `governed execution phase closed with outcome=${summary.execution_outcome || "unknown"}`, content_kind: "status" });
  return events;
}

function shouldUseColor(options = {}) {
  if (options.noColor || process.env.NO_COLOR) {
    return false;
  }
  return Boolean(options.isTTY);
}

function colorize(text, state, options = {}) {
  if (!shouldUseColor(options)) {
    return text;
  }
  const code = STATE_COLORS[state];
  if (!code) {
    return text;
  }
  return `\u001b[${code}m${text}\u001b[0m`;
}

function truncate(text, limit = 96) {
  if (!text) {
    return "";
  }
  const normalized = String(text).replace(/\s+/g, " ").trim();
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, limit - 3).trimEnd()}...`;
}

function getActorsFromEvents(events) {
  const actors = {
    codex: { state: "IDLE", status: "awaiting route" },
    claude: { state: "IDLE", status: "not selected" },
    gemini: { state: "IDLE", status: "not selected" },
  };
  for (const event of events) {
    if (!ACTOR_ORDER.includes(event.actor)) {
      continue;
    }
    const preferredStatus = event.state === "COMPLETED" && event.content_kind === "result_summary"
      ? event.content
      : event.message;
    actors[event.actor] = {
      state: event.state || actors[event.actor].state,
      status: truncate(preferredStatus || actors[event.actor].status, 56),
    };
  }
  return actors;
}

function eventLabel(event) {
  if (event.actor === "route") {
    return "route ";
  }
  if (event.actor === "system") {
    return "system";
  }
  const actor = event.actor || "event";
  return `${actor} `.slice(0, 6).padEnd(6, " ");
}

function formatEventLine(event, options = {}) {
  const prefix = `[${eventLabel(event)}]`;
  const base = `${prefix} ${event.message}`;
  if (!options.trace || !event.content) {
    return base;
  }
  return `${base}\n  -> ${truncate(event.content, 140)}`;
}

function buildHeader(summary, context = {}) {
  const routeEvent = (context.events || []).find((event) => event.actor === "route");
  const route = summary?.specialist_routing?.route_kind || routeEvent?.meta?.route_kind || context.routeKind || "pending";
  const domain = summary?.specialist_routing?.classification?.domain || routeEvent?.meta?.domain || context.domain || "pending";
  const finalExecutor = summary?.specialist_routing?.final_executor || "codex";
  return [
    "EvCode Governed Run",
    `run_id: ${summary?.run_id || context.runId || "pending"}`,
    `route: ${route}`,
    `domain: ${domain}`,
    `final_executor: ${finalExecutor}`,
  ].join("\n");
}

function buildActorBoard(events, options = {}) {
  const actors = getActorsFromEvents(events);
  const rows = ["Actors"];
  for (const actor of ACTOR_ORDER) {
    const label = (ACTOR_LABELS[actor] || actor.toUpperCase()).padEnd(4, " ");
    const state = (actors[actor]?.state || "IDLE").padEnd(11, " ");
    const coloredState = colorize(state, actors[actor]?.state || "IDLE", options);
    rows.push(`${label}  ${coloredState} ${actors[actor]?.status || ""}`);
  }
  return rows.join("\n");
}

function buildRecentActivity(events, options = {}) {
  const recent = events.slice(-8);
  const lines = [options.trace ? "Timeline" : "Recent Activity"];
  if (!recent.length) {
    lines.push("[system] waiting for runtime events");
    return lines.join("\n");
  }
  for (const event of recent) {
    lines.push(formatEventLine(event, options));
  }
  return lines.join("\n");
}

function buildArtifactsFooter(summary) {
  const sessionRoot = summary?.artifacts?.session_root;
  const events = summary?.artifacts?.runtime_events;
  if (!sessionRoot && !events) {
    return "";
  }
  const lines = ["Artifacts"];
  if (sessionRoot) {
    lines.push(`session_root: ${sessionRoot}`);
  }
  if (events) {
    lines.push(`runtime_events: ${events}`);
  }
  return lines.join("\n");
}

function renderRuntimeView(summary, events, options = {}) {
  const sections = [
    buildHeader(summary, { ...(options.context || {}), events }),
    "",
    buildActorBoard(events, options),
    "",
    buildRecentActivity(events, options),
  ];
  const footer = buildArtifactsFooter(summary);
  if (footer) {
    sections.push("", footer);
  }
  return sections.join("\n");
}

module.exports = {
  createRunId,
  resolveSessionRoot,
  loadRuntimeSummary,
  loadRuntimeEvents,
  synthesizeEventsFromSummary,
  renderRuntimeView,
  formatEventLine,
};
