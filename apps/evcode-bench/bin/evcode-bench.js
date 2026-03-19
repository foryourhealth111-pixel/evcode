#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");
const providerRuntime = require(path.join(__dirname, "../../../packages/provider-runtime/src/local_provider_env.js"));
const runtimeDisplay = require(path.join(__dirname, "../../evcode/lib/runtime_display.js"));

function loadJson(root, relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function displayPath(root, candidate) {
  const relative = path.relative(root, candidate);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    return candidate;
  }
  return relative;
}

function isSelfManagedCodexHome(root, candidate) {
  if (!candidate) {
    return false;
  }
  const resolvedCandidate = path.resolve(candidate);
  const distRoot = path.resolve(root, ".evcode-dist");
  const relativeToDist = path.relative(distRoot, resolvedCandidate);
  if (relativeToDist === "standard/codex-home" || relativeToDist === "benchmark/codex-home") {
    return true;
  }
  const parentName = path.basename(path.dirname(resolvedCandidate));
  const baseName = path.basename(resolvedCandidate);
  return baseName === "codex-home" && (parentName === "standard" || parentName === "benchmark");
}

function resolveSourceCodexHome(root) {
  const configured = process.env.EVCODE_SOURCE_CODEX_HOME || process.env.CODEX_HOME;
  if (
    configured
    && !isSelfManagedCodexHome(root, configured)
    && fs.existsSync(path.join(configured, "config.toml"))
  ) {
    return configured;
  }
  const fallback = path.join(os.homedir(), ".codex");
  if (fs.existsSync(path.join(fallback, "config.toml"))) {
    return fallback;
  }
  return null;
}

function resolveBundledHost(root) {
  const candidate = path.join(root, ".evcode-build", "host", "codex");
  return fs.existsSync(candidate) ? candidate : null;
}

function buildAssemblyArgs(root, passthroughArgs = []) {
  const args = [
    path.join(root, "scripts", "build", "assemble_distribution.py"),
    "--channel",
    "benchmark",
    ...passthroughArgs
  ];
  if (!passthroughArgs.includes("--source-codex-home")) {
    const sourceCodexHome = resolveSourceCodexHome(root);
    if (sourceCodexHome) {
      args.push("--source-codex-home", sourceCodexHome);
    }
  }
  if (!passthroughArgs.includes("--bundled-host-binary")) {
    const bundledHost = resolveBundledHost(root);
    if (bundledHost) {
      args.push("--bundled-host-binary", bundledHost);
    }
  }
  return args;
}

function buildGovernanceSurface(assistantPolicy, routingPolicy) {
  const assistants = {};
  for (const [assistantName, config] of Object.entries(assistantPolicy.assistants || {})) {
    const capabilityAccess = config.capability_access || {};
    assistants[assistantName] = {
      authority_tier: config.authority_tier || null,
      capability_mode: capabilityAccess.mode || null,
      required_skill_capsules: [...(config.required_skill_capsules || [])]
    };
  }
  return {
    control_plane: "vco",
    final_executor: assistantPolicy.execution_authority,
    persistent_memory_owner: assistantPolicy.persistent_memory_owner,
    mutation_policy: assistantPolicy.mutation_policy,
    capability_transport: "mcp",
    capability_classes: Object.keys((routingPolicy.capability_policy || {}).classes || {}),
    default_specialist_capability_mode: routingPolicy.capability_policy?.default_specialist_mode || null,
    assistants,
  };
}

function buildBaselineSurface(root, profile) {
  const configPath = profile.baseline_families_config || "config/baseline-families.json";
  const catalog = loadJson(root, configPath);
  const familyName = profile.baseline_family || null;
  return {
    config_path: configPath,
    family: familyName,
    definition: familyName ? catalog.families?.[familyName] || null : null,
  };
}

function buildProviderSetup(root) {
  return {
    local_env_path: displayPath(root, providerEnvState.canonical_local_env_path),
    repo_local_env_path: displayPath(root, providerEnvState.repo_local_env_path),
    portable_config_root: displayPath(root, providerEnvState.portable_config_root),
    portable_env_path: displayPath(root, providerEnvState.portable_env_path),
    resolved_local_env_path: displayPath(root, providerEnvState.resolved_local_env_path),
    active_env_source: providerEnvState.active_env_source,
    example_env_path: displayPath(root, providerEnvState.example_env_path),
    setup_doc_path: displayPath(root, providerEnvState.setup_doc_path),
    local_env_present: providerEnvState.local_env_present,
    loaded_from_file: providerEnvState.loaded_from_file,
    loaded_keys: providerEnvState.loaded_keys,
    skipped_keys: providerEnvState.skipped_keys,
  };
}

function printRunUsage(commandName) {
  console.log(`Usage: ${commandName} run --task <task> [--workspace PATH] [--artifacts-root PATH] [--result-json PATH] [--run-id ID] [--json]`);
}

function printTraceUsage(commandName) {
  console.log(`Usage: ${commandName} trace <run-id> [--artifacts-root PATH] [--json]`);
}

function hasFlag(args, name) {
  return args.includes(name);
}

function valueForFlag(args, name, fallback = "") {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
}

function status(root) {
  const distributions = loadJson(root, "config/distributions.json");
  const runtime = loadJson(root, "config/runtime-contract.json");
  const policy = loadJson(root, "config/provider-policy.benchmark.json");
  const profile = loadJson(root, "profiles/benchmark/profile.json");
  const assistantPolicy = loadJson(root, profile.assistant_policy);
  const routingPolicy = loadJson(root, profile.specialist_routing);
  return {
    product: "EvCode Bench",
    channel: "benchmark",
    mode: distributions.channels.benchmark.default_mode,
    profile: distributions.channels.benchmark.profile,
    host: runtime.host_baseline,
    embedded_runtime_version: runtime.embedded_runtime_version,
    provider_families: policy.allowed_provider_families,
    assistant_policy: profile.assistant_policy,
    specialist_routing: profile.specialist_routing,
    baseline_family: profile.baseline_family || null,
    baseline_families_config: profile.baseline_families_config || null,
    specialist_rollout_phase: assistantPolicy.rollout_phase,
    assistants: Object.keys(assistantPolicy.assistants),
    default_submission_preset: profile.default_submission_preset || null,
    assembled_distribution_exists: fs.existsSync(path.join(root, ".evcode-dist", "benchmark", "bin", "evcode-bench")),
    source_codex_home: resolveSourceCodexHome(root),
    bundled_host_available: Boolean(resolveBundledHost(root)),
    baseline_surface: buildBaselineSurface(root, profile),
    provider_setup: buildProviderSetup(root),
    governance_surface: buildGovernanceSurface(assistantPolicy, routingPolicy),
    assistant_api_compatibility: providerRuntime.OPENAI_COMPATIBILITY_SUMMARY,
    assistant_provider_resolution: providerRuntime.summarizeAssistantProviders(assistantPolicy, process.env)
  };
}

function run(root) {
  const args = process.argv.slice(3);
  const task = valueForFlag(args, "--task");
  if (hasFlag(args, "--help") || hasFlag(args, "-h")) {
    printRunUsage("evcode-bench");
    process.exit(0);
  }
  if (!task) {
    console.error("Missing --task for run");
    process.exit(1);
  }
  const workspace = valueForFlag(args, "--workspace", root);
  const artifactsRoot = valueForFlag(args, "--artifacts-root", fs.mkdtempSync(path.join(os.tmpdir(), "evcode-bench-artifacts-")));
  const runId = valueForFlag(args, "--run-id", runtimeDisplay.createRunId("evcode-bench"));
  const resultJson = valueForFlag(args, "--result-json", "");
  const result = spawnSync(
    "python3",
    [
      path.join(root, "scripts/runtime/run_governed_runtime.py"),
      "--task",
      task,
      "--mode",
      "benchmark_autonomous",
      "--channel",
      "benchmark",
      "--profile",
      "benchmark",
      "--repo-root",
      root,
      "--workspace",
      workspace,
      "--artifacts-root",
      artifactsRoot,
      "--run-id",
      runId,
      ...(resultJson ? ["--result-json", resultJson] : []),
    ],
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  process.stdout.write(result.stdout);
}

function assemble(root) {
  const args = process.argv.slice(3);
  const result = spawnSync(
    "python3",
    buildAssemblyArgs(root, args),
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  process.stdout.write(result.stdout);
}

function hostBuild(root) {
  const args = process.argv.slice(3);
  const result = spawnSync(
    "python3",
    [
      path.join(root, "scripts", "build", "build_patched_host.py"),
      ...args
    ],
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  process.stdout.write(result.stdout);
}

function probeProviders(root) {
  const passthroughArgs = process.argv.slice(3);
  const result = spawnSync(
    "python3",
    [
      path.join(root, "scripts", "verify", "probe_assistant_providers.py"),
      "--repo-root",
      root,
      "--channel",
      "benchmark",
      ...passthroughArgs,
    ],
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  process.stdout.write(result.stdout);
}

function native(root, passthroughArgs) {
  const distBase = process.env.EVCODE_DIST_OUTPUT_ROOT || path.join(root, ".evcode-dist");
  const defaultDistRoot = path.join(distBase, "benchmark");
  const launcherPath = path.join(defaultDistRoot, "bin", "evcode-bench");
  if (!fs.existsSync(launcherPath)) {
    const assembled = spawnSync(
      "python3",
      buildAssemblyArgs(root, ["--output-root", distBase]),
      { encoding: "utf8" }
    );
    if (assembled.status !== 0) {
      process.stderr.write(assembled.stderr);
      process.exit(assembled.status || 1);
    }
  }
  const result = spawnSync(launcherPath, passthroughArgs, { stdio: "inherit" });
  process.exit(result.status || 0);
}

function trace(root) {
  const args = process.argv.slice(3);
  if (hasFlag(args, "--help") || hasFlag(args, "-h")) {
    printTraceUsage("evcode-bench");
    process.exit(0);
  }
  const runId = valueForFlag(args, "--run-id", args.find((item) => !item.startsWith("--")) || "");
  if (!runId) {
    console.error("Missing run id for trace");
    process.exit(1);
  }
  const artifactsRoot = valueForFlag(args, "--artifacts-root", root);
  const sessionRoot = runtimeDisplay.resolveSessionRoot({ root, artifactsRoot, runId });
  const summary = runtimeDisplay.loadRuntimeSummary(sessionRoot);
  if (!summary) {
    console.error(`Unable to locate runtime summary for run_id=${runId}`);
    process.exit(1);
  }
  const events = runtimeDisplay.loadRuntimeEvents(summary?.artifacts?.runtime_events)
    || runtimeDisplay.loadRuntimeEvents(path.join(sessionRoot, "runtime-events.jsonl"));
  const resolvedEvents = events.length ? events : runtimeDisplay.synthesizeEventsFromSummary(summary);
  if (hasFlag(args, "--json")) {
    process.stdout.write(`${JSON.stringify({ summary, events: resolvedEvents }, null, 2)}\n`);
    return;
  }
  const text = runtimeDisplay.renderRuntimeView(summary, resolvedEvents, {
    isTTY: process.stdout.isTTY,
    noColor: hasFlag(args, "--no-color"),
    trace: true,
    context: { runId },
  });
  process.stdout.write(`${text}\n`);
}

const root = path.resolve(__dirname, "../../..");
const providerEnvState = providerRuntime.applyLocalProviderEnv(root, process.env);
const internalCommands = new Set(["status", "run", "trace", "assemble", "host-build", "native", "probe-providers"]);
const command = process.argv[2] || "native";
const jsonFlag = process.argv.includes("--json");

if (command === "status") {
  const result = status(root);
  if (jsonFlag) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`EvCode Bench | mode=${result.mode} | profile=${result.profile} | host=${result.host}`);
  }
  process.exit(0);
}

if (command === "run") {
  run(root);
  process.exit(0);
}

if (command === "trace") {
  trace(root);
  process.exit(0);
}

if (command === "assemble") {
  assemble(root);
  process.exit(0);
}

if (command === "host-build") {
  hostBuild(root);
  process.exit(0);
}

if (command === "native") {
  native(root, process.argv.slice(3));
}

if (command === "probe-providers") {
  probeProviders(root);
  process.exit(0);
}

if (!internalCommands.has(command)) {
  native(root, process.argv.slice(2));
}

console.log("Usage: evcode-bench [status|run|trace|assemble|host-build|native|probe-providers] [--json]");
process.exit(1);
