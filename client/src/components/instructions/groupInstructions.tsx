import * as React from 'react';
import './instructions.less';

export interface Props {
  id: number | string;
}

function GroupInstructions({id}: Props) {
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
              <h4>Stop experiments in the group</h4>
              <div className="instructions-section-content">
                polyaxon group -g {id} stop
              </div>
            </div>
            <div className="instructions-section">
              <h4>Delete experiment group</h4>
              <div className="instructions-section-content">
                polyaxon group -g {id} delete
              </div>
            </div>
            <div className="instructions-section">
              <h4>Add/update the group description</h4>
              <div className="instructions-section-content">
                polyaxon group -g {id} update --description="New group description..."
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

export default GroupInstructions;