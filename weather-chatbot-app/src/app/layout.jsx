import { ConfigProvider } from 'antd';
import 'antd/dist/reset.css';

export const metadata = {
  title: "rAIny - the weather chatbot",
  description: "The best weather chatbot app",
};

export default function RootLayout({ children }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ConfigProvider>{children}</ConfigProvider>
      </body>
    </html>
  );
}
