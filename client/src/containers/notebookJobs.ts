import { AppState } from '../constants/types';
import { connect, Dispatch } from 'react-redux';
import * as actions from '../actions/pluginJob';
import PluginJobs from '../components/pluginJobs';

export function mapStateToProps(state: AppState, params: any) {
  return {
    jobs: state.notebookJobs.notebookJobs,
    count: state.notebookJobs.count,
    currentPage: state.pagination.notebookJobsCurrentPage
  };
}

export interface DispatchProps {
  fetchData?: () => any;
}

export function mapDispatchToProps(dispatch: Dispatch<any>, params: any): DispatchProps {
  return {
    fetchData: (currentPage?: number, ordreBy?: string) => {
      dispatch(actions.fetchNotebookJobs(currentPage, ordreBy));
    }
  };
}

export const NotebookJobs = connect(mapStateToProps, mapDispatchToProps)(PluginJobs);
