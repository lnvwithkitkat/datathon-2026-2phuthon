const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");

const { hasTextValue, parseArgs, printHelp } = require("../scripts/lib/cli.cjs");
const { privacyBlock } = require("../scripts/hooks/privacy-block.cjs");
const { projectPreflight } = require("../scripts/hooks/project-preflight.cjs");
const { generateProject } = require("../scripts/lib/project-generator.cjs");
const { buildDecisionBundle } = require("../scripts/lib/selector.cjs");
const { routeCommand } = require("../scripts/lib/router.cjs");
const { runDocumentManagementWorkflow } = require("../scripts/lib/dv-workflows.cjs");
const { collectPrimaryInput, collectWorkflowUpdateInput } = require("../scripts/lib/workflow-inputs.cjs");
const { docsOutputGate } = require("../scripts/hooks/docs-output-gate.cjs");

test("generateProject creates a git-ready project workspace", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const result = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Retention analysis",
      projectDataset: "Orders and customers",
      projectGoals: "Show churn insight and technical workflow",
      deployTarget: "VPS",
    },
    slug: "retention-analysis",
    preferFreeDeploy: true,
  });

  const files = [
    "README.md",
    ".gitignore",
    "docs/project-brief.md",
    "docs/project-plan.md",
    "docs/data-preparation.md",
    "docs/visualization.md",
    "docs/publish.md",
    "docs/debug-report.md",
    "docs/document-management.md",
    "docs/assets/exports/01-analysis.sql",
    "docs/assets/evidence-build/.gitkeep",
  ];

  for (const relativePath of files) {
    const target = path.join(result.projectRoot, relativePath);
    await assert.doesNotReject(() => fs.access(target));
  }

  await assert.rejects(() => fs.access(path.join(result.projectRoot, "plans")));
  await assert.rejects(() => fs.access(path.join(result.projectRoot, "assets")));

  const planDoc = await fs.readFile(path.join(result.projectRoot, "docs", "project-plan.md"), "utf8");
  assert.match(planDoc, /Metabase/);
  assert.match(planDoc, /Framework/);
  assert.match(planDoc, /\$dv-cook/);
  assert.match(planDoc, /Goal Ladder Suggestions/);
});

test("generateProject selects Grafana for operational time-series goals", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const result = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Platform monitoring",
      projectDataset: "Metrics, logs, and traces",
      projectGoals: "Build a real-time observability dashboard for SLA metrics",
      deployTarget: "VPS",
    },
    slug: "ops-monitoring",
    preferFreeDeploy: true,
  });

  const planDoc = await fs.readFile(path.join(result.projectRoot, "docs", "project-plan.md"), "utf8");
  assert.match(planDoc, /Grafana/);
});

test("generateProject escapes quoted intake values in the python starter", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const result = await generateProject({
    repoRoot,
    intake: {
      projectContext: 'Portfolio for "quoted" context',
      projectDataset: 'Dataset with "quotes"',
      projectGoals: "Show advanced technical workflow",
      deployTarget: "VPS",
    },
    slug: "quoted-intake",
    preferFreeDeploy: true,
  });

  const pythonStarter = await fs.readFile(
    path.join(result.projectRoot, "docs", "assets", "exports", "01-analysis.py"),
    "utf8",
  );
  assert.match(pythonStarter, /Portfolio for \\"quoted\\" context/);
  assert.match(pythonStarter, /Dataset with \\"quotes\\"/);
});

test("generateProject rejects empty slugs and protects the projects root", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  await assert.rejects(
    () =>
      generateProject({
        repoRoot,
        intake: {
          projectContext: "Invalid slug test",
          projectDataset: "N/A",
          projectGoals: "!!!",
        },
        preferFreeDeploy: true,
      }),
    /empty value/,
  );
});

test("collectPortfolioInput rejects malformed non-interactive flags", async () => {
  await assert.rejects(
    () =>
      collectPrimaryInput(
        {
          slug: "malformed-intake",
        "project-context": "true",
        "project-dataset": "true",
        "project-goals": "true",
        "deploy-target": "VPS",
      },
      { interactive: false },
    ),
    /Missing required intake values/,
  );
});

test("collectWorkflowUpdateInput requires slug and brief for non-interactive runs", async () => {
  await assert.rejects(
    () =>
      collectWorkflowUpdateInput(
        {
          slug: "existing-project",
          brief: "true",
        },
        { interactive: false },
      ),
    /Missing required workflow update values/,
  );
});

test("docsOutputGate blocks writes outside a project's docs tree", () => {
  assert.throws(
    () =>
      docsOutputGate({
        repoRoot: "D:\\repo",
        projectSlug: "demo-project",
        targetPath: "D:\\repo\\projects\\demo-project\\plans\\plan.md",
      }),
    /docs/,
  );
});

test("projectPreflight stays read-only for a fresh project target", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  const targetPath = path.join(repoRoot, "projects", "fresh-project");

  await projectPreflight({
    repoRoot,
    projectSlug: "fresh-project",
    targetPath,
    force: false,
  });

  await assert.rejects(() => fs.access(targetPath));
});

test("privacyBlock matches secret filenames without rejecting normal project slugs", () => {
  assert.equal(privacyBlock("D:\\repo\\.env").blocked, true);
  assert.equal(privacyBlock("D:\\repo\\github_token").blocked, true);
  assert.equal(privacyBlock("D:\\repo\\projects\\customer-token-churn").blocked, false);
});

test("printHelp reflects the current public command surface", () => {
  const output = captureConsoleLog(() => printHelp());

  assert.match(output, /\$dv-plan <brief>/);
  assert.match(output, /\$dv-cook <brief>/);
  assert.match(output, /\$dv-document-management <brief>/);
  assert.doesNotMatch(output, /\$dv-primary <brief>/);
  assert.doesNotMatch(output, /\$dv-docs/);
  assert.doesNotMatch(output, /\$dv-hooks/);
  assert.doesNotMatch(output, /\$dv-hook-workflow/);
  assert.doesNotMatch(output, /\$dv-orchestration/);
  assert.doesNotMatch(output, /\$dv-orchestration <brief>/);
});

test("routeCommand sends $dv-help through the help workflow runtime", async () => {
  const output = await captureConsoleLogAsync(() =>
    routeCommand({
      command: "$dv-help",
      flags: {},
      repoRoot: "D:\\repo",
      rawText: "$dv-help publish this project",
      runtimeContext: {
        promptContext: {
          interactive: false,
          rawText: "$dv-help publish this project",
          summary: "Command: $dv-help",
        },
        usage: {
          summary: "5h 20% | 7d 10%",
        },
      },
    }),
  );

  assert.match(output, /Workflow: help/);
  assert.match(output, /Recommended next command: \$dv-publish/);
  assert.doesNotMatch(output, /^Data Visualization Kit\r?\n\r?\nCommands:/);
});

test("routeCommand sends bare $dv to the help workflow when no brief is provided", async () => {
  const output = await captureConsoleLogAsync(() =>
    routeCommand({
      command: "$dv",
      flags: {},
      repoRoot: "D:\\repo",
      rawText: "$dv",
      runtimeContext: {
        promptContext: {
          interactive: true,
          rawText: "$dv",
          summary: "Command: $dv",
        },
      },
    }),
  );

  assert.match(output, /Hub route: \$dv -> \$dv-help/);
  assert.match(output, /Workflow: help/);
});

test("routeCommand sends broad $dv asks to the planning workflow", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const output = await captureConsoleLogAsync(() =>
    routeCommand({
      command: "$dv",
      flags: {
        "project-context": "E-commerce retention",
        "project-dataset": "Orders and customers",
        // plan-intake-validation requires all four decisions in non-interactive mode.
        "project-goals": "Show churn insight and retention trends",
        framework: "CRISP-DM",
        "goal-tier": "Pro",
        "visualization-tool": "Metabase",
        "deploy-target": "VPS",
        "non-interactive": "true",
      },
      repoRoot,
      rawText: "$dv build a churn dashboard portfolio project",
      runtimeContext: {
        promptContext: {
          interactive: false,
          rawText: "$dv build a churn dashboard portfolio project",
          summary: "Command: $dv",
        },
      },
    }),
  );

  assert.match(output, /Hub route: \$dv -> \$dv-plan/);
  assert.match(output, /Workflow: plan/);
});

test("routeCommand sends explicit $dv specialist asks to the matching owner workflow", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const project = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Retention analysis",
      projectDataset: "Orders and customers",
      projectGoals: "Show churn insight and technical workflow",
      deployTarget: "VPS",
    },
    slug: "retention-analysis",
    preferFreeDeploy: true,
  });

  const output = await captureConsoleLogAsync(() =>
    routeCommand({
      command: "$dv",
      flags: {
        slug: project.slug,
        "non-interactive": "true",
      },
      repoRoot,
      rawText: "$dv publish make this project git-ready and deployable",
      runtimeContext: {
        promptContext: {
          interactive: false,
          projectSlug: project.slug,
          rawText: "$dv publish make this project git-ready and deployable",
          summary: "Command: $dv",
        },
      },
    }),
  );

  assert.match(output, /Hub route: \$dv -> \$dv-publish/);
  assert.match(output, /Workflow: publish/);

  const publishDoc = await fs.readFile(path.join(project.projectRoot, "docs", "publish.md"), "utf8");
  assert.match(publishDoc, /make this project git-ready and deployable/);
  assert.doesNotMatch(publishDoc, /publish make this project git-ready and deployable/);
});

test("runDocumentManagementWorkflow parses summarize mode from the brief", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const project = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Retention analysis",
      projectDataset: "Orders and customers",
      projectGoals: "Show churn insight and technical workflow",
      deployTarget: "VPS",
    },
    slug: "retention-analysis",
    preferFreeDeploy: true,
  });

  await captureConsoleLogAsync(() =>
    runDocumentManagementWorkflow({
      flags: {
        slug: project.slug,
        brief: "summarize refresh only the highest-signal docs",
        "non-interactive": "true",
      },
      repoRoot,
      briefText: "summarize refresh only the highest-signal docs",
      runtimeContext: {
        promptContext: {
          interactive: false,
          projectSlug: project.slug,
          rawText: "$dv-document-management summarize refresh only the highest-signal docs",
          summary: "Command: $dv-document-management",
        },
      },
      commandName: "$dv-document-management",
    }),
  );

  const documentManagementDoc = await fs.readFile(
    path.join(project.projectRoot, "docs", "document-management.md"),
    "utf8",
  );

  assert.match(documentManagementDoc, /## Mode\r?\n\r?\nsummarize/);
  assert.match(documentManagementDoc, /refresh only the highest-signal docs/);
  assert.doesNotMatch(documentManagementDoc, /## Brief\r?\n\r?\nsummarize refresh/);
});

test("hasTextValue rejects placeholder boolean flags", () => {
  assert.equal(hasTextValue("true"), false);
  assert.equal(hasTextValue(" real text "), true);
});

test("generateProject records Evidence + Netlify for static portfolio projects", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const result = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Kaggle sales analysis",
      projectDataset: "sales.csv",
      projectGoals: "Show monthly revenue trends",
      framework: "CRISP-DM",
      goalTier: "Basic",
      visualizationTool: "Evidence",
      deployTarget: "Netlify",
      slug: "kaggle-sales",
    },
    preferFreeDeploy: true,
  });

  const planDoc = await fs.readFile(path.join(result.projectRoot, "docs", "project-plan.md"), "utf8");
  const publishDoc = await fs.readFile(path.join(result.projectRoot, "docs", "publish.md"), "utf8");

  assert.match(planDoc, /Evidence/);
  assert.match(planDoc, /Netlify/);
  assert.match(publishDoc, /npm run sources && npm run build/);
  assert.match(publishDoc, /Static Deploy \(Netlify\)/);
  await assert.doesNotReject(() => fs.access(path.join(result.projectRoot, "evidence", "package.json")));
  await assert.doesNotReject(() => fs.access(path.join(result.projectRoot, "evidence", "pages", "index.md")));
  await assert.doesNotReject(() => fs.access(path.join(result.projectRoot, "docs", "assets", "evidence-build", ".gitkeep")));
});

test("buildDecisionBundle auto-selects Evidence for static deploy targets", () => {
  const result = buildDecisionBundle({
    projectGoals: "Show monthly revenue trends from a CSV portfolio dataset",
    preferFreeDeploy: true,
    deployTarget: "Netlify",
  });

  assert.equal(result.tool.name, "Evidence");
  assert.equal(result.deployTarget, "Netlify");
});

test("generateProject records Vercel-specific static publish guidance", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "codex-data-viz-kit-"));
  const repoRoot = path.join(tempRoot, "repo");
  await fs.mkdir(path.join(repoRoot, "projects"), { recursive: true });

  const result = await generateProject({
    repoRoot,
    intake: {
      projectContext: "Spreadsheet KPI portfolio",
      projectDataset: "kpis.xlsx",
      projectGoals: "Build a static KPI showcase for portfolio review",
      framework: "CRISP-DM",
      goalTier: "Basic",
      visualizationTool: "Evidence",
      deployTarget: "Vercel",
    },
    slug: "spreadsheet-kpis",
    preferFreeDeploy: true,
  });

  const publishDoc = await fs.readFile(path.join(result.projectRoot, "docs", "publish.md"), "utf8");
  assert.match(publishDoc, /Static Deploy \(Vercel\)/);
  assert.match(publishDoc, /vercel\.json/);
});

test("parseArgs preserves $dv command and brief text", () => {
  const parsed = parseArgs([
    "$dv-data-visualize",
    "refresh",
    "charts",
    "--slug",
    "demo-project",
    "--brief",
    "Refresh visuals after source change",
  ]);

  assert.equal(parsed.command, "$dv-data-visualize");
  assert.equal(parsed.flags.slug, "demo-project");
  assert.equal(parsed.flags.brief, "Refresh visuals after source change");
  assert.equal(parsed.rawText, "$dv-data-visualize refresh charts");
});

function captureConsoleLog(run) {
  const originalLog = console.log;
  let output = "";
  console.log = (value) => {
    output += `${value}\n`;
  };

  try {
    run();
  } finally {
    console.log = originalLog;
  }

  return output;
}

async function captureConsoleLogAsync(run) {
  const originalLog = console.log;
  let output = "";
  console.log = (value) => {
    output += `${value}\n`;
  };

  try {
    await run();
  } finally {
    console.log = originalLog;
  }

  return output;
}
