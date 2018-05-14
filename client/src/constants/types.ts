import { FormReducer } from 'redux-form';

import { ProjectStateSchema, ProjectsEmptyState } from '../models/project';
import { ExperimentStateSchema, ExperimentsEmptyState } from '../models/experiment';
import { JobStateSchema, JobsEmptyState } from '../models/job';
import { GroupStateSchema, GroupsEmptyState } from '../models/group';
import { TokenStateSchema, TokenEmptyState } from '../models/token';
import { ModalStateSchema } from '../models/modal';
import { UserEmptyState, UserStateSchema } from '../models/user';
import { PaginationStateSchema } from '../models/pagination';
import { MetricsEmptyState, MetricsStateSchema } from '../models/metric';

export interface AppState {
  projects: ProjectStateSchema;
  experiments: ExperimentStateSchema;
  groups: GroupStateSchema;
  jobs: JobStateSchema;
  modal: ModalStateSchema;
  auth: TokenStateSchema;
  users: UserStateSchema;
  form: FormReducer;
  pagination: PaginationStateSchema;
  logs: string;
  metrics: MetricsStateSchema;
}

export const AppEmptyState = {
  projects: ProjectsEmptyState,
  experiments: ExperimentsEmptyState,
  groups: GroupsEmptyState,
  jobs: JobsEmptyState,
  auth: TokenEmptyState,
  user: UserEmptyState,
  metrics: MetricsEmptyState
};
