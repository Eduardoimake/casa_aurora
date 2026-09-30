import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = new URL("../src/", import.meta.url);
const scriptsRoot = new URL("./", import.meta.url);

async function collectJavaScript(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const path = new URL(
      `${encodeURIComponent(entry.name)}${entry.isDirectory() ? "/" : ""}`,
      directory
    );

    if (entry.isDirectory()) {
      files.push(...await collectJavaScript(path));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith(".js")) {
      files.push(path);
    }
  }

  return files;
}

function checkFile(file) {
  return new Promise((resolve) => {
    const child = spawn(
      process.execPath,
      ["--check", fileURLToPath(file)],
      { stdio: ["ignore", "pipe", "pipe"] }
    );

    let stderr = "";

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("close", (code) => {
      resolve({
        code,
        file: relative(process.cwd(), fileURLToPath(file)),
        stderr
      });
    });
  });
}

const files = await collectJavaScript(root);
const results = [];

for (const file of files) {
  results.push(await checkFile(file));
}

let failed = false;

for (const result of results) {
  if (result.code === 0) {
    process.stdout.write(`OK ${result.file}\n`);
  } else {
    failed = true;
    process.stderr.write(`FALHOU ${result.file}\n`);
    process.stderr.write(result.stderr);
  }
}

if (failed) {
  process.exitCode = 1;
} else {
  process.stdout.write(
    `Sintaxe verificada em ${results.length} arquivo(s).\n`
  );
}