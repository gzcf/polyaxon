import { connect, Dispatch } from 'react-redux';

import { AppState } from '../constants/types';
import Queue from '../components/queue';

export function mapStateToProps(state: AppState, params: any) {
  return {};
}

export interface DispatchProps {
  fetchData?: () => any;
}

export function mapDispatchToProps(dispatch: Dispatch<any>, params: any): DispatchProps {
  return {
    fetchData: () => undefined
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Queue);
