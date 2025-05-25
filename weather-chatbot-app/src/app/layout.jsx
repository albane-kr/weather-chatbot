'use client';

import { useState } from 'react';
import { ConfigProvider, Button, Drawer, Card, Radio } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { MenuOutlined, SunOutlined, MoonOutlined, SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import TextArea from 'antd/es/input/TextArea';

const Layout = ({ children }) => {
  const { backgroundColor, toggleDayNightMode, isNightMode, titleColor, sendButtonBackgroundColor, outputBackgroundColor} = useTheme();
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [isGermanMode, setIsGermanMode] = useState(true);
  const [inputValue, setInputValue] = useState('');
  const maxLength = 100;
  const languageMode = isGermanMode ? 'German' : 'French';
  const [output, setOutput] = useState("Hi! I'm rAIny, your friendly weather chatbot!");

  const showDrawer = () => {
    setDrawerVisible(true);
  };

  const closeDrawer = () => {
    setDrawerVisible(false);
  };

  const handleInputChange = (e) => {
    if (e.target.value.length <= maxLength) {
      setInputValue(e.target.value);
    }
  };

  const handleSend = async () => {
    console.log('Current languageMode:', languageMode);
    try {
      const response = await fetch('http://127.0.0.1:5000/generate-response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: inputValue,
          language: languageMode,
          weather_type: 'rainy',
          weather_type_intensity: 'high',
          temperature: '20',
          geolocation: 'Berlin',
          expression: 'il pleut comme vache qui pisse',
          emotion: 'sad',
        }),
      });

      const data = await response.json();
      const generatedText = data.response;

      setInputValue('');
      setOutput(generatedText);
    } catch (error) {
      console.error('Error generating response:', error);
    }
  };

  return (
    <HelmetProvider>
      <html suppressHydrationWarning>
        <Helmet>
          <link href="https://fonts.googleapis.com/css2?family=Cherry+Bomb&display=swap" rel="stylesheet" />
        </Helmet>
        <body style={{ backgroundColor, fontFamily: 'Cherry Bomb, sans-serif' }}>
          <ConfigProvider>
            <Title style={{ color: titleColor, fontFamily: 'Cherry Bomb, sans-serif', left: 1, marginLeft: '10px' }}>rAIny</Title>
            <Button
              icon={<MenuOutlined />}
              onClick={showDrawer}
              style={{ position: 'absolute', right: 1, top: 1, marginRight: '15px', marginTop: '10px' }}
            />
            <Drawer
              title="Menu"
              placement="right"
              onClose={closeDrawer}
              open={drawerVisible}
              style={{ backgroundColor }}
              direction="vertical"
            >
              <Button onClick={toggleDayNightMode} style={{ backgroundColor, color: 'darkblue', borderColor: 'darkblue', marginBottom: '10px' }}>
                {isNightMode ? <SunOutlined /> : <MoonOutlined />} Mode
              </Button>
              <Radio.Group
                value={isGermanMode}
                onChange={e => setIsGermanMode(e.target.value === true || e.target.value === "true")}
                options={[{label: 'DE', value: true}, {label: 'FR', value: false}]}
                block
                optionType="button"
                buttonStyle="solid"
                style={{ backgroundColor, color: 'darkblue', borderColor: 'darkblue', marginBottom: '10px' }}
              />
            </Drawer>
            <div>
              <Card
                id='weather'
                style={{
                  position: 'absolute',
                  borderRadius: 0,
                  backgroundColor: 'grey',
                  paddingTop: '10px',
                  paddingLeft: '10px',
                  paddingRight: '10px',
                  paddingBottom: '10px',
                  marginBottom: '5px',
                  height: '91.5%',
                  width: '100%',
                  alignItems: 'center'
                }}>
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
                      opacity: '0.6',
                      borderRadius: '10px',
                      border: 'dashed',
                      borderColor: '#000000',
                      borderWidth: '2px',
                      boxSizing: 'border-box',
                      color: isNightMode ? '#FFFFFF' : '#000000'
                    }}
                  >
                    <p>{output}</p>
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
                    placeholder="Chat with rAIny..."
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