import { CloseCircleOutlined } from '@ant-design/icons';
import { Button, Result, Typography } from 'antd';
import { Component, ErrorInfo, ReactNode } from 'react';

const { Paragraph, Text } = Typography;

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
}

const ErrorFallback = () => {
  return (
    <Result
      status="error"
      title="Submission Failed"
      subTitle="Please check and modify the following information before resubmitting."
      extra={[
        <Button type="primary" key="console">
          Go Console
        </Button>,
      ]}
    >
      <div className="desc">
        <Paragraph>
          <Text
            strong
            style={{
              fontSize: 16,
            }}
          >
            The content you submitted has the following error:
          </Text>
        </Paragraph>
        <Paragraph>
          <CloseCircleOutlined style={{ color: 'red' }} />
          {/* {error.message} */}
        </Paragraph>
        <Paragraph>
          <CloseCircleOutlined style={{ color: 'red' }} />
          {/* {componentStack} */}
        </Paragraph>
      </div>
    </Result>
  );
};

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  public static getDerivedStateFromError(_: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
