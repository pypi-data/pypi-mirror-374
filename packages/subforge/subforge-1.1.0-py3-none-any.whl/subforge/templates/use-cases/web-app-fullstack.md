# Full-Stack Web Application Use Case

## Context Package
Complete template for building modern full-stack web applications with responsive frontends, robust backends, real-time features, and production-ready deployment.

## Primary Objectives
- Build responsive and performant user interfaces
- Implement secure authentication and authorization
- Create scalable backend APIs and services
- Integrate real-time features (WebSockets, Server-Sent Events)
- Deploy with CI/CD pipelines and monitoring

## Recommended Agent Team
- **@frontend-developer** - Primary UI/UX and client-side logic
- **@backend-developer** - Server-side logic and API development
- **@api-developer** - API design and integration patterns
- **@database-specialist** - Data modeling and optimization
- **@security-auditor** - Authentication, authorization, and security
- **@devops-engineer** - Deployment and infrastructure
- **@test-engineer** - Full-stack testing strategies
- **@performance-optimizer** - Application performance optimization

## Technology Stack Patterns

### Frontend Technologies
- **Frameworks**: React, Vue.js, Angular, Svelte
- **State Management**: Redux, Vuex, NgRx, Zustand
- **Styling**: Tailwind CSS, Styled Components, SCSS
- **Build Tools**: Vite, Webpack, Rollup, esbuild

### Backend Technologies
- **Node.js**: Express, Fastify, NestJS, Koa
- **Python**: FastAPI, Django, Flask, Starlette
- **Java**: Spring Boot, Quarkus, Micronaut
- **Go**: Gin, Echo, Fiber, Chi

### Database Solutions
- **Relational**: PostgreSQL, MySQL, SQLite
- **NoSQL**: MongoDB, DynamoDB, Firestore
- **Caching**: Redis, Memcached, CDN caching
- **Search**: Elasticsearch, Algolia, Typesense

### Infrastructure & Deployment
- **Cloud Platforms**: AWS, Azure, Google Cloud, Vercel
- **Containerization**: Docker, Kubernetes
- **CI/CD**: GitHub Actions, GitLab CI, CircleCI
- **Monitoring**: DataDog, New Relic, Sentry

## Development Workflow

### Phase 1: Architecture & Design
1. **@api-developer** - Define API contracts and data flow
2. **@frontend-developer** - Create UI/UX mockups and component architecture
3. **@database-specialist** - Design database schema and relationships
4. **@security-auditor** - Define security requirements and auth flow

### Phase 2: Core Development
1. **@backend-developer** - Implement server-side logic and APIs
2. **@frontend-developer** - Build UI components and client-side logic
3. **@database-specialist** - Set up database and data access layers
4. **@api-developer** - Implement API endpoints and documentation

### Phase 3: Integration & Features
1. **@frontend-developer** + **@backend-developer** - Integrate frontend with APIs
2. **@security-auditor** - Implement authentication and authorization
3. **@performance-optimizer** - Optimize application performance
4. **@test-engineer** - Create comprehensive test suites

### Phase 4: Deployment & Production
1. **@devops-engineer** - Set up deployment pipelines and infrastructure
2. **@performance-optimizer** - Configure monitoring and alerting
3. **@test-engineer** - Run end-to-end and performance tests
4. **@security-auditor** - Conduct security audits and penetration testing

## Quality Gates

### Frontend Validation
- [ ] Responsive design works across all device sizes
- [ ] Accessibility standards (WCAG 2.1 AA) are met
- [ ] Page load times are <3 seconds on 3G networks
- [ ] Cross-browser compatibility is verified
- [ ] UI components have comprehensive unit tests

### Backend Validation
- [ ] API endpoints have proper error handling
- [ ] Input validation and sanitization is implemented
- [ ] Database queries are optimized (no N+1 queries)
- [ ] Rate limiting and security headers are configured
- [ ] API documentation is complete and accurate

### Security Validation
- [ ] Authentication and authorization work correctly
- [ ] OWASP Top 10 vulnerabilities are addressed
- [ ] Data encryption in transit and at rest
- [ ] Input validation prevents injection attacks
- [ ] Security headers are properly configured

### Performance Validation
- [ ] Frontend bundle size is optimized (<250KB initial)
- [ ] Backend API response times are <200ms
- [ ] Database queries execute in <100ms
- [ ] CDN and caching strategies are effective
- [ ] Real user monitoring shows good metrics

## Success Metrics
- **Page Load Speed**: <3s First Contentful Paint
- **API Performance**: <200ms average response time
- **Uptime**: 99.9% availability
- **User Experience**: Lighthouse score >90
- **Security**: Zero critical vulnerabilities
- **SEO**: Core Web Vitals pass

## Real-Time Features
- **WebSocket Integration**: Real-time updates and notifications
- **Server-Sent Events**: Live data streaming
- **Push Notifications**: Browser and mobile notifications
- **Live Chat**: Real-time messaging capabilities
- **Collaborative Editing**: Multi-user real-time editing

## Production Readiness Checklist
- [ ] Environment configuration management
- [ ] Database migrations and versioning
- [ ] Automated backup and disaster recovery
- [ ] Health checks and monitoring dashboards
- [ ] Error tracking and logging
- [ ] Performance monitoring and alerting
- [ ] Security scanning and vulnerability management
- [ ] Load testing and capacity planning

---
*Use Case Template v1.0 - SubForge Context Engineering*