'use client'

import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isNightMode, setIsNightMode] = useState(false);
  const [isGermanMode, setIsGermanMode] = useState(false);

  const toggleDayNightMode = () => {
    setIsNightMode(!isNightMode);
  };

  const backgroundColor = isNightMode ? '#9886AB' : '#FCD9D9';

  const titleColor = isNightMode ? '#100775' : '#1ED2FF';

  const outputBackgroundColor = isNightMode ? '#505964' : '#BEDBFE';

  const sendButtonBackgroundColor = isNightMode ? '#4C1C1C' : '#B95656';

  const toggleFrenchGermanMode = () => {
    setIsGermanMode(!isGermanMode);
  }

  return (
    <ThemeContext.Provider value={{ isNightMode, toggleDayNightMode, backgroundColor, titleColor, outputBackgroundColor, sendButtonBackgroundColor, toggleFrenchGermanMode, isGermanMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);