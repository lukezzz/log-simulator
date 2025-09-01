import { useAppSelector } from "@/redux/hooks"
import { selectUser } from "@/redux/reducers/userSlice"

const useCurrentUser = () => {
    return useAppSelector(selectUser)
}

export default useCurrentUser