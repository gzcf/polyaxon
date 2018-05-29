import * as React from 'react';
import * as Table from 'react-bootstrap/lib/Table';
import PaginatedList from './paginatedList';
import './queue.less';
import { ExperimentModel } from '../models/experiment';
import { SyntheticEvent } from 'react';

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

enum Direction {
  ASC = 'ASC',
  DESC = 'DESC',
  NONE = 'NONE'
}

interface SortIndicatorProps {
  text: string;
  active?: boolean;
  eventKey: any;
  onToggle: (key: any, direction: string) => any;
  defaultDirection?: string;
}

interface SortIndicatorState {
  direction: Direction;
}

class SortIndicator extends React.Component<SortIndicatorProps, SortIndicatorState> {
  constructor(props: SortIndicatorProps) {
    super(props);
    if (this.props.active) {
      if (this.props.defaultDirection) {
        if (this.props.defaultDirection === 'ASC') {
          this.state = {direction: Direction.ASC};
        } else {
          this.state = {direction: Direction.DESC};
        }
      } else {
        this.state = {direction: Direction.ASC};
      }
    } else {
      this.state = {direction: Direction.NONE};
    }
  }

  onClick = (e: SyntheticEvent<any>) => {
    this.setState((prevState, props): SortIndicatorState => {
      let direction: Direction;
      if (props.active) {
        if (prevState.direction === Direction.ASC)
          direction = Direction.DESC;
        else
          direction = Direction.ASC;
      } else {
        direction = Direction.ASC;
      }
      this.props.onToggle(this.props.eventKey, direction as string);
      return {
        direction: direction
      };
    });
  }

  public render() {
    const active = this.props.active;
    const direction = this.state.direction;
    let className;
    if (!active) {
      className = 'inactive';
    } else if (direction === Direction.ASC) {
      className = 'asc';
    } else {
      className = 'desc';
    }
    return (
      <div onClick={this.onClick}>
        <span>{this.props.text}</span>
        <span className={`sort-indicator ${className}`} />
      </div>
    );
  }
}