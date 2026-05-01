const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execSync } = require("node:child_process");

const USAGE_CACHE_FILE = path.join(os.tmpdir(), "dv-usage-limits-cache.json");
const PROMPT_FETCH_INTERVAL_MS = 60_000;
const TOOL_FETCH_INTERVAL_MS = 300_000;
const OAUTH_ENDPOINT = "https://api.anthropic.com/api/oauth/usage";

function getUsageCacheFile() {
  return USAGE_CACHE_FILE;
}

function getClaudeCredentials() {
  if (process.env.CLAUDE_CODE_OAUTH_TOKEN) {
    return process.env.CLAUDE_CODE_OAUTH_TOKEN;
  }

  if (os.platform() === "darwin") {
    try {
      const raw = execSync('security find-generic-password -s "Claude Code-credentials" -w', {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["pipe", "pipe", "ignore"],
      }).trim();
      const parsed = JSON.parse(raw);
      if (parsed.claudeAiOauth?.accessToken) {
        return parsed.claudeAiOauth.accessToken;
      }
    } catch {
      // Fall back to file-based credentials.
    }
  }

  const credentialsPath = path.join(os.homedir(), ".claude", ".credentials.json");
  try {
    const raw = fs.readFileSync(credentialsPath, "utf8");
    const parsed = JSON.parse(raw);
    return parsed.claudeAiOauth?.accessToken || null;
  } catch {
    return null;
  }
}

function readUsageCache(cacheFile = USAGE_CACHE_FILE) {
  try {
    if (!fs.existsSync(cacheFile)) {
      return null;
    }
    return JSON.parse(fs.readFileSync(cacheFile, "utf8"));
  } catch {
    return null;
  }
}

function writeUsageCache({ status, data = null, cacheFile = USAGE_CACHE_FILE }) {
  const tempFile = `${cacheFile}.${process.pid}.${Date.now()}.tmp`;
  const payload = {
    timestamp: Date.now(),
    status,
    data,
  };

  try {
    fs.writeFileSync(tempFile, JSON.stringify(payload, null, 2));
    fs.renameSync(tempFile, cacheFile);
  } catch {
    try {
      fs.unlinkSync(tempFile);
    } catch {
      // Ignore cleanup failures.
    }
  }
}

function shouldFetch({ event = "UserPromptSubmit", cache = readUsageCache() } = {}) {
  const interval = event === "UserPromptSubmit" ? PROMPT_FETCH_INTERVAL_MS : TOOL_FETCH_INTERVAL_MS;
  if (!cache?.timestamp) {
    return true;
  }
  return Date.now() - cache.timestamp >= interval;
}

function formatResetWindow(resetAt) {
  if (!resetAt) {
    return null;
  }

  const remainingMs = new Date(resetAt).getTime() - Date.now();
  if (!Number.isFinite(remainingMs) || remainingMs <= 0) {
    return null;
  }

  const hours = Math.floor(remainingMs / 3_600_000);
  const minutes = Math.floor((remainingMs % 3_600_000) / 60_000);
  return `${hours}h ${minutes}m`;
}

function summarizeUsageData(data) {
  if (!data) {
    return "Usage unavailable";
  }

  const parts = [];
  if (typeof data.five_hour?.utilization === "number") {
    parts.push(`5h ${Math.round(data.five_hour.utilization)}%`);
    const reset = formatResetWindow(data.five_hour.resets_at);
    if (reset) {
      parts.push(`5h reset ${reset}`);
    }
  }

  if (typeof data.seven_day?.utilization === "number") {
    parts.push(`7d ${Math.round(data.seven_day.utilization)}%`);
  }

  return parts.length > 0 ? parts.join(" | ") : "Usage available";
}

async function fetchUsageFromApi({ token, fetchImpl = globalThis.fetch } = {}) {
  if (!token) {
    return { ok: false, status: "unavailable", note: "missing-credentials", data: null };
  }

  try {
    const response = await fetchImpl(OAUTH_ENDPOINT, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        "anthropic-beta": "oauth-2025-04-20",
        "User-Agent": "data-visualization-kit/0.1.0",
      },
    });

    if (!response.ok) {
      return { ok: false, status: "unavailable", note: `http-${response.status}`, data: null };
    }

    return {
      ok: true,
      status: "available",
      note: "fetched",
      data: await response.json(),
    };
  } catch {
    return { ok: false, status: "unavailable", note: "fetch-failed", data: null };
  }
}

async function runUsageContextAwareness({
  event = "UserPromptSubmit",
  cacheFile = USAGE_CACHE_FILE,
  fetchImpl = globalThis.fetch,
  tokenLoader = getClaudeCredentials,
} = {}) {
  const cache = readUsageCache(cacheFile);
  if (!shouldFetch({ event, cache })) {
    return {
      ok: cache?.status === "available",
      cacheStatus: cache?.status || "unknown",
      note: "throttled",
      data: cache?.data || null,
      summary: summarizeUsageData(cache?.data),
      cacheFile,
    };
  }

  const token = tokenLoader();
  const fetched = await fetchUsageFromApi({ token, fetchImpl });
  writeUsageCache({
    status: fetched.status,
    data: fetched.data,
    cacheFile,
  });

  return {
    ok: fetched.ok,
    cacheStatus: fetched.status,
    note: fetched.note,
    data: fetched.data,
    summary: summarizeUsageData(fetched.data),
    cacheFile,
  };
}

if (require.main === module) {
  runUsageContextAwareness()
    .then((result) => console.log(JSON.stringify(result, null, 2)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  fetchUsageFromApi,
  formatResetWindow,
  getClaudeCredentials,
  getUsageCacheFile,
  PROMPT_FETCH_INTERVAL_MS,
  readUsageCache,
  runUsageContextAwareness,
  shouldFetch,
  summarizeUsageData,
  TOOL_FETCH_INTERVAL_MS,
  writeUsageCache,
};
