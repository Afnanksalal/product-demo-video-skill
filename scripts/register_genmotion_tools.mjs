#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const args = new Set(process.argv.slice(2));
const dryRun = args.has('--dry-run');
const replace = args.has('--replace');
const selected = args.has('--codex') || args.has('--claude');
const hosts = selected ? [...(args.has('--codex') ? ['codex'] : []), ...(args.has('--claude') ? ['claude'] : [])] : ['codex', 'claude'];
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const launcher = path.join(root, 'scripts', 'run_genmotion_mcp.mjs');

function run(command, commandArgs, tolerateFailure = false) {
  if (dryRun) { process.stdout.write(`${JSON.stringify([command, ...commandArgs])}\n`); return { status: 0 }; }
  const result = spawnSync(command, commandArgs, { stdio: tolerateFailure ? 'ignore' : 'inherit', windowsHide: true });
  if (!tolerateFailure && result.status !== 0) throw new Error(`${command} exited with ${String(result.status)}.`);
  return result;
}

for (const host of hosts) {
  const exists = run(host, ['mcp', 'get', 'genmotion'], true).status === 0;
  if (exists && !replace) {
    process.stdout.write(`Genmotion is already registered with ${host}. Use --replace to update it.\n`);
    continue;
  }
  if (exists) run(host, ['mcp', 'remove', 'genmotion']);
  const scope = host === 'claude' ? ['--scope', 'user'] : [];
  run(host, ['mcp', 'add', 'genmotion', ...scope, '--', process.execPath, launcher]);
  process.stdout.write(`Registered Genmotion tools with ${host}.\n`);
}
