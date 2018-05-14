export class MetricModel {
  public values: object;
  public created_at: string;
}

export type MetricsStateSchema = MetricModel[];

export const MetricsEmptyState = [];
