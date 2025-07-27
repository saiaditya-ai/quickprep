// Auth0 Provider - DISABLED
// This file has been disabled since Auth0 authentication was removed

console.warn('Auth0 authentication has been removed from this application');

// Placeholder functions for backward compatibility
export const useAuth0Instance = () => null;
export const getAuth0Instance = () => null;
export const validateAuth0Config = () => false;
export const handleAuth0Error = (error) => console.error('Auth0 disabled:', error);