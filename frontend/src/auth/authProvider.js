import { useAuth0 } from '@auth0/auth0-react';

// Global reference to Auth0 instance
let auth0Instance = null;

/**
 * Auth0 Provider Component
 * This component is already handled by the Auth0Provider in index.js
 * This file provides utility functions for accessing Auth0 instance
 */

/**
 * Hook to get Auth0 instance and store global reference
 * @returns {Object} Auth0 instance
 */
export const useAuth0Instance = () => {
  const auth0 = useAuth0();

  // Store global reference for use in API service
  if (auth0 && !auth0Instance) {
    auth0Instance = auth0;
  }

  return auth0;
};

/**
 * Get global Auth0 instance
 * @returns {Object|null} Auth0 instance or null if not available
 */
export const getAuth0Instance = () => {
  return auth0Instance;
};

/**
 * Auth0 configuration validation
 */
export const validateAuth0Config = () => {
  const requiredEnvVars = [
    'REACT_APP_AUTH0_DOMAIN',
    'REACT_APP_AUTH0_CLIENT_ID',
    'REACT_APP_AUTH0_AUDIENCE',
  ];

  const missing = requiredEnvVars.filter(
    (envVar) => !process.env[envVar]
  );

  if (missing.length > 0) {
    console.error(
      'Missing required Auth0 environment variables:',
      missing.join(', ')
    );
    return false;
  }

  return true;
};

/**
 * Auth0 error handler
 * @param {Error} error - Auth0 error
 */
export const handleAuth0Error = (error) => {
  console.error('Auth0 Error:', error);

  // Common error types and handling
  switch (error.error) {
    case 'login_required':
      console.warn('User needs to log in');
      break;
    case 'consent_required':
      console.warn('User consent required');
      break;
    case 'interaction_required':
      console.warn('User interaction required');
      break;
    case 'access_denied':
      console.warn('Access denied by user or system');
      break;
    default:
      console.error('Unknown Auth0 error:', error.error_description);
  }
};

// Validate configuration on module load
if (process.env.NODE_ENV !== 'test') {
  validateAuth0Config();
}