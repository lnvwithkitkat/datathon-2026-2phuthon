const test = require("node:test");
const assert = require("node:assert/strict");

const { findForbiddenPaths, isZeroSha, normalizePath } = require("../scripts/lib/no-docs-plans-guard.cjs");

test("findForbiddenPaths flags only root docs and plans paths", () => {
  const paths = findForbiddenPaths([
    "docs/system-architecture.md",
    "plans/260417-1746-dv-workflow-architecture-revision/plan.md",
    "projects/demo/docs/project-plan.md",
    ".codex/workflows/primary-workflow.md",
  ]);

  assert.deepEqual(paths, [
    "docs/system-architecture.md",
    "plans/260417-1746-dv-workflow-architecture-revision/plan.md",
  ]);
});

test("normalizePath converts windows separators", () => {
  assert.equal(normalizePath("plans\\phase-01.md"), "plans/phase-01.md");
});

test("isZeroSha detects empty remote refs", () => {
  assert.equal(isZeroSha("0000000000000000000000000000000000000000"), true);
  assert.equal(isZeroSha("8cbec07"), false);
});
