'use client';

import { useState } from 'react';
import { ConfigProvider, Button, Drawer, Card, Radio, Select } from 'antd';
import 'antd/dist/reset.css';
import { ThemeProvider, useTheme } from './themeContext';
import { MenuOutlined, SunOutlined, MoonOutlined, SendOutlined } from '@ant-design/icons';
import Title from 'antd/es/typography/Title';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import TextArea from 'antd/es/input/TextArea';
import { Country, City } from 'country-state-city';

const Layout = ({ children }) => {
  const { backgroundColor, toggleDayNightMode, isNightMode, titleColor, sendButtonBackgroundColor, outputBackgroundColor} = useTheme();
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [isGermanMode, setIsGermanMode] = useState(true);
  const [inputValue, setInputValue] = useState('');
  const maxLength = 100;
  const languageMode = isGermanMode ? 'German' : 'French';
  const [output, setOutput] = useState("Hi! I'm rAIny, your friendly weather chatbot! Before we start, please select your preferred language and location in the menu on the top right corner. You can also toggle between day and night mode for a better experience.");
  const [selectedCountry, setSelectedCountry] = useState('LU');
  const [selectedCity, setSelectedCity] = useState('Luxembourg');
  const [weatherIcon, setWeatherIcon] = useState('lion');

  const countries = Country.getAllCountries()
    .map(country => ({ label: country.name, value: country.isoCode }));
  
  const cityList = City.getCitiesOfCountry(selectedCountry)
    .map(city => ({ label: city.name, value: city.name }));
  
  const handleCountryChange = (value) => {
    setSelectedCountry(value);
  };

  const handleCityChange = (value) => {
    setSelectedCity(value);
  };

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

  function getWeatherIconFromWeatherId(weatherId) {
    if (['1', '2', '3'].includes(String(weatherId))) return 'rain';
    if (['4', '5', '6'].includes(String(weatherId))) return 'sun';
    if (['7', '8', '9'].includes(String(weatherId))) return 'cloud';
    if (['10', '11', '12'].includes(String(weatherId))) return 'snow';
    return 'lion';
  }

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
          geolocation: selectedCity
        }),
      });

      const data = await response.json();
      const generatedText = data.response;
      const weatherId = data.weather_id;
      console.log('data:', data);

      setInputValue('');
      setOutput(generatedText);
      setWeatherIcon(getWeatherIconFromWeatherId(weatherId));
      console.log('Weather ID:', weatherId);
      
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
            <Title style={{ color: titleColor, fontFamily: 'Cherry Bomb, sans-serif', left: 1, marginLeft: '10px', marginTop:'10px' }}>rAIny</Title>
            <Button
              icon={<MenuOutlined />}
              onClick={showDrawer}
              style={{ position: 'absolute', right: 1, top: 1, marginRight: '15px', marginTop: '17px', backgroundColor: sendButtonBackgroundColor }}
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
              <Select
                value={selectedCountry}
                onChange={handleCountryChange}
                options={countries}
                style={{ width: '100%', marginBottom: '10px', backgroundColor, color: 'darkblue', borderColor: 'darkblue' }}
                placeholder="Select a country"
              />
              <Select
                value={selectedCity}
                onChange={handleCityChange}
                options={cityList}
                showSearch
                filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
                style={{ width: '100%', backgroundColor, color: 'darkblue', borderColor: 'darkblue' }}
                placeholder="Select a city"
              />
            </Drawer>
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
                  src="/lion2.png"
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
                    {weatherIcon === 'lion' && <span role="img" aria-label="lion" style={{ fontSize: 24 }}>🦁</span>}
                    {weatherIcon === 'sun' && <span role="img" aria-label="sun" style={{ fontSize: 24 }}>☀️</span>}
                    {weatherIcon === 'cloud' && <span role="img" aria-label="cloud" style={{ fontSize: 24 }}>☁️</span>}
                    {weatherIcon === 'rain' && <span role="img" aria-label="rain" style={{ fontSize: 24 }}>☔</span>}
                    {weatherIcon === 'snow' && <span role="img" aria-label="rain" style={{ fontSize: 24 }}>❄️</span>}
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