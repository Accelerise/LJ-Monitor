import React from 'react'
import cp from '../utils/classPack'

let Logo = (props => cp('Logo', 'foo')(
  <div >hhh</div>
))

class Header extends React.Component {
  render() {
    return (
      <div>
        <Logo />
      </div>
    )
  }
}

export default Header
