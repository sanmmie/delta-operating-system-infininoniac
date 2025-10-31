# Delta OS Production Deployment Script
# Usage: ./scripts/deploy-production.sh

set -e  # Exit on any error

echo "🚀 Δ Delta OS Production Deployment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_error ".env file not found. Please create from .env.example"
        exit 1
    fi
    
    log_info "All prerequisites satisfied ✓"
}

# Load environment variables
load_env() {
    log_info "Loading environment variables..."
    set -a  # Automatically export all variables
    source .env
    set +a
}

# Validate critical environment variables
validate_env() {
    log_info "Validating environment variables..."
    
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD" 
        "SECRET_KEY"
        "GRAFANA_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Validate SECRET_KEY length for JWT
    if [ ${#SECRET_KEY} -lt 32 ]; then
        log_warn "SECRET_KEY should be at least 32 characters for production"
    fi
    
    log_info "Environment validation passed ✓"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."
    docker-compose -f docker-compose.production.yml pull
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    until docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U $POSTGRES_USER; do
        sleep 5
    done
    
    # Run Alembic migrations
    docker-compose -f docker-compose.production.yml run --rm api \
        alembic upgrade head
    
    log_info "Database migrations completed ✓"
}

# Start services
start_services() {
    log_info "Starting Delta OS services..."
    docker-compose -f docker-compose.production.yml up -d
    
    log_info "Scaling API instances..."
    docker-compose -f docker-compose.production.yml up -d --scale api=3
}

# Health checks
health_checks() {
    log_info "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        if curl -s -f http://localhost:8000/health > /dev/null; then
            log_info "API health check passed ✓"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Health check failed after $max_attempts attempts"
            show_service_logs
            exit 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Check individual services
    check_service_health "PostgreSQL" "docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U $POSTGRES_USER"
    check_service_health "Redis" "docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping"
}

check_service_health() {
    local service_name=$1
    local health_cmd=$2
    
    if eval $health_cmd > /dev/null 2>&1; then
        log_info "$service_name health check passed ✓"
    else
        log_error "$service_name health check failed"
        exit 1
    fi
}

# Show service logs for debugging
show_service_logs() {
    log_warn "Showing recent service logs for debugging:"
    docker-compose -f docker-compose.production.yml logs --tail=50
}

# Perform post-deployment checks
post_deployment_checks() {
    log_info "Running post-deployment checks..."
    
    # Check if all services are running
    local running_services=$(docker-compose -f docker-compose.production.yml ps --services --filter "status=running")
    local expected_services=("api" "postgres" "redis" "prometheus" "grafana" "nginx")
    
    for service in "${expected_services[@]}"; do
        if echo "$running_services" | grep -q "$service"; then
            log_info "$service is running ✓"
        else
            log_error "$service is not running"
            exit 1
        fi
    done
    
    # Verify API endpoints
    verify_api_endpoint "Root endpoint" "http://localhost:8000/"
    verify_api_endpoint "Health endpoint" "http://localhost:8000/health"
    verify_api_endpoint "Metrics endpoint" "http://localhost:8000/metrics"
}

verify_api_endpoint() {
    local endpoint_name=$1
    local endpoint_url=$2
    
    if curl -s -f "$endpoint_url" > /dev/null; then
        log_info "$endpoint_name is accessible ✓"
    else
        log_error "$endpoint_name is not accessible"
        exit 1
    fi
}

# Display deployment summary
deployment_summary() {
    echo ""
    echo "🎉 Δ Delta OS Deployment Complete!"
    echo "======================================"
    echo "🌐 API URL: http://localhost:8000"
    echo "📊 Grafana: http://localhost:3000 (admin:${GRAFANA_PASSWORD:0:4}****)"
    echo "📈 Prometheus: http://localhost:9090"
    echo "🗄️  PostgreSQL: localhost:5432"
    echo "🔮 Redis: localhost:6379"
    echo ""
    echo "📋 Next steps:"
    echo "   - Set up SSL certificates in nginx/ssl/"
    echo "   - Configure domain names in production"
    echo "   - Set up automated backups"
    echo ""
    log_info "View logs: docker-compose -f docker-compose.production.yml logs -f"
}

# Main deployment function
main() {
    log_info "Starting Delta OS production deployment..."
    
    check_prerequisites
    load_env
    validate_env
    pull_images
    run_migrations
    start_services
    health_checks
    post_deployment_checks
    deployment_summary
    
    log_info "Δ Delta OS is now running in production! ✨"
}

# Run main function
main "$@"
