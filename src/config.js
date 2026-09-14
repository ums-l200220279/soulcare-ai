const required = ['NODE_ENV'];

function validateEnvironment(env) {
  const missing = required.filter((key) => !env[key]);
  if (missing.length > 0) {
    throw new Error(`Missing required environment variable(s): ${missing.join(', ')}`);
  }
}

function toPositiveInt(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function getConfig(env = process.env) {
  validateEnvironment(env);

  return {
    env: env.NODE_ENV,
    port: toPositiveInt(env.PORT, 3000),
    requestBodyLimitBytes: toPositiveInt(env.REQUEST_BODY_LIMIT_BYTES, 16_384),
    corsOrigin: env.CORS_ORIGIN || '*',
  };
}

module.exports = {
  getConfig,
};
