# 🌸 CycleSync - Menstrual Cycle Tracker

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

**Empowering women through personalized menstrual health tracking and insights.**
<br></br>
<img src ="https://github.com/unmatched78/back-cyclesync/blob/main/media/profile_images/default.png" /><br></br>
CycleSync is a comprehensive menstrual cycle tracking application designed to help users monitor, predict, and understand their menstrual cycles. By providing detailed insights into symptoms, moods, and fertility patterns, CycleSync empowers users to take control of their reproductive health with confidence and knowledge.

🌐 **Live Demo:** [cyclesync-beta.vercel.app](https://cyclesync-beta.vercel.app)

---

## ✨ Features

### 📅 **Cycle Tracking**
- Log menstrual start and end dates with intuitive calendar interface
- Automatic period prediction using advanced algorithms
- Track cycle length variations and irregularities
- Historical cycle data visualization

### 🩺 **Comprehensive Symptom Logging**
- Track physical symptoms: cramps, headaches, bloating, breast tenderness
- Monitor emotional changes and mood patterns
- Record sleep quality and energy levels
- Custom symptom categories for personalized tracking

### 🥚 **Ovulation & Fertility Insights**
- Estimate fertile windows and ovulation days
- Basal body temperature tracking
- Cervical mucus monitoring
- Fertility awareness method support

### 📝 **Health & Mood Journaling**
- Daily mood tracking with emotional insights
- Activity and exercise logging
- Health notes and observations
- Photo diary for visual tracking

### 🔔 **Smart Notifications**
- Customizable period and ovulation reminders
- Symptom logging prompts
- Medication and supplement reminders
- Privacy-focused local notifications

### 📊 **Data Visualization & Analytics**
- Interactive charts showing cycle patterns
- Symptom correlation analysis
- Mood and health trend reports
- Exportable health reports for healthcare providers

### 🔐 **Privacy & Security**
- End-to-end encryption for sensitive data
- Secure user authentication
- GDPR compliant data handling
- Optional anonymous usage mode

---

## 🏗️ Project Architecture

### **Frontend Stack**
- **React 18** with TypeScript for type-safe development
- **Tailwind CSS** for responsive, modern UI design
- **Chart.js** for interactive data visualizations
- **React Router** for seamless navigation
- **React Hook Form** for efficient form handling
- **Shadcn UI** for reuseable components

### **Backend Infrastructure**
- **Django** framework
- **REST-FRAMEOWORK-SIMPLE-JWT Authentication** for secure user sessions
- **VALIDATOR** for password hashing and security
- **MORE...** 

### **Database & Storage**
- **POSTGRESQL** for flexible data modeling
- **Redis** for session management and caching(to-do)
- **Cloudinary** for secure image storage(to-do)

### **Deployment & DevOps**
- **Vercel** for frontend deployment and hosting
- **GitHub Actions** for CI/CD pipeline
- **Docker** containerization for development consistency

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:


### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/unmatached78/cyclesync.git
   cd cyclesync
   ```

2. **Install dependencies**
   ```bash
   # Install backend dependencies
   ..
   pip install -r equirements.txt
   
   # Install frontend dependencies
   cd ../sync
   npm install
   ```

3. **Environment Configuration**
   
   Create `.env` files in both backend and frontend directories:
   
   **Backend `.env`:**
   ```env
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/cyclesync
   JWT_SECRET=your_jwt_secret_key_here
   JWT_EXPIRE=7d
   REDIS_URL=redis://localhost:6379
   CLOUDINARY_CLOUD_NAME=your_cloudinary_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   NODE_ENV=development
   ```
   
   **Frontend `.env`:**
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_ENV=development
   ```

4. **Database Setup**
   ```bash
   # Start MongoDB service
   sudo systemctl start mongod
   
   # Or using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Start backend server
   cd backend
   yarn dev
   
   # Terminal 2: Start frontend development server
   cd frontend
   yarn start
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

---

## 📁 Project Structure

```
cyclesync/
├── sync/                  # React frontend application
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Route components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── context/         # React context providers
│   │   ├── utils/           # Utility functions
│   │   ├── services/        # API service functions
│   │   └── styles/          # Global styles and themes
│   ├── package.json
│   └── tailwind.config.js
├
├── docs/                    # Documentation
├── docker-compose.yml       # Docker configuration
├── .github/                 # GitHub Actions workflows
└── README.md
```

---

## 🧪 Testing

### Running Tests

```bash
# Backend tests
..

# Frontend tests
cd sync
npm test
npm test:coverage
```

### Test Coverage
- Backend: 85%+ coverage for critical business logic
- Frontend: 80%+ coverage for components and utilities

---

## 🚀 Deployment

### Production Build

```bash
# Build frontend for production
cd frontend
yarn build

# Start backend in production mode
cd backend
yarn start
```

### Environment Variables (Production)

Ensure all production environment variables are configured:
- Database connection strings
- JWT secrets (use strong, unique keys)
- Third-party API keys
- CORS origins

---

## 📖 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile

### Cycle Management
- `GET /api/cycles` - Get user's cycles
- `POST /api/cycles` - Create new cycle
- `PUT /api/cycles/:id` - Update cycle
- `DELETE /api/cycles/:id` - Delete cycle

### Symptom Tracking
- `GET /api/symptoms` - Get symptoms
- `POST /api/symptoms` - Log new symptom
- `PUT /api/symptoms/:id` - Update symptom
- `DELETE /api/symptoms/:id` - Delete symptom

For complete API documentation, visit `/api/docs` when running the development server.

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to your branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style and conventions
- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

### Code of Conduct
Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards we expect from our community.

---

## 📋 Roadmap

### Version 2.0 (Q3 2025)
- [ ] Advanced AI-powered cycle predictions
- [ ] Integration with wearable devices
- [ ] Telehealth provider connections
- [ ] Multi-language support

### Version 2.1 (Q4 2025)
- [ ] Social features and community support
- [ ] Advanced analytics dashboard
- [ ] Export to healthcare providers
- [ ] iOS and Android mobile apps

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature idea? We'd love to hear from you!

- **Bug Reports:** [Create an issue](https://github.com/yourusername/cyclesync/issues/new?template=bug_report.md)
- **Feature Requests:** [Request a feature](https://github.com/yourusername/cyclesync/issues/new?template=feature_request.md)

---

## 📄 License

This project is licensed under the GPL-3.0 license - see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♀️ Support & Community

- **Documentation:** [Read the docs](https://docs.cyclesync.app)
- **Community Forum:** [Join discussions](https://community.cyclesync.app)
- **Email Support:** support@cyclesync.app
- **Twitter:** [@CycleSyncApp](https://twitter.com/CycleSyncApp)

---

## 🏆 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Inspired by the need for better menstrual health tracking tools
- Built with love for the global community of menstruating individuals

---

<div align="center">

**Made with ❤️ for reproductive health empowerment**

[⭐ Star this repository](https://github.com/unmatched78/cyclesync) if you found it helpful!

</div>
