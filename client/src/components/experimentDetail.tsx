import * as React from 'react';
import * as _ from 'lodash';
import * as moment from 'moment';

import { ExperimentModel } from '../models/experiment';
import ExperimentJobs from '../containers/experimentJobs';
import Logs from '../containers/logs';
import {
  getGroupUrl,
  getProjectUrl,
  getUserUrl,
  splitGroupName,
  splitProjectName,
} from '../constants/utils';
import Breadcrumb from './breadcrumb';
import TaskRunMetaInfo from './taskRunMetaInfo';
import Status from './status';

export interface Props {
  experiment: ExperimentModel;
  onDelete: () => any;
  fetchData: () => any;
}

export default class ExperimentDetail extends React.Component<Props, Object> {
  componentDidMount() {
    this.props.fetchData();
  }

  public render() {
    const experiment = this.props.experiment;

    if (_.isNil(experiment)) {
      return (<div>Nothing</div>);
    }
    let values = splitProjectName(experiment.project_name);
    let group = null;
    if (!_.isNil(experiment.experiment_group_name)) {
      group = parseInt(splitGroupName(experiment.experiment_group_name)[2], 10);
    }
    let breadcrumbLinks = [
      {name: values[0], value: getUserUrl(values[0])},
      {name: values[1], value: getProjectUrl(values[0], values[1])},
      {name: `Experiment ${experiment.id}`}];
    if (group) {
      breadcrumbLinks.splice(
        2,
        0,
        {name: `Group ${group}`, value: getGroupUrl(values[0], values[1], group)});
    }
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="entity-details">
            <Breadcrumb icon="fa-cube" links={breadcrumbLinks}/>

            <div className="meta-description">
              {experiment.description}
            </div>
            <div className="meta">
              <span className="meta-info">
                <i className="fa fa-user-o icon" aria-hidden="true"/>
                <span className="title">User:</span>
                {experiment.user}
              </span>
              <span className="meta-info">
                <i className="fa fa-clock-o icon" aria-hidden="true"/>
                <span className="title">Created:</span>
                {moment(experiment.created_at).fromNow()}
              </span>
              <span className="meta-info">
                <i className="fa fa-tasks icon" aria-hidden="true"/>
                <span className="title">Jobs:</span>
                {experiment.num_jobs}
              </span>
              <TaskRunMetaInfo startedAt={experiment.started_at} finishedAt={experiment.finished_at} inline={true}/>
              <Status status={experiment.last_status}/>
            </div>
            {experiment.last_metric &&
            <div className="meta meta-metrics">
              {Object.keys(experiment.last_metric).map(
                (xp, idx) =>
                  <span className="meta-info" key={idx}>
                  <i className="fa fa-area-chart icon" aria-hidden="true"/>
                  <span className="title">{xp}:</span>
                    {experiment.last_metric[xp]}
                </span>)}
            </div>
            }
            {experiment.resources &&
            <div className="meta meta-resources">
              {Object.keys(experiment.resources)
                .filter(
                  (res, idx) =>
                    experiment.resources[res] != null
                )
                .map(
                  (res, idx) =>
                    <span className="meta-info" key={idx}>
                <i className="fa fa-microchip icon" aria-hidden="true"/>
                <span className="title">{res}:</span>
                      {experiment.resources[res].requests || ''} - {experiment.resources[res].limits || ''}
              </span>
                )}
            </div>
            }
            {experiment.declarations &&
            <div className="meta meta-declarations">
              {Object.keys(experiment.declarations).map(
                (xp, idx) =>
                  <span className="meta-info" key={idx}>
                  <i className="fa fa-gear icon" aria-hidden="true"/>
                  <span className="title">{xp}:</span>
                    {experiment.declarations[xp]}
                </span>)}
            </div>
            }
          </div>
          <h4 className="polyaxon-header">Jobs</h4>
          <ExperimentJobs fetchData={() => null} user={experiment.user} experiment={experiment}/>
          <h4 className="polyaxon-header">Logs</h4>
          <Logs fetchData={() => null} logs={''} user={experiment.user} experiment={experiment}/>
        </div>
      </div>
    );
  }
}
