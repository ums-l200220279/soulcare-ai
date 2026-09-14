const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { createServer } = require('../src/server');

function request(port, method, path, payload) {
  return new Promise((resolve, reject) => {
    const body = payload ? JSON.stringify(payload) : null;
    const req = http.request(
      {
        host: '127.0.0.1',
        port,
        method,
        path,
        headers: body ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } : {},
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: data ? JSON.parse(data) : {} });
        });
      },
    );

    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

test('GET /health returns status ok', async () => {
  const logs = [];
  const server = createServer(
    { env: 'test', port: 0, requestBodyLimitBytes: 4096, corsOrigin: '*' },
    { info: (message) => logs.push(message) },
  );

  await new Promise((resolve) => server.listen(0, resolve));
  const port = server.address().port;

  const response = await request(port, 'GET', '/health');
  assert.equal(response.statusCode, 200);
  assert.equal(response.body.status, 'ok');

  await new Promise((resolve) => server.close(resolve));
});

test('POST /v1/support-plan returns generated plan', async () => {
  const server = createServer(
    { env: 'test', port: 0, requestBodyLimitBytes: 4096, corsOrigin: '*' },
    { info: () => {} },
  );

  await new Promise((resolve) => server.listen(0, resolve));
  const port = server.address().port;

  const response = await request(port, 'POST', '/v1/support-plan', {
    userId: 'user-1',
    stressScore: 0.8,
  });

  assert.equal(response.statusCode, 200);
  assert.equal(response.body.userId, 'user-1');
  assert.equal(response.body.stressLevel, 'high');
  assert.ok(Array.isArray(response.body.recommendedPlan.actions));

  await new Promise((resolve) => server.close(resolve));
});
