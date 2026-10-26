import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function build(apiBaseUrl) {
  return spawnSync(process.execPath, ["scripts/generate-config.mjs"], {
    cwd: root,
    env: { ...process.env, API_BASE_URL: apiBaseUrl },
    encoding: "utf8",
  });
}

test("deployment build refuses an unset backend URL", () => {
  const result = build("");
  assert.notEqual(result.status, 0);
  assert.match(result.stderr + result.stdout, /API_BASE_URL/);
});

test("deployment build writes the configured backend URL", () => {
  const result = build("https://backend.example.test");
  assert.equal(result.status, 0, result.stderr);
});
