# 🛡️ Data Protection Simulator - Educational Cybersecurity Platform

An interactive web-based educational platform for learning cybersecurity through realistic attack scenarios. Users face cybersecurity threats, make critical decisions, and learn from consequences in a gamified, safe environment.

## 🎮 Features

### Core Functionality
- **Interactive Attack Scenarios**: 5+ carefully designed cybersecurity scenarios including:
  - 🎣 Phishing Attacks
  - 💳 Skimming & Data Theft
  - 🔓 Brute Force Attacks
  - 👥 Social Engineering
  - 🎭 Deepfake & Misinformation

### Learning Contexts
- **Office Environment**: Corporate email and messaging scenarios
- **Home Environment**: Personal device and account security
- **Public WiFi**: Open network security threats

### Gamification Features
- 🎯 Security Level HP System (0-100%)
- 📊 Accuracy Tracking & Statistics
- 🏆 Achievement Badges & Certificates
- 📈 User Ranking System: Beginner → Intermediate → Advanced → Expert
- 🎪 Leaderboard & Progress Visualization

### User Experience
- 🎓 Detailed feedback after each choice explaining consequences
- 📱 Responsive design for desktop, tablet, and mobile
- 🚀 Fast loading and smooth interactions
- 📋 Personal dashboard with detailed stats and progress tracking

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3
- **UI Components**: Heroicons
- **State Management**: Context API + Zustand
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Database**: PostgreSQL 15
- **Authentication**: JWT (Python-Jose)
- **Password Hashing**: Bcrypt
- **Caching**: Redis 7
- **API Documentation**: Swagger/OpenAPI (auto-generated)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL with persistent volumes
- **Orchestration**: Docker Compose

## 📋 Requirements

### System Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Port Availability**: 3000 (frontend), 8000 (backend), 5432 (database)

### OR Manual Installation
- **Node.js**: 18+
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7+

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd centerinvest_case

# Start all services
docker-compose up --build

# Initialize database and seed data
# (Automatically done on first run)

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/data_protection_simulator
export SECRET_KEY=your-super-secret-key
export REDIS_URL=redis://localhost:6379/0

# Run migrations and seed data
python seed_data.py

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Start development server
npm run dev

# Open http://localhost:3000
```

## 📊 Database Schema

### Tables

#### `users`
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `password_hash`: Bcrypt-hashed password
- `created_at`, `updated_at`: Timestamps

#### `attack_scenarios`
- `id`: Primary key
- `title`: Scenario title
- `description`: Scenario description
- `context`: "office", "home", or "public_wifi"
- `attack_type`: Type of attack
- `difficulty`: "beginner", "intermediate", or "advanced"
- `attack_steps`: JSON array of scenario steps
- `created_at`: Creation timestamp

#### `user_progress`
- `id`: Primary key
- `user_id`: Foreign key to users
- `scenario_id`: Foreign key to scenarios
- `status`: "in_progress", "completed", or "failed"
- `security_level`: Current HP (0-100)
- `correct_choices`: Count of correct decisions
- `total_choices`: Total decisions made
- `started_at`, `completed_at`: Timestamps

#### `user_certificates`
- `id`: Primary key
- `user_id`: Foreign key to users
- `scenario_id`: Foreign key to scenarios
- `achievement`: Type of achievement
- `qr_code`: QR code for verification
- `created_at`: Creation timestamp

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register          - Register new user
POST   /api/auth/login             - Login user
GET    /api/auth/me                - Get current user info
```

### Scenarios
```
GET    /api/scenarios              - List all scenarios
GET    /api/scenarios/{id}         - Get scenario details
GET    /api/scenarios?difficulty=  - Filter by difficulty
```

### Game Progress
```
POST   /api/progress/start         - Start a scenario
POST   /api/progress/{id}/choice   - Submit a choice
GET    /api/user/progress          - Get user's progress history
GET    /api/user/stats             - Get user statistics
GET    /api/user/certificates      - Get earned certificates
```

### Health
```
GET    /api/health                 - Health check endpoint
```

## 🎮 How to Play

1. **Register/Login**: Create an account or sign in
2. **Browse Scenarios**: View available attack scenarios
3. **Select Difficulty**: Choose based on your level
4. **Face the Attack**: Read the scenario description
5. **Make a Decision**: Choose from 3-4 options
6. **Learn from Consequence**: Receive detailed feedback
7. **Track Progress**: Monitor your accuracy and security level
8. **Earn Certificates**: Complete scenarios perfectly to earn badges

## 📈 Scoring System

- **Security Level**: Starts at 100%, decreases with wrong choices (-20), increases with correct choices (+10)
- **Accuracy**: Calculated as (correct_choices / total_choices) * 100
- **Rank System**:
  - **Beginner**: 0-1 scenarios completed
  - **Intermediate**: 2-4 scenarios completed
  - **Advanced**: 5+ scenarios, 80%+ average
  - **Expert**: 10+ scenarios, 90%+ average

## 🏆 Achievements & Certificates

- **Perfect Score**: Complete a scenario with 100% security level
- **Speed Learner**: Complete all scenarios
- **Security Expert**: Achieve 90%+ accuracy across all scenarios

## 🔐 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT-based authentication
- ✅ CORS protection
- ✅ TLS 1.2/1.3 support (in production)
- ✅ No real malware - all threats are simulated
- ✅ SQL injection prevention via ORM
- ✅ XSS protection via React's built-in sanitization

## 📚 API Documentation

**Swagger UI**: Available at `http://localhost:8000/docs` when backend is running

**ReDoc**: Available at `http://localhost:8000/redoc`

## 📁 Project Structure

```
centerinvest_case/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── auth.py                 # Authentication utilities
│   ├── seed_data.py            # Initial data seeding
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables
│   └── Dockerfile              # Container image
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Home page
│   │   ├── layout.tsx          # Root layout
│   │   ├── globals.css         # Global styles
│   │   ├── context/
│   │   │   └── AuthContext.tsx # Auth context provider
│   │   ├── login/page.tsx      # Login page
│   │   ├── register/page.tsx   # Registration page
│   │   ├── dashboard/page.tsx  # User dashboard
│   │   ├── scenarios/page.tsx  # Scenarios list
│   │   └── game/[id]/page.tsx  # Game interface
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── tailwind.config.ts      # Tailwind config
│   ├── .env.local              # Frontend env vars
│   └── Dockerfile              # Container image
│
├── docker-compose.yml          # Orchestration config
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Port already in use
```bash
# Find and stop the process using the port
lsof -i :3000          # Frontend
lsof -i :8000          # Backend
lsof -i :5432          # Database
```

**Issue**: Database connection error
```bash
# Ensure PostgreSQL is running and DB exists
docker-compose down && docker-compose up --build
```

**Issue**: Frontend can't connect to backend
```bash
# Check CORS settings in backend/main.py
# Ensure NEXT_PUBLIC_API_URL matches backend URL
# Check backend is running on port 8000
```

## 📝 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎓 Educational Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Kaspersky Security Tips](https://www.kaspersky.com/)
- [APWG Anti-Phishing Resources](https://www.apwg.org/)

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for cybersecurity education**
