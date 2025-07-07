import { useLoginUserStore } from '@/store/useLoginUserStore';

/**
 * 检查用户是否已登录
 * @returns {Promise<boolean>} 返回用户是否已登录
 */
export const checkIsLoggedIn = async () => {
  const loginUserStore = useLoginUserStore();
  return await loginUserStore.checkLoginStatus();
}; 