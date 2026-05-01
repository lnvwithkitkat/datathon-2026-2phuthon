const knownWorkflows = new Set([
  "plan",
  "cook",
  "data-preparation",
  "data-visualize",
  "publish",
  "debug",
  "document-management",
  "help",
]);

function workflowRoutingGate({ workflowName, brief }) {
  if (!knownWorkflows.has(workflowName)) {
    throw new Error(`Unknown workflow: ${workflowName}`);
  }

  if (workflowName !== "help" && (!brief || String(brief).trim() === "")) {
    throw new Error(`Workflow ${workflowName} requires a non-empty brief.`);
  }

  return { ok: true, workflowName };
}

if (require.main === module) {
  try {
    console.log(
      JSON.stringify(
        workflowRoutingGate({
          workflowName: process.argv[2],
          brief: process.argv[3],
        }),
        null,
        2,
      ),
    );
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

module.exports = {
  workflowRoutingGate,
};
