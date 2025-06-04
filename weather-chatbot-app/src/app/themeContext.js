'use client'

import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isNightMode, setIsNightMode] = useState(false);

  const toggleDayNightMode = () => {
    setIsNightMode(!isNightMode);
  };

  const backgroundColor = isNightMode ? '#9886AB' : '#FF9944';

  const titleColor = isNightMode ? '#100775' : '#B95656';

  const outputBackgroundColor = isNightMode ? '#505964' : '#fda172';

  const sendButtonBackgroundColor = isNightMode ? '#4C1C1C' : '#B95656';

  return (
    <ThemeContext.Provider value={{ isNightMode, toggleDayNightMode, backgroundColor, titleColor, outputBackgroundColor, sendButtonBackgroundColor }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);