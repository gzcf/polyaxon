import { Action } from 'redux';
import * as url from 'url';

import { BASE_API_URL } from '../constants/api';
import { getExperimentUrlFromName, handleAuthError, urlifyProjectName } from '../constants/utils';
import { getExperimentUniqueName, getExperimentUrl } from '../constants/utils';
import history from '../history';
import { BookmarkModel } from '../models/bookmark';
import { ExperimentModel } from '../models/experiment';

export enum actionTypes {
  CREATE_EXPERIMENT = 'CREATE_EXPERIMENT',
  DELETE_EXPERIMENT = 'DELETE_EXPERIMENT',
  STOP_EXPERIMENT = 'STOP_EXPERIMENT',
  UPDATE_EXPERIMENT = 'UPDATE_EXPERIMENT',
  RECEIVE_EXPERIMENT = 'RECEIVE_EXPERIMENT',
  RECEIVE_EXPERIMENTS = 'RECEIVE_EXPERIMENTS',
  REQUEST_EXPERIMENTS = 'REQUEST_EXPERIMENTS',
  BOOKMARK_EXPERIMENT = 'BOOKMARK_EXPERIMENT',
  UNBOOKMARK_EXPERIMENT = 'UNBOOKMARK_EXPERIMENT',
}

export interface CreateUpdateReceiveExperimentAction extends Action {
  type: actionTypes.CREATE_EXPERIMENT | actionTypes.UPDATE_EXPERIMENT | actionTypes.RECEIVE_EXPERIMENT;
  experiment: ExperimentModel;
}

export interface DeleteExperimentAction extends Action {
  type: actionTypes.DELETE_EXPERIMENT;
  experimentName: string;
}

export interface StopExperimentAction extends Action {
  type: actionTypes.STOP_EXPERIMENT;
  experimentName: string;
}

export interface ReceiveExperimentsAction extends Action {
  type: actionTypes.RECEIVE_EXPERIMENTS;
  experiments: ExperimentModel[];
  count: number;
}

export interface RequestExperimentsAction extends Action {
  type: actionTypes.REQUEST_EXPERIMENTS;
}

export interface BookmarkExperimentAction extends Action {
  type: actionTypes.BOOKMARK_EXPERIMENT | actionTypes.UNBOOKMARK_EXPERIMENT;
  experimentName: string;
}

export type ExperimentAction =
  CreateUpdateReceiveExperimentAction
  | DeleteExperimentAction
  | StopExperimentAction
  | ReceiveExperimentsAction
  | RequestExperimentsAction
  | BookmarkExperimentAction;

export function createExperimentActionCreator(experiment: ExperimentModel): CreateUpdateReceiveExperimentAction {
  return {
    type: actionTypes.CREATE_EXPERIMENT,
    experiment
  };
}

export function updateExperimentActionCreator(experiment: ExperimentModel): CreateUpdateReceiveExperimentAction {
  return {
    type: actionTypes.UPDATE_EXPERIMENT,
    experiment
  };
}

export function deleteExperimentActionCreator(experimentName: string): DeleteExperimentAction {
  return {
    type: actionTypes.DELETE_EXPERIMENT,
    experimentName,
  };
}

export function stopExperimentActionCreator(experimentName: string): StopExperimentAction {
  return {
    type: actionTypes.STOP_EXPERIMENT,
    experimentName,
  };
}

export function requestExperimentsActionCreator(): RequestExperimentsAction {
  return {
    type: actionTypes.REQUEST_EXPERIMENTS,
  };
}

export function receiveExperimentsActionCreator(experiments: ExperimentModel[],
                                                count: number): ReceiveExperimentsAction {
  return {
    type: actionTypes.RECEIVE_EXPERIMENTS,
    experiments,
    count
  };
}

export function receiveBookmarkedExperimentsActionCreator(bookmarkedExperiments: BookmarkModel[],
                                                          count: number): ReceiveExperimentsAction {
  const experiments: ExperimentModel[] = [];
  for (const bookmarkedExperiment of bookmarkedExperiments) {
    experiments.push(bookmarkedExperiment.content_object as ExperimentModel);
  }
  return {
    type: actionTypes.RECEIVE_EXPERIMENTS,
    experiments,
    count
  };
}

export function receiveExperimentActionCreator(experiment: ExperimentModel): CreateUpdateReceiveExperimentAction {
  return {
    type: actionTypes.RECEIVE_EXPERIMENT,
    experiment
  };
}

export function bookmarkExperimentActionCreator(experimentName: string) {
  return {
    type: actionTypes.BOOKMARK_EXPERIMENT,
    experimentName,
  };
}

export function unbookmarkExperimentActionCreator(experimentName: string) {
  return {
    type: actionTypes.UNBOOKMARK_EXPERIMENT,
    experimentName,
  };
}

function _fetchExperiments(experimentsUrl: string,
                           bookmarks: boolean,
                           filters: { [key: string]: number | boolean | string } = {},
                           dispatch: any,
                           getState: any): any {
  dispatch(requestExperimentsActionCreator());
  const urlPieces = location.hash.split('?');
  const baseUrl = urlPieces[0];
  if (Object.keys(filters).length) {
    experimentsUrl += url.format({query: filters});
    if (baseUrl) {
      history.push(baseUrl + url.format({query: filters}));
    }
  } else if (urlPieces.length > 1) {
    history.push(baseUrl);
  }
  return fetch(experimentsUrl, {
    headers: {
      Authorization: 'token ' + getState().auth.token
    }
  })
    .then((response) => handleAuthError(response, dispatch))
    .then((response) => response.json())
    .then((json) => bookmarks ?
      dispatch(receiveBookmarkedExperimentsActionCreator(json.results, json.count)) :
      dispatch(receiveExperimentsActionCreator(json.results, json.count)));
}

export function fetchBookmarkedExperiments(user: string,
                                           filters: { [key: string]: number | boolean | string } = {}): any {
  return (dispatch: any, getState: any) => {
    const experimentsUrl = `${BASE_API_URL}/bookmarks/${user}/experiments/`;
    return _fetchExperiments(experimentsUrl, true, filters, dispatch, getState);
  };
}

export function fetchExperiments(projectUniqueName: string,
                                 filters: { [key: string]: number | boolean | string } = {}): any {
  return (dispatch: any, getState: any) => {
    const experimentsUrl = `${BASE_API_URL}/${urlifyProjectName(projectUniqueName)}/experiments/`;
    return _fetchExperiments(experimentsUrl, false, filters, dispatch, getState);
  };
}

export function fetchExperiment(user: string, projectName: string, experimentId: number): any {
  const experimentUrl = getExperimentUrl(user, projectName, experimentId, false);
  return (dispatch: any, getState: any) => {
    dispatch(requestExperimentsActionCreator());
    return fetch(`${BASE_API_URL}${experimentUrl}`, {
      headers: {
        Authorization: 'token ' + getState().auth.token
      }
    })
      .then((response) => handleAuthError(response, dispatch))
      .then((response) => response.json())
      .then((json) => dispatch(receiveExperimentActionCreator(json)));
  };
}

export function deleteExperiment(experimentName: string): any {
  const experimentUrl = getExperimentUrlFromName(experimentName, false);
  return (dispatch: any, getState: any) => {
    return fetch(`${BASE_API_URL}${experimentUrl}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'token ' + getState().auth.token,
        'X-CSRFToken': getState().auth.csrftoken
      }
    })
      .then((response) => handleAuthError(response, dispatch))
      .then(() => dispatch(deleteExperimentActionCreator(experimentName)));
  };
}

export function stopExperiment(experimentName: string): any {
  const experimentUrl = getExperimentUrlFromName(experimentName, false);
  return (dispatch: any, getState: any) => {
    return fetch(`${BASE_API_URL}${experimentUrl}/stop`, {
      method: 'POST',
      headers: {
        'Authorization': 'token ' + getState().auth.token,
        'X-CSRFToken': getState().auth.csrftoken
      }
    })
      .then((response) => handleAuthError(response, dispatch))
      .then(() => dispatch(stopExperimentActionCreator(experimentName)));
  };
}

export function bookmark(user: string, projectName: string, experimentId: number | string): any {
  const experimentName = getExperimentUniqueName(user, projectName, experimentId);
  const experimentUrl = getExperimentUrl(user, projectName, experimentId, false);
  return (dispatch: any, getState: any) => {
    return fetch(
      `${BASE_API_URL}${experimentUrl}/bookmark`, {
        method: 'POST',
        headers: {
          'Authorization': 'token ' + getState().auth.token,
          'X-CSRFToken': getState().auth.csrftoken
        },
      })
      .then((response) => handleAuthError(response, dispatch))
      .then(() => dispatch(bookmarkExperimentActionCreator(experimentName)));
  };
}

export function unbookmark(user: string, projectName: string, experimentId: number | string): any {
  const experimentName = getExperimentUniqueName(user, projectName, experimentId);
  const experimentUrl = getExperimentUrl(user, projectName, experimentId, false);
  return (dispatch: any, getState: any) => {
    return fetch(
      `${BASE_API_URL}${experimentUrl}/unbookmark`, {
        method: 'DELETE',
        headers: {
          'Authorization': 'token ' + getState().auth.token,
          'X-CSRFToken': getState().auth.csrftoken
        },
      })
      .then((response) => handleAuthError(response, dispatch))
      .then(() => dispatch(unbookmarkExperimentActionCreator(experimentName)));
  };
}
