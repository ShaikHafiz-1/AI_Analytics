/**
 * Answer Generation Utilities
 * Extracted from CopilotPanel.tsx for reusability
 */

import { DashboardContext } from '../types/dashboard';

/**
 * Build greeting message
 */
export function buildGreeting(
  ctx: DashboardContext,
  entity?: { type: string; item: string } | null
): string {
  const health = ctx.planningHealth || 0;
  const status = health > 70 ? 'healthy' : health > 40 ? 'moderate' : 'concerning';

  let greeting = `Planning health is ${status} (${health}%).`;

  if (entity) {
    greeting += ` Analyzing ${entity.type}: ${entity.item}.`;
  }

  if (ctx.changedRecordCount && ctx.changedRecordCount > 0) {
    greeting += ` ${ctx.changedRecordCount} records have changed.`;
  }

  return greeting;
}

/**
 * Build fallback answer when API fails
 */
export function buildFallbackAnswer(
  question: string,
  ctx: DashboardContext,
  entity?: { type: string; item: string } | null
): string {
  const q = question.toLowerCase();

  // Status questions
  if (q.includes('status') || q.includes('health')) {
    const health = ctx.planningHealth || 0;
    const status = health > 70 ? 'healthy' : health > 40 ? 'moderate' : 'concerning';
    return `Planning health is currently ${status} at ${health}%. ${ctx.changedRecordCount || 0} records have changed.`;
  }

  // Risk questions
  if (q.includes('risk') || q.includes('risky')) {
    if (entity) {
      const records = ctx.detailRecords?.filter(
        (r: any) =>
          (entity.type === 'location' && r.locationId === entity.item) ||
          (entity.type === 'supplier' && r.supplier === entity.item) ||
          (entity.type === 'material' && r.materialId === entity.item)
      ) || [];

      const riskyCount = records.filter((r: any) => r.riskLevel === 'High').length;
      return `${entity.item} has ${riskyCount} high-risk records out of ${records.length} total.`;
    }
    return `There are ${ctx.riskSummary?.highRiskCount || 0} high-risk records in the dataset.`;
  }

  // Change questions
  if (q.includes('change') || q.includes('changed')) {
    const changeRate = ctx.changedRecordCount
      ? Math.round((ctx.changedRecordCount / (ctx.totalRecords || 1)) * 100)
      : 0;
    return `${ctx.changedRecordCount || 0} records have changed (${changeRate}% change rate).`;
  }

  // Supplier questions
  if (q.includes('supplier')) {
    return `${ctx.supplierSummary?.changed || 0} supplier changes detected.`;
  }

  // Default fallback
  return `Planning Intelligence: ${ctx.changedRecordCount || 0} changes, ${ctx.planningHealth || 0}% health.`;
}

/**
 * Filter detail records by entity
 */
export function filterDetailsByEntity(
  details: any[],
  entity: { type: string; item: string }
): any[] {
  if (!details) return [];

  return details.filter((record) => {
    if (entity.type === 'location') {
      return record.locationId === entity.item;
    } else if (entity.type === 'supplier') {
      return record.supplier === entity.item;
    } else if (entity.type === 'material') {
      return record.materialId === entity.item;
    }
    return false;
  });
}

/**
 * Format context label for display
 */
export function contextLabel(entity?: { type: string; item: string } | null): string {
  if (!entity) return 'Global';
  return `${entity.type.charAt(0).toUpperCase() + entity.type.slice(1)}: ${entity.item}`;
}
