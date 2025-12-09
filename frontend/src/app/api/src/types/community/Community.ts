export interface Community {
  id: string;
  name: string;
  description?: string;
  memberCount?: number;
  type_community:
    | "university"
    | "neighborhood"
    | "company"
    | "government"
    | "healthcare"
    | "religious"
    | "commercial"
    | "club";
  createdAt?: string;
  updatedAt?: string;
  imageUrl?: string;
}

export interface CommunityMembers {
  id: string;
  user_id: string;
  community_id: string;
  role: string;
  createdAt?: string;
}

export interface CommunityListCommunities {
  current_limit: number;
  current_offset: number;
  has_more: boolean;
  items: Community[];
  total: number;
}

export interface DeleteCommunity {
    community_id: string;
}

export interface GetCommunity{
    community_id: string;
}

export interface UpdateCommunity {
    community_id: string;
    name?: string;
    description?: string;
    type_community?: string;
    members?: string;
    admins?: string;
    updated_at?: string;
}