import assert from "node:assert/strict";
import test from "node:test";

import { validatePlan } from "../scripts/capture_demo.mjs";

const basePlan = {
  baseUrl: "http://127.0.0.1:3000",
  output: "artifacts/demo.webm",
  viewport: { width: 1440, height: 900 },
  recordingSize: { width: 1440, height: 900 },
  actions: [{ type: "hold", ms: 100 }],
};

test("valid capture plan is accepted", () => {
  assert.equal(validatePlan(structuredClone(basePlan)).actions.length, 1);
});

test("unknown action is rejected", () => {
  const plan = structuredClone(basePlan);
  plan.actions = [{ type: "inventFeature" }];
  assert.throws(() => validatePlan(plan), /unsupported type/);
});

test("empty action list is rejected", () => {
  const plan = structuredClone(basePlan);
  plan.actions = [];
  assert.throws(() => validatePlan(plan), /non-empty array/);
});
