import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

const root = path.resolve(import.meta.dirname, '..');

test('product demo skill drives a complete constructed-motion workflow through Genmotion tools', { timeout: 30_000 }, async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), 'product-demo-genmotion-'));
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [path.join(root, 'scripts', 'run_genmotion_mcp.mjs')],
    cwd: root,
    env: { ...process.env, GENMOTION_ALLOWED_ROOTS: temporary },
    stderr: 'pipe',
  });
  const client = new Client({ name: 'product-demo-skill-test', version: '1.0.0' });
  await client.connect(transport);
  try {
    const { tools } = await client.listTools();
    const names = tools.map((tool) => tool.name);
    assert.ok(names.includes('genmotion_render'));
    assert.ok(names.includes('genmotion_project_save'));
    assert.equal(names.some((name) => /capture|browser|caption|music|finish/.test(name)), false, 'Genmotion must stay scoped to constructed motion');

    const doctor = await client.callTool({ name: 'genmotion_doctor', arguments: {} });
    assert.equal(doctor.structuredContent.ok, true);
    const catalog = await client.callTool({ name: 'genmotion_catalog', arguments: { query: 'confident product reveal', limit: 4 } });
    assert.equal(catalog.structuredContent.results.length, 4);

    const projectDirectory = path.join(temporary, 'tool-film');
    const project = {
      schemaVersion: 1, id: 'tool-film', title: 'Tool Film', width: 320, height: 180, fps: 1, seed: 7,
      brand: { background: '#09090b', foreground: '#fafafa', accent: '#2563eb', muted: '#a1a1aa', fonts: [], radius: 16, tone: ['precise', 'confident'] },
      scenes: [{
        id: 'launch', purpose: 'Introduce the callable renderer.', duration: 1, background: '#09090b',
        transitionIn: { type: 'cut', duration: 0, ease: 'linear' }, transitionOut: { type: 'cut', duration: 0, ease: 'linear' }, referenceDecisions: [], notes: [],
        layers: [
          { id: 'field', type: 'shape', shape: 'round-rect', x: 18, y: 18, width: 284, height: 144, fill: '#18181b', stroke: '#2563eb', strokeWidth: 2, radius: 16, progress: 1, start: 0, duration: 1, z: 0, visible: true, blendMode: 'source-over', tags: ['surface'], motion: [] },
          { id: 'title', type: 'text', text: 'GENMOTION TOOLS', x: 38, y: 58, width: 244, height: 64, fontFamily: 'Arial', fontSize: 28, fontWeight: 800, fontStyle: 'normal', color: '#fafafa', align: 'center', verticalAlign: 'middle', lineHeight: 1, letterSpacing: 0.5, fit: 'shrink', reveal: 'none', revealProgress: 1, countProgress: 1, start: 0, duration: 1, z: 1, visible: true, blendMode: 'source-over', tags: ['headline'], motion: [] },
        ],
      }],
      audio: [], metadata: { source: 'product-demo-video-skill-e2e' },
    };
    await import('node:fs/promises').then(({ mkdir }) => mkdir(projectDirectory, { recursive: true }));
    await writeFile(path.join(projectDirectory, 'genmotion.json'), `${JSON.stringify(project, null, 2)}\n`);

    const read = await client.callTool({ name: 'genmotion_project_read', arguments: { project: projectDirectory } });
    assert.equal(read.structuredContent.summary.resolution, '320x180');
    const validation = await client.callTool({ name: 'genmotion_validate', arguments: { project: projectDirectory, strict: false } });
    assert.equal(validation.structuredContent.ok, true);

    const frameOutput = path.join(temporary, 'review.png');
    await client.callTool({ name: 'genmotion_frame', arguments: { project: projectDirectory, at: 0, output: frameOutput, resolution: { width: 1920, height: 1080 } } });
    assert.ok((await readFile(frameOutput)).length > 10_000);

    const videoOutput = path.join(temporary, 'master.mp4');
    const rendered = await client.callTool({ name: 'genmotion_render', arguments: { project: projectDirectory, output: videoOutput, quality: 'high', workers: 1, strict: false } });
    assert.equal(rendered.structuredContent.width, 1920);
    assert.equal(rendered.structuredContent.height, 1080);
    assert.equal(rendered.structuredContent.probe.videoCodec, 'h264');

    const probe = await client.callTool({ name: 'genmotion_probe', arguments: { video: videoOutput } });
    assert.equal(probe.structuredContent.width, 1920);
    assert.equal(probe.structuredContent.height, 1080);
    const sheetOutput = path.join(temporary, 'contact-sheet.png');
    await client.callTool({ name: 'genmotion_contact_sheet', arguments: { video: videoOutput, output: sheetOutput, count: 4, columns: 2 } });
    assert.ok((await readFile(sheetOutput)).length > 1_000);
  } finally {
    await client.close();
    await rm(temporary, { recursive: true, force: true });
  }
});
