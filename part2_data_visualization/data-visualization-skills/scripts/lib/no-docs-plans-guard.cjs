function normalizePath(value) {
  return String(value || "").replace(/\\/g, "/");
}

function findForbiddenPaths(paths) {
  return paths
    .map((item) => normalizePath(item).trim())
    .filter(Boolean)
    .filter((item) => item.startsWith("docs/") || item.startsWith("plans/"))
    .sort();
}

function isZeroSha(value) {
  return /^0+$/.test(String(value || ""));
}

module.exports = {
  findForbiddenPaths,
  isZeroSha,
  normalizePath,
};
