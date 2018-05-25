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
