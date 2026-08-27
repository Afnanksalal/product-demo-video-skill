#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

const SUPPORTED_ACTIONS = new Set([
  "goto",
  "reload",
  "click",
  "clickAndWaitForResponse",
  "fill",
  "type",
  "press",
  "select",
  "check",
  "uncheck",
  "upload",
  "waitForUrl",
  "waitForVisible",
  "assertVisible",
  "smoothScroll",
  "hold",
]);

function fail(message) {
  throw new Error(message);
}

function requireObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail(`${label} must be an object`);
  }
  return value;
}

function positiveNumber(value, fallback, label) {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) {
    fail(`${label} must be a positive number`);
  }
  return value;
}

function resolveValue(action, index) {
  const hasLiteral = Object.hasOwn(action, "value");
  const hasEnvironment = typeof action.valueFromEnv === "string";
  if (hasLiteral === hasEnvironment) {
    fail(`action ${index}: provide exactly one of value or valueFromEnv`);
  }
  if (hasEnvironment) {
    const value = process.env[action.valueFromEnv];
    if (value === undefined) {
      fail(`action ${index}: environment variable ${action.valueFromEnv} is not set`);
    }
    return value;
  }
  return String(action.value);
}

function locatorFor(page, descriptor, index) {
  if (typeof descriptor.selector === "string") {
    return page.locator(descriptor.selector);
  }
  if (typeof descriptor.role === "string") {
    return page.getByRole(descriptor.role, {
      name: descriptor.name,
      exact: descriptor.exact ?? true,
    });
  }
  if (typeof descriptor.label === "string") {
    return page.getByLabel(descriptor.label, { exact: descriptor.exact ?? true });
  }
  if (typeof descriptor.testId === "string") {
    return page.getByTestId(descriptor.testId);
  }
  if (typeof descriptor.text === "string") {
    return page.getByText(descriptor.text, { exact: descriptor.exact ?? true });
  }
  fail(`action ${index}: provide selector, role, label, testId, or text`);
}

function absoluteUrl(baseUrl, destination) {
  return new URL(destination, baseUrl).toString();
}

function safePageUrl(value) {
  try {
    const url = new URL(value);
    return `${url.origin}${url.pathname}`;
  } catch {
    return "unavailable";
  }
}

function actionSummary(action) {
  const summary = { type: action.type };
  for (const key of ["role", "name", "label", "testId", "text", "selector", "key", "url", "path"]) {
    if (typeof action[key] === "string") summary[key] = action[key];
  }
  if (action.type === "hold") summary.ms = action.ms;
  return summary;
}

async function smoothScroll(page, action) {
  const durationMs = positiveNumber(action.durationMs, 650, "smoothScroll.durationMs");
  let targetTop = action.top;
  if (typeof action.selector === "string") {
    targetTop = await page.locator(action.selector).evaluate((element) => {
      const rect = element.getBoundingClientRect();
      return Math.max(0, window.scrollY + rect.top - window.innerHeight * 0.18);
    });
  }
  if (typeof targetTop !== "number" || !Number.isFinite(targetTop)) {
    fail("smoothScroll requires a numeric top or a selector");
  }
  await page.evaluate(
    ({ top, duration }) =>
      new Promise((resolve) => {
        const start = window.scrollY;
        const delta = top - start;
        const startedAt = performance.now();
        const ease = (t) => 1 - Math.pow(1 - t, 3);
        const tick = (now) => {
          const progress = Math.min(1, (now - startedAt) / duration);
          window.scrollTo(0, start + delta * ease(progress));
          if (progress < 1) requestAnimationFrame(tick);
          else resolve();
        };
        requestAnimationFrame(tick);
      }),
    { top: targetTop, duration: durationMs },
  );
}

export function validatePlan(plan) {
  requireObject(plan, "capture plan");
  if (typeof plan.baseUrl !== "string") fail("baseUrl must be a string");
  if (typeof plan.output !== "string") fail("output must be a string");
  if (!plan.output.toLowerCase().endsWith(".webm")) fail("output must use the .webm extension");
  requireObject(plan.viewport, "viewport");
  requireObject(plan.recordingSize, "recordingSize");
  positiveNumber(plan.viewport.width, null, "viewport.width");
  positiveNumber(plan.viewport.height, null, "viewport.height");
  positiveNumber(plan.recordingSize.width, null, "recordingSize.width");
  positiveNumber(plan.recordingSize.height, null, "recordingSize.height");
  if (!Array.isArray(plan.actions) || plan.actions.length === 0) {
    fail("actions must be a non-empty array");
  }
  if (plan.timelineOutput !== undefined && typeof plan.timelineOutput !== "string") {
    fail("timelineOutput must be a string when provided");
  }
  plan.actions.forEach((action, index) => {
    requireObject(action, `action ${index}`);
    if (!SUPPORTED_ACTIONS.has(action.type)) {
      fail(`action ${index}: unsupported type ${String(action.type)}`);
    }
  });
  return plan;
}

async function performAction(page, action, index, baseUrl, planDirectory) {
  switch (action.type) {
    case "goto":
      await page.goto(absoluteUrl(baseUrl, action.url ?? action.path), {
        waitUntil: action.waitUntil ?? "domcontentloaded",
      });
      break;
    case "reload":
      await page.reload({ waitUntil: action.waitUntil ?? "domcontentloaded" });
      break;
    case "click":
      await locatorFor(page, action, index).click();
      break;
    case "clickAndWaitForResponse": {
      if (typeof action.responseUrl !== "string") {
        fail(`action ${index}: responseUrl is required`);
      }
      const expectedStatus = action.status;
      const responsePromise = page.waitForResponse((response) => {
        const urlMatches = response.url().includes(action.responseUrl);
        return urlMatches && (expectedStatus === undefined || response.status() === expectedStatus);
      });
      await locatorFor(page, action, index).click();
      await responsePromise;
      break;
    }
    case "fill":
      await locatorFor(page, action, index).fill(resolveValue(action, index));
      break;
    case "type":
      await locatorFor(page, action, index).pressSequentially(resolveValue(action, index), {
        delay: positiveNumber(action.delayMs, 45, `action ${index}.delayMs`),
      });
      break;
    case "press":
      if (typeof action.key !== "string") fail(`action ${index}: key is required`);
      await locatorFor(page, action, index).press(action.key);
      break;
    case "select":
      await locatorFor(page, action, index).selectOption(action.option);
      break;
    case "check":
      await locatorFor(page, action, index).check();
      break;
    case "uncheck":
      await locatorFor(page, action, index).uncheck();
      break;
    case "upload":
      if (!action.files) fail(`action ${index}: files is required`);
      await locatorFor(page, action, index).setInputFiles(
        (Array.isArray(action.files) ? action.files : [action.files]).map((file) =>
          path.resolve(planDirectory, file),
        ),
      );
      break;
    case "waitForUrl":
      if (typeof action.url !== "string") fail(`action ${index}: url is required`);
      await page.waitForURL(action.url);
      break;
    case "waitForVisible":
    case "assertVisible":
      await locatorFor(page, action, index).waitFor({ state: "visible" });
      break;
    case "smoothScroll":
      await smoothScroll(page, action);
      break;
    case "hold":
      await page.waitForTimeout(positiveNumber(action.ms, null, `action ${index}.ms`));
      break;
    default:
      fail(`action ${index}: unsupported type ${action.type}`);
  }
}

export async function capture(planPath) {
  const absolutePlanPath = path.resolve(planPath);
  const planDirectory = path.dirname(absolutePlanPath);
  const plan = validatePlan(JSON.parse(await fs.readFile(absolutePlanPath, "utf8")));
  const outputPath = path.resolve(planDirectory, plan.output);
  const outputDirectory = path.dirname(outputPath);
  const temporaryDirectory = path.join(outputDirectory, `.playwright-${Date.now()}`);

  await fs.mkdir(outputDirectory, { recursive: true });
  if (!plan.overwrite) {
    try {
      await fs.access(outputPath);
      fail(`output already exists: ${outputPath}; set overwrite to true to replace it`);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  await fs.mkdir(temporaryDirectory, { recursive: true });

  const browser = await chromium.launch({ headless: plan.headless ?? true });
  let context;
  let page;
  let video;
  let failed = false;
  let finalPath = outputPath;
  let timelineStartedAt = 0;
  const timeline = [];

  try {
    context = await browser.newContext({
      viewport: plan.viewport,
      screen: plan.viewport,
      deviceScaleFactor: plan.deviceScaleFactor ?? 1,
      reducedMotion: "no-preference",
      serviceWorkers: plan.serviceWorkers ?? "allow",
      storageState: plan.storageState
        ? path.resolve(planDirectory, plan.storageState)
        : undefined,
      recordVideo: {
        dir: temporaryDirectory,
        size: plan.recordingSize,
      },
    });
    context.setDefaultTimeout(positiveNumber(plan.defaultTimeoutMs, 15000, "defaultTimeoutMs"));
    page = await context.newPage();
    video = page.video();

    page.on("pageerror", (error) => {
      console.error(`[page error] ${error.message}`);
    });

    timelineStartedAt = performance.now();
    await page.goto(absoluteUrl(plan.baseUrl, plan.startPath ?? "/"), {
      waitUntil: plan.initialWaitUntil ?? "domcontentloaded",
    });

    const actionDelay = positiveNumber(plan.actionDelayMs, 450, "actionDelayMs");
    for (let index = 0; index < plan.actions.length; index += 1) {
      const action = plan.actions[index];
      console.log(`[${index + 1}/${plan.actions.length}] ${action.type} at ${page.url()}`);
      const startedAtMs = performance.now() - timelineStartedAt;
      try {
        await performAction(page, action, index, plan.baseUrl, planDirectory);
      } catch (error) {
        timeline.push({
          index: index + 1,
          ...actionSummary(action),
          startedAtMs: Math.round(startedAtMs),
          endedAtMs: Math.round(performance.now() - timelineStartedAt),
          status: "failed",
          page: safePageUrl(page.url()),
          error: error.message,
        });
        throw new Error(`action ${index + 1} (${action.type}) failed at ${page.url()}: ${error.message}`);
      }
      if (!new Set(["hold", "waitForUrl", "waitForVisible", "assertVisible"]).has(action.type)) {
        await page.waitForTimeout(action.afterMs ?? actionDelay);
      }
      timeline.push({
        index: index + 1,
        ...actionSummary(action),
        startedAtMs: Math.round(startedAtMs),
        endedAtMs: Math.round(performance.now() - timelineStartedAt),
        status: "passed",
        page: safePageUrl(page.url()),
      });
    }
  } catch (error) {
    failed = true;
    console.error(error.stack ?? error.message);
  } finally {
    if (context) await context.close();
    finalPath = failed
      ? outputPath.replace(/(\.[^.]+)?$/, ".failed$1")
      : outputPath;
    if (video) await video.saveAs(finalPath);
    await browser.close();
  }

  if (!video) fail("Playwright did not create a video stream");
  await fs.rm(temporaryDirectory, { recursive: true, force: true });
  if (plan.timelineOutput) {
    const timelinePath = path.resolve(planDirectory, plan.timelineOutput);
    await fs.mkdir(path.dirname(timelinePath), { recursive: true });
    await fs.writeFile(
      timelinePath,
      `${JSON.stringify({ video: finalPath, failed, durationMs: Math.round(performance.now() - timelineStartedAt), actions: timeline }, null, 2)}\n`,
      "utf8",
    );
    console.log(`Capture timeline: ${timelinePath}`);
  }
  console.log(`${failed ? "Failed take preserved" : "Capture saved"}: ${finalPath}`);
  if (failed) process.exitCode = 1;
  return finalPath;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  const planPath = process.argv[2];
  if (!planPath) {
    console.error("Usage: node scripts/capture_demo.mjs <capture-plan.json>");
    process.exit(2);
  }
  await capture(planPath);
}
