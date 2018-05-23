import * as React from 'react';
import * as Table from 'react-bootstrap/lib/Table';
import PaginatedList from './paginatedList';
import { JobModel } from '../models/job';
import { getCssClassForStatus } from '../constants/utils';

export interface Props {
  isCurrentUser: boolean;
  count: number;
  fetchData: (currentPage: number) => any;
}

interface JobResources {
  cpu?: {[key: string]: any};
  gpu?: {[key: string]: any};
  memory?: {[key: string]: any};
  [key: string]: any;
}
interface Job {
  uuid: string;
  created_at: string;
  experiment: string;
  experiment_name: string;
  finished_at: any;
  is_done: boolean;
  is_running: boolean;
  last_status: string;
  started_at: any;
  unique_name: string;
  updated_at: any;
  role: string;
  sequence: number;
  resources?: JobResources;
}
interface Experiment {
  uuid: string;
  unique_name: string;
  description?: any;
  last_status: string;
  last_metric: any;
  started_at: string;
  finished_at: any;
  updated_at: string;
  is_running: boolean;
  is_done: boolean;
  is_clone: boolean;

  project: string;
  experiment_group: string;
  experiment_group_name: string;
  num_jobs: number;
  user: string;
  project_name: string;
  sequence: number;
  created_at: string;
  jobs?: Job[];
}

export default class Queue extends React.Component<Props, Object> {

  constructor(props: Props) {
    super(props);

  }

  public render() {

    const listExperiments = () => {
      const experiments: Experiment[] = [{"uuid":"d3cee86847484488b13ff82b5b803584","unique_name":"admin.cats-vs-dogs.1.5","user":"admin","sequence":5,"description":null,"created_at":"2017-12-24T19:53:48.019000+01:00","updated_at":"2018-01-24T01:48:47.156000+01:00","last_status":"Starting","last_metric":null,"started_at":"2017-12-24T20:02:11.186000+01:00","finished_at":null,"is_running":true,"is_done":false,"is_clone":false,"project":"ac6a3340b926422aa4496e8b8e9dc77f","project_name":"admin.cats-vs-dogs","experiment_group":"a150988dea334ce4915f4297b2baac47","experiment_group_name":"admin.cats-vs-dogs.1","num_jobs":3, "jobs": [{"uuid":"b4a18d579cca59e7858a11c6cc9fcf41","unique_name":"admin.cats-vs-dogs.2.1.master","sequence":1,"role":"master","experiment":"0bfb74cca2c54190b3f16fd5aba11321","experiment_name":"admin.cats-vs-dogs.2","last_status":"Succeeded","is_running":false,"is_done":true,"created_at":"2017-12-24T18:49:54.812000+01:00","updated_at":"2018-01-26T18:22:40.620000+01:00","started_at":"2017-12-24T18:49:55.403000+01:00","finished_at":"2017-12-24T19:06:02.520000+01:00","resources":{"cpu":{"limits":2,"requests":2},"memory":{"limits":1,"requests":1},"gpu":{"limits":3,"requests":3}}}]},{"uuid":"78013845efa544d68efd37e96bd8ab0b","unique_name":"admin.cats-vs-dogs.1.6","user":"admin","sequence":6,"description":null,"created_at":"2017-12-24T19:53:48.040000+01:00","updated_at":"2018-01-24T01:48:47.166000+01:00","last_status":"Stopped","last_metric":null,"started_at":"2017-12-24T19:53:55.041000+01:00","finished_at":"2017-12-24T20:01:58.303000+01:00","is_running":false,"is_done":true,"is_clone":false,"project":"ac6a3340b926422aa4496e8b8e9dc77f","project_name":"admin.cats-vs-dogs","experiment_group":"a150988dea334ce4915f4297b2baac47","experiment_group_name":"admin.cats-vs-dogs.1","num_jobs":3}];
      return (
        <div>
          <Table striped bordered condensed hover>
            <thead>
              <tr>
                <th>User</th>
                <th>Project</th>
                <th>Experiment Sequence</th>
                <th>Created Time</th>
                <th>Status</th>
                <th>Jobs</th>
              </tr>
            </thead>
            <tbody>
              {
                experiments.map(xp =>
                  <tr key={xp.sequence}>
                    <td>{xp.user}</td>
                    <td>{xp.project_name.split('.')[1]}</td>
                    <td>{xp.sequence}</td>
                    <td>{xp.created_at}</td>
                    <td>{xp.last_status}</td>
                    <td>{
                      xp.jobs &&
                      xp.jobs.map(job =>
                        <div className="block">
                          <div className="meta">
                            <span className="meta-info">
                              <i className="fa fa-certificate icon" aria-hidden="true"/>
                              <span className="title">Role:</span>
                              {job.role}
                            </span>
                            <span className="meta-info">
                              <i className="fa fa-circle icon" aria-hidden="true"/>
                              <span className="title">Sequence:</span>
                              {job.sequence}
                            </span>
                            <span className="meta-info">
                              <span className={`status alert-${getCssClassForStatus(job.last_status)}`}>
                                {job.last_status}
                              </span>
                            </span>
                          </div>
                          {job.resources &&
                          <div className="meta meta-resources">
                            {Object.keys(job.resources)
                              .filter(
                                (res, idx) =>
                                  job.resources![res] != null
                              )
                              .map(
                              (res, idx) =>
                                <span className="meta-info" key={idx}>
                                  <i className="fa fa-microchip icon" aria-hidden="true"/>
                                  <span className="title">{res}:</span>
                                  {job.resources![res].requests || ''} - {job.resources![res].limits || ''}
                                </span>
                            )}
                          </div>
                          }
                        </div>
                      )}
                    </td>
                  </tr>)
              }
            </tbody>
          </Table>
        </div>
      );
    };
    return (
      <PaginatedList
        count={this.props.count}
        componentList={listExperiments()}
        fetchData={this.props.fetchData}
      />
    );
  }
}
