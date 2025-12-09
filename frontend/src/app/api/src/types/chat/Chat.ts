export interface Chat {
    id: string;
    community_id: string;
    user_id: string;
    message: string;
    created_at: string;
    updated_at?: string;
}

export interface SendMessage {
    content: string;
    receiver_id: string;
}
export interface DeleteMessage {
    message_id: string;
}

export interface GetConversation {
    user_id: string;
}

export interface GetMessage {
    message_id: string;
}

export interface MarkAsRead {
    message_id: string;
}