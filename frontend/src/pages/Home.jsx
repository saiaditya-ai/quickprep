import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5 }
    }
  };

  const features = [
    {
      icon: "📄",
      title: "PDF Upload",
      description: "Simply upload your PDF study materials and let AI do the work"
    },
    {
      icon: "🤖",
      title: "AI Generation",
      description: "Advanced AI creates relevant questions and answers from your content"
    },
    {
      icon: "🔍",
      title: "Smart Search",
      description: "Find specific flashcards instantly with semantic search"
    },
    {
      icon: "📚",
      title: "Interactive Study",
      description: "Study with animated flashcards designed for better retention"
    }
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen flex flex-col items-center justify-center text-center px-4"
    >
      {/* Hero Section */}
      <motion.div variants={itemVariants} className="max-w-4xl mx-auto mb-16">
        <motion.div
          animate={{ 
            rotate: [0, 5, -5, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            repeatType: "reverse"
          }}
          className="text-8xl mb-8"
        >
          🚀
        </motion.div>

        <motion.h1 
          variants={itemVariants}
          className="text-5xl md:text-6xl font-bold text-gray-900 mb-6"
        >
          Transform PDFs into
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
            {" "}Smart Flashcards
          </span>
        </motion.h1>

        <motion.p 
          variants={itemVariants}
          className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed"
        >
          Upload your study materials and let our AI create personalized flashcards. 
          Study smarter with intelligent question generation and semantic search.
        </motion.p>

        <motion.button
          variants={itemVariants}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/flashcards')}
          className="bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 text-white font-bold py-4 px-8 rounded-xl text-lg shadow-lg transition-all duration-200"
        >
          Get Started Free
        </motion.button>
      </motion.div>

      {/* Features Grid */}
      <motion.div 
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto mb-16"
      >
        {features.map((feature, index) => (
          <motion.div
            key={index}
            variants={itemVariants}
            whileHover={{ y: -5, scale: 1.02 }}
            className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
          >
            <div className="text-4xl mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-600 text-sm">
              {feature.description}
            </p>
          </motion.div>
        ))}
      </motion.div>

      {/* How It Works */}
      <motion.div 
        variants={itemVariants}
        className="max-w-4xl mx-auto"
      >
        <h2 className="text-3xl font-bold text-gray-900 mb-12">
          How It Works
        </h2>

        <div className="flex flex-col md:flex-row items-center justify-center space-y-8 md:space-y-0 md:space-x-8">
          {[
            { step: "1", title: "Upload", desc: "Upload your PDF", icon: "📤" },
            { step: "2", title: "Process", desc: "AI analyzes content", icon: "⚡" },
            { step: "3", title: "Study", desc: "Study with flashcards", icon: "🎯" }
          ].map((step, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ scale: 1.05 }}
              className="flex flex-col items-center"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-primary-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl mb-4">
                {step.step}
              </div>
              <div className="text-4xl mb-2">{step.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1">{step.title}</h3>
              <p className="text-gray-600 text-sm text-center">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Footer */}
      <motion.div 
        variants={itemVariants}
        className="mt-20 text-gray-500 text-sm"
      >
        <p>Powered by Supabase and Hugging Face 🤝</p>
      </motion.div>
    </motion.div>
  );
};

export default Home;