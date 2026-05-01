const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");

const repoRoot = path.join(__dirname, "..");

test("canonical prompt hub and workflow prompts exist", async () => {
  const promptFiles = [
    ".codex/prompts/dv.md",
    ".codex/prompts/dv-help.md",
    ".codex/prompts/dv-plan.md",
    ".codex/prompts/dv-cook.md",
    ".codex/prompts/dv-data-visualize.md",
    ".codex/prompts/dv-publish.md",
  ];

  for (const relativePath of promptFiles) {
    const content = await fs.readFile(path.join(repoRoot, relativePath), "utf8");
    assert.match(content, /^---\r?\n/);
    assert.match(content, /description:/);
  }
});

test("hub prompt exposes canonical $dv routing surface", async () => {
  const content = await fs.readFile(path.join(repoRoot, ".codex/prompts/dv.md"), "utf8");

  assert.match(content, /\$dv-help/);
  assert.match(content, /\$dv-plan/);
  assert.match(content, /\$dv-cook/);
  assert.match(content, /\$dv-data-preparation/);
  assert.match(content, /\$dv-data-visualize/);
});

test("canonical skill hub and workflow wrappers exist", async () => {
  const skillFiles = [
    ".agents/skills/dv/SKILL.md",
    ".agents/skills/dv-help/SKILL.md",
    ".agents/skills/plan/SKILL.md",
    ".agents/skills/dv-cook/SKILL.md",
    ".agents/skills/dv-data-preparation/SKILL.md",
    ".agents/skills/dv-data-visualize/SKILL.md",
    ".agents/skills/dv-publish/SKILL.md",
    ".agents/skills/dv-debug/SKILL.md",
    ".agents/skills/dv-document-management/SKILL.md",
  ];

  for (const relativePath of skillFiles) {
    const content = await fs.readFile(path.join(repoRoot, relativePath), "utf8");
    assert.match(content, /^---\r?\n/);
    assert.match(content, /name:/);
    assert.match(content, /description:/);
  }
});
