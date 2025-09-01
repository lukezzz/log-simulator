import { useAppSelector } from "@/redux/hooks"
import { selectConfig } from "@/redux/reducers/configSlice"

const useCurrentConfig = () => {
    return useAppSelector(selectConfig)
}

export default useCurrentConfig