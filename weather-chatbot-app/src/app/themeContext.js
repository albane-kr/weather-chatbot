'use client'

import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isNightMode, setIsNightMode] = useState(false);

  const toggleDayNightMode = () => {
    setIsNightMode(!isNightMode);
  };

  const backgroundColor = isNightMode ? '#9886AB' : '#FCD9D9';

  const titleColor = isNightMode ? '#100775' : '#1ED2FF';

  const outputBackgroundColor = isNightMode ? '#505964' : '#BEDBFE';

  return (
    <ThemeContext.Provider value={{ isNightMode, toggleDayNightMode, backgroundColor, titleColor, outputBackgroundColor }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);