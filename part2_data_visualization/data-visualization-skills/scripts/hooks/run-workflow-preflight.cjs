const path = require("node:path");
const { pathExists } = require("../lib/fs-utils.cjs");

async function runWorkflowPreflight({ cwd }) {
  const repoRoot = await findRepoRoot(cwd);
  return { ok: true, repoRoot };
}

async function findRepoRoot(startPath) {
  let currentPath = path.resolve(startPath);

  while (true) {
    const requiredPaths = [
      path.join(currentPath, "package.json"),
      path.join(currentPath, "projects"),
      path.join(currentPath, "scripts"),
    ];

    const matches = await Promise.all(requiredPaths.map((target) => pathExists(target)));
    if (matches.every(Boolean)) {
      return currentPath;
    }

    const parentPath = path.dirname(currentPath);
    if (parentPath === currentPath) {
      throw new Error(`Preflight failed. Could not locate repo root from: ${startPath}`);
    }
    currentPath = parentPath;
  }
}

if (require.main === module) {
  runWorkflowPreflight({ cwd: process.cwd() })
    .then((result) => console.log(JSON.stringify(result, null, 2)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  findRepoRoot,
  runWorkflowPreflight,
};
