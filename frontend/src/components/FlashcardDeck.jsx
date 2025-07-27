import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Flashcard from './Flashcard';

const FlashcardDeck = ({ flashcards, onDeleteCard }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('deck'); // 'deck' or 'grid'

  const filteredFlashcards = flashcards.filter(card =>
    card.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % filteredFlashcards.length);
  };

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + filteredFlashcards.length) % filteredFlashcards.length);
  };

  const goToCard = (index) => {
    setCurrentIndex(index);
  };

  if (filteredFlashcards.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="text-gray-400 text-6xl mb-4">📚</div>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">
          {searchTerm ? 'No flashcards match your search' : 'No flashcards yet'}
        </h3>
        <p className="text-gray-500">
          {searchTerm ? 'Try adjusting your search terms' : 'Upload a PDF to get started'}
        </p>
      </motion.div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between"
      >
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search flashcards..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <svg
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">View:</span>
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              onClick={() => setViewMode('deck')}
              className={`px-3 py-1 text-sm font-medium transition-colors ${
                viewMode === 'deck'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              Deck
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 text-sm font-medium transition-colors ${
                viewMode === 'grid'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              Grid
            </button>
          </div>
        </div>
      </motion.div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <AnimatePresence>
            {filteredFlashcards.map((flashcard, index) => (
              <Flashcard
                key={flashcard.id}
                flashcard={flashcard}
                onDelete={onDeleteCard}
              />
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Deck View */}
      {viewMode === 'deck' && (
        <div className="flex flex-col items-center">
          {/* Current Card */}
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            className="w-full max-w-md mb-6"
          >
            <Flashcard
              flashcard={filteredFlashcards[currentIndex]}
              onDelete={onDeleteCard}
            />
          </motion.div>

          {/* Navigation */}
          <div className="flex items-center space-x-4 mb-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={prevCard}
              disabled={filteredFlashcards.length <= 1}
              className="p-2 rounded-full bg-white shadow-md border border-gray-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </motion.button>

            <span className="text-sm text-gray-600 font-medium">
              {currentIndex + 1} of {filteredFlashcards.length}
            </span>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={nextCard}
              disabled={filteredFlashcards.length <= 1}
              className="p-2 rounded-full bg-white shadow-md border border-gray-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </motion.button>
          </div>

          {/* Card Indicators */}
          {filteredFlashcards.length > 1 && (
            <div className="flex space-x-2">
              {filteredFlashcards.slice(0, 10).map((_, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.2 }}
                  whileTap={{ scale: 0.8 }}
                  onClick={() => goToCard(index)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentIndex ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                />
              ))}
              {filteredFlashcards.length > 10 && (
                <span className="text-xs text-gray-500 ml-2">
                  +{filteredFlashcards.length - 10} more
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FlashcardDeck;