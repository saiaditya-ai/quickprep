import { getAuth0Instance } from '../auth/authProvider';

/**
 * Get Auth0 access token for API calls
 * @returns {Promise<string|null>} Access token or null if not available
 */
export const getAuth0Token = async () => {
  try {
    const auth0 = getAuth0Instance();
    if (!auth0) {
      console.warn('Auth0 instance not available');
      return null;
    }

    const token = await auth0.getAccessTokenSilently({
      audience: process.env.REACT_APP_AUTH0_AUDIENCE,
    });

    return token;
  } catch (error) {
    console.error('Error getting Auth0 token:', error);

    // If we can't get token silently, might need to re-authenticate
    if (error.error === 'login_required' || error.error === 'consent_required') {
      console.warn('Token refresh failed, user may need to re-authenticate');
    }

    return null;
  }
};

/**
 * Check if user is authenticated and token is valid
 * @returns {Promise<boolean>} Authentication status
 */
export const isAuthenticated = async () => {
  try {
    const token = await getAuth0Token();
    return !!token;
  } catch (error) {
    console.error('Error checking authentication:', error);
    return false;
  }
};

/**
 * Get user profile information
 * @returns {Promise<Object|null>} User profile or null
 */
export const getUserProfile = async () => {
  try {
    const auth0 = getAuth0Instance();
    if (!auth0) {
      return null;
    }

    const user = await auth0.getUser();
    return user || null;
  } catch (error) {
    console.error('Error getting user profile:', error);
    return null;
  }
};

/**
 * Logout user
 * @param {string} returnTo - URL to redirect to after logout
 */
export const logout = (returnTo = window.location.origin) => {
  try {
    const auth0 = getAuth0Instance();
    if (auth0) {
      auth0.logout({
        logoutParams: {
          returnTo,
        },
      });
    }
  } catch (error) {
    console.error('Error during logout:', error);
  }
};

/**
 * Login user
 * @param {Object} options - Login options
 */
export const login = (options = {}) => {
  try {
    const auth0 = getAuth0Instance();
    if (auth0) {
      auth0.loginWithRedirect({
        authorizationParams: {
          audience: process.env.REACT_APP_AUTH0_AUDIENCE,
          ...options,
        },
      });
    }
  } catch (error) {
    console.error('Error during login:', error);
  }
};