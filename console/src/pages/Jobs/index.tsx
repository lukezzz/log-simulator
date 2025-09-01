/**
 * Jobs page to host the job list and creation form components using Antd Layout.
 */
import React, { useState } from 'react';
import { Layout, Typography, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { JobList } from './components/JobList';
import { CreateJobForm } from './components/CreateJobForm';

const { Content } = Layout;
const { Title, Paragraph } = Typography;

export const Jobs: React.FC = () => {
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);

    const handleOpenCreateForm = () => {
        setIsCreateFormOpen(true);
    };

    const handleCloseCreateForm = () => {
        setIsCreateFormOpen(false);
    };

    return (
        <Content style={{ padding: '24px', backgroundColor: '#f5f5f5', minHeight: 'calc(100vh - 64px)' }}>
            <div style={{ margin: '0 auto' }}>
                {/* Header */}
                <div style={{
                    marginBottom: '24px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    flexWrap: 'wrap',
                    gap: '16px'
                }}>
                    <div>
                        <Title level={2} style={{ margin: 0 }}>
                            Log Sending Jobs
                        </Title>
                        <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
                            Manage and monitor your log sending jobs. Create new jobs to start sending simulated logs
                            to specific destinations.
                        </Paragraph>
                    </div>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        size="large"
                        onClick={handleOpenCreateForm}
                    >
                        New Job
                    </Button>
                </div>

                {/* Main Content */}
                <div style={{
                    backgroundColor: '#fff',
                    borderRadius: '8px',
                    padding: '24px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
                }}>
                    <JobList />
                </div>

                {/* Create Job Form Modal */}
                <CreateJobForm
                    isOpen={isCreateFormOpen}
                    onClose={handleCloseCreateForm}
                />
            </div>
        </Content>
    );
};