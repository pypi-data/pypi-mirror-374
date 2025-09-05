# Docker Setup for mem8

This project provides both development and production Docker configurations.

## Development (with Hot Reloading)

For contributing developers who need hot reloading:

```bash
# Start development environment
docker-compose --env-file .env.dev up -d --build

# View logs
docker-compose --env-file .env.dev logs -f

# Stop development environment  
docker-compose --env-file .env.dev down
```

**Development features:**
- ✅ Frontend hot reloading with volume mounts
- ✅ Development Dockerfile.dev with npm dev server
- ✅ PostgreSQL on port 5433 (external) to avoid local conflicts
- ✅ Debug logging enabled
- ✅ All source code mounted for live editing

**Accessible at:**
- Frontend: http://localhost:22211
- Backend API: http://localhost:8000
- Backend Health: http://localhost:8000/api/v1/health

## Production Deployment

For production deployment or when distributing mem8 for users:

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production environment
docker-compose -f docker-compose.prod.yml down
```

**Production features:**
- ✅ Optimized production Dockerfile with multi-stage builds
- ✅ Next.js standalone output for minimal container size  
- ✅ PostgreSQL on standard port 5432
- ✅ Production logging and security settings
- ✅ No source code mounts - fully containerized

## Environment Files

- **`.env.dev`** - Development configuration with debug settings
- **`.env.prod`** - Production template (update passwords and secrets!)

## File Structure

```
├── docker-compose.yml          # Development compose (default)
├── docker-compose.prod.yml     # Production compose
├── .env.dev                   # Development environment
├── .env.prod                  # Production environment template
├── frontend/
│   ├── Dockerfile             # Production frontend build
│   └── Dockerfile.dev         # Development frontend with hot reload
└── backend/
    └── Dockerfile             # Production backend build
```

## Key Features

1. **No CUDA Dependencies**: Removed sentence-transformers to avoid 3GB+ ML stack
2. **Port 22211**: Updated from 3000 to avoid conflicts
3. **Database Flexibility**: Uses text search fallback instead of embeddings
4. **Hot Reloading**: Development setup supports live frontend editing
5. **Health Checks**: All services have proper health monitoring
6. **Environment Separation**: Clear dev/prod configuration split

## Quick Commands

```bash
# Development workflow
docker-compose --env-file .env.dev up -d --build
curl http://localhost:22211  # Test frontend
curl http://localhost:8000/api/v1/health  # Test backend

# Production deployment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Clean up
docker-compose down --remove-orphans
docker system prune -f  # Remove unused containers/images
```