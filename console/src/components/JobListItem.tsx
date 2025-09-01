/**
 * JobListItem component for individual job actions with Start/Stop/Delete buttons using Antd.
 */
import React from 'react';
import { Button, Space, Popconfirm, message } from 'antd';
import { PlayCircleOutlined, StopOutlined, DeleteOutlined, LoadingOutlined } from '@ant-design/icons';
import { useStartJobMutation, useStopJobMutation, useDeleteJobMutation } from '../store/api';
import type { Job } from '../types';
import { JobStatusEnum } from '../types';

interface JobListItemProps {
    job: Job;
}

export const JobListItem: React.FC<JobListItemProps> = ({ job }) => {
    const [startJob, { isLoading: isStarting }] = useStartJobMutation();
    const [stopJob, { isLoading: isStopping }] = useStopJobMutation();
    const [deleteJob, { isLoading: isDeleting }] = useDeleteJobMutation();

    const handleStart = async () => {
        try {
            await startJob(job.id).unwrap();
            message.success('Job started successfully');
        } catch (error) {
            console.error('Failed to start job:', error);
            message.error('Failed to start job');
        }
    };

    const handleStop = async () => {
        try {
            await stopJob(job.id).unwrap();
            message.success('Job stopped successfully');
        } catch (error) {
            console.error('Failed to stop job:', error);
            message.error('Failed to stop job');
        }
    };

    const handleDelete = async () => {
        try {
            await deleteJob(job.id).unwrap();
            message.success('Job deleted successfully');
        } catch (error) {
            console.error('Failed to delete job:', error);
            message.error('Failed to delete job');
        }
    };

    const canStart = job.status === JobStatusEnum.IDLE || job.status === JobStatusEnum.STOPPED;
    const canStop = job.status === JobStatusEnum.RUNNING;

    return (
        <Space size="small">
            {canStart && (
                <Button
                    type="primary"
                    size="small"
                    icon={isStarting ? <LoadingOutlined /> : <PlayCircleOutlined />}
                    onClick={handleStart}
                    loading={isStarting}
                    style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                >
                    Start
                </Button>
            )}

            {canStop && (
                <Button
                    type="primary"
                    size="small"
                    icon={isStopping ? <LoadingOutlined /> : <StopOutlined />}
                    onClick={handleStop}
                    loading={isStopping}
                    danger
                >
                    Stop
                </Button>
            )}

            <Popconfirm
                title="Delete job"
                description="Are you sure you want to delete this job?"
                onConfirm={handleDelete}
                okText="Yes"
                cancelText="No"
                okButtonProps={{ danger: true }}
            >
                <Button
                    size="small"
                    icon={isDeleting ? <LoadingOutlined /> : <DeleteOutlined />}
                    loading={isDeleting}
                    danger
                    ghost
                >
                    Delete
                </Button>
            </Popconfirm>
        </Space>
    );
};