import { Action } from 'redux';
import * as url from 'url';

import { handleAuthError } from '../constants/utils';
import { BASE_URL } from '../constants/api';
import { getOffset } from '../constants/paginate';
import * as paginationActions from '../actions/pagination';
import { PluginJobModel } from '../models/pluginJob';

export enum actionTypes {
  REQUEST_NOTEBOOK_JOBS = 'REQUEST_NOTEBOOK_JOBS',
  RECEIVE_NOTEBOOK_JOBS = 'RECEIVE_NOTEBOOK_JOBS',
  REQUEST_TENSORBOARD_JOBS = 'REQUEST_TENSORBOARD_JOBS',
  RECEIVE_TENSORBOARD_JOBS = 'RECEIVE_TENSORBOARD_JOBS',
}

export interface ReceiveNotebookJobsAction extends Action {
  type: actionTypes.RECEIVE_NOTEBOOK_JOBS;
  notebookJobs: PluginJobModel[];
  count: number;
}

export interface RequestNotebookJobsAction extends Action {
  type: actionTypes.REQUEST_NOTEBOOK_JOBS;
}

export type PluginJobsAction =
  ReceiveNotebookJobsAction
  | RequestNotebookJobsAction;

export function requestNotebookJobsActionCreator(): RequestNotebookJobsAction {
  return {
    type: actionTypes.REQUEST_NOTEBOOK_JOBS,
  };
}

export function receiveNotebookJobsActionCreator(notebookJobs: PluginJobModel[], count: number): ReceiveNotebookJobsAction {
  return {
    type: actionTypes.RECEIVE_NOTEBOOK_JOBS,
    notebookJobs,
    count
  };
}

function fetchPluginJobs(jobsUrl: string,
                         requestActionCreator: () => PluginJobsAction,
                         receiveActionCreator: (jobs: PluginJobModel[], count: number) => PluginJobsAction,
                         paginateActionCreator: any,
                         currentPage?: number, orderBy?: string): any {
  return (dispatch: any, getState: any) => {
    dispatch(requestActionCreator());
    paginateActionCreator(dispatch, currentPage);
    let filters: { [key: string]: number | boolean | string } = {
      is_running: '1'
    };

    if (orderBy) {
      filters.ordering = orderBy;
    }

    let offset = getOffset(currentPage);
    if (offset != null) {
      filters.offset = offset;
    }
    if (filters) {
      jobsUrl += url.format({query: filters});
    }
    return fetch(jobsUrl, {
      headers: {
        'Authorization': 'token ' + getState().auth.token
      }
    })
      .then(response => handleAuthError(response, dispatch))
      .then(response => response.json())
      .then(json => dispatch(receiveActionCreator(json.results, json.count)));
  };
}

export function fetchNotebookJobs(currentPage?: number, orderBy?: string): any {
  return fetchPluginJobs(
    `${BASE_URL}/notebook_jobs`,
    requestNotebookJobsActionCreator,
    receiveNotebookJobsActionCreator,
    paginationActions.paginateNotebookJobs,
    currentPage,
    orderBy
  );
}
