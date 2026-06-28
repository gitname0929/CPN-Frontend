#!/usr/bin/env node

const http = require('http');
const net = require('net');
const { URL } = require('url');

const LISTEN_HOST = process.env.PUBLIC_PROXY_HOST || '0.0.0.0';
const LISTEN_PORT = Number(process.env.PUBLIC_PROXY_PORT || 7002);
const FRONTEND_TARGET = new URL(process.env.PUBLIC_PROXY_FRONTEND || 'http://127.0.0.1:7001');
const API_TARGET = new URL(process.env.PUBLIC_PROXY_API || 'http://127.0.0.1:8099');
const AUTH_USER = process.env.PUBLIC_PROXY_USER || '709';
const AUTH_PASSWORD = process.env.PUBLIC_PROXY_PASSWORD || 'Sancog123';
const REALM = process.env.PUBLIC_PROXY_REALM || 'CPN';

const expectedAuth = 'Basic ' + Buffer.from(`${AUTH_USER}:${AUTH_PASSWORD}`).toString('base64');

function isAuthorized(req) {
  return req.headers.authorization === expectedAuth;
}

function sendUnauthorized(res) {
  res.writeHead(401, {
    'WWW-Authenticate': `Basic realm="${REALM}"`,
    'Content-Type': 'text/plain; charset=utf-8',
  });
  res.end('Authentication required\n');
}

function pickTarget(pathname) {
  return pathname === '/api' || pathname.startsWith('/api/') ? API_TARGET : FRONTEND_TARGET;
}

function buildForwardHeaders(req, target) {
  const headers = { ...req.headers };
  delete headers.authorization;
  delete headers['proxy-authorization'];
  headers.host = target.host;
  headers['x-forwarded-host'] = req.headers.host || '';
  headers['x-forwarded-proto'] = req.socket.encrypted ? 'https' : 'http';
  headers['x-forwarded-for'] = [req.socket.remoteAddress, req.headers['x-forwarded-for']]
    .filter(Boolean)
    .join(', ');
  return headers;
}

function proxyHttp(req, res) {
  if (!isAuthorized(req)) {
    sendUnauthorized(res);
    return;
  }

  const requestUrl = new URL(req.url, 'http://placeholder.local');
  const target = pickTarget(requestUrl.pathname);
  const upstream = http.request(
    {
      protocol: target.protocol,
      hostname: target.hostname,
      port: target.port || 80,
      path: req.url,
      method: req.method,
      headers: buildForwardHeaders(req, target),
      timeout: 0,
    },
    (upstreamRes) => {
      res.writeHead(upstreamRes.statusCode || 502, upstreamRes.headers);
      upstreamRes.pipe(res);
    },
  );

  upstream.on('error', (error) => {
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' });
    }
    res.end(`Bad gateway to ${target.href}: ${error.message}\n`);
  });

  req.pipe(upstream);
}

function proxyUpgrade(req, socket, head) {
  if (!isAuthorized(req)) {
    socket.write(
      `HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="${REALM}"\r\nConnection: close\r\n\r\n`,
    );
    socket.destroy();
    return;
  }

  const requestUrl = new URL(req.url, 'http://placeholder.local');
  const target = pickTarget(requestUrl.pathname);
  const upstream = net.connect(Number(target.port || 80), target.hostname, () => {
    const headers = buildForwardHeaders(req, target);
    const headerLines = Object.entries(headers)
      .map(([key, value]) => `${key}: ${value}`)
      .join('\r\n');
    upstream.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n${headerLines}\r\n\r\n`);
    if (head && head.length) upstream.write(head);
    socket.pipe(upstream).pipe(socket);
  });

  upstream.on('error', () => socket.destroy());
}

const server = http.createServer(proxyHttp);
server.timeout = 0;
server.keepAliveTimeout = 75000;
server.headersTimeout = 76000;
server.on('upgrade', proxyUpgrade);

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  console.log(
    `public auth proxy listening on ${LISTEN_HOST}:${LISTEN_PORT}; frontend=${FRONTEND_TARGET.href}; api=${API_TARGET.href}; user=${AUTH_USER}`,
  );
});
