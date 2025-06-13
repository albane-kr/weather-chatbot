'use client'

import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isNightMode, setIsNightMode] = useState(false);

  const toggleDayNightMode = () => {
    setIsNightMode(!isNightMode);
  };

  const backgroundColor = isNightMode ? '#9886AB' : '#ecebbd';

  const titleColor = isNightMode ? '#100775' : '#228b22';

  const outputBackgroundColor = isNightMode ? '#505964' : '#d0db61';

  const sendButtonBackgroundColor = isNightMode ? '#4C1C1C' : '#228b22';

  return (
    <ThemeContext.Provider value={{ isNightMode, toggleDayNightMode, backgroundColor, titleColor, outputBackgroundColor, sendButtonBackgroundColor }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);