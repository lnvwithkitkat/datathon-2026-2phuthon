function providerKeyGate(requiredProviders) {
  const missing = [];

  for (const provider of requiredProviders) {
    const envName = `${provider.toUpperCase().replace(/[^A-Z0-9]+/g, "_")}_API_KEY`;
    if (!process.env[envName]) {
      missing.push(envName);
    }
  }

  return {
    ok: missing.length === 0,
    missing,
  };
}

if (require.main === module) {
  const providers = process.argv.slice(2);
  const result = providerKeyGate(providers);
  if (!result.ok) {
    console.error(JSON.stringify(result, null, 2));
    process.exitCode = 1;
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

module.exports = {
  providerKeyGate,
};

