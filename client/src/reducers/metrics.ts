import { Reducer } from 'redux';
import { MetricsAction, actionTypes } from '../actions/metrics';
import { MetricsEmptyState, MetricsStateSchema } from '../models/metric';

export const metricsReducer: Reducer<MetricsStateSchema> =
  (state: MetricsStateSchema = MetricsEmptyState, action: MetricsAction) => {
    switch (action.type) {

      case actionTypes.RECEIVE_METRICS:
        return action.metrics;
      default:
        return state;
    }
  };
