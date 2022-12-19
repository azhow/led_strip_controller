import React from 'react';
import { HuePicker } from 'react-color';

class ColorPicker extends React.Component {
  state = {
    background: '#fff',
  };

  handleChangeComplete = (color) => {
    this.setState({ background: color.hex });
    window.electronAPI.setColor(color.rgb);
  };

  render() {
    return (
      <HuePicker
        color={ this.state.background }
        onChangeComplete={ this.handleChangeComplete }
      />
    );
  }
}

export default ColorPicker;