#!/usr/bin/env node

const path = require("node:path");
const fs = require("node:fs/promises");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");
const { validateGeneratedProject } = require("./lib/project-validator.cjs");

const execFileAsync = promisify(execFile);

async function main() {
  const repoRoot = process.cwd();
  const smokeSlug = "smoke-demo-ecommerce-churn-portfolio";
  const smokePath = path.join(repoRoot, "projects", smokeSlug);

  try {
    const cliPath = path.join(repoRoot, "scripts", "run-kit.cjs");
    await execFileAsync(process.execPath, [
      cliPath,
      "$dv-plan",
      "--slug",
      smokeSlug,
      "--project-context",
      "E-commerce retention analysis for a portfolio case study.",
      "--project-dataset",
      "Orders, customers, support tickets, and campaign touchpoints.",
      "--project-goals",
      "Show churn insight, segmentation, and a reproducible technical workflow.",
      "--framework",
      "CRISP-DM",
      "--goal-tier",
      "Pro",
      "--visualization-tool",
      "Metabase",
      "--deploy-target",
      "VPS",
      "--prefer-free-deploy=true",
    ], { cwd: repoRoot });

    await execFileAsync(process.execPath, [
      cliPath,
      "$dv-cook",
      "--slug",
      smokeSlug,
      "--brief",
      "Run the full smoke workflow after intake approval.",
    ], { cwd: repoRoot });
    await expectFailure(
      execFileAsync(process.execPath, [cliPath, "bogus-workflow"], { cwd: repoRoot }),
      /Unknown command/,
    );

    await expectFailure(
      execFileAsync(process.execPath, [cliPath, "$dv-plan", "--slug", "missing-intake"], {
        cwd: repoRoot,
      }),
      /Missing required intake values/,
    );

    await expectFailure(
      execFileAsync(process.execPath, [cliPath, "plan", "--slug", "missing-intake", "--non-interactive"], {
        cwd: repoRoot,
      }),
      /Missing required intake values/,
    );

    await validateGeneratedProject(smokePath);
    await fs.access(path.join(smokePath, "docs", "assets", "exports", "01-analysis.py"));
    console.log(`Generated smoke project at ${smokePath}`);
  } finally {
    await fs.rm(smokePath, { recursive: true, force: true });
  }
}

async function expectFailure(promise, pattern) {
  try {
    await promise;
    throw new Error("Expected command to fail, but it succeeded.");
  } catch (error) {
    const message = String(error.stderr || error.message || error);
    if (!pattern.test(message)) {
      throw error;
    }
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
