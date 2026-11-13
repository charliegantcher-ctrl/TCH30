// Folds dist/assets/*.js and *.css into dist/index.html so the whole site is one file
// that can be uploaded to GitHub in place of the old index.html.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
let html = readFileSync(join(dist, "index.html"), "utf8");

html = html.replace(/<script type="module" crossorigin src="\.\/(assets\/[^"]+\.js)"><\/script>/g, (_, p) => {
  const js = readFileSync(join(dist, p), "utf8").replace(/<\/script/gi, "<\\/script");
  return `<script type="module">${js}</script>`;
});
html = html.replace(/<link rel="stylesheet" crossorigin href="\.\/(assets\/[^"]+\.css)">/g, (_, p) => {
  return `<style>${readFileSync(join(dist, p), "utf8")}</style>`;
});
if (/src="\.\/assets|href="\.\/assets/.test(html)) throw new Error("an asset was not inlined");

writeFileSync(join(dist, "index.html"), html);
const out = join(root, "..", "upload-to-github");
mkdirSync(out, { recursive: true });
copyFileSync(join(dist, "index.html"), join(out, "index.html"));
console.log(`single-file index.html: ${(html.length / 1024).toFixed(0)} KB -> ${out}`);
