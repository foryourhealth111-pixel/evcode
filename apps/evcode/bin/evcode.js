#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");
const providerRuntime = require(path.join(__dirname, "../../../packages/provider-runtime/src/local_provider_env.js"));

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

function extractTomlString(text, key) {
  const match = text.match(new RegExp(`^${key}\\s*=\\s*\"([^\"]+)\"\\s*$`, "m"));
  return match ? match[1] : null;
}

function extractProviderBaseUrl(text, providerName) {
  if (!providerName) {
    return null;
  }
  const lines = text.split(/\r?\n/);
  const header = `[model_providers.${providerName}]`;
  let start = -1;
  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index].trim() === header) {
      start = index;
      break;
    }
  }
  if (start < 0) {
    return null;
  }
  for (let index = start + 1; index < lines.length; index += 1) {
    const line = lines[index].trim();
    if (line.startsWith("[") && line.endsWith("]")) {
      break;
    }
    const match = line.match(/^base_url\s*=\s*"([^"]+)"\s*$/);
    if (match) {
      return match[1];
    }
  }
  return null;
}

function resolveSourceCodexHome() {
  const configured = process.env.EVCODE_SOURCE_CODEX_HOME || process.env.CODEX_HOME;
  if (configured && fs.existsSync(path.join(configured, "config.toml"))) {
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
    "standard",
    ...passthroughArgs
  ];
  if (!passthroughArgs.includes("--source-codex-home")) {
    const sourceCodexHome = resolveSourceCodexHome();
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

function readAssembledConfig(root) {
  const codexHome = path.join(root, ".evcode-dist", "standard", "codex-home");
  const configPath = path.join(codexHome, "config.toml");
  if (!fs.existsSync(configPath)) {
    return null;
  }
  const text = fs.readFileSync(configPath, "utf8");
  const modelProvider = extractTomlString(text, "model_provider");
  return {
    codex_home: codexHome,
    model_provider: modelProvider,
    model: extractTomlString(text, "model"),
    base_url: extractProviderBaseUrl(text, modelProvider),
    auth_json_present: fs.existsSync(path.join(codexHome, "auth.json")),
    env_local_present: fs.existsSync(path.join(codexHome, "env.local"))
  };
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
  console.log(`Usage: ${commandName} run --task <task> [--workspace PATH] [--artifacts-root PATH]${commandName === "evcode-bench" ? " [--result-json PATH]" : ""} [--run-id ID]`);
}


function doctor(root) {
  const hostBinary = process.env.EVCODE_HOST_BIN || "codex";
  const profile = loadJson(root, "profiles/standard/profile.json");
  const assistantPolicy = loadJson(root, profile.assistant_policy);
  const routingPolicy = loadJson(root, profile.specialist_routing);
  const required = [
    "config/runtime-contract.json",
    "config/distributions.json",
    "config/provider-policy.standard.json",
    "config/assistant-policy.standard.json",
    "config/specialist-routing.json",
    "config/host-integration.json",
    "docs/architecture/evcode-host-runtime-bridge.md",
    "docs/architecture/evcode-governed-specialist-repair.md",
    "scripts/build/assemble_distribution.py"
  ];
  const missing = required.filter((item) => !fs.existsSync(path.join(root, item)));
  const sourceCodexHome = resolveSourceCodexHome();
  const assembled = readAssembledConfig(root);
  const alignedWithSource = Boolean(
    sourceCodexHome &&
    assembled &&
    fs.existsSync(path.join(sourceCodexHome, "config.toml")) &&
    (!fs.existsSync(path.join(sourceCodexHome, "auth.json")) || assembled.auth_json_present) &&
    (!fs.existsSync(path.join(sourceCodexHome, "env.local")) || assembled.env_local_present)
  );
  return {
    product: "EvCode",
    channel: "standard",
    ok: missing.length === 0,
    missing,
    host_binary: hostBinary,
    assembled_distribution_exists: fs.existsSync(path.join(root, ".evcode-dist", "standard", "bin", "evcode")),
    source_codex_home: sourceCodexHome,
    assembled,
    config_aligned_with_source: alignedWithSource,
    baseline_surface: buildBaselineSurface(root, profile),
    provider_setup: buildProviderSetup(root),
    governance_surface: buildGovernanceSurface(assistantPolicy, routingPolicy),
    assistant_api_compatibility: providerRuntime.OPENAI_COMPATIBILITY_SUMMARY,
    assistant_provider_resolution: providerRuntime.summarizeAssistantProviders(assistantPolicy, process.env)
  };
}

function status(root) {
  const distributions = loadJson(root, "config/distributions.json");
  const runtime = loadJson(root, "config/runtime-contract.json");
  const policy = loadJson(root, "config/provider-policy.standard.json");
  const profile = loadJson(root, "profiles/standard/profile.json");
  const assistantPolicy = loadJson(root, profile.assistant_policy);
  const routingPolicy = loadJson(root, profile.specialist_routing);
  const assembled = readAssembledConfig(root);
  return {
    product: "EvCode",
    channel: "standard",
    mode: distributions.channels.standard.default_mode,
    profile: distributions.channels.standard.profile,
    host: runtime.host_baseline,
    embedded_runtime_version: runtime.embedded_runtime_version,
    provider_families: policy.allowed_provider_families,
    assistant_policy: profile.assistant_policy,
    specialist_routing: profile.specialist_routing,
    baseline_family: profile.baseline_family || null,
    baseline_families_config: profile.baseline_families_config || null,
    specialist_rollout_phase: assistantPolicy.rollout_phase,
    assistants: Object.keys(assistantPolicy.assistants),
    assembled_distribution_exists: fs.existsSync(path.join(root, ".evcode-dist", "standard", "bin", "evcode")),
    source_codex_home: resolveSourceCodexHome(),
    bundled_host_available: Boolean(resolveBundledHost(root)),
    baseline_surface: buildBaselineSurface(root, profile),
    provider_setup: buildProviderSetup(root),
    governance_surface: buildGovernanceSurface(assistantPolicy, routingPolicy),
    assistant_api_compatibility: providerRuntime.OPENAI_COMPATIBILITY_SUMMARY,
    assistant_provider_resolution: providerRuntime.summarizeAssistantProviders(assistantPolicy, process.env),
    assembled
  };
}

function run(root) {
  const args = process.argv.slice(3);
  const taskIndex = args.indexOf("--task");
  const task = taskIndex >= 0 ? args[taskIndex + 1] : "";
  if (args.includes("--help") || args.includes("-h")) {
    printRunUsage("evcode");
    process.exit(0);
  }
  if (!task) {
    console.error("Missing --task for run");
    process.exit(1);
  }
  const workspaceIndex = args.indexOf("--workspace");
  const artifactsRootIndex = args.indexOf("--artifacts-root");
  const runIdIndex = args.indexOf("--run-id");
  const workspace = workspaceIndex >= 0 ? args[workspaceIndex + 1] : root;
  const artifactsRoot = artifactsRootIndex >= 0 ? args[artifactsRootIndex + 1] : root;
  const runId = runIdIndex >= 0 ? args[runIdIndex + 1] : "";
  const result = spawnSync(
    "python3",
    [
      path.join(root, "scripts/runtime/run_governed_runtime.py"),
      "--task",
      task,
      "--mode",
      "interactive_governed",
      "--channel",
      "standard",
      "--profile",
      "standard",
      "--repo-root",
      root,
      "--workspace",
      workspace,
      "--artifacts-root",
      artifactsRoot,
      ...(runId ? ["--run-id", runId] : []),
    ],
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  try {
    const payload = JSON.parse(result.stdout);
    if (Array.isArray(payload.warnings)) {
      for (const warning of payload.warnings) {
        const assistantName = warning.assistant_name || "specialist";
        const message = warning.message || `${assistantName} failed; continuing in degraded mode.`;
        process.stderr.write(`Warning: ${message}\n`);
      }
    }
  } catch (error) {
    // Preserve stdout passthrough when the child output is not JSON.
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
  try {
    const payload = JSON.parse(result.stdout);
    if (Array.isArray(payload.warnings)) {
      for (const warning of payload.warnings) {
        const assistantName = warning.assistant_name || "specialist";
        const message = warning.message || `${assistantName} failed; continuing in degraded mode.`;
        process.stderr.write(`Warning: ${message}\n`);
      }
    }
  } catch (error) {
    // Preserve stdout passthrough when the child output is not JSON.
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
  try {
    const payload = JSON.parse(result.stdout);
    if (Array.isArray(payload.warnings)) {
      for (const warning of payload.warnings) {
        const assistantName = warning.assistant_name || "specialist";
        const message = warning.message || `${assistantName} failed; continuing in degraded mode.`;
        process.stderr.write(`Warning: ${message}\n`);
      }
    }
  } catch (error) {
    // Preserve stdout passthrough when the child output is not JSON.
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
      "standard",
      ...passthroughArgs,
    ],
    { encoding: "utf8" }
  );
  if (result.status !== 0) {
    process.stderr.write(result.stderr);
    process.exit(result.status || 1);
  }
  try {
    const payload = JSON.parse(result.stdout);
    if (Array.isArray(payload.warnings)) {
      for (const warning of payload.warnings) {
        const assistantName = warning.assistant_name || "specialist";
        const message = warning.message || `${assistantName} failed; continuing in degraded mode.`;
        process.stderr.write(`Warning: ${message}\n`);
      }
    }
  } catch (error) {
    // Preserve stdout passthrough when the child output is not JSON.
  }
  process.stdout.write(result.stdout);
}

function native(root, passthroughArgs) {
  const distBase = process.env.EVCODE_DIST_OUTPUT_ROOT || path.join(root, ".evcode-dist");
  const defaultDistRoot = path.join(distBase, "standard");
  const launcherPath = path.join(defaultDistRoot, "bin", "evcode");
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

const root = path.resolve(__dirname, "../../..");
const providerEnvState = providerRuntime.applyLocalProviderEnv(root, process.env);
const internalCommands = new Set(["doctor", "status", "run", "assemble", "host-build", "native", "probe-providers"]);
const command = process.argv[2] || "native";
const jsonFlag = process.argv.includes("--json");

if (command === "doctor") {
  const result = doctor(root);
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.ok ? 0 : 1);
}

if (command === "status") {
  const result = status(root);
  if (jsonFlag) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`EvCode | channel=${result.channel} | mode=${result.mode} | host=${result.host}`);
  }
  process.exit(0);
}

if (command === "run") {
  run(root);
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

console.log("Usage: evcode [status|doctor|run|assemble|host-build|native|probe-providers] [--json]");
process.exit(1);
