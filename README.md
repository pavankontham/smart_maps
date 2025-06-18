# SmartCity AI - Intelligent Traffic Optimization System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/Firebase-9.0+-orange.svg)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive AI-powered traffic optimization system that provides intelligent route planning, real-time traffic analysis, and eco-friendly transportation solutions for smart cities.

## 🚀 Features

### Core Functionality
- **Real-time Route Planning**: Get optimized routes using Google Maps Directions API
- **AI-Powered Eco Assistant**: Gemini 1.5 Flash powered chatbot for environmental advice
- **User Authentication**: Firebase Auth with email/password and Google signin
- **Search History**: Firebase Firestore integration for persistent search history
- **Real-time Data Integration**: Weather, traffic, transit, and air quality data

### Technical Features
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Firebase Integration**: Authentication and Firestore database
- **Google Maps Integration**: Interactive maps with traffic layer and custom controls
- **Real-time APIs**: WeatherAPI, TomTom Traffic, Transitland, OpenWeather
- **Responsive Frontend**: Modern HTML/CSS/JS with mobile support

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
    ↓
FastAPI Backend
    ├── Google Maps API (Routes, Traffic)
    ├── Gemini AI (Eco Assistant)
    ├── Real Data APIs (Weather, Traffic, Transit)
    └── Firebase (Auth, Firestore)
```

## 📋 Prerequisites

- Python 3.8+
- Node.js (for frontend dependencies, optional)
- Google Maps API key
- Google Gemini AI API key
- Firebase project setup
- API keys for real data services

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SmartCity-AI
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and update with your API keys:

```env
# Google APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GEMINI_API_KEY=your_gemini_api_key

# Real Data APIs (Optional)
OPENWEATHER_API_KEY=your_openweather_api_key
TOMTOM_API_KEY=your_tomtom_api_key
WEATHERAPI_KEY=your_weatherapi_key
TRANSITLAND_API_KEY=your_transitland_api_key

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 4. Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Authentication (Email/Password and Google)
3. Create a Firestore database
4. Update `frontend/static/js/firebase-config.js` with your Firebase config

### 5. Run the Application
```bash
python -m backend.main
```

The application will be available at http://localhost:8000

## 🎯 Usage Guide

### Authentication
1. Visit http://localhost:8000/auth.html to sign up or sign in
2. Use email/password or Google signin
3. User data is stored in Firebase Firestore

### Route Planning
1. Enter source and destination addresses
2. Select route type (Fastest, Shortest, or Eco-friendly)
3. Configure options (avoid tolls/highways)
4. Click "Get Route" to see optimized path
5. View route details including distance, duration, and eco metrics

### AI Assistant
1. Navigate to the AI Assistant tab
2. Ask questions about routes, environmental impact, or transportation
3. Get personalized eco-friendly advice powered by Gemini AI

### Search History
1. Sign in to automatically save your route searches
2. View previous searches in the History tab
3. Repeat or delete previous searches
4. Data syncs across all your devices

## 🔧 API Endpoints

### Route Planning
- `POST /api/route` - Calculate optimized routes
- `GET /api/weather` - Get weather and air quality data
- `GET /api/traffic` - Get real-time traffic information
- `GET /api/transit` - Get public transit data

### AI Assistant
- `POST /api/eco_chat` - Chat with the eco assistant
- `GET /api/eco_tips` - Get personalized eco tips

### Configuration
- `GET /api/config` - Get application configuration
- `GET /health` - Health check endpoint

## 🌍 Real Data Sources

- **Weather**: WeatherAPI for current conditions and forecasts
- **Traffic**: TomTom Traffic API for real-time traffic flow and incidents
- **Transit**: Transitland API for public transportation data
- **Air Quality**: OpenWeather Air Pollution API

## 🔒 Security Features

- Firebase Authentication with secure token management
- CORS protection for API endpoints
- Input validation and sanitization
- Secure API key management through environment variables

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern web browsers

## 🧪 Testing

### Run the Application
```bash
python -m backend.main
```

### Test API Endpoints
Visit http://localhost:8000/docs for interactive API documentation.

### Frontend Testing
1. Open http://localhost:8000 in your browser
2. Test authentication flow
3. Test route planning with real addresses
4. Verify map functionality and AI assistant

## 🚀 Deployment

### Local Development
```bash
python -m backend.main
```

### Production Deployment
1. Set `DEBUG=False` in environment variables
2. Configure production Firebase settings
3. Use a production WSGI server like Gunicorn:
```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the code comments and documentation
- Open an issue on the repository

## 🔍 Troubleshooting

### Common Issues

**Firestore Index Error**
```
Error: The query requires an index
```
**Solution**: The application includes automatic fallback for missing indexes, but for optimal performance, create the required indexes:
- Use the provided deployment script: `python deploy-firestore-config.py`
- Or click the index creation link provided in the error message

**API Key Issues**
```
Error: API key not valid
```
**Solution**:
- Verify your API keys in the `.env` file
- Ensure APIs are enabled in Google Cloud Console
- Check API quotas and billing

**Authentication Problems**
```
Error: Firebase Auth not configured
```
**Solution**:
- Verify Firebase configuration in `firebase-config.js`
- Enable Authentication methods in Firebase Console
- Check domain authorization settings

### Performance Optimization

- **Enable Firestore Indexes**: Use composite indexes for better query performance
- **API Caching**: Implement caching for frequently requested routes
- **CDN Integration**: Use CDN for static assets in production
- **Database Optimization**: Regular cleanup of old search history data

## 🔒 Enhanced Security Features

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **Authentication**: Secure Firebase Auth with multiple providers
- **Authorization**: Role-based access control
- **Privacy**: User data isolation and GDPR compliance

### API Security
- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Secure cross-origin requests
- **API Key Management**: Secure key storage and rotation

## 📊 Monitoring and Analytics

### Built-in Analytics
- Route calculation performance metrics
- API response times and error rates
- User engagement and feature usage
- Search history patterns and trends

### Integration Options
- Google Analytics for web analytics
- Firebase Analytics for user behavior
- Custom dashboards for traffic insights
- Real-time monitoring with alerts

## 🔄 Version History

- **v2.1.0** - Enhanced search history with filtering and Firestore index optimization
- **v2.0.0** - Complete rewrite with real data integration
- **v1.0.0** - Initial release with basic functionality

## 📈 Roadmap

### Upcoming Features
- [ ] Mobile app development (React Native/Flutter)
- [ ] Advanced ML models for traffic prediction
- [ ] Integration with public transportation APIs
- [ ] Multi-language support
- [ ] Offline mode capabilities
- [ ] Advanced analytics dashboard
- [ ] API rate limiting and quotas
- [ ] Webhook support for real-time updates

### Long-term Vision
- Smart city integration platform
- IoT device connectivity
- Autonomous vehicle support
- City-wide traffic optimization
- Environmental impact tracking

## 🙏 Acknowledgments

- Google Maps API for mapping services
- Google Gemini AI for intelligent assistance
- Firebase for authentication and data storage
- FastAPI for the robust backend framework
- TomTom API for real-time traffic data
- OpenWeather API for weather integration
- All contributors and the open-source community

---

**Made with ❤️ for Smart Cities**

*Building the future of urban mobility, one route at a time.*
