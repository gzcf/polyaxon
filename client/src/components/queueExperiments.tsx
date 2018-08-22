import * as React from 'react';
import * as Table from 'react-bootstrap/lib/Table';
import PaginatedList from './paginatedList';
import { ExperimentModel } from '../models/experiment';
import { SortIndicator } from './sortIndicator';

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

export default class QueueExperiments extends React.Component<Props, State> {
  fields: Array<{ [key: string]: any }>;

  constructor(props: Props) {
    super(props);
    this.state = {
      orderByIndex: 3,
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
      title: 'Experiment Sequence',
      sortable: false,
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

    const listExperiments = () => {
      const experiments = this.props.experiments;
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
              experiments.map(xp =>
                <tr key={xp.sequence}>
                  <td>{xp.user}</td>
                  <td>{xp.project_name.split('.')[1]}</td>
                  <td>{xp.sequence}</td>
                  <td>{this.formatDatetime(xp.created_at)}</td>
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
          componentList={listExperiments()}
          fetchData={_fetchData}
        />
      </div>
    );
  }
}
