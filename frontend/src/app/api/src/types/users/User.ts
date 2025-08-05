export interface User {
  username: string;
  name: string;
  email: string;
  created_at: string;
  bio?: string;
  reputation_level?: string;
  popularity?: number;
  profile_image_url?: string;
}

export interface UpdateUser {
    email?: string;
    name?: string;
    hashed_password?: string;
    profile_image_url?: string;
    reputation_level?: string;
    status?: string;
}

export interface Signup{
    email: string;
    name: string;
    hashed_password: string;
    profile_image_url?: string;
    reputation_level?: string;
    status?: string;
}

export interface Login {
    grant_type?: string;
    username: string;
    password: string;
    scope?: string;
    client_id?: string;
    client_secret?: string;
}

export interface GetUserByEmail {
    email: string;
}