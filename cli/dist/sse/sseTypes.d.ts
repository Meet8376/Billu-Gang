import { z } from 'zod';
export declare const IntakeProgressSchema: z.ZodObject<{
    type: z.ZodLiteral<"intake_progress">;
    step: z.ZodString;
    completed: z.ZodBoolean;
    detail: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "intake_progress";
    step: string;
    completed: boolean;
    detail?: string | undefined;
}, {
    type: "intake_progress";
    step: string;
    completed: boolean;
    detail?: string | undefined;
}>;
export declare const PlanUpdatedSchema: z.ZodObject<{
    type: z.ZodLiteral<"plan_updated">;
    taskTitle: z.ZodString;
    nodes: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        label: z.ZodString;
        status: z.ZodEnum<["done", "running", "pending", "failed"]>;
        parentId: z.ZodOptional<z.ZodString>;
        detail: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }, {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    type: "plan_updated";
    taskTitle: string;
    nodes: {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }[];
}, {
    type: "plan_updated";
    taskTitle: string;
    nodes: {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }[];
}>;
export declare const ToolStartedSchema: z.ZodObject<{
    type: z.ZodLiteral<"tool_started">;
    toolName: z.ZodString;
    args: z.ZodRecord<z.ZodString, z.ZodAny>;
    timestamp: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "tool_started";
    toolName: string;
    args: Record<string, any>;
    timestamp: string;
}, {
    type: "tool_started";
    toolName: string;
    args: Record<string, any>;
    timestamp: string;
}>;
export declare const ToolFinishedSchema: z.ZodObject<{
    type: z.ZodLiteral<"tool_finished">;
    toolName: z.ZodString;
    output: z.ZodString;
    durationSeconds: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    type: "tool_finished";
    toolName: string;
    output: string;
    durationSeconds: number;
}, {
    type: "tool_finished";
    toolName: string;
    output: string;
    durationSeconds: number;
}>;
export declare const VerificationEventSchema: z.ZodObject<{
    type: z.ZodLiteral<"verification_event">;
    suiteName: z.ZodString;
    status: z.ZodEnum<["passed", "failed", "running", "pending"]>;
    durationSeconds: z.ZodOptional<z.ZodNumber>;
    errorReason: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "verification_event";
    suiteName: string;
    status: "running" | "pending" | "failed" | "passed";
    durationSeconds?: number | undefined;
    errorReason?: string | undefined;
}, {
    type: "verification_event";
    suiteName: string;
    status: "running" | "pending" | "failed" | "passed";
    durationSeconds?: number | undefined;
    errorReason?: string | undefined;
}>;
export declare const SessionStatusUpdateSchema: z.ZodObject<{
    type: z.ZodLiteral<"status_update">;
    tokensUsed: z.ZodNumber;
    costSoFar: z.ZodNumber;
    testsPassing: z.ZodString;
    sandboxState: z.ZodEnum<["active", "sandboxed", "idle", "paused"]>;
    elapsedSeconds: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    type: "status_update";
    tokensUsed: number;
    costSoFar: number;
    testsPassing: string;
    sandboxState: "active" | "sandboxed" | "idle" | "paused";
    elapsedSeconds: number;
}, {
    type: "status_update";
    tokensUsed: number;
    costSoFar: number;
    testsPassing: string;
    sandboxState: "active" | "sandboxed" | "idle" | "paused";
    elapsedSeconds: number;
}>;
export declare const SSEEventSchema: z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
    type: z.ZodLiteral<"intake_progress">;
    step: z.ZodString;
    completed: z.ZodBoolean;
    detail: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "intake_progress";
    step: string;
    completed: boolean;
    detail?: string | undefined;
}, {
    type: "intake_progress";
    step: string;
    completed: boolean;
    detail?: string | undefined;
}>, z.ZodObject<{
    type: z.ZodLiteral<"plan_updated">;
    taskTitle: z.ZodString;
    nodes: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        label: z.ZodString;
        status: z.ZodEnum<["done", "running", "pending", "failed"]>;
        parentId: z.ZodOptional<z.ZodString>;
        detail: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }, {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    type: "plan_updated";
    taskTitle: string;
    nodes: {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }[];
}, {
    type: "plan_updated";
    taskTitle: string;
    nodes: {
        status: "done" | "running" | "pending" | "failed";
        id: string;
        label: string;
        parentId?: string | undefined;
        detail?: string | undefined;
    }[];
}>, z.ZodObject<{
    type: z.ZodLiteral<"tool_started">;
    toolName: z.ZodString;
    args: z.ZodRecord<z.ZodString, z.ZodAny>;
    timestamp: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "tool_started";
    toolName: string;
    args: Record<string, any>;
    timestamp: string;
}, {
    type: "tool_started";
    toolName: string;
    args: Record<string, any>;
    timestamp: string;
}>, z.ZodObject<{
    type: z.ZodLiteral<"tool_finished">;
    toolName: z.ZodString;
    output: z.ZodString;
    durationSeconds: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    type: "tool_finished";
    toolName: string;
    output: string;
    durationSeconds: number;
}, {
    type: "tool_finished";
    toolName: string;
    output: string;
    durationSeconds: number;
}>, z.ZodObject<{
    type: z.ZodLiteral<"verification_event">;
    suiteName: z.ZodString;
    status: z.ZodEnum<["passed", "failed", "running", "pending"]>;
    durationSeconds: z.ZodOptional<z.ZodNumber>;
    errorReason: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "verification_event";
    suiteName: string;
    status: "running" | "pending" | "failed" | "passed";
    durationSeconds?: number | undefined;
    errorReason?: string | undefined;
}, {
    type: "verification_event";
    suiteName: string;
    status: "running" | "pending" | "failed" | "passed";
    durationSeconds?: number | undefined;
    errorReason?: string | undefined;
}>, z.ZodObject<{
    type: z.ZodLiteral<"status_update">;
    tokensUsed: z.ZodNumber;
    costSoFar: z.ZodNumber;
    testsPassing: z.ZodString;
    sandboxState: z.ZodEnum<["active", "sandboxed", "idle", "paused"]>;
    elapsedSeconds: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    type: "status_update";
    tokensUsed: number;
    costSoFar: number;
    testsPassing: string;
    sandboxState: "active" | "sandboxed" | "idle" | "paused";
    elapsedSeconds: number;
}, {
    type: "status_update";
    tokensUsed: number;
    costSoFar: number;
    testsPassing: string;
    sandboxState: "active" | "sandboxed" | "idle" | "paused";
    elapsedSeconds: number;
}>]>;
export type IntakeProgressEvent = z.infer<typeof IntakeProgressSchema>;
export type PlanUpdatedEvent = z.infer<typeof PlanUpdatedSchema>;
export type ToolStartedEvent = z.infer<typeof ToolStartedSchema>;
export type ToolFinishedEvent = z.infer<typeof ToolFinishedSchema>;
export type VerificationEvent = z.infer<typeof VerificationEventSchema>;
export type SessionStatusUpdateEvent = z.infer<typeof SessionStatusUpdateSchema>;
export type SSEEvent = z.infer<typeof SSEEventSchema>;
