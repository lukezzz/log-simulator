/**
 * Template list component that displays all log templates in a table format using Antd.
 */
import React, { useState } from 'react';
import { Table, Button, Space, Tag, Popconfirm, message, Typography, Modal, Descriptions, Badge } from 'antd';
import { EditOutlined, CopyOutlined, DeleteOutlined, PlusOutlined, EyeOutlined } from '@ant-design/icons';
import {
    useGetTemplatesQuery,
    useDeleteTemplateMutation,
    useCloneTemplateMutation,
} from '@/services/template';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;

interface TemplateListProps {
    onEditTemplate?: (template: LogTemplate) => void;
    onCreateTemplate?: () => void;
}

export const TemplateList: React.FC<TemplateListProps> = ({
    onEditTemplate,
    onCreateTemplate,
}) => {
    const { data: templates, isLoading, error } = useGetTemplatesQuery({});
    const [deleteTemplate] = useDeleteTemplateMutation();
    const [cloneTemplate] = useCloneTemplateMutation();
    const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});
    const [selectedTemplate, setSelectedTemplate] = useState<LogTemplate | null>(null);

    const getPlaceholderInfo = (contentFormat: string) => {
        const ecsPlaceholders = (contentFormat.match(/\{[^}]+\}/g) || []).length;
        const legacyPlaceholders = (contentFormat.match(/<[^>]+>/g) || []).length;
        const hasECSFormat = ecsPlaceholders > 0;
        const hasLegacyFormat = legacyPlaceholders > 0;

        return { ecsPlaceholders, legacyPlaceholders, hasECSFormat, hasLegacyFormat };
    };

    const handleDelete = async (template: LogTemplate) => {
        try {
            setLoadingStates(prev => ({ ...prev, [`delete_${template.id}`]: true }));
            await deleteTemplate(template.id).unwrap();
            message.success('Template deleted successfully');
        } catch (error) {
            console.error('Failed to delete template:', error);
            message.error('Failed to delete template');
        } finally {
            setLoadingStates(prev => ({ ...prev, [`delete_${template.id}`]: false }));
        }
    };

    const handleClone = async (template: LogTemplate) => {
        try {
            setLoadingStates(prev => ({ ...prev, [`clone_${template.id}`]: true }));
            await cloneTemplate(template.id).unwrap();
            message.success('Template cloned successfully');
        } catch (error) {
            console.error('Failed to clone template:', error);
            message.error('Failed to clone template');
        } finally {
            setLoadingStates(prev => ({ ...prev, [`clone_${template.id}`]: false }));
        }
    };

    const handleEdit = (template: LogTemplate) => {
        onEditTemplate?.(template);
    };

    const columns: ColumnsType<LogTemplate> = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            render: (name: string) => <strong>{name}</strong>,
        },
        {
            title: 'Device Type',
            dataIndex: 'device_type',
            key: 'device_type',
        },
        // {
        //     title: 'Description',
        //     dataIndex: 'description',
        //     key: 'description',
        //     render: (description: string) => description || '-',
        //     ellipsis: true,
        // },
        {
            title: 'Format',
            dataIndex: 'content_format',
            key: 'format',
            render: (contentFormat: string) => {
                const { hasECSFormat, hasLegacyFormat, ecsPlaceholders, legacyPlaceholders } = getPlaceholderInfo(contentFormat);
                return (
                    <Space direction="vertical" size="small">
                        {hasECSFormat && (
                            <Tag color="green" style={{ margin: 0 }}>
                                ECS ({ecsPlaceholders} placeholders)
                            </Tag>
                        )}
                        {hasLegacyFormat && (
                            <Tag color="orange" style={{ margin: 0 }}>
                                Legacy ({legacyPlaceholders} placeholders)
                            </Tag>
                        )}
                        {!hasECSFormat && !hasLegacyFormat && (
                            <Tag color="default" style={{ margin: 0 }}>
                                Static
                            </Tag>
                        )}
                    </Space>
                );
            },
        },
        {
            title: 'Type',
            dataIndex: 'is_predefined',
            key: 'is_predefined',
            render: (isPredefined: boolean) => (
                <Tag color={isPredefined ? 'blue' : 'green'}>
                    {isPredefined ? 'System' : 'Custom'}
                </Tag>
            ),
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => new Date(date).toLocaleDateString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_: any, template: LogTemplate) => (
                <Space size="small">
                    <Button
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={() => setSelectedTemplate(template)}
                        title="View template details"
                    >
                        View
                    </Button>
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(template)}
                        disabled={template.is_predefined}
                        title={template.is_predefined ? 'Cannot edit predefined templates' : 'Edit template'}
                    >
                        Edit
                    </Button>
                    <Button
                        type="link"
                        icon={<CopyOutlined />}
                        onClick={() => handleClone(template)}
                        loading={loadingStates[`clone_${template.id}`]}
                    >
                        Clone
                    </Button>
                    <Popconfirm
                        title="Delete template"
                        description={`Are you sure you want to delete template "${template.name}"?`}
                        onConfirm={() => handleDelete(template)}
                        okText="Yes"
                        cancelText="No"
                        disabled={template.is_predefined}
                    >
                        <Button
                            type="link"
                            danger
                            icon={<DeleteOutlined />}
                            disabled={template.is_predefined}
                            loading={loadingStates[`delete_${template.id}`]}
                            title={template.is_predefined ? 'Cannot delete predefined templates' : 'Delete template'}
                        >
                            Delete
                        </Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    if (error) {
        return (
            <div style={{ padding: '24px', textAlign: 'center' }}>
                <Title level={4} type="danger">Error Loading Templates</Title>
                <p>Failed to load templates. Please try again.</p>
            </div>
        );
    }

    return (
        <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Title level={2}>Log Templates</Title>
                {onCreateTemplate && (
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={onCreateTemplate}
                    >
                        Create Template
                    </Button>
                )}
            </div>

            <Table
                dataSource={templates || []}
                columns={columns}
                loading={isLoading}
                rowKey="id"
                pagination={{ pageSize: 10, showSizeChanger: true }}
                locale={{
                    emptyText: 'No templates found',
                }}
            />

            <Modal
                title="Template Details"
                open={!!selectedTemplate}
                onCancel={() => setSelectedTemplate(null)}
                footer={[
                    <Button key="close" onClick={() => setSelectedTemplate(null)}>
                        Close
                    </Button>,
                    selectedTemplate && !selectedTemplate.is_predefined && (
                        <Button key="edit" type="primary" onClick={() => {
                            setSelectedTemplate(null);
                            handleEdit(selectedTemplate);
                        }}>
                            Edit Template
                        </Button>
                    ),
                ]}
                width={800}
            >
                {selectedTemplate && (
                    <Descriptions bordered column={1}>
                        <Descriptions.Item label="Name">
                            <strong>{selectedTemplate.name}</strong>
                        </Descriptions.Item>
                        <Descriptions.Item label="Device Type">
                            {selectedTemplate.device_type}
                        </Descriptions.Item>
                        <Descriptions.Item label="Description">
                            {selectedTemplate.description || 'No description provided'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Type">
                            <Tag color={selectedTemplate.is_predefined ? 'blue' : 'green'}>
                                {selectedTemplate.is_predefined ? 'System Template' : 'Custom Template'}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Placeholder Format">
                            {(() => {
                                const { hasECSFormat, hasLegacyFormat, ecsPlaceholders, legacyPlaceholders } = getPlaceholderInfo(selectedTemplate.content_format);
                                return (
                                    <Space>
                                        {hasECSFormat && (
                                            <Badge count={ecsPlaceholders} color="green" showZero>
                                                <Tag color="green">ECS Format</Tag>
                                            </Badge>
                                        )}
                                        {hasLegacyFormat && (
                                            <Badge count={legacyPlaceholders} color="orange" showZero>
                                                <Tag color="orange">Legacy Format</Tag>
                                            </Badge>
                                        )}
                                        {!hasECSFormat && !hasLegacyFormat && (
                                            <Tag color="default">Static Template</Tag>
                                        )}
                                    </Space>
                                );
                            })()}
                        </Descriptions.Item>
                        <Descriptions.Item label="Content Format">
                            <div style={{
                                backgroundColor: '#f5f5f5',
                                padding: '12px',
                                borderRadius: '4px',
                                fontFamily: 'monospace',
                                fontSize: '12px',
                                maxHeight: '200px',
                                overflow: 'auto',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-all'
                            }}>
                                {selectedTemplate.content_format}
                            </div>
                        </Descriptions.Item>
                        <Descriptions.Item label="Created">
                            {new Date(selectedTemplate.created_at).toLocaleString()}
                        </Descriptions.Item>
                        <Descriptions.Item label="Last Modified">
                            {new Date(selectedTemplate.updated_at).toLocaleString()}
                        </Descriptions.Item>
                    </Descriptions>
                )}
            </Modal>
        </div>
    );
};