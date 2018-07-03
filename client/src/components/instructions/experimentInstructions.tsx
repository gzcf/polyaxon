import * as React from 'react';
import './instructions.less';

export interface Props {
  id: number | string;
}

function ExperimentInstructions({id}: Props) {
  return (
    <div className="instructions">
      <div className="row">
        <div className="col-md-12">
          <div className="instructions-header">
            Instructions
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">
          <div className="instructions-content">
            <div className="instructions-section">
              <h4>Stop current experiment</h4>
              <div className="instructions-section-content">
                polyaxon experiment -xp {id} stop
              </div>
            </div>
            <div className="instructions-section">
              <h4>Delete current experiment</h4>
              <div className="instructions-section-content">
                polyaxon experiment -xp {id} delete
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExperimentInstructions;