'use client';

import { useState } from 'react';
import { ConfigProvider, Button, Drawer } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { MenuOutlined, SunOutlined, MoonOutlined, SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import TextArea from 'antd/es/input/TextArea';

const Layout = ({ children }) => {
  const { backgroundColor, toggleDayNightMode, isNightMode, titleColor, sendButtonBackgroundColor } = useTheme();
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const maxLength = 100;

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

  const handleSend = (e) => {
    console.log('Sending:', inputValue);
    setInputValue('');
  }

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
            >
              <Button onClick={toggleDayNightMode} style={{ backgroundColor, color: 'darkblue', borderColor: 'darkblue', marginBottom: '10px' }}>
                {isNightMode ? <SunOutlined /> : <MoonOutlined />} Day/Night Mode
              </Button>
            </Drawer>
            <div style={{ flex: 1 }}>
              {children}
            </div>
            <div style={{
              position: 'fixed',
              bottom: 0,
              left: '50%',
              transform: 'translateX(-50%)',
              width: '100%',
              maxWidth: '600px',
              backgroundColor: backgroundColor,
              padding: '10px',
              boxSizing: 'border-box',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '10px',
              marginBottom: '15px',
            }}>
              <TextArea
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
              <Button type="primary" onClick={handleSend} style={{ marginLeft: '10px', backgroundColor: sendButtonBackgroundColor }}>
                <SendOutlined style={{ color: '#ffff' }} />
              </Button>
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