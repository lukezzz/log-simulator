/**
 * Navigation component with links to different pages using Antd Layout.
 */
import { Layout, Menu, Typography } from 'antd';
import { FileTextOutlined, DatabaseOutlined, ToolOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Header } = Layout;
const { Title } = Typography;

export const Navigation = () => {
    const location = useLocation();

    const menuItems = [
        {
            key: '/jobs',
            icon: <FileTextOutlined />,
            label: <Link to="/jobs">Jobs</Link>,
        },
        {
            key: '/templates',
            icon: <DatabaseOutlined />,
            label: <Link to="/templates">Templates</Link>,
        },
        {
            key: '/tools/parser',
            icon: <ToolOutlined />,
            label: <Link to="/tools/parser">Log Parser</Link>,
        },
    ];

    return (
        <Header style={{ display: 'flex', alignItems: 'center', backgroundColor: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginRight: '24px' }}>
                <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff', marginRight: '8px' }} />
                <Title level={4} style={{ margin: 0, color: '#262626' }}>
                    Log Simulator
                </Title>
            </div>
            <Menu
                mode="horizontal"
                selectedKeys={[location.pathname]}
                items={menuItems}
                style={{ border: 'none', flex: 1 }}
            />
        </Header>
    );
};