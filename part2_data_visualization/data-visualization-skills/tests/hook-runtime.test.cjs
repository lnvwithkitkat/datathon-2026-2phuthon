const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const {
  privacyBlock,
  APPROVED_PREFIX,
  isPrivacySensitive,
} = require("../scripts/hooks/privacy-block.cjs");
const { subagentInit } = require("../scripts/hooks/subagent-init.cjs");
const { runUserPromptSubmit } = require("../scripts/hooks/user-prompt-submit.cjs");
const {
  runUsageContextAwareness,
  summarizeUsageData,
  writeUsageCache,
} = require("../scripts/hooks/usage-context-awareness.cjs");

test("privacyBlock returns approval prompt data for sensitive tool input", () => {
  const result = privacyBlock({
    tool_name: "Read",
    tool_input: {
      file_path: "D:\\repo\\.env",
    },
  });

  assert.equal(result.blocked, true);
  assert.equal(result.filePath, "D:\\repo\\.env");
  assert.equal(result.promptData.type, "PRIVACY_PROMPT");
});

test("privacyBlock allows approved sensitive access and ignores safe templates", () => {
  const approved = privacyBlock({
    tool_name: "Read",
    tool_input: {
      file_path: `${APPROVED_PREFIX}.env`,
    },
  });
  const safe = privacyBlock("D:\\repo\\.env.example");

  assert.equal(approved.blocked, false);
  assert.equal(approved.approved, true);
  assert.equal(approved.filePath, ".env");
  assert.equal(safe.blocked, false);
  assert.equal(isPrivacySensitive("D:\\repo\\.env.example"), false);
});

test("privacyBlock warns but does not block bash access to approved workflow files", () => {
  const result = privacyBlock({
    tool_name: "Bash",
    tool_input: {
      command: 'cat ".env"',
    },
  });

  assert.equal(result.blocked, false);
  assert.equal(result.isBash, true);
  assert.match(result.reason, /Bash command accesses sensitive file/);
});

test("subagentInit builds clearer handoff payload", () => {
  const handoff = subagentInit({
    repoRoot: "D:\\repo",
    projectSlug: "demo-project",
    workflowName: "data-visualize",
    commandName: "$dv-data-visualize",
    brief: "Refresh dashboard visuals after schema change",
    promptContext: {
      interactive: false,
      projectSlug: "demo-project",
      rawText: "$dv-data-visualize refresh visuals",
      summary: "Command: $dv-data-visualize",
    },
    usage: {
      summary: "5h 42% | 7d 18%",
    },
  });

  assert.equal(handoff.projectRoot, "D:\\repo\\projects\\demo-project");
  assert.equal(handoff.outputsPath, "D:\\repo\\projects\\demo-project\\docs\\assets\\exports");
  assert.equal(handoff.plansPath, "D:\\repo\\plans");
  assert.equal(handoff.workflow.command, "$dv-data-visualize");
  assert.equal(handoff.promptContext.usageSummary, "5h 42% | 7d 18%");
});

test("runUserPromptSubmit includes usage summary in prompt context", async () => {
  const result = await runUserPromptSubmit({
    repoRoot: "D:\\repo",
    cwd: "D:\\repo",
    command: "$dv-plan",
    flags: {
      slug: "demo-project",
      "non-interactive": "true",
    },
    rawText: "$dv-plan build a churn dashboard",
    usageRunner: async () => ({
      ok: true,
      cacheStatus: "available",
      note: "fetched",
      summary: "5h 33% | 7d 12%",
    }),
  });

  assert.equal(result.projectSlug, "demo-project");
  assert.equal(result.interactive, false);
  assert.match(result.summary, /Usage: 5h 33% \| 7d 12%/);
});

test("runUsageContextAwareness reuses fresh cache without refetching", async () => {
  const cacheFile = path.join(os.tmpdir(), `dv-usage-cache-test-${process.pid}-${Date.now()}.json`);
  writeUsageCache({
    cacheFile,
    status: "available",
    data: {
      five_hour: {
        utilization: 41.6,
        resets_at: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
      },
      seven_day: {
        utilization: 9.2,
      },
    },
  });

  try {
    const result = await runUsageContextAwareness({
      event: "UserPromptSubmit",
      cacheFile,
      tokenLoader: () => {
        throw new Error("tokenLoader should not run when cache is fresh");
      },
    });

    assert.equal(result.note, "throttled");
    assert.match(result.summary, /5h 42%/);
    assert.match(result.summary, /7d 9%/);
  } finally {
    try {
      fs.unlinkSync(cacheFile);
    } catch {
      // Ignore cleanup failures.
    }
  }
});

test("summarizeUsageData falls back cleanly when no data exists", () => {
  assert.equal(summarizeUsageData(null), "Usage unavailable");
});
