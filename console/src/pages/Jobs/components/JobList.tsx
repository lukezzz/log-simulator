/**
 * JobList component for displaying jobs in a table with status and action buttons using Antd.
 */
import React from 'react';
import { Table, Alert, Spin, Empty, Tag, Typography } from 'antd';
import { SyncOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { JobListItem } from './JobListItem';
import { useGetJobsQuery } from '@/services/job';
import { JobStatusEnum } from '@/types';

const { Text } = Typography;

export const JobList: React.FC = () => {
    const {
        data: jobs = [],
        error,
        isLoading,
        refetch,
    } = useGetJobsQuery({});

    if (isLoading) {
        return (
            <div style={{ textAlign: 'center', padding: '48px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>
                    <Text type="secondary">Loading jobs...</Text>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <Alert
                message="Error loading jobs"
                description="Failed to fetch jobs from the server."
                type="error"
                showIcon
                icon={<ExclamationCircleOutlined />}
                action={
                    <button onClick={() => refetch()}>
                        Try again
                    </button>
                }
                style={{ marginBottom: '24px' }}
            />
        );
    }

    if (jobs.length === 0) {
        return (
            <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                    <span>
                        No jobs found
                        <br />
                        <Text type="secondary">Get started by creating a new log sending job.</Text>
                    </span>
                }
            />
        );
    }

    const getStatusTag = (status: string) => {
        switch (status) {
            case JobStatusEnum.IDLE:
                return <Tag color="default">IDLE</Tag>;
            case JobStatusEnum.RUNNING:
                return <Tag color="success" icon={<SyncOutlined spin />}>RUNNING</Tag>;
            case JobStatusEnum.STOPPED:
                return <Tag color="warning">STOPPED</Tag>;
            case JobStatusEnum.ERROR:
                return <Tag color="error">ERROR</Tag>;
            default:
                return <Tag color="default">{status}</Tag>;
        }
    };

    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            render: (id: string) => (
                <Text>{id.slice(0, 8)}...</Text>
            ),
            width: 120,
        },
        {
            title: 'Destination',
            key: 'destination',
            render: (record: Job) => (
                <div>
                    <div>{record.destination_host}</div>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        Port: {record.destination_port}
                    </Text>
                </div>
            ),
        },
        {
            title: 'Protocol',
            dataIndex: 'protocol',
            key: 'protocol',
            render: (protocol: string) => (
                <Tag color="blue">{protocol}</Tag>
            ),
            width: 100,
        },
        {
            title: 'Scheduling',
            key: 'scheduling',
            render: (record: Job) => {
                const hasScheduling = record.start_time || record.end_time || record.send_count || record.send_interval_ms;
                if (!hasScheduling) {
                    return <Text type="secondary">-</Text>;
                }

                const scheduleInfo: string[] = [];
                if (record.start_time) {
                    scheduleInfo.push(`Start: ${new Date(record.start_time).toLocaleString()}`);
                }
                if (record.end_time) {
                    scheduleInfo.push(`End: ${new Date(record.end_time).toLocaleString()}`);
                }
                if (record.send_count) {
                    scheduleInfo.push(`Count: ${record.send_count}`);
                }
                if (record.send_interval_ms && record.send_interval_ms !== 1000) {
                    scheduleInfo.push(`Interval: ${record.send_interval_ms}ms`);
                }

                return (
                    <div style={{ fontSize: '12px' }}>
                        {scheduleInfo.map((info, index) => (
                            <div key={index}>
                                <Text type="secondary">{info}</Text>
                            </div>
                        ))}
                    </div>
                );
            },
            width: 250,
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => getStatusTag(status),
            width: 120,
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => (
                <Text type="secondary">
                    {new Date(date).toLocaleString()}
                </Text>
            ),
            width: 180,
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (record: Job) => <JobListItem job={record} />,
            width: 200,
        },
    ];

    return (
        <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) =>
                    `${range[0]}-${range[1]} of ${total} jobs`,
            }}
            bordered
        />
    );
};