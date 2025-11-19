import { API_URL } from '@/config';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

export async function fetchUserCampaigns() {
    const token = getTokenFromCookies();
    if (!token) return [];
    const res = await fetch(`${API_URL}/posts/post/list-user-campaigns`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });
    if (!res.ok) return [];
    const data = await res.json();
    // data.items deve ser array de campanhas
    return data.items || [];
}
