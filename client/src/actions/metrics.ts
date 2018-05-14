import { Action } from 'redux';
import { MetricModel } from '../models/metric';
import { BASE_URL } from '../constants/api';
import { handleAuthError, urlifyProjectName } from '../constants/utils';

export enum actionTypes {
  RECEIVE_METRICS = 'RECEIVE_METRICS',
  REQUEST_METRICS = 'REQUEST_METRICS'
}

export interface ReceiveMetricsAction extends Action {
  type: actionTypes.RECEIVE_METRICS;
  metrics: MetricModel[];
}

export interface RequestMetricsAction extends Action {
  type: actionTypes.REQUEST_METRICS;
}

export type MetricsAction = ReceiveMetricsAction
  | RequestMetricsAction;

export function requestMetricsActionCreator(): RequestMetricsAction {
  return {
    type: actionTypes.REQUEST_METRICS,
  };
}

export function receiveMetricsActionCreator(metrics: MetricModel[]): ReceiveMetricsAction {
  return {
    type: actionTypes.RECEIVE_METRICS,
    metrics
  };
}

export function fetchMetrics(projectUniqueName: string, experimentSequence: number): any {
  return (dispatch: any, getState: any) => {
    dispatch(requestMetricsActionCreator());

    let metricsUrl =
      BASE_URL + `/${urlifyProjectName(projectUniqueName)}` + '/experiments/' + experimentSequence + '/metrics';

    return fetch(metricsUrl, {
      headers: {
        'Content-Type': 'text/plain;charset=UTF-8',
        'Authorization': 'token ' + getState().auth.token
      }
    })
      .then(response => handleAuthError(response, dispatch))
      .then(response => response.json())
      .then(json => dispatch(receiveMetricsActionCreator(json)))
      .catch(error => undefined);
  };
}