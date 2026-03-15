#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

function loadJson(root, relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function status(root) {
  const distributions = loadJson(root, "config/distributions.json");
  const runtime = loadJson(root, "config/runtime-contract.json");
  const policy = loadJson(root, "config/provider-policy.benchmark.json");
  const profile = loadJson(root, "profiles/benchmark/profile.json");
  return {
    product: "EvCode Bench",
    channel: "benchmark",
    mode: distributions.channels.benchmark.default_mode,
    profile: distributions.channels.benchmark.profile,
    host: runtime.host_baseline,
    embedded_runtime_version: runtime.embedded_runtime_version,
    provider_families: policy.allowed_provider_families,
    default_submission_preset: profile.default_submission_preset || null,
    assembled_distribution_exists: fs.existsSync(path.join(root, ".evcode-dist", "benchmark", "bin", "evcode-bench"))
  };
}

function run(root) {
  const args = process.argv.slice(3);
  const taskIndex = args.indexOf("--task");
  const task = taskIndex >= 0 ? args[taskIndex + 1] : "";
  if (!task) {
    console.error("Missing --task for run");
    process.exit(1);
  }
  const workspaceIndex = args.indexOf("--workspace");
  const artifactsRootIndex = args.indexOf("--artifacts-root");
  const runIdIndex = args.indexOf("--run-id");
  const resultJsonIndex = args.indexOf("--result-json");
  const workspace = workspaceIndex >= 0 ? args[workspaceIndex + 1] : root;
  const artifactsRoot = artifactsRootIndex >= 0
    ? args[artifactsRootIndex + 1]
    : fs.mkdtempSync(path.join(os.tmpdir(), "evcode-bench-artifacts-"));
  const runId = runIdIndex >= 0 ? args[runIdIndex + 1] : "";
  const resultJson = resultJsonIndex >= 0 ? args[resultJsonIndex + 1] : "";
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
      ...(runId ? ["--run-id", runId] : []),
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
    [
      path.join(root, "scripts", "build", "assemble_distribution.py"),
      "--channel",
      "benchmark",
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

function native(root, passthroughArgs) {
  const distBase = process.env.EVCODE_DIST_OUTPUT_ROOT || path.join(root, ".evcode-dist");
  const defaultDistRoot = path.join(distBase, "benchmark");
  const launcherPath = path.join(defaultDistRoot, "bin", "evcode-bench");
  if (!fs.existsSync(launcherPath)) {
    const assembled = spawnSync(
      "python3",
      [
        path.join(root, "scripts", "build", "assemble_distribution.py"),
        "--channel",
        "benchmark",
        "--output-root",
        distBase
      ],
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
const internalCommands = new Set(["status", "run", "assemble", "host-build", "native"]);
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

if (!internalCommands.has(command)) {
  native(root, process.argv.slice(2));
}

console.log("Usage: evcode-bench [status|run|assemble|host-build|native] [--json]");
process.exit(1);
