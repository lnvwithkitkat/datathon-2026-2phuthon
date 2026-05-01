#!/usr/bin/env node

const { parseArgs } = require("./lib/cli.cjs");
const { routeCommand } = require("./lib/router.cjs");
const { runWorkflowPreflight } = require("./hooks/run-workflow-preflight.cjs");
const { runUserPromptSubmit } = require("./hooks/user-prompt-submit.cjs");

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const context = await runWorkflowPreflight({ cwd: process.cwd() });
  const promptContext = await runUserPromptSubmit({
    repoRoot: context.repoRoot,
    cwd: process.cwd(),
    command: parsed.command,
    flags: parsed.flags,
    rawText: parsed.rawText,
  });
  await routeCommand({
    command: parsed.command,
    flags: parsed.flags,
    repoRoot: context.repoRoot,
    rawText: parsed.rawText,
    runtimeContext: {
      promptContext,
      usage: promptContext.usage,
    },
  });
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
