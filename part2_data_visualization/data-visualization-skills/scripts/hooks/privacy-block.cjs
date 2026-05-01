const path = require("node:path");

const APPROVED_PREFIX = "APPROVED:";
const SAFE_PATTERNS = [/\.example$/i, /\.sample$/i, /\.template$/i];
const PRIVACY_PATTERNS = [
  /^\.env$/i,
  /^\.env\./i,
  /\.env$/i,
  /\/\.env\./i,
  /\.npmrc$/i,
  /\.pypirc$/i,
  /credentials/i,
  /secrets?\.json$/i,
  /token(?:\.txt)?$/i,
  /github_token$/i,
  /id_rsa$/i,
  /id_ed25519$/i,
  /\.pem$/i,
  /\.key$/i,
];

function isSafeFile(filePath) {
  const baseName = path.basename(String(filePath || ""));
  return SAFE_PATTERNS.some((pattern) => pattern.test(baseName));
}

function hasApprovalPrefix(filePath) {
  return typeof filePath === "string" && filePath.startsWith(APPROVED_PREFIX);
}

function stripApprovalPrefix(filePath) {
  return hasApprovalPrefix(filePath) ? filePath.slice(APPROVED_PREFIX.length) : filePath;
}

function isSuspiciousPath(filePath) {
  const cleanPath = String(filePath || "");
  return cleanPath.includes("..") || path.isAbsolute(cleanPath);
}

function isPrivacySensitive(filePath) {
  if (!filePath) {
    return false;
  }

  const stripped = stripApprovalPrefix(String(filePath));
  let normalized = stripped.replace(/\\/g, "/");
  try {
    normalized = decodeURIComponent(normalized);
  } catch {
    // Keep the original string when URI decoding fails.
  }

  if (isSafeFile(normalized)) {
    return false;
  }

  const baseName = path.basename(normalized);
  return PRIVACY_PATTERNS.some((pattern) => pattern.test(baseName) || pattern.test(normalized));
}

function extractPaths(toolInput) {
  const paths = [];
  if (!toolInput || typeof toolInput !== "object") {
    return paths;
  }

  for (const field of ["file_path", "path", "pattern"]) {
    if (toolInput[field]) {
      paths.push({ field, value: toolInput[field] });
    }
  }

  if (toolInput.command) {
    const command = String(toolInput.command);
    const approvedMatches = command.match(/APPROVED:[^\s"'`]+/g) || [];
    for (const match of approvedMatches) {
      paths.push({ field: "command", value: match });
    }

    if (approvedMatches.length === 0) {
      const envMatches = command.match(/\.env(?:[^\s"'`)]*)/g) || [];
      for (const match of envMatches) {
        paths.push({ field: "command", value: match });
      }
    }
  }

  return paths;
}

function buildPromptData(filePath) {
  const basename = path.basename(filePath);
  return {
    type: "PRIVACY_PROMPT",
    file: filePath,
    basename,
    question: {
      header: "File Access",
      text: `I need to read "${basename}" which may contain sensitive data (API keys, passwords, tokens). Do you approve?`,
      options: [
        { label: "Yes, approve access", description: `Allow reading ${basename} this time` },
        { label: "No, skip this file", description: "Continue without accessing this file" },
      ],
    },
  };
}

function checkPrivacy({ toolName = "", toolInput = {}, options = {} }) {
  const isBashTool = toolName === "Bash";
  const allowBash = options.allowBash !== false;

  for (const candidate of extractPaths(toolInput)) {
    if (!isPrivacySensitive(candidate.value)) {
      continue;
    }

    if (hasApprovalPrefix(candidate.value)) {
      const stripped = stripApprovalPrefix(candidate.value);
      return {
        blocked: false,
        approved: true,
        filePath: stripped,
        field: candidate.field,
        suspicious: isSuspiciousPath(stripped),
        reason: "approved",
      };
    }

    if (isBashTool && allowBash) {
      return {
        blocked: false,
        filePath: candidate.value,
        field: candidate.field,
        isBash: true,
        reason: `Bash command accesses sensitive file: ${candidate.value}`,
      };
    }

    return {
      blocked: true,
      filePath: candidate.value,
      field: candidate.field,
      reason: "Sensitive file access requires user approval.",
      promptData: buildPromptData(candidate.value),
    };
  }

  return {
    blocked: false,
    reason: "ok",
  };
}

function privacyBlock(input) {
  if (typeof input === "string") {
    return checkPrivacy({
      toolName: "Read",
      toolInput: { file_path: input },
    });
  }

  if (input && typeof input === "object" && (input.toolName || input.toolInput)) {
    return checkPrivacy({
      toolName: input.toolName,
      toolInput: input.toolInput,
      options: input.options,
    });
  }

  if (input && typeof input === "object") {
    return checkPrivacy({
      toolName: input.tool_name,
      toolInput: input.tool_input,
      options: input.options,
    });
  }

  return {
    blocked: false,
    reason: "ok",
  };
}

if (require.main === module) {
  const rawInput = process.argv[2] || "";
  try {
    const parsed = rawInput.trim().startsWith("{") ? JSON.parse(rawInput) : rawInput;
    console.log(JSON.stringify(privacyBlock(parsed), null, 2));
  } catch {
    console.log(JSON.stringify(privacyBlock(rawInput), null, 2));
  }
}

module.exports = {
  APPROVED_PREFIX,
  buildPromptData,
  checkPrivacy,
  extractPaths,
  hasApprovalPrefix,
  isPrivacySensitive,
  isSafeFile,
  isSuspiciousPath,
  privacyBlock,
  stripApprovalPrefix,
};
