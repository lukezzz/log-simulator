import { ProLayout } from '@ant-design/pro-components';
import type { ProSettings } from '@ant-design/pro-components';
import { useContext, useEffect, useState } from 'react';
import { theme, ConfigProvider, App as AntdApp, Flex } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import useCurrentUser from '@/hooks/useCurrentUser';
// import { UserMenu } from '../menu/user';
import { SettingsContext } from '@/providers/Setting.provider';
import { ErrorBoundary } from '@ant-design/pro-components';
import { ThemeProvider } from 'antd-style';
import { useGetSelfQuery } from '@/services/auth';
import { LogoIcon } from './icon';
import { RoleEnum } from '@/data/SiteData';
import siteRoutes from '@/data/RouteData';
import { UserMenu } from './menu/user';
import { LogoutBtn } from './menu/logout';
import Loader from './loader';

const { useToken } = theme;

export const MainLayout = () => {
    const { token: siteToken, componentsToken, currentLocale } = useContext(SettingsContext);

    const [settings] = useState<Partial<ProSettings> | undefined>({
        layout: 'top',
    });

    const currentUser = useCurrentUser();

    const navigate = useNavigate();
    const location = useLocation();

    // console.log(location);

    const [pathname, setPathname] = useState(location.pathname || '/home');


    useEffect(() => {
        setPathname(location.pathname);
    }, [location.pathname]);

    const [collapsed, setCollapsed] = useState(false);

    const { token } = useToken();

    const checkAuth = useGetSelfQuery(void 0, {
        skip: currentUser.isAuthenticating || currentUser.isSessionTimeout,
    });

    useEffect(() => {
        checkAuth.refetch();
    }, []);

    // useEffect(() => {
    //   if (checkAuth.isError) {
    //     navigate('/login', {
    //       state: { from: location.pathname },
    //     });
    //   }
    // }, [currentUser]);

    useEffect(() => {
        if (currentUser.isSessionTimeout) {
            navigate('/login', {
                state: { from: location.pathname },
            });
        }
    }, [currentUser.isSessionTimeout, location.pathname, navigate]);


    if (currentUser.isAuthenticating || !currentUser.data) {
        return <Loader fullScreen spinning />;
    }

    // if no access_token or token expired, redirect to login page
    // if (!currentUser.access_token || currentUser.isSessionTimeout) {
    //   return (
    //     <Navigate
    //       to="/login"
    //       replace
    //       state={{
    //         from: location.pathname,
    //       }}
    //     />
    //   );
    // }

    return (
        <div
            id="MainLayout"
            style={{
                height: '100vh',
                overflow: 'auto',
            }}
        >
            <ConfigProvider
                theme={{
                    algorithm: theme.defaultAlgorithm,
                    token: siteToken,
                    components: componentsToken,
                }}
                locale={currentLocale}
            >
                <ErrorBoundary>
                    <ThemeProvider>
                        <AntdApp
                            notification={{
                                placement: 'bottomRight',
                                duration: 3,
                                bottom: 50,
                                maxCount: 1,
                            }}>
                            <ProLayout
                                title="UAR System"
                                menuHeaderRender={(logo, title) => (
                                    <Flex align="center" gap="middle">
                                        {logo}
                                        <div
                                            style={{
                                                fontSize: 14,
                                            }}
                                        >
                                            {title}
                                        </div>
                                    </Flex>
                                )}
                                logo={
                                    <LogoIcon
                                        style={{
                                            fontSize: 24,
                                            marginLeft: 4,
                                            marginRight: 4,
                                        }}
                                    />
                                }
                                token={{
                                    header: {
                                        heightLayoutHeader: 62,
                                        colorTextMenuActive: siteToken!.colorPrimaryActive,
                                        colorTextMenuSelected: siteToken!.colorPrimary,
                                        colorTextMenu: 'black',
                                    },
                                    pageContainer: {
                                        paddingBlockPageContainerContent: 12,
                                        paddingInlinePageContainerContent: 24,
                                    },
                                }}
                                route={siteRoutes}
                                collapsed={collapsed}
                                onCollapse={setCollapsed}
                                location={{
                                    pathname,
                                }}

                                actionsRender={() => (
                                    <Flex
                                        align='center' style={{
                                            marginRight: 20,
                                            height: '100%',
                                        }}
                                        gap="small"
                                    >
                                        <UserMenu />
                                        <LogoutBtn />
                                    </Flex>)}
                                menu={{
                                    defaultOpenAll: true,
                                }}
                                menuItemRender={(item, dom) => {
                                    const currentPath = pathname === '/' ? '/Home' : pathname;

                                    return (
                                        <div
                                            onClick={() => {
                                                setPathname(item.path || '/home');
                                                navigate(item.path as string, {
                                                    state: { from: pathname },
                                                });
                                            }}
                                            style={{
                                                fontSize: 16,
                                                fontWeight: 500,
                                                borderBottom: currentPath.startsWith(item.path || '/home')
                                                    ? `4px solid ${siteToken!.colorPrimary}`
                                                    : 'none',
                                            }}
                                        >
                                            {dom}
                                        </div>
                                    );
                                }}
                                menuDataRender={(menuData) => {
                                    menuData.map((item) => {
                                        if (item.authority && item.authority.length > 0) {
                                            // check current user role is in authority
                                            const checkRole = item.authority.some(
                                                (role: RoleEnum) => role === currentUser.data!.role.name,
                                            );
                                            if (!checkRole) {
                                                item.hideInMenu = true;
                                            }
                                        }
                                        return item;
                                    });
                                    return menuData;
                                }}
                                {...settings}
                            >
                                <Outlet />
                            </ProLayout>
                        </AntdApp>
                    </ThemeProvider>
                </ErrorBoundary>
            </ConfigProvider>
        </div>
    );
};
