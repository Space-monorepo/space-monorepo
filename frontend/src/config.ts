export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const CLOUD_NAME = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
export const UPLOAD_PRESET = process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET;
export const API_KEY = process.env.NEXT_PUBLIC_CLOUDINARY_API_KEY;
export const CLOUDINARY_URL = process.env.CLOUDINARY_URL;
export const cloudinary_link = process.env.NEXT_PUBLIC_cloudinary_link;

const inferWebSocketBaseUrl = () => {
  if (!API_URL) {
    return "";
  }

  if (API_URL.startsWith("https://")) {
    return `wss://${API_URL.slice("https://".length)}`;
  }

  if (API_URL.startsWith("http://")) {
    return `ws://${API_URL.slice("http://".length)}`;
  }

  return API_URL;
};

export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || inferWebSocketBaseUrl();
