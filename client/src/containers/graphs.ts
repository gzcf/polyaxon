import { connect, Dispatch } from 'react-redux';

import { AppState } from '../constants/types';
import * as actions from '../actions/metrics';
import Graphs from '../components/graphs';

export function mapStateToProps(state: AppState, params: any) {
  return {metrics: state.metrics};
}

export interface DispatchProps {
  fetchData?: () => any;
}

export function mapDispatchToProps(dispatch: Dispatch<actions.MetricsAction>, params: any): DispatchProps {
  return {
    fetchData: () => console.log("fetchData")
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Graphs);
