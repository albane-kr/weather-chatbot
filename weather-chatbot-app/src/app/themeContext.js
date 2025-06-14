'use client'

import React, { createContext, useContext } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {

  const backgroundColor = '#ecebbd';

  const titleColor = '#228b22';

  const outputBackgroundColor = '#d0db61';

  const sendButtonBackgroundColor = '#228b22';

  return (
    <ThemeContext.Provider value={{ backgroundColor, titleColor, outputBackgroundColor, sendButtonBackgroundColor }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);