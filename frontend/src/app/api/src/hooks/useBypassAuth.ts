export const useBypassAuth = () => {
  return process.env.NEXT_PUBLIC_BYPASS_AUTH === '1';
};