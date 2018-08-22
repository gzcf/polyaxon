import { Reducer } from 'redux';
import { EmptyNotebookJobsState, NotebookJobsStateSchema } from '../models/pluginJob';
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
