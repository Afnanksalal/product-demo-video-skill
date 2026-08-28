#!/usr/bin/env node
import { access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

async function resolveEntry() {
  if (process.env.GENMOTION_MCP_ENTRY) return path.resolve(process.env.GENMOTION_MCP_ENTRY);
  try {
    const packageEntry = require.resolve('genmotion');
    return path.join(path.dirname(packageEntry), 'mcp.js');
  } catch {
    return path.join(skillRoot, 'node_modules', 'genmotion', 'dist', 'mcp.js');
  }
}

const entry = await resolveEntry();
try { await access(entry); }
catch { throw new Error('Genmotion MCP is unavailable. Install Genmotion 1.9.1 or newer, then run this launcher again.'); }

await import(pathToFileURL(entry).href);
