const path = require("node:path");

function subagentInit({ repoRoot, projectSlug, workflowName, commandName, brief, promptContext, usage }) {
  const hasProject = typeof projectSlug === "string" && projectSlug.trim() !== "";
  const workContext = hasProject ? path.join(repoRoot, "projects", projectSlug) : null;
  const docsPath = workContext ? path.join(workContext, "docs") : null;
  return {
    repoRoot,
    projectRoot: workContext,
    workContext,
    docsPath,
    reportsPath: docsPath,
    outputsPath: docsPath ? path.join(docsPath, "assets", "exports") : null,
    plansPath: path.join(repoRoot, "plans"),
    workflow: {
      name: workflowName ?? null,
      command: commandName ?? null,
      brief: brief ? String(brief).trim() : null,
    },
    promptContext:
      promptContext || usage
        ? {
            interactive: promptContext?.interactive ?? null,
            projectSlug: promptContext?.projectSlug ?? projectSlug,
            rawText: promptContext?.rawText ?? null,
            summary: promptContext?.summary ?? null,
            usageSummary: usage?.summary ?? promptContext?.usage?.summary ?? null,
          }
        : null,
    constraints: [
      "Keep generated project outputs inside the project docs tree only.",
      "Use repo-level plans/ for kit planning context, not project output files.",
    ],
    naming: "kebab-case, project-scoped docs outputs, concise reports",
  };
}

if (require.main === module) {
  console.log(
    JSON.stringify(
      subagentInit({
        repoRoot: process.cwd(),
        projectSlug: process.argv[2],
        workflowName: process.argv[3],
        commandName: process.argv[4],
      }),
      null,
      2,
    ),
  );
}

module.exports = {
  subagentInit,
};
