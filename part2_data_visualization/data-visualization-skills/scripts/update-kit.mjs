#!/usr/bin/env node

import path from "node:path";
import { spawnSync } from "node:child_process";
import core from "./lib/update-kit-core.cjs";

const {
  backupProjects,
  cleanupBackup,
  collectCoreChanges,
  normalizePath,
  parseStatusEntriesFromText,
  removeProjectUserData,
  restoreProjects,
} = core;

const args = new Set(process.argv.slice(2));
const help = args.has("--help") || args.has("-h");
const reset = args.has("--reset");
const repoRoot = process.cwd();
const projectsRoot = path.join(repoRoot, "projects");
const projectsReadme = normalizePath(path.relative(repoRoot, path.join(projectsRoot, "README.md")));

function printHelp() {
  console.log("Data Visualization Kit Update");
  console.log("");
  console.log("Safe by default:");
  console.log("- Preserves everything inside projects/ except projects/README.md");
  console.log("- Updates only the core kit");
  console.log("- Stops if local changes exist outside projects/");
  console.log("");
  console.log("Usage:");
  console.log("  npm run kit:update");
  console.log("  npm run kit:update:reset");
  console.log("");
  console.log("Flags:");
  console.log("  --reset  Reset local core kit to origin/<current-branch> while still preserving projects/");
}

function bin(name) {
  return process.platform === "win32" && name === "npm" ? "npm.cmd" : name;
}

function formatCommand(command, commandArgs) {
  return [command, ...commandArgs].join(" ");
}

function run(command, commandArgs, options = {}) {
  const result = spawnSync(bin(command), commandArgs, {
    encoding: "utf8",
    stdio: options.stdio ?? "inherit",
    ...options,
  });

  if (result.error) {
    throw new Error(`Failed to run ${command}: ${result.error.message}`);
  }

  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    const stdout = (result.stdout || "").trim();
    const details = stderr || stdout;
    throw new Error(
      details
        ? `${formatCommand(command, commandArgs)} failed: ${details}`
        : `${formatCommand(command, commandArgs)} failed with exit code ${result.status ?? 1}`,
    );
  }

  return result;
}

function capture(command, commandArgs) {
  const result = run(command, commandArgs, { stdio: "pipe" });
  return (result.stdout || "").trim();
}

function parseStatusEntries() {
  return parseStatusEntriesFromText(capture("git", ["status", "--porcelain=1", "-uall"]));
}

function fetchRemote(branch) {
  console.log(`Fetching latest changes from origin/${branch}...`);
  run("git", ["fetch", "origin", branch]);
}

function getAheadBehind(branch) {
  const output = capture("git", ["rev-list", "--left-right", "--count", `origin/${branch}...HEAD`]);
  const parts = output.split(/\s+/).filter(Boolean);
  if (parts.length < 2) {
    throw new Error(`Cannot parse branch divergence for '${branch}'.`);
  }

  return {
    behind: Number.parseInt(parts[0], 10) || 0,
    ahead: Number.parseInt(parts[1], 10) || 0,
  };
}

function printCoreChanges(paths) {
  console.error("Safe update stopped because local changes exist outside projects/:");
  for (const targetPath of paths) {
    console.error(`- ${targetPath}`);
  }
  console.error("");
  console.error("Commit, stash, or discard those core-kit changes first.");
  console.error("If you want to discard core-kit changes but keep projects/, run:");
  console.error("  npm run kit:update:reset");
}

if (help) {
  printHelp();
  process.exit(0);
}

try {
  if (capture("git", ["rev-parse", "--is-inside-work-tree"]) !== "true") {
    throw new Error("Current directory is not a git repository.");
  }

  const originUrl = capture("git", ["remote", "get-url", "origin"]);
  if (!originUrl) {
    throw new Error("Cannot update without an origin remote. Clone from git or add origin first.");
  }

  const branch = capture("git", ["rev-parse", "--abbrev-ref", "HEAD"]);
  if (!branch || branch === "HEAD") {
    throw new Error("Cannot update from a detached HEAD. Checkout a branch first.");
  }

  console.log(`Updating Data Visualization Kit on branch '${branch}'...`);

  const coreChanges = collectCoreChanges(parseStatusEntries(), projectsReadme);
  if (!reset && coreChanges.length > 0) {
    printCoreChanges(coreChanges);
    process.exit(1);
  }

  fetchRemote(branch);

  const { behind, ahead } = getAheadBehind(branch);
  if (!reset && ahead > 0) {
    console.error("Safe update stopped because this branch has local commits.");
    console.error("Create a backup branch first, or use reset mode if you want to discard local core commits.");
    console.error("Suggested:");
    console.error("  git branch backup/local-kit-before-update");
    console.error("  npm run kit:update:reset");
    process.exit(1);
  }

  if (!reset && behind === 0) {
    console.log("Core kit is already up to date.");
    process.exit(0);
  }

  const backup = backupProjects(projectsRoot);
  if (backup) {
    console.log(`Backed up ${backup.entries.length} project entr${backup.entries.length === 1 ? "y" : "ies"} to ${backup.backupRoot}`);
  }

  let restoreNeeded = Boolean(backup);

  try {
    removeProjectUserData(projectsRoot);

    if (reset) {
      console.log("Reset mode enabled: local core-kit changes will be discarded, projects/ will be restored after update.");
      run("git", ["reset", "--hard", `origin/${branch}`]);
      run("git", ["clean", "-fd"]);
    } else {
      run("git", ["pull", "--ff-only", "origin", branch]);
    }
  } catch (error) {
    if (restoreNeeded) {
      restoreProjects(projectsRoot, backup);
      cleanupBackup(backup);
      restoreNeeded = false;
    }
    throw error;
  }

  if (restoreNeeded) {
    restoreProjects(projectsRoot, backup);
    cleanupBackup(backup);
  }

  console.log("Update completed. Local projects/ content was preserved.");
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
