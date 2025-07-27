// Auth Service - DISABLED
// This file has been disabled since Auth0 authentication was removed

console.warn('Auth0 authentication has been removed from this application');

// Placeholder functions for backward compatibility
export const getAuth0Token = async () => null;
export const isAuthenticated = async () => true; // Always return true since no auth required
export const getUserProfile = async () => ({ name: 'Anonymous User' });
export const logout = () => console.log('No authentication to logout from');
export const login = () => console.log('No authentication required');