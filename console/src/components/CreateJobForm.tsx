/**
 * CreateJobForm component - modal/form for creating new jobs with template selection and destination input using Antd.
 */
import React from 'react';
import { Modal, Form, Select, Input, InputNumber, Button, message, DatePicker, Divider, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { useCreateJobMutation, useGetTemplatesQuery } from '../store/api';
import type { CreateJobFormData } from '../types';
import { ProtocolEnum } from '../types';

const { Text } = Typography;

interface CreateJobFormProps {
    isOpen: boolean;
    onClose: () => void;
}

export const CreateJobForm: React.FC<CreateJobFormProps> = ({ isOpen, onClose }) => {
    const [form] = Form.useForm();
    const [createJob, { isLoading: isCreating }] = useCreateJobMutation();
    const { data: templates = [], isLoading: templatesLoading } = useGetTemplatesQuery({});

    const handleSubmit = async (values: CreateJobFormData) => {
        try {
            // Convert date objects to ISO strings if they exist
            const jobData = {
                ...values,
                start_time: values.start_time ? new Date(values.start_time).toISOString() : undefined,
                end_time: values.end_time ? new Date(values.end_time).toISOString() : undefined,
            };

            await createJob(jobData).unwrap();
            message.success('Job created successfully');
            form.resetFields();
            onClose();
        } catch (error) {
            console.error('Failed to create job:', error);
            message.error('Failed to create job');
        }
    };

    const handleCancel = () => {
        form.resetFields();
        onClose();
    };

    return (
        <Modal
            title="Create New Job"
            open={isOpen}
            onCancel={handleCancel}
            footer={[
                <Button key="cancel" onClick={handleCancel}>
                    Cancel
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    loading={isCreating}
                    onClick={() => form.submit()}
                    icon={isCreating ? <LoadingOutlined /> : null}
                >
                    Create Job
                </Button>,
            ]}
            width={700}
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                    protocol: ProtocolEnum.TCP,
                    destination_port: 514,
                    send_interval_ms: 1000,
                }}
            >
                <Form.Item
                    label="Log Template"
                    name="template_id"
                    rules={[{ required: true, message: 'Please select a template' }]}
                >
                    <Select
                        placeholder={templatesLoading ? 'Loading templates...' : 'Select a template'}
                        loading={templatesLoading}
                        showSearch
                        optionFilterProp="children"
                        filterOption={(input, option) =>
                            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                        }
                        options={templates.map((template) => ({
                            value: template.id,
                            label: `${template.name} (${template.device_type})`,
                        }))}
                    />
                </Form.Item>

                <Form.Item
                    label="Protocol"
                    name="protocol"
                    rules={[{ required: true, message: 'Please select a protocol' }]}
                >
                    <Select>
                        <Select.Option value={ProtocolEnum.TCP}>TCP</Select.Option>
                        <Select.Option value={ProtocolEnum.UDP}>UDP</Select.Option>
                    </Select>
                </Form.Item>

                <Form.Item
                    label="Destination Host"
                    name="destination_host"
                    rules={[
                        { required: true, message: 'Destination host is required' },
                        { type: 'string', min: 1, message: 'Host cannot be empty' },
                    ]}
                >
                    <Input placeholder="e.g., 192.168.1.100 or log-server.example.com" />
                </Form.Item>

                <Form.Item
                    label="Destination Port"
                    name="destination_port"
                    rules={[
                        { required: true, message: 'Destination port is required' },
                        { type: 'number', min: 1, max: 65535, message: 'Port must be between 1 and 65535' },
                    ]}
                >
                    <InputNumber
                        style={{ width: '100%' }}
                        min={1}
                        max={65535}
                        placeholder="514"
                    />
                </Form.Item>

                <Divider orientation="left">
                    <Text type="secondary">Scheduling Options (Optional)</Text>
                </Divider>

                <Form.Item
                    label="Start Time"
                    name="start_time"
                    extra="When to start sending logs (leave empty to start immediately)"
                >
                    <DatePicker
                        showTime
                        style={{ width: '100%' }}
                        placeholder="Select start time"
                    />
                </Form.Item>

                <Form.Item
                    label="End Time"
                    name="end_time"
                    extra="When to stop sending logs (leave empty for no end time)"
                >
                    <DatePicker
                        showTime
                        style={{ width: '100%' }}
                        placeholder="Select end time"
                    />
                </Form.Item>

                <Form.Item
                    label="Total Logs to Send"
                    name="send_count"
                    extra="Total number of logs to send (leave empty for unlimited)"
                >
                    <InputNumber
                        style={{ width: '100%' }}
                        min={1}
                        placeholder="e.g., 100"
                    />
                </Form.Item>

                <Form.Item
                    label="Send Interval (milliseconds)"
                    name="send_interval_ms"
                    extra="Delay between each log sent"
                    rules={[
                        { type: 'number', min: 1, message: 'Interval must be at least 1ms' },
                    ]}
                >
                    <InputNumber
                        style={{ width: '100%' }}
                        min={1}
                        placeholder="1000"
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
};