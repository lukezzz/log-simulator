import { useState, useEffect, useContext } from 'react';
import { Layout, Button, Form, Input, Row, Col, Flex, Tooltip, message } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { ConfigProvider, theme as antdTheme } from 'antd';


import { useAppDispatch } from '@/redux/hooks';
import { useGetSelfQuery, useGetSSOUrlMutation, useLoginMutation } from '@/services/auth';
import { SiteDefaultData } from '@/data/SiteData';
// import zhCN from 'antd/locale/zh_CN';
import useCurrentUser from '@/hooks/useCurrentUser';
import { SettingsContext } from '@/providers/Setting.provider';
import { LogoIcon } from '@/components/icon';
import { setToken } from '@/redux/reducers/userSlice';
import { useLocation, useNavigate } from 'react-router-dom';

type LoginProps = {
  username: string;
  password: string;
  remember: string;
};

const { Header } = Layout;

export const AdminLoginForm = () => {

  const [messageApi, contextHolder] = message.useMessage();

  const { token, componentsToken } = useContext(SettingsContext);





  const queryParameters = new URLSearchParams(window.location.search)
  const access_token = queryParameters.get('access_token')
  const refresh_token = queryParameters.get('refresh_token')
  const server_error = queryParameters.get('error')

  const currentUser = useCurrentUser();
  const [tipOpen, setTipOpen] = useState(false);

  const checkAuth = useGetSelfQuery();

  const tipCountDown = () => {
    let secondsToGo = 5;

    const timer = setInterval(() => {
      secondsToGo -= 1;
      setTipOpen(true);
    }, 1000);

    setTimeout(() => {
      clearInterval(timer);
      setTipOpen(false);
    }, secondsToGo * 1000);
  };

  const dispatch = useAppDispatch();
  const [login, loginResult] = useLoginMutation();

  const navigate = useNavigate();
  const location = useLocation()

  const handleSubmit = async (values: LoginProps) => {
    const formData = new FormData();
    formData.append('username', values.username);
    formData.append('password', values.password);
    // formData.append('remember', values.remember);
    login(formData);
  };



  useEffect(() => {
    if (loginResult.isSuccess && loginResult.data) {

      console.log("login success")
      checkAuth.refetch();

    }
    if (loginResult.isError) {
      tipCountDown();
    }
  }, [loginResult]);

  useEffect(() => {
    if (currentUser.access_token) {
      if (location.pathname === '/login') {
        navigate(location.state?.from || '/Home');
      } else {
        navigate(location.pathname || '/Home');
      }
    }
  }, [currentUser])



  // sso
  const [getLoginURL, getLoginURLResult] = useGetSSOUrlMutation();

  useEffect(() => {
    if (getLoginURLResult.isSuccess) {
      window.location.replace(getLoginURLResult.data.data);
    } else if (getLoginURLResult.isError) {
      if ('message' in getLoginURLResult.error) {
        // TODO put error message in content
        // message.error(getLoginURLResult.error.message);
      }
    }
  }, [getLoginURLResult]);

  const ssoLogin = () => {
    getLoginURL({
      redirectUrl: btoa(window.location.href),
    });
  };


  if (access_token && refresh_token) {
    // remove the token from the url
    window.history.replaceState({}, document.title, window.location.pathname);
    dispatch(
      setToken({
        access_token: access_token,
        refresh_token: refresh_token,
      })
    );
  }

  useEffect(() => {
    if (server_error) {
      console.error(server_error)
      messageApi.open({
        type: 'error',
        content: "Authentication service error, please contact administrator",
        duration: 5
      });
    }
  }, [server_error])


  return (
    <ConfigProvider
      theme={{
        algorithm: antdTheme.defaultAlgorithm,
        token: token,
        components: componentsToken,
      }}
    // locale={zhCN}
    >
      {contextHolder}
      <Layout
        style={{
          margin: 0,
          padding: 0,
          height: '100vh',
          width: '100vw',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <Header
          style={{
            position: 'absolute',
            top: 0,
            width: '100%',
            zIndex: 100,
            backgroundColor: 'transparent',
            paddingLeft: 15,
          }}
        >
          <LogoIcon
            style={{
              fontSize: 40,
              marginRight: 10,
              marginTop: 10,
            }}
          />
        </Header>
        <div
          style={{
            margin: 0,
            width: '100%',
            position: 'absolute',
            top: '50%',
            msTransform: 'translateY(-65%)',
            transform: 'translateY(-65%)',
          }}
        >
          <Row justify="center" align="middle" gutter={[24, 24]}>
            <Col
              span={24}
              style={{
                textAlign: 'center',
              }}
            >
              <Flex gap="small" align="center" justify="center">
                <span
                  style={{
                    fontSize: 24,
                    fontWeight: 600,
                  }}
                >
                  {SiteDefaultData.siteName.toUpperCase()}
                </span>
              </Flex>
            </Col>
            <Col span={24}>
              <Form
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 24 }}
                layout="vertical"
                onFinish={handleSubmit}
                autoComplete="off"
                style={{
                  margin: '0 auto',
                  maxWidth: 350,
                }}
              >
                <Form.Item
                  name="username"
                  label="Username"
                  rules={[
                    {
                      required: true,
                      // message: t("rule.inputRequired", { ns: namespaces.errors, field: t('login.username') }),
                    },
                  ]}
                >
                  <Input
                    prefix={<UserOutlined className={'prefixIcon'} />}
                    // placeholder={t("login.username")}
                    size="large"
                    autoComplete="off"
                  />
                </Form.Item>

                <Form.Item
                  name="password"
                  label="Password"
                  rules={[
                    {
                      required: true,
                      // message: t("rule.inputRequired", { ns: namespaces.errors, field: t('login.password') }),
                    },
                  ]}
                >
                  <Input.Password
                    size="large"
                    prefix={<LockOutlined className={'prefixIcon'}
                      autoComplete="off"
                    />}
                  // placeholder="Your login password"
                  />
                </Form.Item>

                {/* <Form.Item name="remember" valuePropName="checked">
                  <Checkbox onChange={onChangeRemember}>Remember Me</Checkbox>
                </Form.Item> */}

                <Form.Item wrapperCol={{ span: 24 }}>
                  <Flex gap="small">
                    <Button htmlType="submit" loading={loginResult.isLoading} block>
                      Login
                    </Button>
                    <Tooltip
                      title="Try Single Sign On"
                      placement="bottom"
                      open={tipOpen}
                      color="red"
                    >
                      <Button style={{
                        backgroundColor: '#000',
                        color: '#fff',

                      }}
                        loading={getLoginURLResult.isLoading}
                        onClick={ssoLogin}
                        disabled
                        block>
                        SSO
                      </Button>
                    </Tooltip>
                  </Flex>
                </Form.Item>
              </Form>
            </Col>
            <Col>{SiteDefaultData.version}</Col>
          </Row>
        </div>

        {/* <MainFooter /> */}
      </Layout>
    </ConfigProvider>
  );
};
