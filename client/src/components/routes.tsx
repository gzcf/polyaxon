import * as React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

import ProjectDetail from '../containers/projectDetail';
import ExperimentDetail from '../containers/experimentDetail';
import GroupDetail from '../containers/groupDetail';
import JobDetail from '../containers/jobDetail';
import Projects from '../containers/projects';
import Login from '../containers/login';
import Logout from '../containers/logout';
import Token from '../containers/token';

import { getHomeUrl, getLoginUrl, getLogoutUrl, isUserAuthenticated } from '../constants/utils';
import Queue from '../components/queue';


function Routes() {
  let tokenRoute = '/app/token';
  let projectDetailRoute = '/app/:user/:projectName/';
  let projectsRoute = '/app/:user/';
  let experimentDetailRoute = '/app/:user/:projectName/experiments/:experimentSequence/';
  let groupDetailRoute = '/app/:user/:projectName/groups/:groupSequence/';
  let jobDetailRoute = '/app/:user/:projectName/experiments/:experimentSequence/jobs/:jobSequence/';
  let queueRoute = '/app/queue';

  return (
    <Switch>
      <Route path={getLoginUrl()} component={Login}/>
      <Route path={getLogoutUrl()} component={Logout}/>
      <Route
        path={tokenRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={tokenRoute} component={Token}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={queueRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={queueRoute} component={Queue}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={jobDetailRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={jobDetailRoute} component={JobDetail}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={groupDetailRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={groupDetailRoute} component={GroupDetail}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={experimentDetailRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={experimentDetailRoute} component={ExperimentDetail}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={projectDetailRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={projectDetailRoute} component={ProjectDetail}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path={projectsRoute}
        render={() => (
          isUserAuthenticated() ? (
            <Route path={projectsRoute} component={Projects}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />

      <Route
        path="*"
        render={() => (
          isUserAuthenticated() ? (
            <Redirect to={getHomeUrl()}/>
          ) : (
            <Redirect to={getLoginUrl()}/>
          )
        )}
      />
    </Switch>
  );
}

export default Routes;
