import { PluginJobModel } from '../models/pluginJob';
import * as React from 'react';
import { Table } from 'react-bootstrap';
import { SortIndicator } from './sortIndicator';
import PaginatedList from './paginatedList';

export interface Props {
  count: number;
  fetchData: (currentPage?: number, ordreBy?: string) => any;
  jobs: PluginJobModel[];
  currentPage: number;
}

interface State {
  orderByIndex: number;
  orderByDirection: string;
}

export default class PluginJobs extends React.Component<Props, State> {
  fields: Array<{[key: string]: any}>;

  constructor(props: Props) {
    super(props);
    this.state = {
      orderByIndex: 2,
      orderByDirection: 'DESC'
    };

    this.fields = [{
      title: 'User',
      sortable: true,
      field: 'user__username'
    }, {
      title: 'Project',
      sortable: true,
      field: 'project__name'
    }, {
      title: 'Create Time',
      sortable: true,
      field: 'created_at'
    }, {
      title: 'Status',
      sortable: false,
    }, {
      title: 'Resources',
      sortable: false,
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

  formatDatetime(date: string) {
    let d = new Date(date);
    return d.toLocaleString();
  }

  headerOnToggle = (index: number, direction: string) => {
    this.setState({
      orderByIndex: index,
      orderByDirection: direction
    });
  }

  public render() {

    const listJobs = () => {
      const jobs = this.props.jobs;
      return (
        <div>
          <Table striped bordered condensed hover>
            <thead>
              <tr>
                {this.fields.map((field, index) => {
                  if (field.sortable) {
                    return (
                      <th>
                        <SortIndicator
                          onToggle={this.headerOnToggle}
                          eventKey={index}
                          text={field.title}
                          active={index === this.state.orderByIndex}
                          defaultDirection={this.state.orderByDirection}
                        />
                      </th>
                    );
                  } else {
                    return <th><span>{field.title}</span></th>
                  }
                })}
              </tr>
            </thead>
            <tbody>
              {
                jobs.map((job, index) =>
                  <tr key={index}>
                    <td>{job.user}</td>
                    <td>{job.project_name.split('.')[1]}</td>
                    <td>{this.formatDatetime(job.created_at)}</td>
                    <td>{job.last_status}</td>
                    <td>{job.resources &&
                      <div className="meta meta-resources">
                        {Object.keys(job.resources)
                          .filter(
                            (res, idx) =>
                              job.resources[res] != null
                          )
                          .map(
                            (res, idx) =>
                              <span className="meta-info" key={idx}>
                          <i className="fa fa-microchip icon" aria-hidden="true"/>
                          <span className="title">{res}:</span>
                                {job.resources[res].requests || ''} - {job.resources[res].limits || ''}
                        </span>
                          )}
                      </div>
                      }
                    </td>
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
        <PaginatedList
          count={this.props.count}
          componentList={listJobs()}
          fetchData={_fetchData}
        />
      </div>
    );
  }
}