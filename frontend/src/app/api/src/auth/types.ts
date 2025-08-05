export interface User {
  name: string;
  username: string;
  profile_image_url: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
}