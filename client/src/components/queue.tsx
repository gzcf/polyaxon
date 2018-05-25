import * as React from 'react';
import * as Table from 'react-bootstrap/lib/Table';
import PaginatedList from './paginatedList';
import { JobModel } from '../models/job';
import { getCssClassForStatus } from '../constants/utils';
import { ExperimentModel } from '../models/experiment';

export interface Props {
  count: number;
  fetchData: (currentPage: number) => any;
  experiments: ExperimentModel[];
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
      const experiments = this.props.experiments;
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
                <th>Resources</th>
                {/*<th>Jobs</th>*/}
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
                    <td>{xp.resources &&
                      <div className="meta meta-resources">
                        {Object.keys(xp.resources)
                          .filter(
                            (res, idx) =>
                              xp.resources[res] != null
                          )
                          .map(
                            (res, idx) =>
                              <span className="meta-info" key={idx}>
                          <i className="fa fa-microchip icon" aria-hidden="true"/>
                          <span className="title">{res}:</span>
                                {xp.resources[res].requests || ''} - {xp.resources[res].limits || ''}
                        </span>
                          )}
                      </div>
                      }
                    </td>
                    {/*<td>{*/}
                      {/*xp.jobs &&*/}
                      {/*xp.jobs.map(job =>*/}
                        {/*<div className="block">*/}
                          {/*<div className="meta">*/}
                            {/*<span className="meta-info">*/}
                              {/*<i className="fa fa-certificate icon" aria-hidden="true"/>*/}
                              {/*<span className="title">Role:</span>*/}
                              {/*{job.role}*/}
                            {/*</span>*/}
                            {/*<span className="meta-info">*/}
                              {/*<i className="fa fa-circle icon" aria-hidden="true"/>*/}
                              {/*<span className="title">Sequence:</span>*/}
                              {/*{job.sequence}*/}
                            {/*</span>*/}
                            {/*<span className="meta-info">*/}
                              {/*<span className={`status alert-${getCssClassForStatus(job.last_status)}`}>*/}
                                {/*{job.last_status}*/}
                              {/*</span>*/}
                            {/*</span>*/}
                          {/*</div>*/}
                          {/*{job.resources &&*/}
                          {/*<div className="meta meta-resources">*/}
                            {/*{Object.keys(job.resources)*/}
                              {/*.filter(*/}
                                {/*(res, idx) =>*/}
                                  {/*job.resources![res] != null*/}
                              {/*)*/}
                              {/*.map(*/}
                              {/*(res, idx) =>*/}
                                {/*<span className="meta-info" key={idx}>*/}
                                  {/*<i className="fa fa-microchip icon" aria-hidden="true"/>*/}
                                  {/*<span className="title">{res}:</span>*/}
                                  {/*{job.resources![res].requests || ''} - {job.resources![res].limits || ''}*/}
                                {/*</span>*/}
                            {/*)}*/}
                          {/*</div>*/}
                          {/*}*/}
                        {/*</div>*/}
                      {/*)}*/}
                    {/*</td>*/}
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
