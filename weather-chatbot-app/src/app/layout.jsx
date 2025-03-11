'use client';

import { useState } from 'react';
import { ConfigProvider, Button, Drawer, Input } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { MenuOutlined, SunOutlined, MoonOutlined, SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { Helmet } from 'react-helmet';

const Layout = ({ children }) => {
  const { backgroundColor, toggleDayNightMode, isNightMode, titleColor } = useTheme();
  const [drawerVisible, setDrawerVisible] = useState(false);

  const showDrawer = () => {
    setDrawerVisible(true);
  };

  const closeDrawer = () => {
    setDrawerVisible(false);
  };

  return (
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
            style={{backgroundColor}}
          >
            <Button onClick={toggleDayNightMode} style={{ backgroundColor, color:'darkblue', borderColor:'darkblue', marginBottom: '10px' }}>
              {isNightMode ? <SunOutlined /> : <MoonOutlined />} Day/Night Mode
            </Button>
          </Drawer>
          {children}
          <Input
            placeholder="Chat with rAIny..."
            addonAfter={
              <Button type='primary' icon={ <SendOutlined /> }/>
            }
            style={{ 
              position: 'fixed',
              bottom: 0,
              left: '50%',
              transform: 'translateX(-50%)',
              width: '97%',
              backgroundColor: backgroundColor,
              color: isNightMode ? '#FFFFFF' : '#000000',
              placeholderColor: isNightMode ? '#FFFFFF' : '#000000',
              padding: '10px',
              boxSizing: 'border-box',
              border: 'solid 1px',
              opacity:"70%",
              borderRadius: '10px',
              marginBottom: '15px'
            }}
            count={{ show: true, max: 100 }}
            autosize={{ minRows: 1, maxRows: 3 }}
          />
        </ConfigProvider>
      </body>
    </html>
  );
};

export default function RootLayout({ children }) {
  return (
    <ThemeProvider>
      <Layout>{children}</Layout>
    </ThemeProvider>
  );
}