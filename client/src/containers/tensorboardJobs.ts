import { AppState } from '../constants/types';
import { connect, Dispatch } from 'react-redux';
import * as actions from '../actions/pluginJobs';
import PluginJobs from '../components/pluginJobs';

export function mapStateToProps(state: AppState, params: any) {
  return {
    jobs: state.tensorboardJobs.tensorboardJobs,
    count: state.tensorboardJobs.count,
    currentPage: state.pagination.tensorboardJobsCurrentPage
  };
}

export interface DispatchProps {
  fetchData?: () => any;
}

export function mapDispatchToProps(dispatch: Dispatch<any>, params: any): DispatchProps {
  return {
    fetchData: (currentPage?: number, ordreBy?: string) => {
      dispatch(actions.fetchTensorboardJobs(currentPage, ordreBy));
    }
  };
}

export const TensorboardJobs = connect(mapStateToProps, mapDispatchToProps)(PluginJobs);
