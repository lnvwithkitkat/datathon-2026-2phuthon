const path = require("node:path");

function docsOutputGate({ repoRoot, projectSlug, targetPath }) {
  const docsRoot = path.join(repoRoot, "projects", projectSlug, "docs");
  const relative = path.relative(docsRoot, targetPath);

  if (relative.startsWith("..") || path.isAbsolute(relative) || relative === "") {
    throw new Error(`Project docs output must stay inside docs/: ${targetPath}`);
  }

  return { ok: true, docsRoot };
}

if (require.main === module) {
  try {
    console.log(
      JSON.stringify(
        docsOutputGate({
          repoRoot: process.cwd(),
          projectSlug: process.argv[2],
          targetPath: process.argv[3],
        }),
        null,
        2,
      ),
    );
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

module.exports = {
  docsOutputGate,
};

