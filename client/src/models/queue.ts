import { ExperimentModel } from './experiment';

export class QueueStateSchema {
  count: number;
  experiments: ExperimentModel[];
}

export const EmptyQueueState = {
  count: 0,
  experiments: []
};