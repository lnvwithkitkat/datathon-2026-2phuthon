const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function normalizePath(value) {
  return String(value || "").replace(/\\/g, "/");
}

function parseStatusEntriesFromText(output) {
  if (!output) {
    return [];
  }

  return String(output)
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      const match = line.match(/^(.{2})\s(.*)$/);
      if (!match) {
        return {
          code: line.slice(0, 2),
          paths: [normalizePath(line.slice(2).trim())],
        };
      }

      const [, code, rawPaths] = match;
      const paths = rawPaths.includes(" -> ")
        ? rawPaths.split(" -> ").map((item) => normalizePath(item.trim()))
        : [normalizePath(rawPaths)];
      return { code, paths };
    });
}

function isProjectUserPath(targetPath, projectsReadme = "projects/README.md") {
  return normalizePath(targetPath).startsWith("projects/") && normalizePath(targetPath) !== normalizePath(projectsReadme);
}

function collectCoreChanges(entries, projectsReadme = "projects/README.md") {
  const paths = new Set();

  for (const entry of entries) {
    for (const targetPath of entry.paths) {
      if (!isProjectUserPath(targetPath, projectsReadme)) {
        paths.add(normalizePath(targetPath));
      }
    }
  }

  return [...paths].sort();
}

function listProjectEntries(projectsRoot) {
  if (!fs.existsSync(projectsRoot)) {
    return [];
  }

  return fs.readdirSync(projectsRoot).filter((entry) => entry !== "README.md");
}

function copyRecursive(source, target) {
  const stat = fs.statSync(source);
  if (stat.isDirectory()) {
    fs.mkdirSync(target, { recursive: true });
    for (const entry of fs.readdirSync(source)) {
      copyRecursive(path.join(source, entry), path.join(target, entry));
    }
    return;
  }

  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
}

function backupProjects(projectsRoot) {
  const entries = listProjectEntries(projectsRoot);
  if (entries.length === 0) {
    return null;
  }

  const backupRoot = fs.mkdtempSync(path.join(os.tmpdir(), "dv-kit-projects-backup-"));
  for (const entry of entries) {
    copyRecursive(path.join(projectsRoot, entry), path.join(backupRoot, entry));
  }

  return { backupRoot, entries };
}

function removeProjectUserData(projectsRoot) {
  for (const entry of listProjectEntries(projectsRoot)) {
    fs.rmSync(path.join(projectsRoot, entry), { recursive: true, force: true });
  }
}

function restoreProjects(projectsRoot, backup) {
  if (!backup) {
    return;
  }

  fs.mkdirSync(projectsRoot, { recursive: true });
  for (const entry of backup.entries) {
    copyRecursive(path.join(backup.backupRoot, entry), path.join(projectsRoot, entry));
  }
}

function cleanupBackup(backup) {
  if (!backup) {
    return;
  }

  fs.rmSync(backup.backupRoot, { recursive: true, force: true });
}

module.exports = {
  backupProjects,
  cleanupBackup,
  collectCoreChanges,
  listProjectEntries,
  normalizePath,
  parseStatusEntriesFromText,
  removeProjectUserData,
  restoreProjects,
};
