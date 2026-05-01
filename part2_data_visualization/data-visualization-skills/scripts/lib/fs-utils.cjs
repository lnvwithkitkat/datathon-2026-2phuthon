const fs = require("node:fs/promises");
const path = require("node:path");

async function ensureDir(targetPath) {
  await fs.mkdir(targetPath, { recursive: true });
}

async function writeTextFile(filePath, content) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, content, "utf8");
}

async function writeMany(files) {
  for (const [filePath, content] of Object.entries(files)) {
    await writeTextFile(filePath, content);
  }
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-")
    .slice(0, 60);
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function safeRemoveDir(targetPath, rootPath) {
  const relative = path.relative(rootPath, targetPath);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`Refusing to remove path outside root: ${targetPath}`);
  }
  await fs.rm(targetPath, { recursive: true, force: true });
}

module.exports = {
  ensureDir,
  pathExists,
  safeRemoveDir,
  slugify,
  writeMany,
  writeTextFile,
};
