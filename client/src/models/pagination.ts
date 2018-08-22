export class PaginationStateSchema {
  public projectCurrentPage: number;
  public groupCurrentPage: number;
  public experimentCurrentPage: number;
  public jobCurrentPage: number;
  public queueCurrentPage: number;
  public notebookJobsCurrentPage: number;
  public tensorboardJobsCurrentPage: number;
}

export const PaginationEmptyState = {
  projectCurrentPage: 1,
  groupCurrentPage: 1,
  experimentCurrentPage: 1,
  jobCurrentPage: 1,
  queueCurrentPage: 1,
  notebookJobsCurrentPage: 1,
  tensorboardJobsCurrentPage: 1
};
