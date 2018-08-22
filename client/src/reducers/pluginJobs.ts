import { Reducer } from 'redux';
import {
  EmptyNotebookJobsState, EmptyTensorboardJobsState, NotebookJobsStateSchema,
  TensorboardJobsStateSchema
} from '../models/pluginJob';
import { PluginJobsAction, actionTypes } from '../actions/pluginJobs';

export const notebookJobsReducer: Reducer<NotebookJobsStateSchema> =
  (state: NotebookJobsStateSchema = EmptyNotebookJobsState, action: PluginJobsAction) => {
    switch (action.type) {
      case actionTypes.RECEIVE_NOTEBOOK_JOBS:
        return {
          notebookJobs: action.notebookJobs,
          count: action.count
        };
      case actionTypes.REQUEST_NOTEBOOK_JOBS:
        return EmptyNotebookJobsState;
      default:
        return state;
    }
  };

export const tensorboardJobsReducer: Reducer<TensorboardJobsStateSchema> =
  (state: TensorboardJobsStateSchema = EmptyTensorboardJobsState, action: PluginJobsAction) => {
    switch (action.type) {
      case actionTypes.RECEIVE_TENSORBOARD_JOBS:
        return {
          tensorboardJobs: action.tensorboardJobs,
          count: action.count
        };
      case actionTypes.REQUEST_TENSORBOARD_JOBS:
        return EmptyTensorboardJobsState;
      default:
        return state;
    }
  };
