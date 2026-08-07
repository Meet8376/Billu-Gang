import { z } from 'zod';

export const IntakeProgressSchema = z.object({
  type: z.literal('intake_progress'),
  step: z.string(),
  completed: z.boolean(),
  detail: z.string().optional()
});

export const PlanUpdatedSchema = z.object({
  type: z.literal('plan_updated'),
  taskTitle: z.string(),
  nodes: z.array(
    z.object({
      id: z.string(),
      label: z.string(),
      status: z.enum(['done', 'running', 'pending', 'failed']),
      parentId: z.string().optional(),
      detail: z.string().optional()
    })
  )
});

export const ToolStartedSchema = z.object({
  type: z.literal('tool_started'),
  toolName: z.string(),
  args: z.record(z.any()),
  timestamp: z.string()
});

export const ToolFinishedSchema = z.object({
  type: z.literal('tool_finished'),
  toolName: z.string(),
  output: z.string(),
  durationSeconds: z.number()
});

export const VerificationEventSchema = z.object({
  type: z.literal('verification_event'),
  suiteName: z.string(),
  status: z.enum(['passed', 'failed', 'running', 'pending']),
  durationSeconds: z.number().optional(),
  errorReason: z.string().optional()
});

export const SessionStatusUpdateSchema = z.object({
  type: z.literal('status_update'),
  tokensUsed: z.number(),
  costSoFar: z.number(),
  testsPassing: z.string(),
  sandboxState: z.enum(['active', 'sandboxed', 'idle', 'paused']),
  elapsedSeconds: z.number()
});

export const SSEEventSchema = z.discriminatedUnion('type', [
  IntakeProgressSchema,
  PlanUpdatedSchema,
  ToolStartedSchema,
  ToolFinishedSchema,
  VerificationEventSchema,
  SessionStatusUpdateSchema
]);

export type IntakeProgressEvent = z.infer<typeof IntakeProgressSchema>;
export type PlanUpdatedEvent = z.infer<typeof PlanUpdatedSchema>;
export type ToolStartedEvent = z.infer<typeof ToolStartedSchema>;
export type ToolFinishedEvent = z.infer<typeof ToolFinishedSchema>;
export type VerificationEvent = z.infer<typeof VerificationEventSchema>;
export type SessionStatusUpdateEvent = z.infer<typeof SessionStatusUpdateSchema>;
export type SSEEvent = z.infer<typeof SSEEventSchema>;
