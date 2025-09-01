import i18next from "i18next";
import type { i18n as i18nInstance } from "i18next"
import { initReactI18next } from "react-i18next";
import { languages } from "./i18n.constants";
import Backend from "i18next-http-backend";
// import LanguageDetector from "i18next-browser-languagedetector";

const createI18n = (language: string): i18nInstance => {
    const i18n = i18next.createInstance().use(initReactI18next);

    // TODO uncomment this line to enable language detection.
    // i18n.use(LanguageDetector)
    i18n.use(Backend) // Use assets plugin for translation file download.
        .init({
            backend: {
                loadPath: "/locales/{{lng}}/{{ns}}.json", // Specify where assets will find translation files.
            },
            lng: language,
            fallbackLng: language,
            ns: ["common", "errors", "pages"],
            defaultNS: "common",
            react: {
                useSuspense: false,
            },
        });

    return i18n as i18nInstance & { reportNamespaces: boolean };
};

export const i18n = createI18n(languages.zh);
