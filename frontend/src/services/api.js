import axios from 'axios';
// import { getAuth0Token } from './auth'; // Auth0 removed

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    // Auth0 removed - no authentication required
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || 
                          error.response.data?.message || 
                          `HTTP ${error.response.status}: ${error.response.statusText}`;
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error: Unable to connect to server');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

/**
 * API Service Methods
 */
const apiService = {
  /**
   * Test connection to the API
   */
  async testConnection() {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error) {
      throw new Error(`Connection test failed: ${error.message}`);
    }
  },

  /**
   * Test protected endpoint (requires authentication)
   */
  async testProtected() {
    try {
      const response = await apiClient.get('/protected');
      return response.data;
    } catch (error) {
      throw new Error(`Protected endpoint test failed: ${error.message}`);
    }
  },

  /**
   * Upload PDF and generate flashcards
   * @param {File} file - PDF file to upload
   * @returns {Promise<Object>} Response with generated flashcards
   */
  async uploadPDF(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/upload-pdf/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Override timeout for file uploads
        timeout: 120000, // 2 minutes
      });

      return response.data;
    } catch (error) {
      throw new Error(`PDF upload failed: ${error.message}`);
    }
  },

  /**
   * Search flashcards using semantic search
   * @param {string} query - Search query
   * @param {number} limit - Maximum number of results
   * @returns {Promise<Array>} Matching flashcards
   */
  async searchFlashcards(query, limit = 10) {
    try {
      const response = await apiClient.post('/search-flashcards', {
        query,
        limit,
      });

      return response.data.results || [];
    } catch (error) {
      throw new Error(`Flashcard search failed: ${error.message}`);
    }
  },

  /**
   * Get all flashcards for the authenticated user
   * @param {number} limit - Maximum number of flashcards to fetch
   * @returns {Promise<Array>} User's flashcards
   */
  async getUserFlashcards(limit = 50) {
    try {
      console.log('API: Making request to /flashcards/');
      const response = await apiClient.get('/flashcards/');
      console.log('API: Received response:', response.data);
      return response.data.flashcards || [];
    } catch (error) {
      console.error('API: Failed to load user flashcards:', error);
      throw error; // Re-throw so the component can handle it
    }
  },

  /**
   * Delete a flashcard
   * @param {number} cardId - ID of the flashcard to delete
   * @returns {Promise<boolean>} Success status
   */
  async deleteFlashcard(cardId) {
    try {
      // Note: This endpoint would need to be implemented in the backend
      const response = await apiClient.delete(`/flashcards/${cardId}`);
      return response.data.success || true;
    } catch (error) {
      throw new Error(`Failed to delete flashcard: ${error.message}`);
    }
  },

  /**
   * Update a flashcard
   * @param {number} cardId - ID of the flashcard to update
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated flashcard
   */
  async updateFlashcard(cardId, updates) {
    try {
      const response = await apiClient.put(`/flashcards/${cardId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update flashcard: ${error.message}`);
    }
  },

  /**
   * Get user statistics
   * @returns {Promise<Object>} User stats
   */
  async getUserStats() {
    try {
      const response = await apiClient.get('/user/stats');
      return response.data;
    } catch (error) {
      console.warn('Failed to load user stats:', error.message);
      return {
        total_flashcards: 0,
        easy_cards: 0,
        medium_cards: 0,
        hard_cards: 0,
      };
    }
  },
};

export default apiService;