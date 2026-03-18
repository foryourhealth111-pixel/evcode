const fs = require("fs");
const os = require("os");
const path = require("path");

const CANONICAL_LOCAL_PROVIDER_ENV_RELATIVE_PATH = path.join("config", "assistant-providers.env.local");
const EXAMPLE_PROVIDER_ENV_RELATIVE_PATH = path.join("config", "assistant-providers.env.example");
const PROVIDER_SETUP_DOC_RELATIVE_PATH = path.join("docs", "configuration", "openai-compatible-provider-setup.md");
const PORTABLE_PROVIDER_ENV_FILENAME = "assistant-providers.env";

const OPENAI_COMPATIBILITY_SUMMARY = {
  api_surface: "openai_style",
  primary_wire_api: "chat_completions",
  secondary_wire_api_support: "responses_tolerant",
  validated_runtime_scope: "validated_on_current_rightcodes_codex_claude_gemini_paths",
  portability_note:
    "OpenAI-style request shapes are supported, but provider-specific differences still require governed defaults and verification.",
  mcp_positioning: "capability_transport_not_second_orchestrator",
};

function stripWrappingQuotes(value) {
  if (
    value.length >= 2 &&
    ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'")))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function parseEnvFile(text) {
  const parsed = {};
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    const normalized = line.startsWith("export ") ? line.slice("export ".length).trim() : line;
    const separatorIndex = normalized.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }
    const key = normalized.slice(0, separatorIndex).trim();
    const value = stripWrappingQuotes(normalized.slice(separatorIndex + 1).trim());
    if (key) {
      parsed[key] = value;
    }
  }
  return parsed;
}

function resolvePortableConfigRoot(env = process.env, platform = process.platform) {
  if (env.EVCODE_CONFIG_ROOT) {
    return path.resolve(env.EVCODE_CONFIG_ROOT);
  }
  if (platform === "win32") {
    const appData = env.APPDATA || path.join(env.USERPROFILE || os.homedir(), "AppData", "Roaming");
    return path.join(appData, "EvCode");
  }
  if (platform === "darwin") {
    return path.join(env.HOME || os.homedir(), "Library", "Application Support", "EvCode");
  }
  const xdgConfigHome = env.XDG_CONFIG_HOME || path.join(env.HOME || os.homedir(), ".config");
  return path.join(xdgConfigHome, "evcode");
}

function resolveProviderEnvSelection(root, env = process.env, platform = process.platform) {
  const repoLocalEnvPath = path.join(root, CANONICAL_LOCAL_PROVIDER_ENV_RELATIVE_PATH);
  const portableConfigRoot = resolvePortableConfigRoot(env, platform);
  const portableEnvPath = path.join(portableConfigRoot, PORTABLE_PROVIDER_ENV_FILENAME);
  if (env.EVCODE_PROVIDER_ENV_FILE) {
    return {
      portableConfigRoot,
      portableEnvPath,
      repoLocalEnvPath,
      selectedEnvPath: path.resolve(env.EVCODE_PROVIDER_ENV_FILE),
      source: "explicit_env_file",
    };
  }
  if (fs.existsSync(portableEnvPath)) {
    return {
      portableConfigRoot,
      portableEnvPath,
      repoLocalEnvPath,
      selectedEnvPath: portableEnvPath,
      source: "portable_user_config",
    };
  }
  if (fs.existsSync(repoLocalEnvPath)) {
    return {
      portableConfigRoot,
      portableEnvPath,
      repoLocalEnvPath,
      selectedEnvPath: repoLocalEnvPath,
      source: "repo_local_override",
    };
  }
  return {
    portableConfigRoot,
    portableEnvPath,
    repoLocalEnvPath,
    selectedEnvPath: portableEnvPath,
    source: "none",
  };
}

function resolveProviderEnvPath(root, env = process.env, platform = process.platform) {
  return resolveProviderEnvSelection(root, env, platform).selectedEnvPath;
}

function applyLocalProviderEnv(root, env = process.env, platform = process.platform) {
  const selection = resolveProviderEnvSelection(root, env, platform);
  const report = {
    canonical_local_env_path: path.join(root, CANONICAL_LOCAL_PROVIDER_ENV_RELATIVE_PATH),
    repo_local_env_path: selection.repoLocalEnvPath,
    portable_config_root: selection.portableConfigRoot,
    portable_env_path: selection.portableEnvPath,
    resolved_local_env_path: selection.selectedEnvPath,
    active_env_source: selection.source,
    example_env_path: path.join(root, EXAMPLE_PROVIDER_ENV_RELATIVE_PATH),
    setup_doc_path: path.join(root, PROVIDER_SETUP_DOC_RELATIVE_PATH),
    local_env_present: fs.existsSync(selection.selectedEnvPath),
    loaded_from_file: false,
    loaded_keys: [],
    skipped_keys: [],
  };

  if (!report.local_env_present) {
    return report;
  }

  const parsed = parseEnvFile(fs.readFileSync(selection.selectedEnvPath, "utf8"));
  for (const [key, value] of Object.entries(parsed)) {
    if (Object.prototype.hasOwnProperty.call(env, key) && env[key] !== "") {
      report.skipped_keys.push(key);
      continue;
    }
    env[key] = value;
    report.loaded_keys.push(key);
  }
  report.loaded_from_file = report.loaded_keys.length > 0;
  return report;
}

function summarizeAssistantProviders(assistantPolicy, env = process.env) {
  const summary = {};
  for (const [assistantName, config] of Object.entries(assistantPolicy.assistants || {})) {
    const capabilityAccess = config.capability_access || {};
    summary[assistantName] = {
      enabled: Boolean(config.enabled),
      provider: config.provider,
      wire_api: config.wire_api || "responses",
      base_url: env[config.base_url_env_var] || config.default_base_url || null,
      model: env[config.model_env_var] || config.default_model || null,
      authority_tier: config.authority_tier || null,
      capability_mode: capabilityAccess.mode || null,
      required_skill_capsules: [...(config.required_skill_capsules || [])],
      direct_read_only_allowlist: [...(capabilityAccess.direct_read_only_allowlist || [])],
      proxy_allowlist: [...(capabilityAccess.proxy_allowlist || [])],
      mutation_allowlist: [...(capabilityAccess.mutation_allowlist || [])],
      denied_capabilities: [...(capabilityAccess.denied || [])],
      api_key_env_var: config.api_key_env_var || null,
      api_key_present: Boolean(config.api_key_env_var && env[config.api_key_env_var]),
    };
  }
  return summary;
}

module.exports = {
  CANONICAL_LOCAL_PROVIDER_ENV_RELATIVE_PATH,
  EXAMPLE_PROVIDER_ENV_RELATIVE_PATH,
  PROVIDER_SETUP_DOC_RELATIVE_PATH,
  PORTABLE_PROVIDER_ENV_FILENAME,
  OPENAI_COMPATIBILITY_SUMMARY,
  resolvePortableConfigRoot,
  resolveProviderEnvSelection,
  resolveProviderEnvPath,
  applyLocalProviderEnv,
  summarizeAssistantProviders,
};
