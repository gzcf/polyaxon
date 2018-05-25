import { Action } from 'redux';
import * as url from 'url';

import { handleAuthError } from '../constants/utils';
import { ExperimentModel } from '../models/experiment';
import { BASE_URL } from '../constants/api';
import { getOffset } from '../constants/paginate';
import * as paginationActions from '../actions/pagination';

export enum actionTypes {
  REQUEST_QUEUE_EXPERIMENTS = 'REQUEST_QUEUE_EXPERIMENTS',
  RECEIVE_QUEUE_EXPERIMENTS = 'RECEIVE_QUEUE_EXPERIMENTS'
}

export interface ReceiveQueueExperimentsAction extends Action {
  type: actionTypes.RECEIVE_QUEUE_EXPERIMENTS;
  experiments: ExperimentModel[];
}

export interface RequestQueueExperimentsAction extends Action {
  type: actionTypes.REQUEST_QUEUE_EXPERIMENTS;
}

export type QueueExperimentsAction =
  ReceiveQueueExperimentsAction
  | RequestQueueExperimentsAction;

export function requestQueueExperimentsActionCreator(): RequestQueueExperimentsAction {
  return {
    type: actionTypes.REQUEST_QUEUE_EXPERIMENTS,
  };
}

export function receiveQueueExperimentsActionCreator(experiments: ExperimentModel[]): ReceiveQueueExperimentsAction {
  return {
    type: actionTypes.RECEIVE_QUEUE_EXPERIMENTS,
    experiments
  };
}

export function fetchQueueExperiments(currentPage?: number, orderBy?: string): any {
  return (dispatch: any, getState: any) => {
    dispatch(requestQueueExperimentsActionCreator());
    paginationActions.paginateExperiment(dispatch, currentPage);
    let experimentsUrl = `${BASE_URL}/experiments`;
    let filters: {[key: string]: number|boolean|string} = {
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
      experimentsUrl += url.format({ query: filters });
    }
    return fetch(experimentsUrl, {
      headers: {
        'Authorization': 'token ' + getState().auth.token
      }
    })
      .then(response => handleAuthError(response, dispatch))
      .then(response => response.json())
      .then(json => json.results)
      .then(json => dispatch(receiveQueueExperimentsActionCreator(json)));
  };
}
