import { Reducer } from 'redux';
import { QueueExperimentsAction, actionTypes } from '../actions/queueExperiment';
import { ExperimentModel } from '../models/experiment';
import { EmptyQueueState, QueueStateSchema } from '../models/queue';

export const queueExperimentsReducer: Reducer<QueueStateSchema> =
  (state: QueueStateSchema = EmptyQueueState, action: QueueExperimentsAction) => {
    switch (action.type) {

      case actionTypes.RECEIVE_QUEUE_EXPERIMENTS:
        return {
          experiments: action.experiments,
          count: action.count
        };
      case actionTypes.REQUEST_QUEUE_EXPERIMENTS:
        return EmptyQueueState;
      default:
        return state;
    }
  };
