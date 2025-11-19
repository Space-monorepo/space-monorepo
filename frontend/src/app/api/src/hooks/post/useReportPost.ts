import axios from "axios";
import { API_URL } from "@/config";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { toast } from "react-toastify";

const useReportPost = () => {
    const reportPost = async (communityId: string, postId: string) => {
        try {
            const token = getTokenFromCookies();
            await axios.patch(
                `${API_URL}/posts/${communityId}/post/${postId}/report`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            toast.success('Post denunciado com sucesso!');
        } catch (err) {
            toast.error('Erro ao denunciar post');
            throw err;
        }
    };
    return { reportPost };
};

export default useReportPost;