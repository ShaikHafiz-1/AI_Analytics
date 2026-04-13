/**
 * Prompt Generation Utilities
 * Extracted from CopilotPanel.tsx for reusability
 */

import { DashboardContext } from '../types/dashboard';

export interface PromptCandidate {
  prompt: string;
  category: 'status' | 'risk' | 'change' | 'supplier' | 'entity';
  priority: number;
}

/**
 * Build smart prompts based on dashboard context
 */
export function buildSmartPrompts(
  ctx: DashboardContext,
  entity?: { type: string; item: string } | null
): string[] {
  const candidates: PromptCandidate[] = [];

  // Status prompts
  if (ctx.planningHealth !== undefined) {
    candidates.push({
      prompt: `What's the current planning health status?`,
      category: 'status',
      priority: 10,
    });
  }

  // Risk prompts
  if (ctx.riskSummary && ctx.riskSummary.highRiskCount > 0) {
    candidates.push({
      prompt: `Why are these records risky?`,
      category: 'risk',
      priority: 9,
    });
    candidates.push({
      prompt: `What are the top risk drivers?`,
      category: 'risk',
      priority: 8,
    });
  }

  // Change prompts
  if (ctx.changedRecordCount && ctx.changedRecordCount > 0) {
    candidates.push({
      prompt: `What changed most?`,
      category: 'change',
      priority: 9,
    });
    candidates.push({
      prompt: `Which locations have the most changes?`,
      category: 'change',
      priority: 8,
    });
  }

  // Supplier prompts
  if (ctx.supplierSummary && ctx.supplierSummary.changed > 0) {
    candidates.push({
      prompt: `Which suppliers have changes?`,
      category: 'supplier',
      priority: 7,
    });
  }

  // Entity-specific prompts
  if (entity) {
    const entityPrompts = buildEntityPrompts(ctx, entity);
    candidates.push(
      ...entityPrompts.map((p) => ({
        prompt: p,
        category: 'entity' as const,
        priority: 6,
      }))
    );
  }

  // Select diverse prompts
  return selectDiversePrompts(candidates, 4);
}

/**
 * Build entity-specific prompts
 */
export function buildEntityPrompts(
  ctx: DashboardContext,
  entity: { type: string; item: string }
): string[] {
  const prompts: string[] = [];

  if (entity.type === 'location') {
    prompts.push(`Why is ${entity.item} risky?`);
    prompts.push(`What changed at ${entity.item}?`);
    prompts.push(`Which suppliers serve ${entity.item}?`);
  } else if (entity.type === 'supplier') {
    prompts.push(`What changes did ${entity.item} introduce?`);
    prompts.push(`Which locations use ${entity.item}?`);
    prompts.push(`Is ${entity.item} reliable?`);
  } else if (entity.type === 'material') {
    prompts.push(`Why is ${entity.item} risky?`);
    prompts.push(`Where is ${entity.item} used?`);
    prompts.push(`What changed for ${entity.item}?`);
  }

  return prompts;
}

/**
 * Select diverse prompts from candidates
 */
export function selectDiversePrompts(
  candidates: PromptCandidate[],
  maxCount: number
): string[] {
  // Sort by priority
  const sorted = [...candidates].sort((a, b) => b.priority - a.priority);

  // Select one from each category if possible
  const selected: PromptCandidate[] = [];
  const categories = new Set<string>();

  for (const candidate of sorted) {
    if (selected.length >= maxCount) break;
    if (!categories.has(candidate.category)) {
      selected.push(candidate);
      categories.add(candidate.category);
    }
  }

  // Fill remaining slots with highest priority
  for (const candidate of sorted) {
    if (selected.length >= maxCount) break;
    if (!selected.includes(candidate)) {
      selected.push(candidate);
    }
  }

  return selected.map((c) => c.prompt);
}

/**
 * Build follow-up questions
 */
export function buildFollowUps(
  question: string,
  ctx: DashboardContext,
  entity?: { type: string; item: string } | null
): string[] {
  const followUps: string[] = [];
  const q = question.toLowerCase();

  // If asked about status, follow up with risk
  if (q.includes('status') || q.includes('health')) {
    if (ctx.riskSummary && ctx.riskSummary.highRiskCount > 0) {
      followUps.push('What are the top risks?');
    }
  }

  // If asked about risk, follow up with drivers
  if (q.includes('risk') || q.includes('risky')) {
    followUps.push('What are the root causes?');
    if (entity) {
      followUps.push(`How can we mitigate ${entity.item}?`);
    }
  }

  // If asked about changes, follow up with impact
  if (q.includes('change') || q.includes('changed')) {
    followUps.push('What is the impact?');
    followUps.push('Which locations are affected?');
  }

  // If asked about suppliers, follow up with details
  if (q.includes('supplier')) {
    followUps.push('Which materials are affected?');
    followUps.push('What is the timeline?');
  }

  return followUps.slice(0, 3);
}
