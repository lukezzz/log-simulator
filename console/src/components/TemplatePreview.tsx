/**
 * Template Preview component that shows how a log template will look
 * when generated with sample data.
 */
import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Space, Alert, Spin } from 'antd';
import { PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface TemplatePreviewProps {
    template: string;
    deviceType?: string;
}

// Sample data generators that match the backend ECS placeholders
const SAMPLE_DATA: Record<string, () => string> = {
    // Network
    'source.ip': () => '192.168.1.100',
    'destination.ip': () => '10.0.0.50',
    'source.port': () => '8080',
    'destination.port': () => '443',
    'source.nat.ip': () => '192.168.1.1',
    'source.nat.port': () => '5432',
    'source.mac': () => 'a2:e9:00:ec:40:01',
    'network.transport': () => 'tcp',
    'network.service': () => 'HTTPS',
    'network.session_id': () => '1234567',

    // Event
    'event.created': () => String(Math.floor(Date.now() / 1000)),
    'event.id': () => '0000000013',
    'event.action': () => 'allow',
    'event.duration': () => '300',

    // Timestamp
    '@timestamp.date': () => new Date().toISOString().split('T')[0],
    '@timestamp.time': () => new Date().toISOString().split('T')[1].split('.')[0],

    // User
    'source.user.id': () => 'ae28f494-5735-51e9-f247-d1d2ce663f4b',
    'destination.user.id': () => 'be38f594-6845-52f9-g357-e2e3df774g5c',

    // Geographic
    'source.geo.country_name': () => 'Canada',
    'destination.geo.country_name': () => 'United States',

    // Service
    'service.id': () => '12345',
    'service.name': () => 'HTTP.BROWSER_Firefox',

    // Host
    'host.os.name': () => 'Ubuntu',

    // Traffic
    'source.bytes': () => '1024',
    'destination.bytes': () => '2048',
    'source.packets': () => '10',
    'destination.packets': () => '15',

    // Rules
    'rule.id': () => '100',
    'rule.uuid': () => 'ccb269e0-5735-51e9-a218-a397dd08b7eb',

    // Legacy placeholders for backward compatibility
    'srcip': () => '192.168.1.100',
    'dstip': () => '10.0.0.50',
    'srcport': () => '8080',
    'dstport': () => '443',
    'eventtime': () => String(Math.floor(Date.now() / 1000)),
    'date': () => new Date().toISOString().split('T')[0],
    'time': () => new Date().toISOString().split('T')[1].split('.')[0],
    'sessionid': () => '1234567',
    'proto': () => 'tcp',
    'action': () => 'allow',
    'policyid': () => '100',
    'transip': () => '192.168.1.1',
    'transport': () => '5432',
    'appid': () => '12345',
    'duration': () => '300',
    'sentbyte': () => '1024',
    'rcvdbyte': () => '2048',
    'sentpkt': () => '10',
    'rcvdpkt': () => '15',
};

export const TemplatePreview: React.FC<TemplatePreviewProps> = ({
    template,
    deviceType,
}) => {
    const [generatedLog, setGeneratedLog] = useState<string>('');
    const [isGenerating, setIsGenerating] = useState(false);

    const generatePreview = () => {
        if (!template.trim()) {
            setGeneratedLog('');
            return;
        }

        setIsGenerating(true);

        // Simulate some processing time
        setTimeout(() => {
            let result = template;

            // Replace ECS format placeholders {placeholder}
            result = result.replace(/\{([^}]+)\}/g, (match, placeholder) => {
                if (SAMPLE_DATA[placeholder]) {
                    return SAMPLE_DATA[placeholder]();
                }
                return match; // Return original if no generator found
            });

            // Replace legacy format placeholders <placeholder>
            result = result.replace(/<([^>]+)>/g, (match, placeholder) => {
                if (SAMPLE_DATA[placeholder]) {
                    return SAMPLE_DATA[placeholder]();
                }
                return match; // Return original if no generator found
            });

            setGeneratedLog(result);
            setIsGenerating(false);
        }, 500);
    };

    // Auto-generate preview when template changes
    useEffect(() => {
        const debounceTimer = setTimeout(() => {
            generatePreview();
        }, 1000);

        return () => clearTimeout(debounceTimer);
    }, [template]);

    const hasPlaceholders = /\{[^}]+\}|<[^>]+>/.test(template);

    return (
        <Card
            title={
                <Space>
                    <PlayCircleOutlined />
                    <span>Log Preview</span>
                    {deviceType && <Text type="secondary">({deviceType})</Text>}
                </Space>
            }
            extra={
                <Button
                    size="small"
                    icon={<ReloadOutlined />}
                    onClick={generatePreview}
                    loading={isGenerating}
                    disabled={!template.trim()}
                >
                    Regenerate
                </Button>
            }
            size="small"
        >
            {!template.trim() ? (
                <Alert
                    message="No template content"
                    description="Enter a template in the content format field to see a preview."
                    type="info"
                    showIcon
                />
            ) : !hasPlaceholders ? (
                <Alert
                    message="Static template"
                    description="This template contains no placeholders and will always generate the same output."
                    type="warning"
                    showIcon
                />
            ) : (
                <div>
                    <div style={{ marginBottom: 8 }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                            Sample generated log with random data:
                        </Text>
                    </div>
                    {isGenerating ? (
                        <div style={{ textAlign: 'center', padding: '20px' }}>
                            <Spin size="small" />
                            <div style={{ marginTop: 8 }}>
                                <Text type="secondary">Generating preview...</Text>
                            </div>
                        </div>
                    ) : (
                        <div style={{
                            backgroundColor: '#f5f5f5',
                            padding: '12px',
                            borderRadius: '4px',
                            fontFamily: 'monospace',
                            fontSize: '11px',
                            maxHeight: '150px',
                            overflow: 'auto',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-all',
                            border: '1px solid #d9d9d9'
                        }}>
                            {generatedLog || 'No preview available'}
                        </div>
                    )}
                </div>
            )}
        </Card>
    );
};