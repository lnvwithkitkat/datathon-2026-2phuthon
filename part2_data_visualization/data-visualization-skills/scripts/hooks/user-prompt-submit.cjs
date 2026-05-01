const path = require("node:path");
const { runUsageContextAwareness } = require("./usage-context-awareness.cjs");

function buildUserPromptContext({ repoRoot, cwd, command, flags, rawText, usage }) {
  const slug = typeof flags.slug === "string" && flags.slug.trim() ? flags.slug.trim() : null;
  const candidateProjectRoot = slug ? path.join(repoRoot, "projects", slug) : null;
  const interactive = flags["non-interactive"] !== "true";
  const lines = [
    `Command: ${command}`,
    `Mode: ${interactive ? "interactive" : "non-interactive"}`,
    slug ? `Project slug: ${slug}` : "Project slug: unresolved",
    `Repo root: ${repoRoot}`,
    `Working dir: ${cwd}`,
  ];

  if (candidateProjectRoot) {
    lines.push(`Project root: ${candidateProjectRoot}`);
    lines.push(`Docs path: ${path.join(candidateProjectRoot, "docs")}`);
  }

  if (rawText) {
    lines.push(`Prompt: ${rawText}`);
  }

  if (usage?.summary) {
    lines.push(`Usage: ${usage.summary}`);
  }

  return {
    command,
    cwd,
    repoRoot,
    rawText,
    projectSlug: slug,
    projectRoot: candidateProjectRoot,
    docsPath: candidateProjectRoot ? path.join(candidateProjectRoot, "docs") : null,
    interactive,
    usage,
    summary: lines.join("\n"),
  };
}

async function runUserPromptSubmit({
  repoRoot,
  cwd = process.cwd(),
  command,
  flags = {},
  rawText = "",
  usageRunner = runUsageContextAwareness,
} = {}) {
  const usage = await usageRunner({ event: "UserPromptSubmit" });
  return buildUserPromptContext({
    repoRoot,
    cwd,
    command,
    flags,
    rawText,
    usage,
  });
}

if (require.main === module) {
  const payload = process.argv[2] ? JSON.parse(process.argv[2]) : {};
  runUserPromptSubmit(payload)
    .then((result) => console.log(JSON.stringify(result, null, 2)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  buildUserPromptContext,
  runUserPromptSubmit,
};
