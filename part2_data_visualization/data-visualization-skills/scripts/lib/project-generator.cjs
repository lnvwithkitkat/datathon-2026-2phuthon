const path = require("node:path");

const { buildDecisionBundle } = require("./selector.cjs");
const { pathExists, safeRemoveDir, slugify, writeMany } = require("./fs-utils.cjs");
const {
  renderDataPreparationDoc,
  renderDebugReportDoc,
  renderDesignGuidelinesDoc,
  renderEvidenceIndexPage,
  renderEvidencePackageJson,
  renderProjectBriefDoc,
  renderProjectGitignore,
  renderProjectPlanDoc,
  renderProjectReadme,
  renderPublishDoc,
  renderVisualizationDoc,
} = require("./project-doc-templates.cjs");
const { docsOutputGate } = require("../hooks/docs-output-gate.cjs");

async function generateProject(options) {
  const slug = options.slug && options.slug.trim() ? slugify(options.slug) : slugify(options.intake.projectGoals);
  if (!slug) {
    throw new Error("Project slug resolved to an empty value. Provide an explicit slug or clearer goals.");
  }

  const projectRoot = options.outputPath ?? path.join(options.repoRoot, "projects", slug);
  const projectsRoot = path.join(options.repoRoot, "projects");
  const relative = path.relative(projectsRoot, projectRoot);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`Project output path must stay inside projects/: ${projectRoot}`);
  }
  const exists = await pathExists(projectRoot);

  if (exists && !options.force) {
    throw new Error(`Project path already exists: ${projectRoot}`);
  }
  if (exists && options.force) {
    await safeRemoveDir(projectRoot, projectsRoot);
  }

  const decisions = buildDecisionBundle({
    projectGoals: options.intake.projectGoals,
    preferFreeDeploy: options.preferFreeDeploy,
    // Pass explicitly confirmed decisions from the intake validation hook.
    // These take priority over keyword-based auto-selection in selector.cjs.
    framework: options.intake.framework ?? null,
    goalTier: options.intake.goalTier ?? null,
    visualizationTool: options.intake.visualizationTool ?? null,
    deployTarget: options.intake.deployTarget ?? null,
  });

  const docsRoot = path.join(projectRoot, "docs");
  const evidenceRoot = path.join(projectRoot, "evidence");
  const docsFiles = {
    projectBrief: path.join(docsRoot, "project-brief.md"),
    projectPlan: path.join(docsRoot, "project-plan.md"),
    dataPreparation: path.join(docsRoot, "data-preparation.md"),
    visualization: path.join(docsRoot, "visualization.md"),
    publish: path.join(docsRoot, "publish.md"),
    debugReport: path.join(docsRoot, "debug-report.md"),
    designGuidelines: path.join(docsRoot, "design-guidelines.md"),
    documentManagement: path.join(docsRoot, "document-management.md"),
    screenshots: path.join(docsRoot, "assets", "screenshots", ".gitkeep"),
    userFiles: path.join(docsRoot, "assets", "user-files", ".gitkeep"),
    exports: path.join(docsRoot, "assets", "exports", ".gitkeep"),
    evidenceBuild: path.join(docsRoot, "assets", "evidence-build", ".gitkeep"),
  };

  for (const target of Object.values(docsFiles)) {
    docsOutputGate({
      repoRoot: options.repoRoot,
      projectSlug: slug,
      targetPath: target,
    });
  }

  const files = {
    [path.join(projectRoot, "README.md")]: renderProjectReadme({
      slug,
      workflowSummary: {
        ownerWorkflow: "plan",
        tool: decisions.tool.name,
        framework: decisions.framework.name,
      },
    }),
    [path.join(projectRoot, ".gitignore")]: renderProjectGitignore(),
    [docsFiles.projectBrief]: renderProjectBriefDoc({ slug, intake: options.intake }),
    [docsFiles.projectPlan]: renderProjectPlanDoc({ intake: options.intake, decisions }),
    [docsFiles.dataPreparation]: renderDataPreparationDoc({ intake: options.intake, decisions }),
    [docsFiles.visualization]: renderVisualizationDoc({ decisions }),
    [docsFiles.publish]: renderPublishDoc({
      slug,
      decisions,
      preferFreeDeploy: options.preferFreeDeploy,
    }),
    [docsFiles.debugReport]: renderDebugReportDoc(),
    [docsFiles.designGuidelines]: renderDesignGuidelinesDoc(),
    [docsFiles.documentManagement]:
      "# Document Management\n\nKeep plans, notes, screenshots, exports, and user files inside this docs tree only.\n",
    [docsFiles.screenshots]: "",
    [docsFiles.userFiles]: "",
    [docsFiles.exports]: "",
    [docsFiles.evidenceBuild]: "",
    [path.join(docsRoot, "assets", "exports", "01-analysis.sql")]: buildSqlStarter(options.intake),
  };

  if (decisions.layer.requiresPython) {
    files[path.join(docsRoot, "assets", "exports", "01-analysis.py")] = buildPythonStarter(options.intake);
  } else {
    files[path.join(docsRoot, "assets", "exports", ".gitkeep")] = "";
  }

  if (decisions.tool.name === "Evidence") {
    Object.assign(files, buildEvidenceWorkspaceFiles(evidenceRoot));
  }

  await writeMany(files);
  return { decisions, projectRoot, slug };
}

function buildSqlStarter(intake) {
  const context = flattenLine(intake.projectContext);
  const dataset = flattenLine(intake.projectDataset);
  return `-- Starter SQL for the generated portfolio project
-- Context: ${context}
-- Dataset: ${dataset}

select *
from your_source_table
limit 100;
`;
}

function buildPythonStarter(intake) {
  const context = toPythonStringLiteral(intake.projectContext);
  const dataset = toPythonStringLiteral(intake.projectDataset);
  return `"""Starter Python for the generated portfolio project."""

def describe_project():
    return {
        "context": ${context},
        "dataset": ${dataset},
        "next_step": "Implement cleaning, feature work, or advanced analysis here.",
    }


if __name__ == "__main__":
    print(describe_project())
`;
}

function flattenLine(value) {
  return String(value).replace(/\s+/g, " ").trim();
}

function toPythonStringLiteral(value) {
  return JSON.stringify(String(value));
}

function buildEvidenceWorkspaceFiles(evidenceRoot) {
  return {
    [path.join(evidenceRoot, "package.json")]: renderEvidencePackageJson(),
    [path.join(evidenceRoot, "pages", "index.md")]: renderEvidenceIndexPage(),
    [path.join(evidenceRoot, "components", ".gitkeep")]: "",
    [path.join(evidenceRoot, "sources", "data", "dataset.csv")]: "category,value\nexample,1\n",
  };
}

module.exports = {
  generateProject,
};
