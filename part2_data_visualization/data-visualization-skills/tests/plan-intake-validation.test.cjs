const test = require("node:test");
const assert = require("node:assert/strict");

const {
  planIntakeValidation,
  VALID_FRAMEWORKS,
  VALID_GOAL_TIERS,
  VALID_TOOLS,
  VALID_DEPLOY_TARGETS,
} = require("../scripts/hooks/plan-intake-validation.cjs");

// ---------------------------------------------------------------------------
// Non-interactive path - all four decisions supplied via flags
// ---------------------------------------------------------------------------

test("planIntakeValidation accepts explicit flag values in non-interactive mode", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "CRISP-DM",
      "goal-tier": "Pro",
      "visualization-tool": "Metabase",
      "deploy-target": "VPS",
    },
    interactive: false,
  });

  assert.equal(result.ok, true);
  assert.equal(result.framework, "CRISP-DM");
  assert.equal(result.goalTier, "Pro");
  assert.equal(result.visualizationTool, "Metabase");
  assert.equal(result.deployTarget, "VPS");
});

test("planIntakeValidation accepts Grafana and Advanced in non-interactive mode", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "Data Pipeline",
      "goal-tier": "Advanced",
      "visualization-tool": "Grafana",
      "deploy-target": "VPS",
    },
    interactive: false,
  });

  assert.equal(result.framework, "Data Pipeline");
  assert.equal(result.goalTier, "Advanced");
  assert.equal(result.visualizationTool, "Grafana");
  assert.equal(result.deployTarget, "VPS");
});

test("planIntakeValidation is case-insensitive for flag values", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "crisp-dm",
      "goal-tier": "basic",
      "visualization-tool": "evidence",
      "deploy-target": "netlify",
    },
    interactive: false,
  });

  assert.equal(result.framework, "CRISP-DM");
  assert.equal(result.goalTier, "Basic");
  assert.equal(result.visualizationTool, "Evidence");
  assert.equal(result.deployTarget, "Netlify");
});

test("planIntakeValidation applies Pro and Metabase defaults in non-interactive mode when flags are absent", async () => {
  // Pro and Metabase have defaults; framework has no default → should still not throw
  // because non-interactive with no framework flag falls back to null default path.
  // In non-interactive mode with missing framework, it should throw.
  await assert.rejects(
    () => planIntakeValidation({ flags: {}, interactive: false }),
    (err) => {
      assert.match(err.message, /Framework/);
      assert.match(err.message, /non-interactive/);
      return true;
    },
  );
});

test("planIntakeValidation rejects invalid flag value with descriptive error", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "NotAFramework",
          "goal-tier": "Pro",
          "visualization-tool": "Metabase",
          "deploy-target": "VPS",
        },
        interactive: false,
      }),
    (err) => {
      assert.match(err.message, /Invalid Framework/);
      assert.match(err.message, /NotAFramework/);
      return true;
    },
  );
});

test("planIntakeValidation rejects invalid goal-tier in non-interactive mode", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "CRISP-DM",
          "goal-tier": "Expert",
          "visualization-tool": "Metabase",
          "deploy-target": "VPS",
        },
        interactive: false,
      }),
    (err) => {
      assert.match(err.message, /Invalid Goal tier/);
      return true;
    },
  );
});

test("planIntakeValidation rejects invalid visualization-tool in non-interactive mode", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "CRISP-DM",
          "goal-tier": "Pro",
          "visualization-tool": "Tableau",
          "deploy-target": "VPS",
        },
        interactive: false,
      }),
    (err) => {
      assert.match(err.message, /Invalid Visualization tool/);
      return true;
    },
  );
});

test("accepts Netlify as deploy target", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "CRISP-DM",
      "goal-tier": "Pro",
      "visualization-tool": "Evidence",
      "deploy-target": "Netlify",
    },
    interactive: false,
  });

  assert.equal(result.deployTarget, "Netlify");
});

test("accepts VPS as deploy target", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "CRISP-DM",
      "goal-tier": "Pro",
      "visualization-tool": "Metabase",
      "deploy-target": "VPS",
    },
    interactive: false,
  });

  assert.equal(result.deployTarget, "VPS");
});

test("defaults deployTarget to Netlify when not provided (non-interactive)", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "CRISP-DM",
      "goal-tier": "Pro",
    },
    interactive: false,
  });

  assert.equal(result.deployTarget, "Netlify");
  assert.equal(result.visualizationTool, "Evidence");
});

test("throws on invalid deploy target in non-interactive mode", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "CRISP-DM",
          "goal-tier": "Pro",
          "visualization-tool": "Metabase",
          "deploy-target": "AWS",
        },
        interactive: false,
      }),
    /Invalid Deploy target/,
  );
});

test("accepts Evidence as visualization tool", async () => {
  const result = await planIntakeValidation({
    flags: {
      framework: "CRISP-DM",
      "goal-tier": "Basic",
      "visualization-tool": "Evidence",
      "deploy-target": "Netlify",
    },
    interactive: false,
  });

  assert.equal(result.visualizationTool, "Evidence");
});

test("rejects Metabase on Netlify", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "CRISP-DM",
          "goal-tier": "Pro",
          "visualization-tool": "Metabase",
          "deploy-target": "Netlify",
        },
        interactive: false,
      }),
    /requires VPS deployment/,
  );
});

test("rejects Evidence on VPS", async () => {
  await assert.rejects(
    () =>
      planIntakeValidation({
        flags: {
          framework: "CRISP-DM",
          "goal-tier": "Basic",
          "visualization-tool": "Evidence",
          "deploy-target": "VPS",
        },
        interactive: false,
      }),
    /static-site path/,
  );
});

// ---------------------------------------------------------------------------
// Constants sanity checks
// ---------------------------------------------------------------------------

test("VALID_FRAMEWORKS contains exactly CRISP-DM and Data Pipeline", () => {
  assert.deepEqual(VALID_FRAMEWORKS, ["CRISP-DM", "Data Pipeline"]);
});

test("VALID_GOAL_TIERS contains exactly Basic, Pro, Advanced", () => {
  assert.deepEqual(VALID_GOAL_TIERS, ["Basic", "Pro", "Advanced"]);
});

test("VALID_TOOLS contains exactly Evidence, Metabase, Grafana, Apache Superset", () => {
  assert.deepEqual(VALID_TOOLS, ["Evidence", "Metabase", "Grafana", "Apache Superset"]);
});

test("VALID_DEPLOY_TARGETS contains exactly Netlify, Vercel, VPS", () => {
  assert.deepEqual(VALID_DEPLOY_TARGETS, ["Netlify", "Vercel", "VPS"]);
});
