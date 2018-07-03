import * as React from 'react';
import * as _ from 'lodash';
import * as moment from 'moment';
import { Tab, Nav, NavItem, Col, Row } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

import { GroupModel } from '../models/group';
import Experiments from '../containers/experiments';
import { getProjectUrl, getUserUrl, splitProjectName } from '../constants/utils';
import GroupInstructions from './instructions/groupInstructions';

export interface Props {
  group: GroupModel;
  onDelete: () => undefined;
  fetchData: () => undefined;
}

export default class GroupDetail extends React.Component<Props, Object> {
  componentDidMount() {
    this.props.fetchData();
  }

  public render() {
    const group = this.props.group;
    if (_.isNil(group)) {
      return (<div>Nothing</div>);
    }
    let values = splitProjectName(group.project_name);
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="entity-details">
            <span className="title">
              <i className="fa fa-cubes icon" aria-hidden="true"/>
              <LinkContainer to={getUserUrl(values[0])}>
                <span>
                  <a className="title">
                    {values[0]}
                  </a>/
                </span>
              </LinkContainer>
              <LinkContainer to={getProjectUrl(values[0], values[1])}>
                <span>
                  <a className="title">
                    {values[1]}
                  </a>/
                </span>
              </LinkContainer>
              <span className="title">
                Group {group.sequence}
              </span>
            </span>
            <div className="meta-description">
              {group.description}
            </div>
            <div className="meta">
              <span className="meta-info">
                <i className="fa fa-user-o icon" aria-hidden="true"/>
                <span className="title">User:</span>
                {group.user}
              </span>
              <span className="meta-info">
                <i className="fa fa-clock-o icon" aria-hidden="true"/>
                <span className="title">Last updated:</span>
                {moment(group.updated_at).fromNow()}
              </span>
              <span className="meta-info">
                <i className="fa fa-share-alt icon" aria-hidden="true"/>
                <span className="title">Concurrency:</span>
                {group.concurrency}
              </span>
            </div>
            <div className="meta">
              <span className="meta-info">
                <i className="fa fa-cube icon" aria-hidden="true"/>
                <span className="title">Experiments:</span>
                {group.num_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-hourglass-1 icon" aria-hidden="true"/>
                <span className="title">Scheduled:</span>
                {group.num_scheduled_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-hourglass-end icon" aria-hidden="true"/>
                <span className="title">Pending:</span>
                {group.num_pending_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-bolt icon" aria-hidden="true"/>
                <span className="title">Running:</span>
                {group.num_running_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-check icon" aria-hidden="true"/>
                <span className="title">Succeeded:</span>
                {group.num_succeeded_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-close icon" aria-hidden="true"/>
                <span className="title">Failed:</span>
                {group.num_failed_experiments}
              </span>
              <span className="meta-info">
                <i className="fa fa-stop icon" aria-hidden="true"/>
                <span className="title">Stopped:</span>
                {group.num_stopped_experiments}
              </span>
            </div>
          </div>

          <Tab.Container defaultActiveKey={1} id="experiment-tabs" className="plx-nav">
            <Row className="clearfix">
              <Col sm={12}>
                <Nav bsStyle="tabs">
                  <NavItem eventKey={1}>Experiments</NavItem>
                  <NavItem eventKey={2}>Instructions</NavItem>
                </Nav>
              </Col>
              <Col sm={12}>
                <Tab.Content animation={true} mountOnEnter={true}>
                  <Tab.Pane eventKey={1}>
                    <Experiments user={group.user} projectName={group.project_name} groupSequence={group.sequence}/>
                  </Tab.Pane>
                  <Tab.Pane eventKey={2}>
                    <GroupInstructions id={group.sequence}/>
                  </Tab.Pane>
                </Tab.Content>
              </Col>
            </Row>
          </Tab.Container>

        </div>
      </div>
    );
  }
}
