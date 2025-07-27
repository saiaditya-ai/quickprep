# QuickPrep - AI-Powered Flashcard Generator

Transform your PDF study materials into interactive flashcards using AI. QuickPrep leverages cutting-edge technologies to help you study more effectively.

## 🚀 Features

- **PDF Upload & Processing**: Extract text from PDFs using PyMuPDF
- **AI-Powered Generation**: Create flashcards using Hugging Face transformers
- **Vector Search**: Find relevant flashcards with semantic search using Supabase pgvector
- **Interactive UI**: Beautiful animated flashcards with Framer Motion
- **Secure Authentication**: Auth0 integration for user management
- **Responsive Design**: Works perfectly on desktop and mobile

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PyMuPDF**: PDF text extraction
- **Hugging Face Transformers**: AI model integration
- **Supabase**: PostgreSQL database with pgvector
- **Auth0**: Authentication and authorization
- **Sentence Transformers**: Text embeddings

### Frontend
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Beautiful animations
- **Auth0 React SDK**: Authentication integration
- **Axios**: HTTP client for API calls

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase account
- Auth0 account
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd quickprep
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your credentials (see Configuration section)
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your credentials (see Configuration section)
```

### 4. Database Setup

```bash
# Navigate to supabase directory
cd ../supabase

# Run the schema.sql in your Supabase SQL editor
# This will create tables and functions needed for the app
```

### 5. Run the Application

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## ⚙️ Configuration

### Backend Environment Variables (.env)

```env
# Auth0 Configuration
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_API_AUDIENCE=https://your-api-audience
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Optional: OpenAI for enhanced embeddings
OPENAI_API_KEY=your-openai-key

# Optional: Hugging Face token for model access
HUGGINGFACE_API_TOKEN=your-hf-token
```

### Frontend Environment Variables (.env)

```env
# Auth0 Configuration
REACT_APP_AUTH0_DOMAIN=your-domain.auth0.com
REACT_APP_AUTH0_CLIENT_ID=your-client-id
REACT_APP_AUTH0_AUDIENCE=https://your-api-audience
REACT_APP_AUTH0_REDIRECT_URI=http://localhost:3000

# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 🔧 Auth0 Setup

1. Create an Auth0 account at [auth0.com](https://auth0.com)
2. Create a new Application (Single Page Application)
3. Configure settings:
   - **Allowed Callback URLs**: `http://localhost:3000, https://yourdomain.com`
   - **Allowed Logout URLs**: `http://localhost:3000, https://yourdomain.com`
   - **Allowed Web Origins**: `http://localhost:3000, https://yourdomain.com`
4. Create an API in Auth0:
   - **Name**: QuickPrep API
   - **Identifier**: `https://your-api-audience`
5. Copy credentials to your .env files

## 🗄️ Supabase Setup

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project
3. In the SQL Editor, run the contents of `supabase/schema.sql`
4. Go to Settings > API to get your URL and keys
5. Copy credentials to your backend .env file

## 🚀 Deployment

### Backend Deployment (Railway/Heroku/DigitalOcean)

1. Set environment variables on your hosting platform
2. Deploy from GitHub or upload your code
3. Ensure your hosting platform supports Python 3.8+

### Frontend Deployment (Vercel/Netlify)

1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Add environment variables in your hosting platform
5. Update Auth0 URLs to include your production domain

### Environment-Specific Configurations

Update your Auth0 and Supabase settings for production:
- Add production URLs to Auth0 allowed origins
- Update CORS settings in your backend
- Set production environment variables

## 📁 Project Structure

```
quickprep/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── auth.py              # Auth0 JWT verification
│   ├── pdf_utils.py         # PDF text extraction
│   ├── flashcard_generator.py # AI flashcard generation
│   ├── db/
│   │   └── vector_store.py  # Supabase vector operations
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── .env                 # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service layer
│   │   ├── auth/           # Auth0 utilities
│   │   └── App.js          # Main React component
│   ├── public/             # Static assets
│   └── .env                # Frontend environment variables
├── supabase/
│   └── schema.sql          # Database schema and functions
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🤝 API Endpoints

### Authentication Required Endpoints

- `POST /upload-pdf` - Upload PDF and generate flashcards
- `POST /search-flashcards` - Search flashcards with vector similarity
- `GET /protected` - Test protected endpoint

### Public Endpoints

- `GET /` - Health check

## 🎯 Usage

1. **Sign Up/Login**: Use the Auth0 authentication
2. **Upload PDF**: Click the upload area and select your PDF
3. **Wait for Processing**: AI will extract text and generate flashcards
4. **Study**: Click cards to flip them and reveal answers
5. **Search**: Use the search bar to find specific flashcards
6. **View Modes**: Switch between deck and grid views

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your frontend URL is in the backend's CORS origins
2. **Auth0 Errors**: Check that all Auth0 URLs and credentials are correct
3. **Database Errors**: Verify Supabase connection and that schema.sql was run
4. **File Upload Errors**: Check file size limits and supported formats

### Debug Mode

Enable debug mode by setting:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🛡️ Security Features

- JWT token validation with Auth0
- Row Level Security (RLS) in Supabase
- CORS protection
- File type and size validation
- Environment variable protection

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [Auth0 Documentation](https://auth0.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the configuration steps
3. Create an issue in the GitHub repository
4. Contact the development team

---

**Happy studying with QuickPrep! 🚀📚**
