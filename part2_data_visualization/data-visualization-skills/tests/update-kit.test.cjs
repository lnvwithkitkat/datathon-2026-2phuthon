const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");

const {
  backupProjects,
  cleanupBackup,
  collectCoreChanges,
  parseStatusEntriesFromText,
  removeProjectUserData,
  restoreProjects,
} = require("../scripts/lib/update-kit-core.cjs");

test("parseStatusEntriesFromText parses modified, untracked, and renamed entries", () => {
  const entries = parseStatusEntriesFromText([
    " M README.md",
    "?? projects/demo-user/notes.md",
    "R  docs/old.md -> docs/new.md",
  ].join("\n"));

  assert.deepEqual(entries, [
    { code: " M", paths: ["README.md"] },
    { code: "??", paths: ["projects/demo-user/notes.md"] },
    { code: "R ", paths: ["docs/old.md", "docs/new.md"] },
  ]);
});

test("collectCoreChanges ignores user project paths but keeps core paths", () => {
  const changes = collectCoreChanges([
    { code: " M", paths: ["README.md"] },
    { code: "??", paths: ["projects/demo-user/docs/project-plan.md"] },
    { code: " M", paths: ["projects/README.md"] },
    { code: "??", paths: [".codex/workflows/primary-workflow.md"] },
  ]);

  assert.deepEqual(changes, [
    ".codex/workflows/primary-workflow.md",
    "README.md",
    "projects/README.md",
  ]);
});

test("backup and restore preserve project entries while leaving projects README alone", async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "dv-kit-update-"));
  const projectsRoot = path.join(tempRoot, "projects");

  await fs.mkdir(path.join(projectsRoot, "demo-one", "docs"), { recursive: true });
  await fs.writeFile(path.join(projectsRoot, "demo-one", "docs", "project-brief.md"), "demo one", "utf8");
  await fs.writeFile(path.join(projectsRoot, "custom-note.txt"), "keep me", "utf8");
  await fs.writeFile(path.join(projectsRoot, "README.md"), "core readme", "utf8");

  const backup = backupProjects(projectsRoot);
  removeProjectUserData(projectsRoot);

  await assert.rejects(() => fs.access(path.join(projectsRoot, "demo-one")));
  await assert.rejects(() => fs.access(path.join(projectsRoot, "custom-note.txt")));
  await assert.doesNotReject(() => fs.access(path.join(projectsRoot, "README.md")));

  restoreProjects(projectsRoot, backup);

  await assert.doesNotReject(() => fs.access(path.join(projectsRoot, "demo-one", "docs", "project-brief.md")));
  await assert.doesNotReject(() => fs.access(path.join(projectsRoot, "custom-note.txt")));

  const readme = await fs.readFile(path.join(projectsRoot, "README.md"), "utf8");
  assert.equal(readme, "core readme");

  cleanupBackup(backup);
});
