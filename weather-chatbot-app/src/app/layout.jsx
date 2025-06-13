'use client';

if (typeof window !== "undefined") {
  const originalError = console.error;
  console.error = (...args) => {
    if (
      typeof args[0] === "string" &&
      args[0].includes("[antd: compatible] antd v5 support React is 16 ~ 18")
    ) {
      return;
    }
    originalError(...args);
  };
}

import React from 'react';
import { useState } from 'react';
import { ConfigProvider, Button, Card } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { SunOutlined, MoonOutlined, SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import TextArea from 'antd/es/input/TextArea';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // You can log error info here if needed
  }

  render() {
    if (this.state.hasError) {
      return <h2>Something went wrong.</h2>;
    }
    return this.props.children;
  }
}

const Layout = ({ children }) => {
  const { backgroundColor, toggleDayNightMode, isNightMode, titleColor, sendButtonBackgroundColor, outputBackgroundColor} = useTheme();
  const [inputValue, setInputValue] = useState('');
  const maxLength = 200;
  const [output, setOutput] = useState("Hi! I'm rAIny, your friendly weather chatbot! I mainly talk French and German though! By the way, you can toggle between day and night mode for a better experience.");
  const [weatherIcon, setWeatherIcon] = useState('frog');

  const handleInputChange = (e) => {
    if (e.target.value.length <= maxLength) {
      setInputValue(e.target.value);
    }
  };

  const handleSend = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/weather', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: inputValue
        }),
      });

      const data = await response.json();
      const generatedText = data.output;
      console.log('data:', data);

      setInputValue('');
      setOutput(generatedText);
      
    } catch (error) {
      console.error('Error generating response:', error);
    }
  };

  return (
    <HelmetProvider>
      <ErrorBoundary>
      <html suppressHydrationWarning>
        <Helmet>
          <link href="https://fonts.googleapis.com/css2?family=Cherry+Bomb&display=swap" rel="stylesheet" />
        </Helmet>
        <body style={{ backgroundColor, fontFamily: 'Cherry Bomb, sans-serif' }}>
          <ConfigProvider>
            <Title style={{ color: titleColor, fontFamily: 'Cherry Bomb, sans-serif', left: 1, marginLeft: '10px', marginTop:'10px' }}>rAIny</Title>
            <Button
              icon={isNightMode ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleDayNightMode}
              style={{ position: 'absolute', right: 1, top: 1, marginRight: '15px', marginTop: '17px', backgroundColor: sendButtonBackgroundColor }}
            />
            <div>
              <Card
                id='weather'
                style={{
                  position: 'absolute',
                  borderRadius: 0,
                  paddingTop: '10px',
                  paddingLeft: '10px',
                  paddingRight: '10px',
                  paddingBottom: '10px',
                  marginBottom: '5px',
                  height: '91.5%',
                  width: '100%',
                  alignItems: 'center'
                }}
              >
                <img
                  src="/frog1.png"
                  alt="Weather"
                  style={{
                    width: "100%",
                    height: "100%",
                    display: "block",
                    margin: "0px 0px 0px 0px",
                  }}
                />
                <div>{children}</div>
                <div>
                  <Card
                    id='textOutputArea'
                    style={{
                      display: 'flex',
                      position: 'fixed',
                      bottom: 0,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '100%',
                      maxWidth: '97%',
                      marginRight: '15px',
                      marginBottom: '90px',
                      backgroundColor: outputBackgroundColor,
                      borderRadius: '10px',
                      borderColor: '#000000',
                      borderWidth: '2px',
                      boxSizing: 'border-box',
                      color: isNightMode ? '#FFFFFF' : '#000000',
                    }}
                  >
                    <div
                      style={{
                        position: 'absolute',
                        top: '10px',
                        left: '10px',
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: '#fff',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 2,
                      }}
                    >
                    {weatherIcon === 'frog' && <span role="img" aria-label="lion" style={{ fontSize: 24 }}>🐸</span>}
                    </div>
                    <p style={{ paddingLeft: "28px", paddingTop: "5px", margin: 0 }}>{output}</p>
                  </Card>
                <div
                  id='inputArea'
                  style={{
                    position: 'fixed',
                    bottom: 0,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: '100%',
                    maxWidth: '97%',
                    backgroundColor: backgroundColor,
                    padding: '5px',
                    boxSizing: 'border-box',
                    display: 'flex',
                    alignItems: 'center',
                    borderRadius: '10px',
                    marginBottom: '15px',
                    marginTop: '5px',
                    borderStyle: 'solid',
                    borderColor: '#FFFFFF',
                  }}
                >
                  <TextArea
                    id='textInputArea'
                    placeholder="Ask rAIny about the weather..."
                    autosize={{ minRows: 1, maxRows: 3 }}
                    value={inputValue}
                    onChange={handleInputChange}
                    count={{ show: true, max: maxLength }}
                    style={{
                      flex: 1,
                      backgroundColor: backgroundColor,
                      color: isNightMode ? '#FFFFFF' : '#000000',
                      border: 'border-box',
                      borderStyle: 'solid',
                      borderColor: '#FFFFFF',
                      resize: 'block',
                    }}
                  />
                  <Button id='sendButton' type='primary' onClick={handleSend} style={{ marginLeft: '10px', backgroundColor: sendButtonBackgroundColor }}>
                    <SendOutlined style={{ color: '#ffff' }} />
                  </Button>
                </div>
                </div>
              </Card>
            </div>
          </ConfigProvider>
        </body>
      </html>
      </ErrorBoundary>
    </HelmetProvider>
  );
};

export default function RootLayout({ children }) {
  return (
    <ThemeProvider>
      <Layout>{children}</Layout>
    </ThemeProvider>
  );
}