const path = require("node:path");

const { slugify, writeTextFile } = require("./fs-utils.cjs");
const { generateProject } = require("./project-generator.cjs");
const { renderWorkflowUpdateDoc } = require("./project-doc-templates.cjs");
const { validateGeneratedProject } = require("./project-validator.cjs");
const { collectPrimaryInput, collectWorkflowUpdateInput } = require("./workflow-inputs.cjs");
const { providerKeyGate } = require("../hooks/provider-key-gate.cjs");
const { projectPreflight } = require("../hooks/project-preflight.cjs");
const { subagentInit } = require("../hooks/subagent-init.cjs");
const { workflowRoutingGate } = require("../hooks/workflow-routing-gate.cjs");
const { docsOutputGate } = require("../hooks/docs-output-gate.cjs");
const { pathExists } = require("./fs-utils.cjs");

async function runPlanWorkflow({ flags, repoRoot, briefText, runtimeContext, commandName }) {
  const intake = await collectPrimaryInput(
    {
      ...flags,
      "project-goals": flags["project-goals"] ?? briefText,
    },
    { interactive: resolveInteractiveMode(flags) },
  );

  workflowRoutingGate({ workflowName: "plan", brief: intake.projectGoals });

  const slug = intake.slug?.trim() ? slugify(intake.slug) : slugify(intake.projectGoals);
  if (!slug) {
    throw new Error("Could not derive a valid project slug. Use clearer goals or pass --slug.");
  }

  const projectRoot = path.join(repoRoot, "projects", slug);

  const providerCheck = providerKeyGate([]);
  if (!providerCheck.ok) {
    throw new Error(`Provider key gate failed: ${providerCheck.missing.join(", ")}`);
  }

  await projectPreflight({
    repoRoot,
    projectSlug: slug,
    targetPath: projectRoot,
    force: flags.force === "true",
  });

  const result = await generateProject({
    repoRoot,
    intake,
    slug,
    preferFreeDeploy: intake.preferFreeDeploy,
    force: flags.force === "true",
  });

  const validation = await validateGeneratedProject(result.projectRoot);
  const handoff = subagentInit({
    repoRoot,
    projectSlug: result.slug,
    workflowName: "plan",
    commandName,
    brief: intake.projectGoals,
    promptContext: runtimeContext?.promptContext,
    usage: runtimeContext?.usage,
  });

  console.log(`Created project: ${result.projectRoot}`);
  console.log(`Workflow: plan`);
  console.log(`Framework: ${result.decisions.framework.name}`);
  console.log(`Layer: ${result.decisions.layer.name}`);
  console.log(`Tool: ${result.decisions.tool.name}`);
  console.log(`Validation: checked ${validation.checked} required paths`);
  console.log(`Codex handoff: ${JSON.stringify(handoff, null, 2)}`);
}

async function runProjectUpdateWorkflow({
  flags,
  repoRoot,
  workflowName,
  title,
  fileName,
  notesBuilder,
  runtimeContext,
  commandName,
}) {
  const input = await collectWorkflowUpdateInput(flags, {
    interactive: resolveInteractiveMode(flags),
  });

  const { slug, projectRoot, validation } = await updateProjectWorkflowDoc({
    repoRoot,
    workflowName,
    fileName,
    notesBuilder,
    brief: input.brief,
    rawSlug: input.slug,
  });

  const handoff = subagentInit({
    repoRoot,
    projectSlug: slug,
    workflowName,
    commandName,
    brief: input.brief,
    promptContext: runtimeContext?.promptContext,
    usage: runtimeContext?.usage,
  });

  console.log(`Updated project: ${projectRoot}`);
  console.log(`Workflow: ${workflowName}`);
  console.log(`Doc updated: ${path.join("docs", fileName)}`);
  console.log(`Validation: checked ${validation.checked} required paths`);
  console.log(`Codex handoff: ${JSON.stringify(handoff, null, 2)}`);
}

async function runDocumentManagementWorkflow({ flags, repoRoot, briefText, runtimeContext, commandName }) {
  const input = await collectWorkflowUpdateInput(
    {
      ...flags,
      brief: flags.brief ?? briefText,
    },
    { interactive: resolveInteractiveMode(flags) },
  );

  const slug = slugify(input.slug);
  if (!slug) {
    throw new Error("Document management requires a valid project slug.");
  }

  const projectRoot = path.join(repoRoot, "projects", slug);
  if (!(await pathExists(projectRoot))) {
    throw new Error(`Project does not exist: ${projectRoot}. Start with $dv-plan first.`);
  }

  const mode = await resolveDocumentManagementMode({
    flags,
    projectRoot,
    brief: input.brief,
  });
  const normalizedBrief = normalizeDocumentManagementBrief({ brief: input.brief, mode });

  const result = await updateProjectWorkflowDoc({
    repoRoot,
    workflowName: "document-management",
    fileName: "document-management.md",
    brief: normalizedBrief,
    rawSlug: slug,
    notesBuilder: ({ brief }) =>
      renderWorkflowUpdateDoc({
        title: "Document Management",
        brief,
        mode,
        notes: buildDocumentManagementNotes(mode),
      }),
  });

  const handoff = subagentInit({
    repoRoot,
    projectSlug: result.slug,
    workflowName: "document-management",
    commandName,
    brief: normalizedBrief,
    promptContext: runtimeContext?.promptContext,
    usage: runtimeContext?.usage,
  });

  console.log(`Updated project: ${result.projectRoot}`);
  console.log("Workflow: document-management");
  console.log(`Mode: ${mode}`);
  console.log(`Doc updated: ${path.join("docs", "document-management.md")}`);
  console.log(`Validation: checked ${result.validation.checked} required paths`);
  console.log(`Codex handoff: ${JSON.stringify(handoff, null, 2)}`);
}

async function runCookWorkflow({ flags, repoRoot, briefText, runtimeContext, commandName }) {
  const input = await collectWorkflowUpdateInput(
    {
      ...flags,
      brief: flags.brief ?? briefText,
    },
    { interactive: resolveInteractiveMode(flags) },
  );

  workflowRoutingGate({ workflowName: "cook", brief: input.brief });

  const preTestStages = [
    {
      workflowName: "data-preparation",
      fileName: "data-preparation.md",
      notesBuilder: ({ brief }) =>
        buildCookStageDoc({
          title: "Data Preparation",
          brief,
          notes: "Triggered by `$dv-cook`. Record ingestion, cleaning, validation, and transformation work here.",
        }),
    },
    {
      workflowName: "data-visualize",
      fileName: "visualization.md",
      notesBuilder: ({ brief }) =>
        buildCookStageDoc({
          title: "Visualization",
          brief,
          notes: "Triggered by `$dv-cook`. Record chart choices, source changes, exports, and presentation updates here.",
        }),
    },
  ];

  const postTestStages = [
    {
      workflowName: "document-management",
      fileName: "document-management.md",
      notesBuilder: ({ brief }) =>
        buildCookStageDoc({
          title: "Document Management",
          brief,
          notes: "Triggered by `$dv-cook`. Record doc sync, asset placement, and workspace cleanup here.",
        }),
    },
    {
      workflowName: "publish",
      fileName: "publish.md",
      notesBuilder: ({ brief }) =>
        buildCookStageDoc({
          title: "Publish",
          brief,
          notes: "Triggered by `$dv-cook`. Capture git readiness, deployment choice, and final publish checks here.",
        }),
    },
  ];

  const updatedDocs = [];
  let slug = "";
  let projectRoot = "";

  for (const stage of preTestStages) {
    const result = await updateProjectWorkflowDoc({
      repoRoot,
      workflowName: stage.workflowName,
      fileName: stage.fileName,
      notesBuilder: stage.notesBuilder,
      brief: input.brief,
      rawSlug: input.slug,
    });
    slug = result.slug;
    projectRoot = result.projectRoot;
    updatedDocs.push(path.join("docs", stage.fileName));
  }

  const testValidation = await validateGeneratedProject(projectRoot);

  for (const stage of postTestStages) {
    const result = await updateProjectWorkflowDoc({
      repoRoot,
      workflowName: stage.workflowName,
      fileName: stage.fileName,
      notesBuilder: stage.notesBuilder,
      brief: input.brief,
      rawSlug: input.slug,
    });
    slug = result.slug;
    projectRoot = result.projectRoot;
    updatedDocs.push(path.join("docs", stage.fileName));
  }

  const finalValidation = await validateGeneratedProject(projectRoot);
  const handoff = subagentInit({
    repoRoot,
    projectSlug: slug,
    workflowName: "cook",
    commandName,
    brief: input.brief,
    promptContext: runtimeContext?.promptContext,
    usage: runtimeContext?.usage,
  });

  console.log(`Updated project: ${projectRoot}`);
  console.log("Workflow: cook");
  console.log("Sequence: data-preparation -> data-visualize -> test -> document-management -> publish");
  console.log(`Docs updated: ${updatedDocs.join(", ")}`);
  console.log(`Test: project validation passed (${testValidation.checked} required paths)`);
  console.log(`Final validation: checked ${finalValidation.checked} required paths`);
  console.log(`Codex handoff: ${JSON.stringify(handoff, null, 2)}`);
}

async function runHelpWorkflow({ repoRoot, briefText, runtimeContext, commandName }) {
  workflowRoutingGate({ workflowName: "help", brief: briefText });

  const recommendation = resolveHelpRecommendation(briefText);
  const handoff = subagentInit({
    repoRoot,
    workflowName: "help",
    commandName,
    brief: briefText,
    promptContext: runtimeContext?.promptContext,
    usage: runtimeContext?.usage,
  });

  console.log("Data Visualization Kit Help");
  console.log("Workflow: help");
  console.log(`Recommended next command: ${recommendation.command}`);
  console.log(`Why: ${recommendation.reason}`);
  console.log(`Example: ${recommendation.example}`);
  console.log("Canonical commands: $dv-help, $dv-plan, $dv-cook, $dv-data-preparation, $dv-data-visualize, $dv-publish, $dv-debug, $dv-document-management");
  console.log(`Codex handoff: ${JSON.stringify(handoff, null, 2)}`);
}

async function updateProjectWorkflowDoc({ repoRoot, workflowName, fileName, notesBuilder, brief, rawSlug }) {
  workflowRoutingGate({ workflowName, brief });

  const slug = slugify(rawSlug);
  if (!slug) {
    throw new Error("Workflow update requires a valid project slug.");
  }

  const projectRoot = path.join(repoRoot, "projects", slug);
  if (!(await pathExists(projectRoot))) {
    throw new Error(`Project does not exist: ${projectRoot}. Start with $dv-plan first.`);
  }

  const targetFile = path.join(projectRoot, "docs", fileName);
  docsOutputGate({
    repoRoot,
    projectSlug: slug,
    targetPath: targetFile,
  });

  await writeTextFile(
    targetFile,
    notesBuilder({
      brief,
      workflowName,
      slug,
    }),
  );

  const validation = await validateGeneratedProject(projectRoot);
  return { slug, projectRoot, validation };
}

function buildCookStageDoc({ title, brief, notes }) {
  return `# ${title}

## Brief

${brief}

## Mode

Triggered by \`$dv-cook\`

## Notes

${notes}
`;
}

async function resolveDocumentManagementMode({ flags, projectRoot, brief }) {
  const explicitMode = normalizeDocumentManagementMode(flags.mode);
  if (explicitMode) {
    return explicitMode;
  }

  const briefMode = normalizeDocumentManagementMode(extractLeadingToken(brief));
  if (briefMode) {
    return briefMode;
  }

  const docsDir = path.join(projectRoot, "docs");
  const canonicalDocs = [
    "project-brief.md",
    "project-plan.md",
    "data-preparation.md",
    "visualization.md",
    "publish.md",
  ];
  let populatedDocs = 0;

  for (const fileName of canonicalDocs) {
    if (await pathExists(path.join(docsDir, fileName))) {
      populatedDocs += 1;
    }
  }

  return populatedDocs >= 3 ? "update" : "init";
}

function normalizeDocumentManagementBrief({ brief, mode }) {
  const trimmed = String(brief ?? "").trim();
  const withoutMode = normalizeDocumentManagementMode(extractLeadingToken(trimmed))
    ? trimmed.split(/\s+/).slice(1).join(" ").trim()
    : trimmed;

  if (withoutMode) {
    return withoutMode;
  }

  return `Run ${mode} pass for project docs.`;
}

function normalizeDocumentManagementMode(value) {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (normalized === "init" || normalized === "update" || normalized === "summarize") {
    return normalized;
  }
  return null;
}

function extractLeadingToken(value) {
  return String(value ?? "").trim().split(/\s+/, 1)[0] ?? "";
}

function buildDocumentManagementNotes(mode) {
  switch (mode) {
    case "init":
      return "Create or normalize the initial project docs set, keep all docs under `docs/`, and remove path confusion before downstream workflows continue.";
    case "summarize":
      return "Refresh only the highest-signal project summaries, keep the docs tree compact, and avoid broad rewrites unless they are required for correctness.";
    case "update":
    default:
      return "Refresh project docs after workflow changes, keep assets inside `docs/assets/`, and update only the smallest correct doc set.";
  }
}

function resolveHelpRecommendation(briefText) {
  const brief = String(briefText ?? "").trim();
  const normalized = brief.toLowerCase();

  const recommendations = [
    {
      command: "$dv-help",
      reason: "Your ask is about command discovery or choosing the right workflow.",
      example: "npm run dv -- '$dv-help'",
      matches: ["help", "commands", "command surface", "which command", "what command", "workflow roster", "how do i start"],
    },
    {
      command: "$dv-publish",
      reason: "Your ask sounds like git-readiness, deployment, or release packaging work.",
      example: 'npm run dv -- \'$dv-publish\' --slug ecommerce-churn --brief "Make this project git-ready and deployable"',
      matches: ["publish", "deploy", "release", "ship", "git-ready", "go live", "deployment"],
    },
    {
      command: "$dv-debug",
      reason: "Your ask sounds like failure diagnosis, runtime debugging, or root-cause analysis.",
      example: 'npm run dv -- \'$dv-debug\' --slug ecommerce-churn --brief "Find why the dashboard build is failing"',
      matches: ["debug", "bug", "error", "broken", "failure", "failing", "issue", "root cause"],
    },
    {
      command: "$dv-document-management",
      reason: "Your ask sounds like project docs cleanup, summaries, or asset organization.",
      example: 'npm run dv -- \'$dv-document-management\' --slug ecommerce-churn --brief "summarize refresh the project docs after the latest workflow pass"',
      matches: ["docs", "document", "summary", "summarize", "documentation", "assets", "cleanup"],
    },
    {
      command: "$dv-data-visualize",
      reason: "Your ask sounds like dashboard construction, refresh, or visualization-path work.",
      example: 'npm run dv -- \'$dv-data-visualize\' --slug ecommerce-churn --brief "Rebuild visuals after source schema changed"',
      matches: ["visual", "visualize", "dashboard", "chart", "grafana", "metabase", "superset"],
    },
    {
      command: "$dv-data-preparation",
      reason: "Your ask sounds like ingestion, cleaning, shaping, or dataset-readiness work.",
      example: 'npm run dv -- \'$dv-data-preparation\' --slug ecommerce-churn --brief "Clean order and customer data into dashboard-ready tables"',
      matches: ["prepare", "preparation", "clean", "etl", "transform", "schema", "dataset", "sql", "pipeline", "ingest"],
    },
    {
      command: "$dv-cook",
      reason: "Your ask sounds like a post-intake execution pass across the full project workflow.",
      example: 'npm run dv -- \'$dv-cook\' --slug ecommerce-churn --brief "Run the full project workflow from the approved intake"',
      matches: ["cook", "full project", "end-to-end", "continue project", "approved intake", "full workflow"],
    },
  ];

  for (const recommendation of recommendations) {
    if (recommendation.matches.some((keyword) => normalized.includes(keyword))) {
      return recommendation;
    }
  }

  return {
    command: "$dv-plan",
    reason: brief
      ? "Your ask is still broad enough that planning-first intake is the safest starting point."
      : "No specific workflow was requested, so the planning-first entrypoint is the safest default.",
    example:
      'npm run dv -- \'$dv-plan\' --project-context "E-commerce analysis" --project-dataset "Orders and customers" --project-goals "Show churn insights"',
  };
}

function resolveInteractiveMode(flags) {
  if (flags["non-interactive"] === "true") {
    return false;
  }
  return undefined;
}

module.exports = {
  resolveInteractiveMode,
  resolveHelpRecommendation,
  runCookWorkflow,
  runDocumentManagementWorkflow,
  runHelpWorkflow,
  runPlanWorkflow,
  runProjectUpdateWorkflow,
};
