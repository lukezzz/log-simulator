/**
 * Templates page for managing log templates using Antd.
 */
import React, { useState } from 'react';
import { Button, Space } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { TemplateList } from '../components/TemplateList';
import { TemplateForm } from '../components/TemplateForm';
import type { LogTemplate } from '../types';

type ViewMode = 'list' | 'create' | 'edit';

export const Templates: React.FC = () => {
    const [viewMode, setViewMode] = useState<ViewMode>('list');
    const [selectedTemplate, setSelectedTemplate] = useState<LogTemplate | undefined>();

    const handleCreateTemplate = () => {
        setSelectedTemplate(undefined);
        setViewMode('create');
    };

    const handleEditTemplate = (template: LogTemplate) => {
        setSelectedTemplate(template);
        setViewMode('edit');
    };

    const handleFormSuccess = () => {
        setViewMode('list');
        setSelectedTemplate(undefined);
    };

    const handleFormCancel = () => {
        setViewMode('list');
        setSelectedTemplate(undefined);
    };

    return (
        <div style={{ minHeight: 'calc(100vh - 64px)', backgroundColor: '#f5f5f5' }}>
            {viewMode === 'list' ? (
                <TemplateList
                    onCreateTemplate={handleCreateTemplate}
                    onEditTemplate={handleEditTemplate}
                />
            ) : (
                <div style={{ padding: '24px' }}>
                    <Space style={{ marginBottom: '24px' }}>
                        <Button
                            icon={<ArrowLeftOutlined />}
                            onClick={handleFormCancel}
                        >
                            Back to Templates
                        </Button>
                    </Space>
                    <TemplateForm
                        template={selectedTemplate}
                        onCancel={handleFormCancel}
                        onSuccess={handleFormSuccess}
                    />
                </div>
            )}
        </div>
    );
};