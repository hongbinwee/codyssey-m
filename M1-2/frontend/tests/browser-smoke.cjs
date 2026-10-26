// Optional local browser check: run with Playwright available on NODE_PATH.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const schedules = [];
const conversations = [];
let failNextCreate = false;

function send(res, status, data) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(status === 204 ? "" : JSON.stringify(data));
}

const server = http.createServer(async (req, res) => {
  const pathname = new URL(req.url, "http://localhost").pathname;
  if (pathname === "/config.js") {
    res.writeHead(200, { "content-type": "text/javascript" });
    res.end(`window.APP_CONFIG = { API_BASE_URL: "http://${req.headers.host}" };`);
    return;
  }
  if (pathname === "/api/data/summary") {
    send(res, 200, {
      count: schedules.length,
      metrics: { total_hours: schedules.reduce((sum, row) => sum + row.value, 0) / 60 },
      busiest_weekday: null,
      top_category: null,
      weekday_distribution: {},
      recent_trend: { status: schedules.length ? "maintain" : "no_data", change_percent: 0 },
    });
    return;
  }
  if (pathname === "/api/data" && req.method === "GET") return send(res, 200, schedules);
  if (pathname === "/api/data" && req.method === "POST") {
    if (failNextCreate) {
      failNextCreate = false;
      return send(res, 503, { detail: "테스트 연결 실패" });
    }
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const row = { id: `schedule-${schedules.length + 1}`, ...JSON.parse(Buffer.concat(chunks).toString()) };
    schedules.push(row);
    return send(res, 201, row);
  }
  if (pathname.startsWith("/api/data/") && req.method === "DELETE") {
    const index = schedules.findIndex((row) => row.id === pathname.split("/").at(-1));
    if (index < 0) return send(res, 404, { detail: "not found" });
    schedules.splice(index, 1);
    return send(res, 204, null);
  }
  if (pathname === "/api/conversations" && req.method === "GET") return send(res, 200, conversations);
  if (pathname === "/api/chat" && req.method === "POST") {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = JSON.parse(Buffer.concat(chunks).toString());
    const conversation = conversations.find((row) => row.id === body.conversation_id) || {
      id: `conversation-${conversations.length + 1}`,
      title: body.message,
      messages: [],
    };
    if (!conversations.includes(conversation)) conversations.push(conversation);
    conversation.messages.push({ role: "user", content: body.message }, { role: "assistant", content: "테스트 답변: 일정 요약을 확인했습니다." });
    return send(res, 200, { conversation_id: conversation.id, answer: "테스트 답변: 일정 요약을 확인했습니다." });
  }
  if (pathname.startsWith("/api/conversations/") && req.method === "GET") {
    const row = conversations.find((item) => item.id === pathname.split("/").at(-1));
    return send(res, row ? 200 : 404, row || { detail: "not found" });
  }
  const file = pathname === "/" ? "index.html" : pathname.slice(1);
  if (!["index.html", "app.js", "styles.css"].includes(file)) return send(res, 404, { detail: "not found" });
  res.writeHead(200, { "content-type": file.endsWith(".css") ? "text/css" : file.endsWith(".js") ? "text/javascript" : "text/html" });
  fs.createReadStream(path.join(root, file)).pipe(res);
});

(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const browser = await chromium.launch({ channel: "chrome" });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("dialog", (dialog) => dialog.accept());
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await assert.equal(await page.locator("#trendBadge").textContent(), "데이터 없음");

    await page.locator("#date").fill("2026-09-26");
    await page.locator("#startTime").fill("09:00");
    await page.locator("#endTime").fill("10:00");
    await page.locator("#title").fill("브라우저 검증 일정");
    await page.locator("#scheduleForm button").click();
    await page.locator("#scheduleRows tr").waitFor();
    assert.match(await page.locator("#scheduleRows").textContent(), /브라우저 검증 일정/);
    assert.equal(await page.locator("#countMetric").textContent(), "1개");

    await page.locator("#chatInput").fill("최근 일정은 어때?");
    await page.locator("#chatForm button").click();
    await page.getByText("테스트 답변: 일정 요약을 확인했습니다.").waitFor();
    await page.reload();
    await page.locator("[data-conversation]").click();
    await page.locator("#messages .message.user").waitFor();
    assert.match(await page.locator("#messages").textContent(), /최근 일정은 어때\?/);
    assert.match(await page.locator("#messages").textContent(), /테스트 답변/);

    await page.locator("[data-delete]").click();
    await page.locator("#scheduleRows tr").waitFor({ state: "detached" });
    assert.equal(await page.locator("#countMetric").textContent(), "0개");

    failNextCreate = true;
    await page.locator("#date").fill("2026-09-26");
    await page.locator("#startTime").fill("09:00");
    await page.locator("#endTime").fill("10:00");
    await page.locator("#title").fill("실패 일정");
    await page.locator("#scheduleForm button").click();
    await page.getByText(/일정 저장 실패/).waitFor();
    assert.equal(await page.locator("#scheduleForm button").isDisabled(), false);

    await page.setViewportSize({ width: 390, height: 844 });
    const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    assert.equal(horizontalOverflow, false);
    assert.deepEqual(pageErrors, []);
    console.log("Browser smoke passed: CRUD refresh, chat history reload, error recovery, mobile width, no page errors");
  } finally {
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
})().catch((error) => {
  console.error(error);
  server.close();
  process.exitCode = 1;
});
