import React from 'react'
import { Route, Switch } from 'react-router'

const HomePage = props => (
  <div>
    首页
  </div>
)

export default () => (
  <Switch>
    <Switch>
      <Route path="/" exact component={HomePage} />
    </Switch>
  </Switch>
)
