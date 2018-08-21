export class PluginJobModel {
  public user: string;
  public config: {[key: string]: any};
  public created_at: string;
  public last_status: string;
  public resources: {[key: string]: any};
  public project_name: string;
}

export class NotebookJobsStateSchema {
  count: number;
  notebookJobs: PluginJobModel[];
}

export const EmptyNotebookJobsState = {
  count: 0,
  notebookJobs: []
};

export class TensorboardJobsStateSchema {
  count: number;
  tensorboardJobs: PluginJobModel[];
}

export const EmptyTensorboardJobsState = {
  count: 0,
  tensorboardJobs: []
};