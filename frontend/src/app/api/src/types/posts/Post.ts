// Em algum lugar como src/types/post.ts

export enum PostTypeEnum {
  CAMPAIGN = 'campaign',
  COMPLAINT = 'complaint',
  POLL = 'poll',
  ANNOUNCEMENT = 'announcement',
}

export enum PostStatusEnum {
  ACTIVE = 'active',
  REPORTED = 'reported',
  SUSPENDED = 'suspended',
}

export interface PostCreatePayload {
  community_id: string; // UUID
  user_id: string;      // UUID
  type_post: PostTypeEnum;
  title: string;
  content: string;
  image_url?: string | null;
  status?: PostStatusEnum; // O backend tem um default, então pode ser opcional no payload inicial
}

export interface CommunityRelated {
  id: string; // UUID
  name: string;
}

export interface PostAuthor {
  id: string; // UUID
  name: string;
  username?: string; // Adicionando username para poder criar URLs amigáveis
  profile_picture?: string | null;
  role: string; // Você pode definir um Enum para CommunityMemberRoleEnum também
}

export interface PollOption {
  id: string; // UUID
  answer: string;
  votes_count: number;
}

export interface PostResponse {
  id: string; // UUID
  community: CommunityRelated;
  user: PostAuthor;
  type_post: PostTypeEnum;
  title: string;
  content: string;
  image_url?: string | null;
  status: PostStatusEnum;
  status_campaign?: string; // Status específico da campanha (approved, rejected, under_analysis, etc.)
  target_participants?: number; // Meta de participantes da campanha
  current_participants?: number; // Participantes atuais da campanha
  likes_count: number;
  comments_count: number;
  report_count: number;
  created_at: string; // ou Date, se você for converter
  updated_at: string; // ou Date
  level_complaint?: string; // Nível de denúncia vindo do backend (low, medium, high)
  status_complaint?: string; // Status da denúncia vindo do backend (pending, under_analysis, resolved, archived)
  poll_question?: string | null; // Apenas para posts do tipo poll
  poll_options?: PollOption[] | null; // Apenas para posts do tipo poll
}

// Você também definiria tipos para PollCreate, CampaignResponse, etc.
// Exemplo para PollOptionCreate e PollCreate
export interface PollOptionCreatePayload {
  text: string;
}

export interface PollCreatePayload {
  post: PostCreatePayload; // type_post aqui deve ser 'poll'
  options: PollOptionCreatePayload[];
}

// Defina os campos baseados no seu schema PollResponse do backend
// Ex: post: PostResponse; options: PollOptionResponse[]; etc.
export type PollResponse = object;

export interface PostsListFeed {
  current_limit: number;
  current_offset: number;
  has_more: boolean;
  items: PostResponse[];
  total: number;
}