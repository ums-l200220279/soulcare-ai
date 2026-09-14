const http = require('node:http');
const { URL } = require('node:url');
const { buildSupportPlan } = require('./supportPlan');

function setCommonHeaders(response, corsOrigin) {
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none';");
  response.setHeader('Access-Control-Allow-Origin', corsOrigin);
  response.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  response.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
}

function sendJson(response, statusCode, payload, corsOrigin) {
  setCommonHeaders(response, corsOrigin);
  response.statusCode = statusCode;
  response.end(JSON.stringify(payload));
}

function readBody(request, limitBytes) {
  return new Promise((resolve, reject) => {
    let body = '';

    request.on('data', (chunk) => {
      body += chunk;
      if (Buffer.byteLength(body, 'utf8') > limitBytes) {
        reject(new Error('Payload too large'));
        request.destroy();
      }
    });

    request.on('end', () => resolve(body));
    request.on('error', reject);
  });
}

function createServer(config, logger) {
  return http.createServer(async (request, response) => {
    const startedAt = Date.now();
    const requestUrl = new URL(request.url, `http://${request.headers.host || 'localhost'}`);

    if (request.method === 'OPTIONS') {
      sendJson(response, 204, {}, config.corsOrigin);
      return;
    }

    if (request.method === 'GET' && requestUrl.pathname === '/health') {
      sendJson(
        response,
        200,
        {
          status: 'ok',
          service: 'soulcare-api',
          environment: config.env,
          timestamp: new Date().toISOString(),
        },
        config.corsOrigin,
      );
      return;
    }

    if (request.method === 'POST' && requestUrl.pathname === '/v1/support-plan') {
      try {
        const body = await readBody(request, config.requestBodyLimitBytes);
        const parsed = body ? JSON.parse(body) : {};
        const supportPlan = buildSupportPlan(parsed);
        sendJson(response, 200, supportPlan, config.corsOrigin);
      } catch (error) {
        const statusCode = error.message === 'Payload too large' ? 413 : 400;
        sendJson(
          response,
          statusCode,
          {
            error: 'invalid_request',
            message: statusCode === 413 ? 'Request payload exceeds limit' : 'Malformed JSON request body',
          },
          config.corsOrigin,
        );
      }
      return;
    }

    sendJson(response, 404, { error: 'not_found' }, config.corsOrigin);

    logger.info('request_completed', {
      method: request.method,
      path: requestUrl.pathname,
      statusCode: response.statusCode,
      durationMs: Date.now() - startedAt,
    });
  });
}

module.exports = {
  createServer,
};
