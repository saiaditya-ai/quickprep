import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Flashcard = ({ flashcard, onDelete }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const flipVariants = {
    front: {
      rotateY: 0,
      transition: { duration: 0.6, ease: "easeInOut" }
    },
    back: {
      rotateY: 180,
      transition: { duration: 0.6, ease: "easeInOut" }
    }
  };

  const contentVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { duration: 0.3, delay: 0.1 }
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      whileHover={{ y: -5 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="relative w-full h-80 perspective-1000 cursor-pointer"
      onClick={() => setIsFlipped(!isFlipped)}
    >
      {/* Card Container */}
      <motion.div
        className="w-full h-full relative preserve-3d"
        variants={flipVariants}
        animate={isFlipped ? "back" : "front"}
      >
        {/* Front Side */}
        <motion.div
          className="absolute inset-0 w-full h-full flashcard flashcard-front backface-hidden"
          variants={contentVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex flex-col justify-between h-full">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full font-medium">
                Question
              </span>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete && onDelete(flashcard.id);
                }}
                className="text-gray-400 hover:text-red-500 transition-colors"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </motion.button>
            </div>

            <div className="flex-1 flex items-center justify-center">
              <p className="text-lg font-medium text-gray-900 text-center leading-relaxed">
                {flashcard.question}
              </p>
            </div>

            <div className="flex justify-between items-end">
              <span className="text-xs text-gray-500">
                {flashcard.difficulty || 'Medium'}
              </span>
              <motion.div
                animate={isHovered ? { x: 5 } : { x: 0 }}
                className="text-xs text-gray-400"
              >
                Click to flip →
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Back Side */}
        <motion.div
          className="absolute inset-0 w-full h-full flashcard flashcard-back backface-hidden rotate-y-180"
          variants={contentVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex flex-col justify-between h-full">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                Answer
              </span>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete && onDelete(flashcard.id);
                }}
                className="text-gray-400 hover:text-red-500 transition-colors"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </motion.button>
            </div>

            <div className="flex-1 flex items-center justify-center">
              <p className="text-base text-gray-800 text-center leading-relaxed">
                {flashcard.answer}
              </p>
            </div>

            <div className="flex justify-between items-end">
              <span className="text-xs text-gray-500">
                {new Date(flashcard.created_at).toLocaleDateString()}
              </span>
              <motion.div
                animate={isHovered ? { x: -5 } : { x: 0 }}
                className="text-xs text-gray-400"
              >
                ← Click to flip
              </motion.div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Flashcard;