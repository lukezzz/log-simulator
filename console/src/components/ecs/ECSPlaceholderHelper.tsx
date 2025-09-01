/**
 * ECS Placeholder Helper component for showing available placeholders
 * and their descriptions for log template creation.
 */
import React, { useState } from 'react';
import { Card, Collapse, Typography, Tag, Button, Input, message, Space, Tooltip } from 'antd';
import { InfoCircleOutlined, CopyOutlined, SearchOutlined } from '@ant-design/icons';

const { Panel } = Collapse;
const { Text } = Typography;
const { Search } = Input;

interface PlaceholderInfo {
    placeholder: string;
    description: string;
    example: string;
    category: string;
}

const ECS_PLACEHOLDERS: PlaceholderInfo[] = [
    // Network and connection info
    { placeholder: '{source.ip}', description: 'Source IP address', example: '192.168.1.100', category: 'Network' },
    { placeholder: '{destination.ip}', description: 'Destination IP address', example: '10.0.0.50', category: 'Network' },
    { placeholder: '{source.port}', description: 'Source port number', example: '8080', category: 'Network' },
    { placeholder: '{destination.port}', description: 'Destination port number', example: '443', category: 'Network' },
    { placeholder: '{source.nat.ip}', description: 'Source NAT IP address', example: '192.168.1.1', category: 'Network' },
    { placeholder: '{source.nat.port}', description: 'Source NAT port number', example: '5432', category: 'Network' },
    { placeholder: '{source.mac}', description: 'Source MAC address', example: 'a2:e9:00:ec:40:01', category: 'Network' },
    { placeholder: '{network.transport}', description: 'Network transport protocol', example: 'tcp', category: 'Network' },
    { placeholder: '{network.service}', description: 'Network service name', example: 'HTTP', category: 'Network' },
    { placeholder: '{network.session_id}', description: 'Network session identifier', example: '1234567', category: 'Network' },

    // Event information
    { placeholder: '{event.created}', description: 'Event creation timestamp (Unix)', example: '1692900000', category: 'Event' },
    { placeholder: '{event.id}', description: 'Event identifier', example: '0000000013', category: 'Event' },
    { placeholder: '{event.action}', description: 'Event action taken', example: 'allow', category: 'Event' },
    { placeholder: '{event.duration}', description: 'Event duration in seconds', example: '300', category: 'Event' },

    // Timestamp fields
    { placeholder: '{@timestamp.date}', description: 'Current date', example: '2023-08-28', category: 'Timestamp' },
    { placeholder: '{@timestamp.time}', description: 'Current time', example: '14:30:15', category: 'Timestamp' },

    // User and authentication
    { placeholder: '{source.user.id}', description: 'Source user identifier', example: 'ae28f494-5735-51e9-f247-d1d2ce663f4b', category: 'User' },
    { placeholder: '{destination.user.id}', description: 'Destination user identifier', example: 'be38f594-6845-52f9-g357-e2e3df774g5c', category: 'User' },

    // Geographic info
    { placeholder: '{source.geo.country_name}', description: 'Source country name', example: 'Canada', category: 'Geographic' },
    { placeholder: '{destination.geo.country_name}', description: 'Destination country name', example: 'United States', category: 'Geographic' },

    // Service and application
    { placeholder: '{service.id}', description: 'Service identifier', example: '12345', category: 'Service' },
    { placeholder: '{service.name}', description: 'Service name', example: 'HTTP.BROWSER_Firefox', category: 'Service' },

    // Host information
    { placeholder: '{host.os.name}', description: 'Host operating system', example: 'Ubuntu', category: 'Host' },

    // Traffic metrics
    { placeholder: '{source.bytes}', description: 'Bytes sent from source', example: '1024', category: 'Traffic' },
    { placeholder: '{destination.bytes}', description: 'Bytes received at destination', example: '2048', category: 'Traffic' },
    { placeholder: '{source.packets}', description: 'Packets sent from source', example: '10', category: 'Traffic' },
    { placeholder: '{destination.packets}', description: 'Packets received at destination', example: '15', category: 'Traffic' },

    // Rules and policies
    { placeholder: '{rule.id}', description: 'Rule identifier', example: '100', category: 'Rule' },
    { placeholder: '{rule.uuid}', description: 'Rule UUID', example: 'ccb269e0-5735-51e9-a218-a397dd08b7eb', category: 'Rule' },
];

const CATEGORY_COLORS: Record<string, string> = {
    'Network': 'blue',
    'Event': 'green',
    'Timestamp': 'orange',
    'User': 'purple',
    'Geographic': 'cyan',
    'Service': 'geekblue',
    'Host': 'magenta',
    'Traffic': 'red',
    'Rule': 'volcano',
};

interface ECSPlaceholderHelperProps {
    onPlaceholderSelect?: (placeholder: string) => void;
}

export const ECSPlaceholderHelper: React.FC<ECSPlaceholderHelperProps> = ({
    onPlaceholderSelect,
}) => {
    const [searchTerm, setSearchTerm] = useState('');

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            message.success(`Copied "${text}" to clipboard`);
        } catch (error) {
            message.error('Failed to copy to clipboard');
        }
    };

    const handlePlaceholderClick = (placeholder: string) => {
        onPlaceholderSelect?.(placeholder);
        copyToClipboard(placeholder);
    };

    const filteredPlaceholders = ECS_PLACEHOLDERS.filter(item =>
        item.placeholder.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const groupedPlaceholders = filteredPlaceholders.reduce((acc, item) => {
        if (!acc[item.category]) {
            acc[item.category] = [];
        }
        acc[item.category].push(item);
        return acc;
    }, {} as Record<string, PlaceholderInfo[]>);

    return (
        <Card
            title={
                <Space>
                    <InfoCircleOutlined />
                    <span>ECS Placeholder Reference</span>
                </Space>
            }
            size="small"
        >
            <div style={{ marginBottom: 16 }}>
                <Text type="secondary">
                    Click on any placeholder to copy it to your clipboard. These placeholders follow the
                    Elastic Common Schema (ECS) format and will be replaced with realistic data when generating logs.
                </Text>
            </div>

            <Search
                placeholder="Search placeholders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ marginBottom: 16 }}
                prefix={<SearchOutlined />}
                allowClear
            />

            <Collapse size="small" ghost>
                {Object.entries(groupedPlaceholders).map(([category, placeholders]) => (
                    <Panel
                        header={
                            <Space>
                                <Tag color={CATEGORY_COLORS[category]}>{category}</Tag>
                                <Text type="secondary">({placeholders.length} placeholders)</Text>
                            </Space>
                        }
                        key={category}
                    >
                        <div style={{ display: 'grid', gap: 8 }}>
                            {placeholders.map((item) => (
                                <div
                                    key={item.placeholder}
                                    style={{
                                        padding: 8,
                                        border: '1px solid #f0f0f0',
                                        borderRadius: 4,
                                        backgroundColor: '#fafafa'
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                        <Text code style={{ fontSize: '12px', fontWeight: 'bold' }}>
                                            {item.placeholder}
                                        </Text>
                                        <Tooltip title="Click to copy">
                                            <Button
                                                type="text"
                                                size="small"
                                                icon={<CopyOutlined />}
                                                onClick={() => handlePlaceholderClick(item.placeholder)}
                                            />
                                        </Tooltip>
                                    </div>
                                    <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: 4 }}>
                                        {item.description}
                                    </Text>
                                    <Text type="secondary" style={{ fontSize: '11px', fontStyle: 'italic' }}>
                                        Example: {item.example}
                                    </Text>
                                </div>
                            ))}
                        </div>
                    </Panel>
                ))}
            </Collapse>

            <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 4 }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                    <strong>Note:</strong> Legacy placeholders like <Text code>{'<srcip>'}</Text> are still supported for backward compatibility,
                    but we recommend using the new ECS format for consistency and better integration.
                </Text>
            </div>
        </Card>
    );
};