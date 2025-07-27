import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { loginWithRedirect, logout, isAuthenticated, user, isLoading } = useAuth0();

  return (
    <motion.nav 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-white shadow-lg border-b border-gray-200"
    >
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-2"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">Q</span>
            </div>
            <span className="text-xl font-bold text-gray-900">QuickPrep</span>
          </motion.div>

          {/* Navigation Items */}
          <div className="flex items-center space-x-4">
            {!isLoading && (
              <>
                {isAuthenticated ? (
                  <div className="flex items-center space-x-4">
                    {/* User Profile */}
                    <div className="flex items-center space-x-3">
                      {user?.picture && (
                        <motion.img
                          whileHover={{ scale: 1.1 }}
                          src={user.picture}
                          alt={user.name || 'User'}
                          className="w-8 h-8 rounded-full"
                        />
                      )}
                      <span className="text-sm text-gray-700 hidden sm:block">
                        {user?.name || user?.email}
                      </span>
                    </div>

                    {/* Logout Button */}
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => logout({ 
                        logoutParams: { 
                          returnTo: window.location.origin 
                        }
                      })}
                      className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
                    >
                      Logout
                    </motion.button>
                  </div>
                ) : (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => loginWithRedirect()}
                    className="btn-primary"
                  >
                    Login
                  </motion.button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;