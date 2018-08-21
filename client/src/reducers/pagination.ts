import { Reducer } from 'redux';

import { PaginationAction, actionTypes } from '../actions/pagination';
import { PaginationEmptyState, PaginationStateSchema } from '../models/pagination';

export const PaginationReducer: Reducer<PaginationStateSchema> =
  (state: PaginationStateSchema = PaginationEmptyState, action: PaginationAction) => {
    switch (action.type) {
      case actionTypes.PAGINATE_PROJECT:
        return {
          ...state,
          projectCurrentPage: action.currentPage,
        };
      case actionTypes.PAGINATE_GROUP:
        return {
          ...state,
          groupCurrentPage: action.currentPage,
        };
      case actionTypes.PAGINATE_EXPERIMENT:
        return {
          ...state,
          experimentCurrentPage: action.currentPage,
        };
      case actionTypes.PAGINATE_JOB:
        return {
          ...state,
          jobCurrentPage: action.currentPage,
        };
      case actionTypes.PAGINATE_QUEUE:
        return {
          ...state,
          queueCurrentPage: action.currentPage,
        };
      case actionTypes.PAGINATE_NOTEBOOK_JOBS:
        return {
          ...state,
          notebookJobsCurrentPage: action.currentPage,
        };
      default:
        return state;
    }

  };
