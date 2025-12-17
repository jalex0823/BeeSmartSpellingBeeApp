// Debug tool: fetch rendered /quiz HTML, extract inline <script> blocks,
// and validate each block with the JS parser, mapping failures back to HTML line numbers.
//
// Usage: node debug_quiz_js_syntax.js

const http = require('http');

function parseSetCookie(setCookieHeaders) {
  const cookies = [];
  for (const h of setCookieHeaders || []) {
    const first = String(h || '').split(';')[0];
    if (first && first.includes('=')) cookies.push(first);
  }
  return cookies;
}

function mergeCookies(existing, newOnes) {
  const jar = new Map();
  for (const c of existing || []) {
    const [k, v] = String(c).split('=');
    if (k) jar.set(k, `${k}=${v ?? ''}`);
  }
  for (const c of newOnes || []) {
    const [k, v] = String(c).split('=');
    if (k) jar.set(k, `${k}=${v ?? ''}`);
  }
  return Array.from(jar.values());
}

function request(url, { method = 'GET', headers = {}, body = null, cookies = [] } = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = {
      protocol: u.protocol,
      hostname: u.hostname,
      port: u.port,
      path: u.pathname + u.search,
      method,
      headers: {
        ...headers,
      },
    };
    if (cookies.length) {
      opts.headers.Cookie = cookies.join('; ');
    }

    const req = http.request(opts, (res) => {
      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        const setCookies = parseSetCookie(res.headers['set-cookie']);
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data,
          cookies: mergeCookies(cookies, setCookies),
        });
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function fetchFollow(url, opts = {}, maxHops = 5) {
  let currentUrl = url;
  let cookies = opts.cookies || [];
  for (let i = 0; i <= maxHops; i++) {
    const res = await request(currentUrl, { ...opts, cookies });
    cookies = res.cookies || cookies;
    if (res.status >= 300 && res.status < 400 && res.headers && res.headers.location) {
      const next = new URL(res.headers.location, currentUrl).toString();
      currentUrl = next;
      // After a redirect, always GET
      opts = { ...opts, method: 'GET', body: null };
      continue;
    }
    return { ...res, finalUrl: currentUrl, cookies };
  }
  throw new Error(`Too many redirects fetching ${url}`);
}

function lineOfIndex(text, idx) {
  // 1-based line numbers
  let line = 1;
  for (let i = 0; i < idx && i < text.length; i++) {
    if (text[i] === '\n') line++;
  }
  return line;
}

function extractInlineScripts(html) {
  const scripts = [];
  const re = /<script(\s[^>]*)?>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const fullMatch = m[0];
    const content = m[2] || '';
    const startIdx = m.index;
    const contentStartIdx = startIdx + fullMatch.indexOf(content);
    const htmlStartLine = lineOfIndex(html, contentStartIdx);
    scripts.push({
      htmlStartLine,
      content,
    });
  }
  return scripts;
}

function checkScript(script, idx) {
  // Wrap in a function to allow top-level returns? We'll just parse as-is.
  try {
    // If the script contains "use strict" etc, new Function will still parse.
    // It will throw SyntaxError on invalid JS.
    // eslint-disable-next-line no-new-func
    new Function(script);
    return { ok: true };
  } catch (e) {
    const message = String(e && e.message ? e.message : e);

    // Try to extract the line number from stack.
    // Node stack often looks like: "SyntaxError: ...\n    at new Function (<anonymous>)\n    at checkScript ..."
    // Unfortunately it doesn't include line/col. We'll do a best effort by re-parsing
    // using vm.Script to get line/col.
    let line = null;
    let column = null;
    let stack = null;
    let excerpt = null;
    try {
      const vm = require('vm');
      new vm.Script(script, { filename: `inline-script-${idx}.js` });
    } catch (e2) {
      stack = String(e2 && e2.stack ? e2.stack : '');

      // Prefer the first reference to our synthetic filename.
      const re = new RegExp(`inline-script-${idx}\\.js:(\\d+):(\\d+)`, 'm');
      const m1 = stack.match(re);
      const m2 = m1 || stack.match(/:(\d+):(\d+)\)?\s*$/m);
      if (m2) {
        line = parseInt(m2[1], 10);
        column = parseInt(m2[2], 10);
        const scriptLines = script.split(/\r?\n/);
        const srcLine = scriptLines[line - 1] ?? '';
        const caretPos = Math.max(0, Math.min(srcLine.length, (column || 1) - 1));
        excerpt = srcLine + "\n" + " ".repeat(caretPos) + "^";
      }
    }

    return { ok: false, message, line, column, stack, excerpt };
  }
}

(async () => {
  const base = 'http://127.0.0.1:5000';

  // 1) Prime a session cookie
  const primed = await fetchFollow(`${base}/`, { method: 'GET' });
  let cookies = primed.cookies || [];

  // 2) Seed wordbank so /quiz doesn't redirect with ?error=no_words
  const seedPayload = JSON.stringify({ text: 'apple\nbanana\ncat\ndog', clear_first: true });
  const seeded = await fetchFollow(`${base}/api/wordbank/import-text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: seedPayload,
    cookies,
  });
  cookies = seeded.cookies || cookies;

  // 3) Fetch rendered quiz HTML
  const quizUrl = `${base}/quiz?resume=1`;
  const quizRes = await fetchFollow(quizUrl, { method: 'GET', cookies });

  if (quizRes.status !== 200) {
    console.error(`HTTP ${quizRes.status} for ${quizRes.finalUrl}`);
    process.exit(2);
  }

  const scripts = extractInlineScripts(quizRes.body);
  console.log(`Found ${scripts.length} inline <script> blocks`);

  let failures = 0;
  scripts.forEach((s, i) => {
    const r = checkScript(s.content, i + 1);
    if (!r.ok) {
      failures++;
      const htmlLine = r.line ? (s.htmlStartLine + r.line - 1) : s.htmlStartLine;
      console.log('---');
      console.log(`FAIL script #${i + 1}`);
      console.log(`HTML starts at line: ${s.htmlStartLine}`);
      if (r.line) {
        console.log(`JS error at script line ${r.line}${r.column ? ':' + r.column : ''} (≈ HTML line ${htmlLine})`);
      }
      console.log(`Message: ${r.message}`);
      if (r.excerpt) {
        console.log('Source excerpt:');
        console.log(r.excerpt);
      }
      if (r.stack) {
        console.log('Stack:');
        console.log(r.stack);
      }
    }
  });

  if (failures === 0) {
    console.log('✅ No JS syntax errors detected in inline scripts for /quiz');
  } else {
    console.log(`❌ ${failures} inline script(s) failed JS syntax validation`);
    process.exit(1);
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
