const readline = require("node:readline/promises");
const { stdin, stdout } = require("node:process");

// Valid values for each decision dimension.
const VALID_FRAMEWORKS = ["CRISP-DM", "Data Pipeline"];
const VALID_GOAL_TIERS = ["Basic", "Pro", "Advanced"];
const VALID_TOOLS = ["Evidence", "Metabase", "Grafana", "Apache Superset"];
const VALID_DEPLOY_TARGETS = ["Netlify", "Vercel", "VPS"];

// Descriptions shown to the user when prompting interactively.
const FRAMEWORK_DESCRIPTIONS = {
  "CRISP-DM": "insight-first — business understanding, analysis, recommendations",
  "Data Pipeline": "engineering-first — ingestion, transformation, orchestration, data quality",
};

const GOAL_TIER_DESCRIPTIONS = {
  Basic: "descriptive questions, data profiling, lighter dashboard output",
  Pro: "harder stakeholder questions, driver/segment analysis, stronger analytical story (default)",
  Advanced: "forecasting, anomaly detection, scenario analysis, senior portfolio narrative",
};

const TOOL_DESCRIPTIONS = {
  Evidence: "static portfolio dashboards, CSV/Excel/Kaggle, Netlify/Vercel deploy",
  Metabase: "general BI, stakeholder dashboards, SQL-backed questions (default)",
  Grafana: "operational monitoring, time-series, observability, alert-aware panels",
  "Apache Superset": "legacy Superset estates only or migration analysis",
};

const DEPLOY_TARGET_DESCRIPTIONS = {
  Netlify: "static hosting - free tier, deploys Evidence.dev and static sites",
  Vercel: "static hosting - free tier, deploys Evidence.dev and static sites",
  VPS: "self-hosted server - required for Metabase, Grafana, Apache Superset",
};

/**
 * Validate that all four planning decisions (framework, goal tier, visualization tool, deploy target)
 * are either explicitly provided via flags or confirmed by the user interactively.
 *
 * When running interactively, presents each decision with all options + descriptions
 * and prompts the user to select one (suggest-and-confirm pattern).
 *
 * Returns an object with validated framework, goalTier, visualizationTool, and deployTarget.
 * Throws if running non-interactively with missing values.
 */
async function planIntakeValidation({ flags = {}, interactive, rl: externalRl } = {}) {
  const isInteractive = interactive ?? stdin.isTTY;

  const framework = await resolveDecision({
    flagValue: flags["framework"],
    validValues: VALID_FRAMEWORKS,
    descriptions: FRAMEWORK_DESCRIPTIONS,
    promptLabel: "Framework",
    defaultValue: null,
    isInteractive,
    rl: externalRl,
  });

  const goalTier = await resolveDecision({
    flagValue: flags["goal-tier"],
    validValues: VALID_GOAL_TIERS,
    descriptions: GOAL_TIER_DESCRIPTIONS,
    promptLabel: "Goal tier",
    defaultValue: "Pro",
    isInteractive,
    rl: externalRl,
  });

  const deployTarget = await resolveDecision({
    flagValue: flags["deploy-target"],
    validValues: VALID_DEPLOY_TARGETS,
    descriptions: DEPLOY_TARGET_DESCRIPTIONS,
    promptLabel: "Deploy target",
    defaultValue: "Netlify",
    isInteractive,
    rl: externalRl,
  });

  const visualizationTool = await resolveDecision({
    flagValue: flags["visualization-tool"],
    validValues: VALID_TOOLS,
    descriptions: TOOL_DESCRIPTIONS,
    promptLabel: "Visualization tool",
    defaultValue: getDefaultVisualizationTool(deployTarget),
    isInteractive,
    rl: externalRl,
  });

  validateDecisionCombination({ visualizationTool, deployTarget });

  return { ok: true, framework, goalTier, visualizationTool, deployTarget };
}

/**
 * Resolve one decision dimension.
 * If a valid flag value is already present, use it directly.
 * If interactive and missing, prompt the user.
 * If non-interactive and missing, throw.
 */
async function resolveDecision({ flagValue, validValues, descriptions, promptLabel, defaultValue, isInteractive, rl }) {
  // Exact match against provided flag value (case-insensitive).
  if (flagValue) {
    const normalized = matchValue(flagValue, validValues);
    if (normalized) {
      return normalized;
    }
    throw new Error(
      `Invalid ${promptLabel}: "${flagValue}". Valid options: ${validValues.join(", ")}.`,
    );
  }

  if (!isInteractive) {
    if (defaultValue) {
      return defaultValue;
    }
    throw new Error(
      `${promptLabel} is required for non-interactive $dv-plan. Pass --${toFlagName(promptLabel)} with one of: ${validValues.join(", ")}.`,
    );
  }

  return promptSelection({ validValues, descriptions, promptLabel, defaultValue, rl });
}

/**
 * Display numbered options with descriptions and ask the user to pick one.
 * Pressing Enter with no input selects the default when one is defined.
 */
async function promptSelection({ validValues, descriptions, promptLabel, defaultValue, rl }) {
  const owned = !rl;
  const iface = rl ?? readline.createInterface({ input: stdin, output: stdout });

  try {
    const defaultNote = defaultValue ? ` [default: ${defaultValue}]` : "";
    console.log(`\n${promptLabel}${defaultNote}:`);
    for (let i = 0; i < validValues.length; i++) {
      const value = validValues[i];
      console.log(`  ${i + 1}. ${value} — ${descriptions[value]}`);
    }

    const answer = await iface.question(`Select 1-${validValues.length}: `);
    const trimmed = answer.trim();

    if (!trimmed && defaultValue) {
      return defaultValue;
    }

    // Accept a number (1-based index) or a literal value name.
    const byIndex = parseInt(trimmed, 10);
    if (!Number.isNaN(byIndex) && byIndex >= 1 && byIndex <= validValues.length) {
      return validValues[byIndex - 1];
    }

    const byName = matchValue(trimmed, validValues);
    if (byName) {
      return byName;
    }

    throw new Error(
      `Invalid selection "${trimmed}" for ${promptLabel}. Enter a number (1-${validValues.length}) or a valid name.`,
    );
  } finally {
    if (owned) {
      iface.close();
    }
  }
}

/** Case-insensitive exact match against the valid values list. */
function matchValue(input, validValues) {
  const lower = String(input).trim().toLowerCase();
  return validValues.find((v) => v.toLowerCase() === lower) ?? null;
}

/** Convert a human-readable label to a flag name (e.g. "Goal tier" -> "goal-tier"). */
function toFlagName(label) {
  return label.toLowerCase().replace(/\s+/g, "-");
}

function getDefaultVisualizationTool(deployTarget) {
  return deployTarget === "VPS" ? "Metabase" : "Evidence";
}

function validateDecisionCombination({ visualizationTool, deployTarget }) {
  const isStaticTarget = deployTarget === "Netlify" || deployTarget === "Vercel";
  const isServerOnlyTool = visualizationTool === "Metabase" || visualizationTool === "Grafana" || visualizationTool === "Apache Superset";

  if (isStaticTarget && isServerOnlyTool) {
    throw new Error(
      `${visualizationTool} requires VPS deployment. Use Evidence for ${deployTarget}, or switch deploy target to VPS.`,
    );
  }

  if (deployTarget === "VPS" && visualizationTool === "Evidence") {
    throw new Error("Evidence is the static-site path. Use Netlify or Vercel as the deploy target.");
  }
}

if (require.main === module) {
  const payload = process.argv[2] ? JSON.parse(process.argv[2]) : {};
  planIntakeValidation(payload)
    .then((result) => console.log(JSON.stringify(result, null, 2)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  planIntakeValidation,
  VALID_FRAMEWORKS,
  VALID_GOAL_TIERS,
  VALID_TOOLS,
  VALID_DEPLOY_TARGETS,
};
