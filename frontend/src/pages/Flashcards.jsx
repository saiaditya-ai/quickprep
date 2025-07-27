import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import { useAuth0 } from '@auth0/auth0-react'; // Auth0 removed
import UploadBox from '../components/UploadBox';
import FlashcardDeck from '../components/FlashcardDeck';
import apiService from '../services/api';

const Flashcards = () => {
  // const { user } = useAuth0(); // Auth0 removed
  const [flashcards, setFlashcards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadUserFlashcards();
  }, []);

  const loadUserFlashcards = async () => {
    try {
      setLoading(true);
      const userFlashcards = await apiService.getUserFlashcards();
      setFlashcards(userFlashcards);
    } catch (error) {
      console.error('Error loading flashcards:', error);
      setError('Failed to load your flashcards');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (result) => {
    setSuccess(`Successfully generated ${result.flashcards.length} flashcards!`);
    setError(null);
    setFlashcards(prev => [...result.flashcards, ...prev]);

    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);
  };

  const handleUploadError = (errorMessage) => {
    setError(errorMessage);
    setSuccess(null);
  };

  const handleDeleteCard = async (cardId) => {
    if (!window.confirm('Are you sure you want to delete this flashcard?')) {
      return;
    }

    try {
      await apiService.deleteFlashcard(cardId);
      setFlashcards(prev => prev.filter(card => card.id !== cardId));
      setSuccess('Flashcard deleted successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      console.error('Error deleting flashcard:', error);
      setError('Failed to delete flashcard');
    }
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-gray-200 border-t-primary-600 rounded-full"
        />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl mx-auto"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Welcome back, Learner! 👋
        </h1>
        <p className="text-gray-600">
          {flashcards.length === 0 
            ? "Upload your first PDF to get started with AI-powered flashcards"
            : `You have ${flashcards.length} flashcard${flashcards.length !== 1 ? 's' : ''} ready for study`
          }
        </p>
      </motion.div>

      {/* Notifications */}
      <AnimatePresence>
        {(error || success) && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`mb-6 p-4 rounded-lg border ${
              error 
                ? 'bg-red-50 border-red-200 text-red-800' 
                : 'bg-green-50 border-green-200 text-green-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-lg">
                  {error ? '❌' : '✅'}
                </span>
                <span>{error || success}</span>
              </div>
              <button
                onClick={clearMessages}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-12"
      >
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Upload New PDF
          </h2>
          <p className="text-gray-600">
            Transform your study materials into interactive flashcards
          </p>
        </div>

        <UploadBox
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
      </motion.div>

      {/* Flashcards Section */}
      {flashcards.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Your Flashcards
            </h2>
            <p className="text-gray-600">
              Click on any card to flip it and see the answer
            </p>
          </div>

          <FlashcardDeck
            flashcards={flashcards}
            onDeleteCard={handleDeleteCard}
          />
        </motion.div>
      )}

      {/* Empty State */}
      {flashcards.length === 0 && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center py-16"
        >
          <motion.div
            animate={{ 
              y: [0, -10, 0],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatType: "reverse"
            }}
            className="text-8xl mb-6"
          >
            📚
          </motion.div>
          <h3 className="text-2xl font-semibold text-gray-600 mb-2">
            Ready to start learning?
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Upload your first PDF document above to generate AI-powered flashcards 
            and supercharge your study sessions!
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default Flashcards;