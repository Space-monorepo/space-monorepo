export interface ModeratePost {
    post_id: string;
    newStatus: "pending" | "approved" | "rejected" | "reported";
    community_id: string;
    }

export type PostStatus = "pending" | "approved" | "rejected" | "reported";

export interface ModeratePost {
    post_id: string;
    newStatus: PostStatus;
    community_id: string;
}

export interface ListPostUnderAnalisys {
    community_id: string;
    status_filter?: string;
}

export interface SuspendUser {
    user_id: string;
    community_id: string;
}

export interface UnsuspendUser {
    user_id: string;
    community_id: string;
}