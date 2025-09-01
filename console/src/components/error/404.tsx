import { Button, Result } from "antd"
import { StopOutlined } from "@ant-design/icons"

export const Error404: React.FC = () => {

    return (
        <Result
            status="error"
            title="404"
            subTitle="Sorry, the page you visited does not exist."
            icon={<StopOutlined />}
            extra={[
                <Button type="primary" key="home" onClick={() => window.location.href = "/Campaigns"}>
                    Go back to Campaigns
                </Button>,
            ]}
        />
    )
}