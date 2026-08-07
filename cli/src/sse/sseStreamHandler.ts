    import { SSEEvent } from './sseTypes.js';
import { SessionInfo, TaskGraphNode, VerificationItem, IntakeStep, StageStatus } from '../api/apiTypes.js';

export interface SSEStreamState {
  session: SessionInfo;
  intakeSteps: IntakeStep[];
  stages?: StageStatus[];
  intakeReady: boolean;
  taskTitle: string;
  taskNodes: TaskGraphNode[];
  verifications: VerificationItem[];
  logs: string[];
  finalSummary?: {
    score?: number;
    testsPassing?: string;
    executionTimeSec?: number;
    reportPath?: string;
  };
  recoveringReason?: string;
}

export function handleIncomingSSEEvent(prevState: SSEStreamState, event: SSEEvent): SSEStreamState {
  switch (event.type) {
    case 'intake_progress': {
      const existingIndex = prevState.intakeSteps.findIndex((s) => s.step === event.step);
      let updatedSteps = [...prevState.intakeSteps];

      if (existingIndex >= 0) {
        updatedSteps[existingIndex] = {
          ...updatedSteps[existingIndex],
          completed: event.completed,
          running: !event.completed,
          detail: event.detail
        };
      } else {
        updatedSteps.push({
          id: String(updatedSteps.length + 1),
          step: event.step,
          completed: event.completed,
          running: !event.completed,
          detail: event.detail
        });
      }

      const isReady = updatedSteps.length > 0 && updatedSteps.every((s) => s.completed);
      return {
        ...prevState,
        intakeSteps: updatedSteps,
        intakeReady: isReady
      };
    }

    case 'status_update': {
      return {
        ...prevState,
        session: {
          ...prevState.session,
          tokensUsed: event.tokensUsed,
          costSoFar: event.costSoFar,
          testsPassing: event.testsPassing,
          sandboxState: event.sandboxState,
          elapsedSeconds: event.elapsedSeconds
        }
      };
    }

    case 'plan_updated': {
      return {
        ...prevState,
        taskTitle: event.taskTitle,
        taskNodes: event.nodes
      };
    }

    case 'tool_started': {
      const logLine = `[${event.timestamp}] Tool started: ${event.toolName}(${JSON.stringify(event.args)})`;
      return {
        ...prevState,
        logs: [...prevState.logs, logLine]
      };
    }

    case 'tool_finished': {
      const logLine = `Tool finished: ${event.toolName} (${event.durationSeconds}s) -> ${event.output}`;
      return {
        ...prevState,
        logs: [...prevState.logs, logLine]
      };
    }

    case 'verification_event': {
      const updatedVerifications = [...prevState.verifications];
      const existingIndex = updatedVerifications.findIndex((v) => v.name === event.suiteName);
      const newSuite: VerificationItem = {
        name: event.suiteName,
        status: event.status,
        durationSeconds: event.durationSeconds,
        errorReason: event.errorReason
      };

      if (existingIndex >= 0) {
        updatedVerifications[existingIndex] = newSuite;
      } else {
        updatedVerifications.push(newSuite);
      }

      const recovering = event.status === 'failed' ? `re-inspecting failing test (${event.suiteName}) → patching` : undefined;

      return {
        ...prevState,
        verifications: updatedVerifications,
        recoveringReason: recovering || prevState.recoveringReason
      };
    }

    default:
      return prevState;
  }
}
