/**
 * Template form component for creating and editing log templates using Antd.
 */
import React, { useEffect, useRef } from 'react';
import { Form, Input, Button, Card, message, Row, Col } from 'antd';
import {
    useCreateTemplateMutation,
    useUpdateTemplateMutation,
} from '@/services/template';
import { TemplatePreview } from './TemplatePreview';
import { ECSPlaceholderHelper } from '@/components/ecs/ECSPlaceholderHelper';

const { TextArea } = Input;

interface TemplateFormProps {
    template?: LogTemplate;
    onCancel: () => void;
    onSuccess: () => void;
}

interface TemplateFormData {
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
}

export const TemplateForm: React.FC<TemplateFormProps> = ({
    template,
    onCancel,
    onSuccess,
}) => {
    const [form] = Form.useForm();
    const contentFormatRef = useRef<any>(null);
    const [formValues, setFormValues] = React.useState<TemplateFormData>({
        name: '',
        device_type: '',
        content_format: '',
        description: '',
    });
    const isEditing = !!template;
    const [createTemplate, { isLoading: isCreating }] = useCreateTemplateMutation();
    const [updateTemplate, { isLoading: isUpdating }] = useUpdateTemplateMutation();

    // Populate form when editing
    useEffect(() => {
        if (template) {
            const values = {
                name: template.name,
                device_type: template.device_type,
                content_format: template.content_format,
                description: template.description || '',
            };
            form.setFieldsValue(values);
            setFormValues(values);
        }
    }, [template, form]);

    const handleFormChange = () => {
        const currentValues = form.getFieldsValue();
        setFormValues(currentValues);
    };

    const handleSubmit = async (values: TemplateFormData) => {
        try {
            if (isEditing && template) {
                await updateTemplate({
                    templateId: template.id,
                    templateData: {
                        name: values.name,
                        device_type: values.device_type,
                        content_format: values.content_format,
                        description: values.description || undefined,
                    },
                }).unwrap();
                message.success('Template updated successfully');
            } else {
                await createTemplate({
                    name: values.name,
                    device_type: values.device_type,
                    content_format: values.content_format,
                    description: values.description || undefined,
                    is_predefined: false,
                }).unwrap();
                message.success('Template created successfully');
            }
            form.resetFields();
            onSuccess();
        } catch (error) {
            console.error('Failed to save template:', error);
            message.error('Failed to save template');
        }
    };

    const handlePlaceholderSelect = (placeholder: string) => {
        const currentValue = form.getFieldValue('content_format') || '';
        const newValue = currentValue + placeholder;
        form.setFieldValue('content_format', newValue);

        // Focus the textarea and set cursor position after the inserted placeholder
        if (contentFormatRef.current?.resizableTextArea?.textArea) {
            const textarea = contentFormatRef.current.resizableTextArea.textArea;
            setTimeout(() => {
                textarea.focus();
                textarea.setSelectionRange(newValue.length, newValue.length);
            }, 10);
        }
    };

    const isLoading = isCreating || isUpdating;

    return (
        <Row gutter={24}>
            <Col span={10}>
                <Card
                    title={isEditing ? 'Edit Template' : 'Create New Template'}
                    style={{ height: 'fit-content', marginBottom: 16 }}
                >
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleSubmit}
                        onValuesChange={handleFormChange}
                        requiredMark={false}
                    >
                        <Form.Item
                            label="Name"
                            name="name"
                            rules={[
                                { required: true, message: 'Please enter a template name' },
                                { max: 255, message: 'Name must be less than 255 characters' },
                            ]}
                        >
                            <Input placeholder="e.g., Custom FortiGate Template" />
                        </Form.Item>

                        <Form.Item
                            label="Device Type"
                            name="device_type"
                            rules={[
                                { required: true, message: 'Please enter a device type' },
                                { max: 100, message: 'Device type must be less than 100 characters' },
                            ]}
                        >
                            <Input placeholder="e.g., FortiGate, Cisco ASA, Palo Alto" />
                        </Form.Item>

                        <Form.Item
                            label="Description"
                            name="description"
                            extra="Optional description for this template"
                        >
                            <TextArea
                                rows={3}
                                placeholder="Optional description for this template"
                            />
                        </Form.Item>

                        <Form.Item
                            label="Content Format"
                            name="content_format"
                            rules={[
                                { required: true, message: 'Please enter the content format' },
                            ]}
                            extra="Use ECS format placeholders like {source.ip}, {destination.port}, {@timestamp.date}, etc. Click on placeholders in the helper panel to insert them."
                        >
                            <TextArea
                                ref={contentFormatRef}
                                rows={8}
                                placeholder="Log format template with ECS placeholder variables like {source.ip}, {event.action}, {@timestamp.date}, etc."
                                style={{ fontFamily: 'monospace', fontSize: '12px' }}
                            />
                        </Form.Item>

                        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                            <Button
                                onClick={onCancel}
                                disabled={isLoading}
                                style={{ marginRight: 8 }}
                            >
                                Cancel
                            </Button>
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={isLoading}
                            >
                                {isEditing ? 'Update Template' : 'Create Template'}
                            </Button>
                        </Form.Item>
                    </Form>
                </Card>
                <TemplatePreview
                    template={formValues.content_format || ''}
                    deviceType={formValues.device_type}
                />
            </Col>
            <Col span={14}>
                <ECSPlaceholderHelper onPlaceholderSelect={handlePlaceholderSelect} />
            </Col>
        </Row>
    );
};