import { Reducer } from 'redux';
import { QueueExperimentsAction, actionTypes } from '../actions/queue';
import { ExperimentModel } from '../models/experiment';

export const queueExperimentsReducer: Reducer<ExperimentModel[]> =
  (state: ExperimentModel[] = [], action: QueueExperimentsAction) => {
    switch (action.type) {

      case actionTypes.RECEIVE_QUEUE_EXPERIMENTS:
        return action.experiments;
      case actionTypes.REQUEST_QUEUE_EXPERIMENTS:
        return [];
      default:
        return state;
    }
  };
