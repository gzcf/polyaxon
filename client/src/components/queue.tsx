import * as React from 'react';
import { Col, Nav, NavItem, Row, Tab } from 'react-bootstrap';
import QueueExperiments from '../containers/queueExperiments';
import { NotebookJobs } from '../containers/notebookJobs';
import { TensorboardJobs } from '../containers/tensorboardJobs';
import './queue.less';

export interface Props {}

interface State {}

export default class Queue extends React.Component<Props, State> {

  public render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <Tab.Container defaultActiveKey={1} id="queue-tabs" className="plx-nav">
            <Row className="clearfix">
              <Col sm={12}>
                <Nav bsStyle="tabs">
                  <NavItem eventKey={1}>Experiments</NavItem>
                  <NavItem eventKey={2}>Notebooks</NavItem>
                  <NavItem eventKey={3}>Tensorboards</NavItem>
                </Nav>
              </Col>
              <Col sm={12}>
                <Tab.Content animation={true} mountOnEnter={true}>
                  <Tab.Pane eventKey={1}>
                    <QueueExperiments />
                  </Tab.Pane>
                  <Tab.Pane eventKey={2}>
                    <NotebookJobs/>
                  </Tab.Pane>
                  <Tab.Pane eventKey={3}>
                    <TensorboardJobs/>
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
