import * as React from 'react';
import { SyntheticEvent } from 'react';

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

export class SortIndicator extends React.Component<SortIndicatorProps, SortIndicatorState> {
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