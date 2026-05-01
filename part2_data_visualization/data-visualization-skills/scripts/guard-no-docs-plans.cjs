#!/usr/bin/env node

const { spawnSync } = require("node:child_process");
const { findForbiddenPaths, isZeroSha } = require("./lib/no-docs-plans-guard.cjs");

const args = process.argv.slice(2);

function captureGit(commandArgs) {
  const result = spawnSync("git", commandArgs, {
    encoding: "utf8",
    stdio: "pipe",
  });

  if (result.error) {
    throw new Error(`Failed to run git ${commandArgs.join(" ")}: ${result.error.message}`);
  }

  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    throw new Error(stderr || `git ${commandArgs.join(" ")} failed`);
  }

  return (result.stdout || "").trim();
}

function getPathsFromStaged() {
  const output = captureGit(["diff", "--cached", "--name-only", "--diff-filter=ACMRD"]);
  return output ? output.split(/\r?\n/).filter(Boolean) : [];
}

function getPathsFromPushRange(remoteSha, localSha) {
  if (!localSha || isZeroSha(localSha)) {
    return [];
  }

  if (!remoteSha || isZeroSha(remoteSha)) {
    const output = captureGit(["diff-tree", "--no-commit-id", "--name-only", "-r", localSha]);
    return output ? output.split(/\r?\n/).filter(Boolean) : [];
  }

  const output = captureGit(["diff", "--name-only", "--diff-filter=ACMRD", `${remoteSha}..${localSha}`]);
  return output ? output.split(/\r?\n/).filter(Boolean) : [];
}

function printBlocked(paths, mode) {
  console.error(`Blocked ${mode}: docs/ and plans/ must never be committed or pushed.`);
  for (const item of paths) {
    console.error(`- ${item}`);
  }
  console.error("");
  console.error("Unstage or remove those paths, then try again.");
}

function main() {
  if (args[0] === "--staged") {
    const forbidden = findForbiddenPaths(getPathsFromStaged());
    if (forbidden.length > 0) {
      printBlocked(forbidden, "commit");
      process.exitCode = 1;
    }
    return;
  }

  if (args[0] === "--push") {
    const forbidden = findForbiddenPaths(getPathsFromPushRange(args[1], args[2]));
    if (forbidden.length > 0) {
      printBlocked(forbidden, "push");
      process.exitCode = 1;
    }
    return;
  }

  console.error("Usage:");
  console.error("  node scripts/guard-no-docs-plans.cjs --staged");
  console.error("  node scripts/guard-no-docs-plans.cjs --push <remote-sha> <local-sha>");
  process.exitCode = 1;
}

main();
