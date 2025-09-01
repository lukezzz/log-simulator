import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Result, Button } from 'antd';
import { Navigation } from './components';
import { Jobs } from './pages/Jobs';
import { Templates } from './pages/Templates';
import LogParserPage from './pages/LogParserPage';
import './App.css';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<Navigate to="/jobs" replace />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/tools/parser" element={<LogParserPage />} />
          <Route
            path="*"
            element={
              <Content style={{ padding: '50px', textAlign: 'center' }}>
                <Result
                  status="404"
                  title="404"
                  subTitle="Sorry, the page you visited does not exist."
                  extra={
                    <Button type="primary" onClick={() => window.location.href = '/jobs'}>
                      Back to Jobs
                    </Button>
                  }
                />
              </Content>
            }
          />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
