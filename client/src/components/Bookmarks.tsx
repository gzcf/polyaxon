import * as React from 'react';

import { getBookmarksUrl, getUserUrl } from '../constants/utils';
import Builds from '../containers/builds';
import Experiments from '../containers/experiments';
import Groups from '../containers/groups';
import Jobs from '../containers/jobs';
import Projects from '../containers/projects';
import Breadcrumb from './breadcrumb';
import LinkedTab from './linkedTab';

export interface Props {
  user: string;
}

export default class Bookmarks extends React.Component<Props, Object> {
  public render() {
    const bookmarksUrl = getBookmarksUrl(this.props.user);

    return (
      <div className="row">
        <div className="col-md-12">
          <Breadcrumb
            icon="fa-star"
            links={[
              {name: this.props.user, value: getUserUrl(this.props.user)},
              {name: 'bookmarks'}]}
          />
          <LinkedTab
            baseUrl={bookmarksUrl}
            tabs={[
              {
                title: 'Experiments',
                component: <Experiments user={this.props.user} bookmarks={true} useFilters={false}/>,
                relUrl: 'experiments'
              }, {
                title: 'Experiment groups',
                component: <Groups user={this.props.user} bookmarks={true} useFilters={false}/>,
                relUrl: 'groups'
              }, {
                title: 'Jobs',
                component: <Jobs user={this.props.user} bookmarks={true} useFilters={false}/>,
                relUrl: 'jobs'
              }, {
                title: 'Builds',
                component: <Builds user={this.props.user} bookmarks={true} useFilters={false}/>,
                relUrl: 'builds'
              }, {
                title: 'Projects',
                component: <Projects user={this.props.user} bookmarks={true}/>,
                relUrl: 'Projects'
              }
            ]}
          />
        </div>
      </div>
    );
  }
}
