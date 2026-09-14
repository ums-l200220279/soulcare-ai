function format(level, message, metadata = {}) {
  return JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    ...metadata,
  });
}

function createLogger(out = console) {
  return {
    info(message, metadata) {
      out.log(format('info', message, metadata));
    },
    error(message, metadata) {
      out.error(format('error', message, metadata));
    },
  };
}

module.exports = {
  createLogger,
};
