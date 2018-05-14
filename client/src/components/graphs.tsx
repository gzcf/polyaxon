import * as React from 'react';
import { LineChart, Line } from 'recharts';

export interface Props {
  fetchData: () => any;
}

export default class Graphs extends React.Component<Props, Object> {
  componentDidMount() {
    this.props.fetchData();
  }

  public render() {
    const data = [];
    for (let i = 0; i < 300; i++) {
      data.push({name: i + "", p: Math.random() * i});
    }
    return (
      <LineChart width={400} height={400} data={data}>
        <Line type="monotone" dataKey="p" stroke="#8884d8" />
      </LineChart>
    );
  }
}