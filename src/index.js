const { getConfig } = require('./config');
const { createLogger } = require('./logger');
const { createServer } = require('./server');

function start() {
  const config = getConfig();
  const logger = createLogger();
  const server = createServer(config, logger);

  server.listen(config.port, () => {
    logger.info('server_started', {
      port: config.port,
      environment: config.env,
    });
  });

  const shutdown = () => {
    logger.info('shutdown_signal_received');
    server.close(() => {
      logger.info('server_stopped');
      process.exit(0);
    });
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

if (require.main === module) {
  start();
}

module.exports = {
  start,
};
