const readline = require("node:readline/promises");
const { stdin, stdout } = require("node:process");

const { hasTextValue, resolveBoolean } = require("./cli.cjs");
const { planIntakeValidation } = require("../hooks/plan-intake-validation.cjs");

async function collectPrimaryInput(flags, options = {}) {
  const interactive = options.interactive ?? stdin.isTTY;

  // All base fields supplied - run decision validation without a prompt loop.
  if (
    hasTextValue(flags["project-context"]) &&
    hasTextValue(flags["project-dataset"]) &&
    hasTextValue(flags["project-goals"])
  ) {
    // Validate (or auto-confirm) framework, goal tier, visualization tool, and deploy target.
    const decisions = await planIntakeValidation({ flags, interactive });
    return {
      projectContext: flags["project-context"],
      projectDataset: flags["project-dataset"],
      projectGoals: flags["project-goals"],
      preferFreeDeploy: resolveBoolean(flags["prefer-free-deploy"], true),
      slug: flags.slug,
      framework: decisions.framework,
      goalTier: decisions.goalTier,
      visualizationTool: decisions.visualizationTool,
      deployTarget: decisions.deployTarget,
    };
  }

  if (!interactive) {
    throw new Error("Missing required intake values for non-interactive execution.");
  }

  // Interactive path — open one shared readline interface for all prompts.
  const rl = readline.createInterface({ input: stdin, output: stdout });
  try {
    const projectContext = hasTextValue(flags["project-context"])
      ? flags["project-context"]
      : await rl.question("Project context: ");
    const projectDataset = hasTextValue(flags["project-dataset"])
      ? flags["project-dataset"]
      : await rl.question("Project dataset: ");
    const projectGoals = hasTextValue(flags["project-goals"])
      ? flags["project-goals"]
      : await rl.question("Project goals: ");
    const preferFreeDeploy =
      flags["prefer-free-deploy"] ??
      (await rl.question("Prefer free-tier or self-host-friendly open-source deployment by default? [Y/n]: "));
    const slug = flags.slug ?? (await rl.question("Project slug (optional): "));

    // Present framework, goal tier, tool, and deploy target choices - user must confirm each.
    const decisions = await planIntakeValidation({ flags, interactive, rl });

    return {
      projectContext,
      projectDataset,
      projectGoals,
      preferFreeDeploy: resolveBoolean(preferFreeDeploy, true),
      slug,
      framework: decisions.framework,
      goalTier: decisions.goalTier,
      visualizationTool: decisions.visualizationTool,
      deployTarget: decisions.deployTarget,
    };
  } finally {
    rl.close();
  }
}

async function collectWorkflowUpdateInput(flags, options = {}) {
  const interactive = options.interactive ?? stdin.isTTY;

  if (hasTextValue(flags.slug) && hasTextValue(flags.brief)) {
    return {
      slug: flags.slug,
      brief: flags.brief,
    };
  }

  if (!interactive) {
    throw new Error("Missing required workflow update values: --slug and --brief.");
  }

  const rl = readline.createInterface({ input: stdin, output: stdout });
  try {
    const slug = hasTextValue(flags.slug) ? flags.slug : await rl.question("Project slug: ");
    const brief = hasTextValue(flags.brief) ? flags.brief : await rl.question("Workflow brief: ");
    return { slug, brief };
  } finally {
    rl.close();
  }
}

module.exports = {
  collectPrimaryInput,
  collectWorkflowUpdateInput,
};

