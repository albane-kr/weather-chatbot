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
import { useState, useEffect } from 'react';
import { ConfigProvider, Button, Card } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { HelmetProvider } from 'react-helmet-async';
import TextArea from 'antd/es/input/TextArea';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <h2>Something went wrong.</h2>;
    }
    return this.props.children;
  }
}

const Layout = ({ children }) => {
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    let sid = localStorage.getItem('weatherbot_session_id');
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem('weatherbot_session_id', sid);
    }
    setSessionId(sid);
  }, []);

  const { backgroundColor, titleColor, sendButtonBackgroundColor, outputBackgroundColor } = useTheme();
  const [inputValue, setInputValue] = useState('');
  const maxLength = 200;
  const [output, setOutput] = useState("Hi! I'm rAIny, your friendly weather chatbot! You ca talk to me in English, French and German!");
  const [weatherIcon, setWeatherIcon] = useState('frog');

  const handleInputChange = (e) => {
    if (e.target.value.length <= maxLength) {
      setInputValue(e.target.value);
    }
  };

  const handleSend = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/weather_chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: inputValue,
          session_id: sessionId
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
          <body
            style={{
              backgroundColor,
              overflow: 'hidden',
              height: '100vh',
              margin: 0,
              padding: 0,
            }}>
            <ConfigProvider>
              <Title
                style={{
                  color: titleColor,
                  fontFamily: "'Impact', sans-serif",
                  marginTop: '4%',
                  display: 'block',
                  textAlign: 'center',
                  fontSize: '3rem',
                  fontWeight: '700',
                }}
              >
                rAIny
              </Title>
              <div
                style={{
                  position: 'relative',
                  height: '100%',
                  width: '100%',
                  overflow: 'hidden',
                }}>
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
                    width: '100%',
                    alignItems: 'center',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    height: 'auto',
                    overflow: 'hidden',
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
                        color: '#000000',
                        maxHeight: '30%',
                        overflowY: 'auto',
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
                          color: '#000000',
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