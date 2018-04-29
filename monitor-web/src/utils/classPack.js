import React from 'react'
import classNames from 'classnames'

const classPack = (...name) => {
  return WrappedThing => {
    if (WrappedThing.isReactComponent) {
      return props => React.createElement(WrappedThing, {className: classNames(...name), ...props})
    }
    if (React.isValidElement(WrappedThing)) {
      return React.cloneElement(WrappedThing, {className: classNames(...name)})
    }
    throw Error('That is not a React Component or React Element')
  }
}

export default classPack
