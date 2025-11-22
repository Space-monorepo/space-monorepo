import { API_URL } from '@/config';
import axios from 'axios';

export const updateCampaignStatus = async ({
    token,
    communityId,
    postId,
    status_campaign,
    subject,
    message,
}: {
    token: string;
    communityId: string;
    postId: string;
    status_campaign: 'approved' | 'rejected';
    subject: string;
    message: string;
}) => {
    const url = `${API_URL}/admin/${communityId}/post/${postId}/campaign`;
    const payload = {
        status_campaign,
        subject,
        message,
    };
    const response = await axios.patch(url, payload, {
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    return response.data;
};

export const updateCampaign = async ({
    token,
    communityId,
    postId,
    status_campaign,
}: {
    token: string;
    communityId: string;
    postId: string;
    status_campaign: 'in_progress' | 'canceled' | 'finished';
}) => {
    const url = `${API_URL}/admin/${communityId}/post/${postId}/campaign`;
    const payload = {
        status_campaign,
    };
    const response = await axios.patch(url, payload, {
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    return response.data;
};
