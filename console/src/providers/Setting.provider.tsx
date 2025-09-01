/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { FC } from 'react'
import type { ThemeConfig } from 'antd/es/config-provider/context';
import enUS from 'antd/lib/locale/en_US';
import zhCN from 'antd/lib/locale/zh_CN';
import type { Locale } from 'antd/lib/locale';
import { SiteThemeComponentsToken, SiteThemeDefaultToken } from '@/data/SiteData';
import { useTranslation } from 'react-i18next';
import { notification } from 'antd';
import useCurrentConfig from '@/hooks/useCurrentConfig';

export type ThemeName = 'light' | 'dark' | 'compact';

interface ISettingsContext {
  sideMenuCollapsed: boolean;
  toggleSideMenuCollapsed?: (status: boolean) => any;
  themeName: ThemeName;
  setTheme: (name: ThemeName) => any;
  token: ThemeConfig['token'];
  componentsToken?: ThemeConfig['components'];
  currentLocale: Locale;
}

type Props = {
  children?: React.ReactNode;
};

export const SettingsContext = createContext<ISettingsContext>({
  sideMenuCollapsed: false,
  toggleSideMenuCollapsed: () => { },
  themeName: 'light',
  setTheme: () => { },
  token: SiteThemeDefaultToken,
  componentsToken: SiteThemeComponentsToken,
  currentLocale: enUS,
});


notification.config({
  placement: 'bottomRight',
  duration: 3,
  bottom: 50,
  maxCount: 1,
});

const SettingsProvider: FC<Props> = ({ children }) => {
  const currentConfig = useCurrentConfig();

  const [sideMenuCollapsed, setSideMenuCollapsed] = useState(false);
  const toggleSideMenuCollapsed = (status: boolean) => {
    setSideMenuCollapsed(status);
  };

  const [themeName, setThemeName] = useState<ThemeName>(
    currentConfig.theme ? currentConfig.theme : 'light',
  );
  const setTheme = (name: ThemeName) => {
    setThemeName(name);
  };

  const [token] = useState(SiteThemeDefaultToken);
  const [componentsToken] = useState(SiteThemeComponentsToken);

  const { i18n } = useTranslation();
  const setCurLanguage = useCallback(() => {
    switch (i18n.language) {
      case 'en':
        return enUS;

      default:
        return enUS;
    }
  }, [i18n.language]);

  const [currentLocale, setCurrentLocale] = useState(setCurLanguage);

  useEffect(() => {
    setCurrentLocale(setCurLanguage);
  }, [setCurLanguage]);


  return (
    <SettingsContext.Provider
      value={{
        sideMenuCollapsed,
        toggleSideMenuCollapsed,
        themeName,
        setTheme,
        token,
        componentsToken,
        currentLocale,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export default SettingsProvider;
