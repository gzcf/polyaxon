import * as React from 'react';
import * as Table from 'react-bootstrap/lib/Table';
import PaginatedList from './paginatedList';
import { JobModel } from '../models/job';
import { getCssClassForStatus } from '../constants/utils';
import { ExperimentModel } from '../models/experiment';
import { DropdownButton, MenuItem, SelectCallback } from 'react-bootstrap';

export interface Props {
  count: number;
  fetchData: (currentPage?: number, ordreBy?: string) => any;
  experiments: ExperimentModel[];
  currentPage: number;
}

interface State {
  orderByIndex: number;
  orderByDirection: string;
}

export default class Queue extends React.Component<Props, State> {
  fields: Array<{[key: string]: any}>;

  constructor(props: Props) {
    super(props);
    this.state = {
      orderByIndex: 2,
      orderByDirection: 'DESC'
    };

    this.fields = [{
      title: 'User',
      field: 'user__username'
    }, {
      title: 'Project',
      field: 'project__name'
    }, {
      title: 'Create Time',
      field: 'created_at'
    }];
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    if (this.state.orderByIndex != prevState.orderByIndex ||
        this.state.orderByDirection != prevState.orderByDirection) {
      this.props.fetchData(this.props.currentPage, this.getOrderBy());
    }
  }

  getOrderBy() {
    let symbol = this.state.orderByDirection === 'DESC' ? '-' : '';
    return symbol + this.fields[this.state.orderByIndex].field;
  }

  orderByDirectionOnSelect: SelectCallback = (eventKey: any) => {
    this.setState({
      orderByDirection: eventKey
    });
  }

  orderByOnSelect: SelectCallback = (eventKey: any) => {
    this.setState({orderByIndex: eventKey});
  };

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

    const _fetchData =
      (currentPage: number) => {
        this.props.fetchData(currentPage, this.getOrderBy());
      };

    return (
      <div>
        <div>
          <span>
            Order by：
          </span>
          <DropdownButton
            bsStyle="default"
            title={this.fields[this.state.orderByIndex].title}
            key="1"
            id="dropdown-order-by">
            {
              this.fields.map((field, index) =>
                <MenuItem
                  eventKey={index}
                  onSelect={this.orderByOnSelect}
                  active={index === this.state.orderByIndex}>
                    {field.title}
                </MenuItem>)
            }
          </DropdownButton>
          <DropdownButton
            bsStyle="default"
            title={this.state.orderByDirection}
            key="2"
            id="dropdown-order-by-direction">
            <MenuItem eventKey="ASC" onSelect={this.orderByDirectionOnSelect}>
              ASC
            </MenuItem>
            <MenuItem eventKey="DESC" onSelect={this.orderByDirectionOnSelect}>
              DESC
            </MenuItem>
          </DropdownButton>
        </div>
        <PaginatedList
          count={this.props.count}
          componentList={listExperiments()}
          fetchData={_fetchData}
        />
      </div>
    );
  }
}
