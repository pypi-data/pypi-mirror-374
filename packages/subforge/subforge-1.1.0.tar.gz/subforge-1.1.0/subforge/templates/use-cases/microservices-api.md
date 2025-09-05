# Microservices API Development Use Case

## Context Package
Comprehensive template for building scalable microservices API architectures with proper service isolation, inter-service communication, and data consistency.

## Primary Objectives
- Design and implement microservices architecture patterns
- Establish service boundaries and API contracts
- Implement inter-service communication mechanisms
- Ensure data consistency across distributed services
- Set up monitoring and observability

## Recommended Agent Team
- **@api-developer** - Primary API design and implementation
- **@backend-developer** - Service logic and business rules
- **@database-specialist** - Data modeling and consistency patterns
- **@devops-engineer** - Service orchestration and deployment
- **@performance-optimizer** - Load balancing and scaling
- **@security-auditor** - API security and authentication
- **@test-engineer** - Integration and contract testing

## Technology Stack Patterns

### Service Communication
- **Synchronous**: REST APIs, GraphQL
- **Asynchronous**: Message queues (RabbitMQ, Kafka), Event sourcing
- **Service Discovery**: Consul, Eureka, Kubernetes DNS

### Data Management
- **Database per Service**: Isolated data stores
- **Event Sourcing**: Audit trail and data reconstruction
- **CQRS**: Separate read/write models
- **Distributed Transactions**: Saga patterns

### Infrastructure
- **Containerization**: Docker containers
- **Orchestration**: Kubernetes, Docker Swarm
- **API Gateway**: Kong, Istio, AWS API Gateway
- **Monitoring**: Prometheus, Grafana, Jaeger

## Development Workflow

### Phase 1: Service Design
1. **@api-developer** - Define service boundaries and API contracts
2. **@database-specialist** - Design data models and relationships
3. **@security-auditor** - Define authentication and authorization patterns

### Phase 2: Implementation
1. **@backend-developer** - Implement service logic
2. **@api-developer** - Build API endpoints and documentation
3. **@database-specialist** - Set up data persistence layer

### Phase 3: Integration
1. **@devops-engineer** - Configure service orchestration
2. **@performance-optimizer** - Implement load balancing
3. **@test-engineer** - Create integration test suites

### Phase 4: Deployment
1. **@devops-engineer** - Deploy services to production
2. **@performance-optimizer** - Monitor performance metrics
3. **@security-auditor** - Validate security configurations

## Quality Gates

### Architecture Validation
- [ ] Service boundaries are properly defined
- [ ] API contracts are documented and versioned
- [ ] Data consistency patterns are implemented
- [ ] Security policies are enforced at service level

### Performance Validation
- [ ] Load testing passes for expected traffic
- [ ] Response times meet SLA requirements
- [ ] Resource utilization is optimized
- [ ] Auto-scaling mechanisms function correctly

### Integration Validation
- [ ] All service-to-service communications work
- [ ] Error handling and circuit breakers function
- [ ] Monitoring and alerting are operational
- [ ] Rollback procedures are tested

## Success Metrics
- **Service Availability**: 99.9% uptime per service
- **API Response Time**: < 200ms for standard operations
- **Error Rate**: < 0.1% across all services
- **Deployment Frequency**: Multiple deployments per day
- **Recovery Time**: < 15 minutes for critical issues

## Integration Points
- CI/CD pipelines for automated deployment
- Monitoring dashboards for operational visibility
- Documentation portal for API consumers
- Testing environments that mirror production

---
*Use Case Template v1.0 - SubForge Context Engineering*