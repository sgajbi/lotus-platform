export type LotusPanelState =
  | "loading"
  | "ready"
  | "empty"
  | "partial"
  | "stale"
  | "degraded"
  | "error"
  | "permission_blocked"
  | "unsupported";

export type LotusAttentionType =
  | "panel_stale"
  | "panel_degraded"
  | "panel_repeated_failure"
  | "source_partial"
  | "permission_blocked";

export const LOTUS_ALLOWED_OBSERVABILITY_LABELS = [
  "route",
  "panel",
  "service",
  "operation",
  "state",
  "reason",
  "freshness_bucket",
  "supportability_state",
  "attention_type",
  "severity",
  "status_class",
  "error_category",
  "region",
  "environment",
] as const;

export const LOTUS_FORBIDDEN_OBSERVABILITY_FIELDS = [
  "portfolio_id",
  "client_id",
  "client_name",
  "household_id",
  "account_id",
  "instrument_id",
  "holding_id",
  "transaction_id",
  "trace_id",
  "correlation_id",
  "document_id",
  "advisor_id",
  "advisor_behavior",
  "screen_content",
  "request_body",
  "response_body",
  "raw_entitlement_failure",
] as const;

export interface LotusWorkbenchSurfaceObservability {
  route: string;
  panel: string;
  service: string;
  operation: string;
  state: LotusPanelState;
  reason?: string;
  freshness_bucket?: string;
  supportability_state?: string;
  status_class?: string;
  error_category?: string;
}

export interface LotusWorkbenchAttentionEvent extends LotusWorkbenchSurfaceObservability {
  attention_type: LotusAttentionType;
  severity: "info" | "warning" | "action_required" | "critical";
}

export function assertNoSensitiveObservabilityKeys(
  fields: Record<string, unknown>,
): void {
  for (const forbidden of LOTUS_FORBIDDEN_OBSERVABILITY_FIELDS) {
    if (Object.prototype.hasOwnProperty.call(fields, forbidden)) {
      throw new Error(`Forbidden observability field: ${forbidden}`);
    }
  }
}

export function emitPanelStateMetric(
  fields: LotusWorkbenchSurfaceObservability,
  emit: (eventName: string, fields: LotusWorkbenchSurfaceObservability) => void,
): void {
  assertNoSensitiveObservabilityKeys(fields as Record<string, unknown>);
  emit("workbench.analytics.panel_state", fields);
}

export function emitAttentionEvent(
  fields: LotusWorkbenchAttentionEvent,
  emit: (eventName: string, fields: LotusWorkbenchAttentionEvent) => void,
): void {
  assertNoSensitiveObservabilityKeys(fields as Record<string, unknown>);
  emit("workbench.analytics.attention", fields);
}
