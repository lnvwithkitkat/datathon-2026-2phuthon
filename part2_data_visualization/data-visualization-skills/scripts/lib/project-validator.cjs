const fs = require("node:fs/promises");
const path = require("node:path");

async function validateGeneratedProject(projectRoot) {
  const requiredPaths = [
    "README.md",
    ".gitignore",
    "docs/project-brief.md",
    "docs/project-plan.md",
    "docs/data-preparation.md",
    "docs/visualization.md",
    "docs/publish.md",
    "docs/debug-report.md",
    "docs/design-guidelines.md",
    "docs/document-management.md",
    "docs/assets/screenshots/.gitkeep",
    "docs/assets/user-files/.gitkeep",
    "docs/assets/exports/.gitkeep",
    "docs/assets/exports/01-analysis.sql",
  ];

  for (const relativePath of requiredPaths) {
    await fs.access(path.join(projectRoot, relativePath));
  }

  for (const forbiddenPath of ["plans", "assets"]) {
    try {
      await fs.access(path.join(projectRoot, forbiddenPath));
      throw new Error(`Forbidden legacy project path exists: ${forbiddenPath}`);
    } catch (error) {
      if (error.code !== "ENOENT") {
        throw error;
      }
    }
  }

  const visualizationDoc = await fs.readFile(path.join(projectRoot, "docs", "visualization.md"), "utf8");
  if (visualizationDoc.includes("Tool: Evidence")) {
    for (const relativePath of [
      "docs/assets/evidence-build/.gitkeep",
      "evidence/package.json",
      "evidence/pages/index.md",
      "evidence/sources/data/dataset.csv",
    ]) {
      await fs.access(path.join(projectRoot, relativePath));
    }
  }

  return {
    ok: true,
    checked: requiredPaths.length,
  };
}

module.exports = {
  validateGeneratedProject,
};
