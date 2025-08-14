# BookExchange - Social Network for Book Lovers

A comprehensive book exchange social network that allows users to share, discover, and exchange books within their social circles and local communities.

## Features

- **User Management**: Create accounts, manage profiles, and invite friends
- **Book Management**: Add books to your collection (manual entry with future OCR automation)
- **Social Features**: Private messaging and public book discussions
- **Book Exchange**: Request and manage book exchanges with friends
- **Discovery**: Search for books among friends, friends-of-friends, and geo-localized search

## Tech Stack

### Frontend
- **React** with TypeScript
- Modern UI components and responsive design
- Real-time messaging capabilities

### Backend
- **Django** with **Django-Ninja** for API development
- **PostgreSQL** database
- JWT-based authentication
- RESTful API design

### Infrastructure
- **Google Cloud Platform** for deployment
- **Terraform** for infrastructure as code
- **GitHub Actions** for CI/CD
- Containerized deployment with Docker

## Project Structure

```
bapp/
├── backend/          # Django-Ninja API server
├── frontend/         # React TypeScript application
├── infra/           # Terraform infrastructure configuration
├── .github/         # GitHub Actions workflows
└── docker-compose.yml # Local development setup
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Docker (optional, for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd bapp
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Database Setup**
   - Install PostgreSQL locally or use Docker
   - Create a database named `bookexchange`
   - Update environment variables in `.env` files

### Using Docker (Alternative)
```bash
docker-compose up -d
```

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/bookexchange
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## API Documentation

Once the backend is running, visit:
- API Documentation: `http://localhost:8000/api/docs`
- Interactive API: `http://localhost:8000/api/docs/swagger`

## Deployment

The application is configured for deployment on Google Cloud Platform using Terraform. See the `infra/` directory for infrastructure configuration.

```bash
cd infra
terraform init
terraform plan
terraform apply
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Future Enhancements

- OCR integration for automatic book cataloging from bookshelf photos
- Mobile app development
- Advanced recommendation algorithms
- Integration with online bookstores
- Book condition tracking and ratings 