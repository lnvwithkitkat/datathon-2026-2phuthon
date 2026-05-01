const readline = require("node:readline/promises");
const { stdin, stdout } = require("node:process");

function parseArgs(argv) {
  const flags = {};
  const positional = [];

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) {
      positional.push(arg);
      continue;
    }

    const [rawKey, inlineValue] = arg.slice(2).split("=");
    const nextValue = inlineValue ?? argv[index + 1];
    const value = inlineValue ?? (nextValue && !nextValue.startsWith("--") ? nextValue : "true");
    if (inlineValue === undefined && value === nextValue && value !== "true") {
      index += 1;
    }
    flags[rawKey] = value;
  }

  return {
    command: positional[0] ?? "$dv-help",
    flags,
    positional,
    rawText: positional.join(" ").trim(),
  };
}

function printHelp() {
  const lines = [
    "Data Visualization Kit",
    "",
    "Commands:",
    "  $dv-plan <brief>",
    "  $dv-cook <brief>",
    "  $dv-data-preparation <brief>",
    "  $dv-data-visualize <brief>",
    "  $dv-publish <brief>",
    "  $dv-debug <brief>",
    "  $dv-document-management <brief>",
    "  $dv-help",
    "",
    "Examples:",
    '  npm run dv -- \'$dv-plan\' --project-context "E-commerce analysis" --project-dataset "Orders and customers" --project-goals "Show churn insights"',
    '  npm run dv -- \'$dv-cook\' --slug ecommerce-churn --brief "Run the full project workflow after intake approval"',
    '  npm run dv -- \'$dv-data-visualize\' --slug ecommerce-churn --brief "Rebuild visuals after source schema changed"',
  ];
  console.log(lines.join("\n"));
}

function resolveBoolean(value, fallback) {
  if (value === undefined || value === "") {
    return fallback;
  }
  return !["false", "0", "n", "no"].includes(String(value).trim().toLowerCase());
}

function hasTextValue(value) {
  return typeof value === "string" && value.trim() !== "" && value !== "true";
}

module.exports = {
  hasTextValue,
  parseArgs,
  printHelp,
  resolveBoolean,
};
