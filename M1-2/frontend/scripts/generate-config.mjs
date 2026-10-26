import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const out = path.join(root, "dist");
const api = process.env.API_BASE_URL?.trim();
if (!api) {
  console.error("API_BASE_URL을 설정한 뒤 빌드하세요.");
  process.exit(1);
}
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
for (const file of ["index.html", "styles.css", "app.js"]) fs.copyFileSync(path.join(root, file), path.join(out, file));
fs.writeFileSync(path.join(out, "config.js"), `window.APP_CONFIG = ${JSON.stringify({ API_BASE_URL: api })};\n`);
console.log(`Built vanilla frontend with API_BASE_URL=${api}`);
