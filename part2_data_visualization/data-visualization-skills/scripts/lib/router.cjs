const {
  resolveHelpRecommendation,
  runCookWorkflow,
  runDocumentManagementWorkflow,
  runHelpWorkflow,
  runPlanWorkflow,
  runProjectUpdateWorkflow,
} = require("./dv-workflows.cjs");
const { renderWorkflowUpdateDoc } = require("./project-doc-templates.cjs");

async function routeCommand({ command, flags, repoRoot, rawText, runtimeContext }) {
  const normalizedCommand = normalizeCommand(command);
  const briefText = deriveBriefText(normalizedCommand, rawText, command);

  if (normalizedCommand === "$dv") {
    const hubDispatch = resolveHubDispatch({ briefText, flags });
    const targetCommand = hubDispatch.targetCommand;
    console.log(`Hub route: $dv -> ${targetCommand}`);
    await routeCommand({
      command: targetCommand,
      flags,
      repoRoot,
      rawText: [targetCommand, hubDispatch.forwardedBrief].filter(Boolean).join(" "),
      runtimeContext,
    });
    return;
  }

  if (normalizedCommand === "$dv-help") {
    await runHelpWorkflow({
      repoRoot,
      briefText,
      runtimeContext,
      commandName: normalizedCommand,
    });
    return;
  }

  switch (normalizedCommand) {
    case "$dv-plan":
      await runPlanWorkflow({ flags, repoRoot, briefText, runtimeContext, commandName: normalizedCommand });
      return;
    case "$dv-cook":
      await runCookWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        briefText,
        runtimeContext,
        commandName: normalizedCommand,
      });
      return;
    case "$dv-data-preparation":
      await runProjectUpdateWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        runtimeContext,
        commandName: normalizedCommand,
        workflowName: "data-preparation",
        title: "Data Preparation",
        fileName: "data-preparation.md",
        notesBuilder: ({ brief }) =>
          renderWorkflowUpdateDoc({
            title: "Data Preparation",
            brief,
            notes: "Use this document to record ingestion, cleaning, validation, and transformation work.",
          }),
      });
      return;
    case "$dv-data-visualize":
      await runProjectUpdateWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        runtimeContext,
        commandName: normalizedCommand,
        workflowName: "data-visualize",
        title: "Visualization",
        fileName: "visualization.md",
        notesBuilder: ({ brief }) =>
          renderWorkflowUpdateDoc({
            title: "Visualization",
            brief,
            notes: "Use this document to record visualization choices, source changes, exports, and presentation updates.",
          }),
      });
      return;
    case "$dv-publish":
      await runProjectUpdateWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        runtimeContext,
        commandName: normalizedCommand,
        workflowName: "publish",
        title: "Publish",
        fileName: "publish.md",
        notesBuilder: ({ brief }) =>
          renderWorkflowUpdateDoc({
            title: "Publish",
            brief,
            notes: "Use this document to capture git readiness, deployment choices, and publish checklists.",
          }),
      });
      return;
    case "$dv-debug":
      await runProjectUpdateWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        runtimeContext,
        commandName: normalizedCommand,
        workflowName: "debug",
        title: "Debug Report",
        fileName: "debug-report.md",
        notesBuilder: ({ brief }) =>
          renderWorkflowUpdateDoc({
            title: "Debug Report",
            brief,
            notes: "Use this document to record root cause analysis, fixes, and unresolved issues.",
          }),
      });
      return;
    case "$dv-document-management":
      await runDocumentManagementWorkflow({
        flags: withBrief(flags, briefText),
        repoRoot,
        briefText,
        runtimeContext,
        commandName: normalizedCommand,
      });
      return;
    default:
      if (!command.startsWith("$dv-") && hasNaturalLanguageFallback(normalizedCommand, rawText)) {
        await runPlanWorkflow({
          flags,
          repoRoot,
          briefText: rawText,
          runtimeContext,
          commandName: "$dv-plan",
        });
        return;
      }
      throw new Error(`Unknown command: ${command}`);
  }
}

function normalizeCommand(command) {
  if (command === "$dv") {
    return "$dv";
  }
  if (command === "$dv-docs") {
    return "$dv-document-management";
  }
  if (command === "$dv-primary") {
    return "$dv-plan";
  }
  if (command === "help") {
    return "$dv-help";
  }
  if (command === "primary" || command === "plan") {
    return "$dv-plan";
  }
  if (command === "cook") {
    return "$dv-cook";
  }
  if (command === "data-preparation") {
    return "$dv-data-preparation";
  }
  if (command === "data-visualize") {
    return "$dv-data-visualize";
  }
  if (command === "publish") {
    return "$dv-publish";
  }
  if (command === "debug") {
    return "$dv-debug";
  }
  if (command === "docs" || command === "document-management") {
    return "$dv-document-management";
  }
  return command;
}

function deriveBriefText(normalizedCommand, rawText, originalCommand = normalizedCommand) {
  if (!rawText) {
    return "";
  }
  if (rawText.startsWith(normalizedCommand)) {
    return rawText.slice(normalizedCommand.length).trim();
  }
  if (rawText.startsWith(originalCommand)) {
    return rawText.slice(originalCommand.length).trim();
  }
  return rawText;
}

function withBrief(flags, briefText) {
  return {
    ...flags,
    brief: flags.brief ?? briefText,
  };
}

function hasNaturalLanguageFallback(normalizedCommand, rawText) {
  return !normalizedCommand.startsWith("$dv-") && rawText.trim().includes(" ");
}

function resolveHubDispatch({ briefText, flags }) {
  const brief = String(briefText ?? "").trim();
  if (!brief) {
    return {
      targetCommand: "$dv-help",
      forwardedBrief: "",
    };
  }

  const firstToken = extractLeadingToken(brief);
  const explicitCommand = normalizeHubWorkflowToken(firstToken);
  if (explicitCommand) {
    return {
      targetCommand: explicitCommand,
      forwardedBrief: stripLeadingToken(brief),
    };
  }

  const normalizedBrief = brief.toLowerCase();
  if (isDiscoveryIntent(normalizedBrief)) {
    return {
      targetCommand: "$dv-help",
      forwardedBrief: brief,
    };
  }

  if (!hasSlugValue(flags?.slug) && isBroadPlanningIntent(normalizedBrief)) {
    return {
      targetCommand: "$dv-plan",
      forwardedBrief: brief,
    };
  }

  return {
    targetCommand: resolveHelpRecommendation(brief).command,
    forwardedBrief: brief,
  };
}

function extractLeadingToken(value) {
  return String(value ?? "").trim().split(/\s+/, 1)[0] ?? "";
}

function stripLeadingToken(value) {
  return String(value ?? "").trim().split(/\s+/).slice(1).join(" ").trim();
}

function normalizeHubWorkflowToken(token) {
  const value = String(token ?? "").trim().toLowerCase();
  const tokenMap = {
    "$dv-help": "$dv-help",
    help: "$dv-help",
    "$dv-plan": "$dv-plan",
    plan: "$dv-plan",
    primary: "$dv-plan",
    "$dv-primary": "$dv-plan",
    "$dv-cook": "$dv-cook",
    cook: "$dv-cook",
    "$dv-data-preparation": "$dv-data-preparation",
    "data-preparation": "$dv-data-preparation",
    preparation: "$dv-data-preparation",
    "$dv-data-visualize": "$dv-data-visualize",
    "data-visualize": "$dv-data-visualize",
    visualize: "$dv-data-visualize",
    visualization: "$dv-data-visualize",
    "$dv-publish": "$dv-publish",
    publish: "$dv-publish",
    "$dv-debug": "$dv-debug",
    debug: "$dv-debug",
    "$dv-document-management": "$dv-document-management",
    "document-management": "$dv-document-management",
    docs: "$dv-document-management",
    "$dv-docs": "$dv-document-management",
  };

  return tokenMap[value] ?? null;
}

function isDiscoveryIntent(normalizedBrief) {
  const discoveryPhrases = [
    "what commands",
    "which command",
    "what workflow",
    "workflow roster",
    "command surface",
    "how do i start",
    "how to start",
    "show commands",
    "available commands",
  ];

  return discoveryPhrases.some((phrase) => normalizedBrief.includes(phrase));
}

function isBroadPlanningIntent(normalizedBrief) {
  const planningPhrases = [
    "build ",
    "create ",
    "start ",
    "new project",
    "portfolio project",
    "dataset",
    "project goals",
    "project context",
    "business context",
    "analysis project",
  ];

  return planningPhrases.some((phrase) => normalizedBrief.includes(phrase));
}

function hasSlugValue(value) {
  return typeof value === "string" && value.trim() !== "" && value !== "true";
}

module.exports = {
  routeCommand,
};
