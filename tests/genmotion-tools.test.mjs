import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
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
    assert.ok(names.includes('genmotion_schema'));
    assert.ok(names.includes('genmotion_project_patch'));
    assert.ok(names.includes('genmotion_timeline_inspect'));
    assert.equal(names.some((name) => /capture|browser|caption|music|finish/.test(name)), false, 'Genmotion must stay scoped to constructed motion');

    const doctor = await client.callTool({ name: 'genmotion_doctor', arguments: {} });
    assert.equal(doctor.structuredContent.ok, true);
    const schema = await client.callTool({ name: 'genmotion_schema', arguments: {} });
    assert.match(schema.structuredContent.authoring.recipePolicy, /optional/);

    const projectDirectory = path.join(temporary, 'tool-film');
    await client.callTool({ name: 'genmotion_init', arguments: { directory: projectDirectory, title: 'Tool Film', promise: 'Show agent-authored native motion', proof: 'The rendered pixels are returned to the agent', action: 'Review the composition', audience: 'product teams', mode: 'launch', duration: 1 } });
    const project = {
      schemaVersion: 1, id: 'tool-film', title: 'Tool Film', width: 320, height: 180, fps: 1, seed: 7,
      brand: { background: '#09090b', foreground: '#fafafa', accent: '#2563eb', muted: '#a1a1aa', fonts: [], radius: 16, tone: ['precise', 'confident'] },
      scenes: [{
        id: 'launch', purpose: 'Introduce the callable renderer.', duration: 1, background: '#09090b',
        transitionIn: { type: 'cut', duration: 0, ease: 'linear' }, transitionOut: { type: 'cut', duration: 0, ease: 'linear' }, referenceDecisions: [], notes: [],
        layers: [
          { id: 'field', type: 'shape', shape: 'path', path: 'M0 0 L100 0 L100 60 L0 60 Z', x: 18, y: 18, width: 284, height: 144, fill: '#18181b', stroke: '#2563eb', strokeWidth: 2, radius: 16, progress: 1, start: 0, duration: 1, z: 0, visible: true, blendMode: 'source-over', tags: ['surface'], motion: [], tracks: [{ id: 'field-arrival', target: 'transform.scaleX', operation: 'replace', extrapolate: 'clamp', enabled: true, keyframes: [{ at: 0, value: 0.85, ease: 'linear' }, { at: 0.7, value: 1, ease: { type: 'spring', mass: 1, stiffness: 170, damping: 26, velocity: 0 } }] }] },
          { id: 'title', type: 'text', text: 'GENMOTION TOOLS', x: 38, y: 58, width: 244, height: 64, fontFamily: 'Arial', fontSize: 28, fontWeight: 800, fontStyle: 'normal', color: '#fafafa', align: 'center', verticalAlign: 'middle', lineHeight: 1, letterSpacing: 0.5, fit: 'shrink', reveal: 'none', revealProgress: 1, countProgress: 1, start: 0, duration: 1, z: 1, visible: true, blendMode: 'source-over', tags: ['headline'], motion: [], tracks: [{ id: 'title-rise', target: 'transform.y', operation: 'replace', extrapolate: 'clamp', enabled: true, keyframes: [{ at: 0, value: 18, ease: 'linear' }, { at: 0.6, value: 0, ease: { type: 'cubic-bezier', x1: 0.2, y1: 0.8, x2: 0.2, y2: 1 } }] }] },
        ],
      }],
      audio: [], metadata: { source: 'product-demo-video-skill-e2e' },
    };
    const read = await client.callTool({ name: 'genmotion_project_read', arguments: { project: projectDirectory } });
    const patched = await client.callTool({ name: 'genmotion_project_patch', arguments: { project: projectDirectory, expectedRevision: read.structuredContent.revision, operations: [{ op: 'replace', path: '/width', value: project.width }, { op: 'replace', path: '/height', value: project.height }, { op: 'replace', path: '/fps', value: project.fps }, { op: 'replace', path: '/scenes', value: project.scenes }, { op: 'replace', path: '/metadata', value: project.metadata }], strict: false } });
    assert.equal(patched.structuredContent.operationsApplied, 5);
    const validation = await client.callTool({ name: 'genmotion_validate', arguments: { project: projectDirectory, strict: false } });
    assert.equal(validation.structuredContent.ok, true);

    const frameOutput = path.join(temporary, 'review.png');
    const frame = await client.callTool({ name: 'genmotion_frame', arguments: { project: projectDirectory, at: 0.5, output: frameOutput, resolution: { width: 1920, height: 1080 } } });
    assert.ok((await readFile(frameOutput)).length > 10_000);
    assert.ok(frame.content.some((item) => item.type === 'image' && item.mimeType === 'image/png'));
    const timeline = await client.callTool({ name: 'genmotion_timeline_inspect', arguments: { project: projectDirectory, at: 0.5 } });
    assert.equal(timeline.structuredContent.scene.id, 'launch');

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
