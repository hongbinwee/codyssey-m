import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import vm from "node:vm";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = fs.readFileSync(path.join(root, "app.js"), "utf8");

const emptySummary = {
  count: 0,
  metrics: { total_hours: 0 },
  busiest_weekday: null,
  top_category: null,
  weekday_distribution: {},
  recent_trend: { status: "no_data", change_percent: null },
};

function response(data, status = 200) {
  return { ok: status < 400, status, json: async () => data };
}

async function mount(fetchOverride = null) {
  const elements = new Map();
  const classes = () => {
    const names = new Set();
    return {
      add: (name) => names.add(name),
      remove: (name) => names.delete(name),
      contains: (name) => names.has(name),
      toggle: (name) => names.has(name) ? names.delete(name) : names.add(name),
    };
  };
  const element = (id) => {
    if (!elements.has(id)) {
      elements.set(id, {
        value: "",
        textContent: "",
        innerHTML: "",
        disabled: false,
        classList: classes(),
        handlers: {},
        addEventListener(name, callback) { this.handlers[name] = callback; },
        querySelector: () => null,
        reset() {},
        focus() {},
      });
    }
    return elements.get(id);
  };
  const submit = { disabled: false };
  element("scheduleForm").querySelector = () => submit;
  const deleteButton = { dataset: { delete: "row-1" }, disabled: false };
  const document = {
    body: { classList: classes() },
    getElementById: element,
    querySelectorAll: (selector) => selector === "[data-delete]" ? [deleteButton] : [],
    createElement: () => ({ textContent: "", innerHTML: "" }),
  };
  const fetch = async (url, options = {}) => {
    const path = new URL(url).pathname;
    if (fetchOverride) {
      const custom = await fetchOverride(path, options);
      if (custom) return custom;
    }
    if (path === "/api/data/summary") return response(emptySummary);
    if (path === "/api/data") return response([]);
    if (path === "/api/conversations") return response([]);
    return response({}, 404);
  };
  const context = vm.createContext({
    window: { APP_CONFIG: { API_BASE_URL: "http://localhost:8000" } },
    document,
    fetch,
    AbortController,
    URL,
    console,
    localStorage: { getItem: () => null, setItem() {} },
    confirm: () => true,
    setTimeout: (callback, ms) => ms >= 1000 ? 0 : setTimeout(callback, ms),
    clearTimeout,
  });
  vm.runInContext(source, context);
  await new Promise(setImmediate);
  return { context, element, submit, deleteButton };
}

test("empty summary is identified as no data", async () => {
  const { element } = await mount();
  assert.match(element("trendBadge").textContent, /데이터 없음/);
    assert.match(element("periodMetric").textContent, /없음/);
});

test("summary shows the analysis period from the API", async () => {
  const { element } = await mount((path) => path === "/api/data/summary" ? response({
    ...emptySummary, count: 3, period: { start: "2026-10-01", end: "2026-10-26" },
  }) : null);
  assert.match(element("periodMetric").textContent, /2026-10-01.*2026-10-26/);
});

test("failed conversation reload reports an error and preserves existing messages", async () => {
  const { context, element } = await mount((path) => path === "/api/conversations/missing"
    ? response({ detail: "대화를 찾을 수 없습니다." }, 404) : null);
  element("messages").innerHTML = "기존 메시지";
  await context.loadConversation("missing");
  assert.match(element("toast").textContent, /대화.*실패/);
  assert.equal(element("messages").innerHTML, "기존 메시지");
});

test("failed schedule save shows an error and restores the button", async () => {
  const { element, submit } = await mount((path, options) => {
    if (path === "/api/data" && options.method === "POST") throw new TypeError("Failed to fetch");
  });
  element("date").value = "2026-09-26";
  element("startTime").value = "09:00";
  element("endTime").value = "10:00";
  element("title").value = "테스트 일정";
  element("category").value = "study";

  await element("scheduleForm").handlers.submit({ preventDefault() {}, target: element("scheduleForm") });

  assert.match(element("toast").textContent, /실패|연결/);
  assert.equal(submit.disabled, false);
});

test("failed schedule deletion shows an error and restores the button", async () => {
  const { context, element, deleteButton } = await mount((path, options) => {
    if (path === "/api/data" && !options.method) {
      return response([{ id: "row-1", date: "2026-09-26", start_time: "09:00", end_time: "10:00", title: "일정", category: "study" }]);
    }
    if (path === "/api/data/row-1" && options.method === "DELETE") throw new TypeError("Failed to fetch");
  });
  await context.loadSchedules();

  await deleteButton.onclick();

  assert.match(element("toast").textContent, /실패|연결/);
  assert.equal(deleteButton.disabled, false);
});

test("a stalled request times out with a readable error", async () => {
  const { context } = await mount((path, options) => {
    if (path !== "/slow") return null;
    return new Promise((resolve, reject) => {
      options.signal?.addEventListener("abort", () => reject(Object.assign(new Error("aborted"), { name: "AbortError" })));
    });
  });

  const outcome = await Promise.race([
    vm.runInContext('request("/slow", { timeoutMs: 10 })', context).then(() => "resolved", (error) => error.message),
    new Promise((resolve) => setTimeout(() => resolve("still waiting"), 100)),
  ]);
  assert.match(outcome, /시간|초과/);
});
