import React, { useState } from 'react';
import {
    Card,
    Form,
    Select,
    Input,
    Button,
    Typography,
    Space,
    Alert,
    Spin,
} from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import { useGetTemplatesQuery } from '@/services/template';
import { useParseLogMutation } from '@/services/tool';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const LogParserPage: React.FC = () => {
    const [form] = Form.useForm();
    const [selectedTemplate, setSelectedTemplate] = useState<LogTemplate | null>(null);
    const [templateContent, setTemplateContent] = useState<string>('');
    const [logMessage, setLogMessage] = useState<string>('');

    // API hooks
    const { data: templates = [], isLoading: templatesLoading } = useGetTemplatesQuery({});
    const [parseLog, { data: parseResult, isLoading: parseLoading, error: parseError }] = useParseLogMutation();

    const handleTemplateSelect = (templateId: string) => {
        const template = templates.find(t => t.id === templateId);
        if (template) {
            setSelectedTemplate(template);
            setTemplateContent(template.content_format);
            form.setFieldValue('templateContent', template.content_format);
        }
    };

    const handleParse = async () => {
        try {
            await form.validateFields();
            await parseLog({
                template_content_format: templateContent,
                log_message: logMessage,
            });
        } catch (error) {
            console.error('Validation failed:', error);
        }
    };

    const renderParseResult = () => {
        if (!parseResult) return null;

        return (
            <Card
                title="Parse Result"
                style={{ marginTop: 16 }}
                type="inner"
            >
                {parseResult.is_match ? (
                    <div>
                        <Alert
                            message="Successfully Parsed!"
                            type="success"
                            showIcon
                            style={{ marginBottom: 16 }}
                        />
                        <Text strong>Structured ECS Data:</Text>
                        <pre
                            style={{
                                background: '#f5f5f5',
                                padding: '12px',
                                borderRadius: '4px',
                                marginTop: '8px',
                                overflow: 'auto',
                                fontSize: '12px',
                                lineHeight: '1.4',
                            }}
                        >
                            {JSON.stringify(parseResult.parsed_ecs, null, 2)}
                        </pre>
                    </div>
                ) : (
                    <Alert
                        message="Parse Failed"
                        description={parseResult.error_message || 'Log message does not match the template pattern'}
                        type="error"
                        showIcon
                    />
                )}
            </Card>
        );
    };

    const renderErrorAlert = () => {
        if (!parseError) return null;

        const errorMessage = 'status' in parseError
            ? `API Error ${parseError.status}: ${JSON.stringify(parseError.data)}`
            : parseError.message || 'Unknown error occurred';

        return (
            <Alert
                message="Request Failed"
                description={errorMessage}
                type="error"
                showIcon
                style={{ marginTop: 16 }}
            />
        );
    };

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>Log Parser</Title>
            <Text type="secondary">
                Test a log template against a sample log message to see how it gets parsed into structured ECS format.
            </Text>

            <Card style={{ marginTop: 24 }}>
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleParse}
                >
                    <Form.Item
                        label="Select Template"
                        name="templateId"
                    >
                        <Select
                            placeholder="Choose an existing template"
                            loading={templatesLoading}
                            onSelect={handleTemplateSelect}
                            allowClear
                            showSearch
                            optionFilterProp="children"
                        >
                            {templates.map((template) => (
                                <Option key={template.id} value={template.id}>
                                    {template.name} ({template.device_type})
                                </Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        label="Template Content"
                        name="templateContent"
                        rules={[
                            { required: true, message: 'Template content is required' },
                        ]}
                    >
                        <TextArea
                            placeholder="Enter or edit template content (e.g., srcip={source.ip} dstip={dest.ip})"
                            rows={4}
                            value={templateContent}
                            onChange={(e) => setTemplateContent(e.target.value)}
                        />
                    </Form.Item>

                    <Form.Item
                        label="Sample Log Message"
                        name="logMessage"
                        rules={[
                            { required: true, message: 'Sample log message is required' },
                        ]}
                    >
                        <TextArea
                            placeholder="Enter the raw log message to test (e.g., srcip=1.2.3.4 dstip=5.6.7.8)"
                            rows={3}
                            value={logMessage}
                            onChange={(e) => setLogMessage(e.target.value)}
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            icon={<PlayCircleOutlined />}
                            loading={parseLoading}
                            size="large"
                        >
                            Parse Log
                        </Button>
                    </Form.Item>
                </Form>

                {parseLoading && (
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 8 }}>
                            <Text type="secondary">Parsing log message...</Text>
                        </div>
                    </div>
                )}

                {renderErrorAlert()}
                {renderParseResult()}
            </Card>

            {selectedTemplate && (
                <Card
                    title="Template Details"
                    style={{ marginTop: 16 }}
                    type="inner"
                    size="small"
                >
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div>
                            <Text strong>Name:</Text> {selectedTemplate.name}
                        </div>
                        <div>
                            <Text strong>Device Type:</Text> {selectedTemplate.device_type}
                        </div>
                        {selectedTemplate.description && (
                            <div>
                                <Text strong>Description:</Text> {selectedTemplate.description}
                            </div>
                        )}
                        <div>
                            <Text strong>Predefined:</Text> {selectedTemplate.is_predefined ? 'Yes' : 'No'}
                        </div>
                    </Space>
                </Card>
            )}
        </div>
    );
};

export default LogParserPage;