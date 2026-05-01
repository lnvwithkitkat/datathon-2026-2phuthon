const path = require("node:path");
const { ensureDir, pathExists, slugify } = require("../lib/fs-utils.cjs");

async function projectPreflight({ repoRoot, projectSlug, targetPath, force }) {
  const projectsRoot = path.join(repoRoot, "projects");
  await ensureDir(projectsRoot);

  if (!projectSlug) {
    throw new Error("Project slug resolved to an empty value. Provide clearer goals or an explicit slug.");
  }

  if (slugify(projectSlug) !== projectSlug) {
    throw new Error(`Project slug must already be kebab-case: ${projectSlug}`);
  }

  const relative = path.relative(projectsRoot, targetPath);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`Target project path must stay inside projects/: ${targetPath}`);
  }

  const exists = await pathExists(targetPath);
  if (exists && !force) {
    throw new Error(`Target project already exists. Use --force=true to overwrite: ${targetPath}`);
  }

  return { ok: true, projectsRoot };
}

if (require.main === module) {
  projectPreflight({
    repoRoot: process.cwd(),
    projectSlug: process.argv[2],
    targetPath: process.argv[3],
    force: process.argv[4] === "true",
  })
    .then((result) => console.log(JSON.stringify(result, null, 2)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  projectPreflight,
};
