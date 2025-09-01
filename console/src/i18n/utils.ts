import { i18n } from './i18n'

type OptionsType = {
    value: number;
    label: string;
    locale: string;
}[]

export const i18nSelectOption = (options: OptionsType) => {
    const optionList = options
    optionList.map(item => item.label = i18n.t(`${item.locale}`, { ns: "common" }))
    return optionList
}