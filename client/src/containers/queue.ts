import { connect, Dispatch } from 'react-redux';

import { AppState } from '../constants/types';
import Queue from '../components/queue';
import * as actions from '../actions/queue';

export function mapStateToProps(state: AppState, params: any) {
  return {
    experiments: state.queueExperiments.experiments,
    count: state.queueExperiments.count
  };
}

export interface DispatchProps {
  fetchData?: () => any;
}

export function mapDispatchToProps(dispatch: Dispatch<any>, params: any): DispatchProps {
  return {
    fetchData: (currentPage?: number, ordreBy?: string) => {
      dispatch(actions.fetchQueueExperiments(currentPage, ordreBy));
    }
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Queue);
