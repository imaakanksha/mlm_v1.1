# Implementation Plan: The Multilingual Mandi

## Overview

This implementation plan breaks down the Multilingual Mandi platform into discrete, incremental coding tasks. The approach follows a bottom-up strategy: starting with core infrastructure and data models, then building service layers, integrating AI capabilities, implementing the frontend, and finally adding offline support and deployment configuration. Each task builds on previous work, ensuring no orphaned code and continuous integration.

The implementation uses a modern web stack:
- **Backend**: Node.js with Express, TypeScript
- **Frontend**: React with TypeScript, TailwindCSS
- **Database**: PostgreSQL with TypeORM
- **Cache**: Redis
- **AI Integration**: OpenAI APIs (GPT-4, Whisper, TTS)
- **Deployment**: Docker and Docker Compose

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Initialize monorepo with backend and frontend workspaces
  - Configure TypeScript, ESLint, Prettier
  - Set up Docker Compose with PostgreSQL and Redis services
  - Create environment variable configuration system
  - Set up testing frameworks (Jest for backend, Vitest for frontend, fast-check for property tests)
  - _Requirements: 12.1, 12.2, 12.4, 12.6, 15.1, 15.2_

- [x] 1.1 Write property test for environment configuration
  - **Property 53: Environment Variable Configuration**
  - **Validates: Requirements 12.2, 13.7**

- [x] 1.2 Write property test for invalid configuration handling
  - **Property 54: Invalid Configuration Handling**
  - **Validates: Requirements 12.7**

- [-] 2. Implement database schema and data models
  - [-] 2.1 Create database migration system using TypeORM
    - Define all table schemas (users, products, conversations, messages, transactions)
    - Add indexes for performance optimization
    - _Requirements: 14.3_

  - [ ] 2.2 Implement User entity and repository
    - Create User model with validation
    - Implement UserRepository with CRUD operations
    - _Requirements: 1.2, 1.6, 1.7_

  - [ ] 2.3 Write property tests for User entity
    - **Property 6: Registration Creates Profile**
    - **Property 8: Profile Update Persistence**
    - **Validates: Requirements 1.2, 1.6, 1.7**

  - [ ] 2.4 Implement Product entity and repository
    - Create Product and ProductTranslation models
    - Implement ProductRepository with multilingual support
    - _Requirements: 9.5, 9.6_

  - [ ] 2.5 Write property tests for Product entity
    - **Property 3: Automatic Product Translation**
    - **Validates: Requirements 9.5**

  - [ ] 2.6 Implement Message and Conversation entities
    - Create Message, MessageTranslation, and Conversation models
    - Implement repositories with efficient querying
    - _Requirements: 2.5, 2.6, 2.7_

  - [ ] 2.7 Write property tests for Message ordering
    - **Property 14: Conversation Message Display**
    - **Property 16: Message History Preservation**
    - **Validates: Requirements 2.3, 2.5, 2.7, 6.6, 10.1**

  - [ ] 2.8 Implement Transaction and PriceQuote entities
    - Create Transaction and PriceQuote models
    - Implement repositories with filtering and search
    - _Requirements: 6.6, 10.1, 10.3_

  - [ ] 2.9 Write property tests for Transaction entity
    - **Property 38: Transaction Summary Generation**
    - **Validates: Requirements 10.4**

- [ ] 3. Checkpoint - Database layer complete
  - Ensure all database tests pass
  - Verify migrations run successfully
  - Ask the user if questions arise

- [ ] 4. Implement Authentication Service
  - [ ] 4.1 Create authentication middleware and JWT utilities
    - Implement JWT token generation and verification
    - Create authentication middleware for protected routes
    - _Requirements: 11.2, 11.3_

  - [ ] 4.2 Implement password hashing with bcrypt
    - Create password hashing and verification utilities
    - _Requirements: 11.4_

  - [ ] 4.3 Write property test for password security
    - **Property 10: Password Security**
    - **Validates: Requirements 11.4**

  - [ ] 4.3 Implement registration endpoint
    - Create POST /api/auth/register endpoint
    - Validate input and create user profile
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 4.4 Write property tests for registration
    - **Property 6: Registration Creates Profile**
    - **Property 7: Invalid Registration Rejection**
    - **Validates: Requirements 1.2, 1.3, 1.6**

  - [ ] 4.5 Implement login and logout endpoints
    - Create POST /api/auth/login and POST /api/auth/logout
    - Implement session management with Redis
    - _Requirements: 11.3_

  - [ ] 4.6 Write property test for authentication requirement
    - **Property 9: Authentication Required**
    - **Validates: Requirements 11.2, 11.3, 10.7**

  - [ ] 4.7 Implement session timeout mechanism
    - Create middleware to check session expiry
    - Auto-logout after 30 minutes of inactivity
    - _Requirements: 11.6_

  - [ ] 4.8 Write property test for session timeout
    - **Property 11: Session Timeout**
    - **Validates: Requirements 11.6**

- [ ] 5. Implement User Management Service
  - [ ] 5.1 Create user profile endpoints
    - Implement GET /api/users/:id and PATCH /api/users/:id
    - Add language preference update endpoint
    - _Requirements: 1.4, 1.5, 1.7_

  - [ ] 5.2 Write property test for language preference
    - **Property 4: Language Preference Consistency**
    - **Validates: Requirements 1.4, 1.5, 5.5, 6.4**

  - [ ] 5.3 Implement account deletion endpoint
    - Create DELETE /api/users/:id with cascade deletion
    - _Requirements: 11.7_

  - [ ] 5.4 Write property test for account deletion
    - **Property 12: Account Deletion Completeness**
    - **Validates: Requirements 11.7**

- [ ] 6. Implement Translation Engine
  - [ ] 6.1 Create OpenAI API client for translation
    - Implement translation service using GPT-4 API
    - Add support for all 10 Indian languages
    - _Requirements: 2.1, 13.1_

  - [ ] 6.2 Implement Redis caching for translations
    - Cache translations with 7-day TTL
    - Implement cache key generation and lookup
    - _Requirements: 14.4_

  - [ ] 6.3 Write property tests for translation
    - **Property 1: Translation Completeness**
    - **Property 43: Translation Performance**
    - **Validates: Requirements 2.1, 2.2, 2.5**

  - [ ] 6.4 Implement translation fallback handling
    - Handle API failures gracefully
    - Return original text with error indicator
    - _Requirements: 2.4, 13.4_

  - [ ] 6.5 Write property test for translation fallback
    - **Property 15: Translation Fallback**
    - **Property 41: API Failure Graceful Degradation**
    - **Validates: Requirements 2.4, 13.4**

  - [ ] 6.6 Create batch translation endpoint
    - Implement POST /api/translate/batch for efficiency
    - _Requirements: 2.1_

- [ ] 7. Implement Speech Processor
  - [ ] 7.1 Create OpenAI Whisper integration for STT
    - Implement speech-to-text service
    - Support all 10 Indian languages
    - _Requirements: 3.1, 13.2_

  - [ ] 7.2 Create OpenAI TTS integration
    - Implement text-to-speech service
    - Support all 10 Indian languages
    - _Requirements: 3.3, 3.4, 13.2_

  - [ ] 7.3 Write property tests for speech processing
    - **Property 5: Speech-to-Text Round Trip**
    - **Property 44: Speech Processing Performance**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

  - [ ] 7.4 Implement speech error handling
    - Handle recognition failures with retry prompts
    - _Requirements: 3.5_

  - [ ] 7.5 Write property test for speech error handling
    - **Property 42: Speech Recognition Failure Recovery**
    - **Validates: Requirements 3.5**

- [ ] 8. Checkpoint - AI services integrated
  - Ensure translation and speech tests pass
  - Verify API integrations work with test keys
  - Ask the user if questions arise

- [ ] 9. Implement Messaging Service
  - [ ] 9.1 Create message sending endpoint
    - Implement POST /api/messages with translation
    - Support both text and voice messages
    - _Requirements: 2.1, 2.2, 3.1, 3.2_

  - [ ] 9.2 Write property tests for message delivery
    - **Property 13: Message Delivery**
    - **Validates: Requirements 2.2, 2.6**

  - [ ] 9.3 Implement conversation endpoints
    - Create GET /api/conversations and GET /api/conversations/:id
    - Return messages in user's preferred language
    - _Requirements: 2.3, 2.7_

  - [ ] 9.4 Write property test for conversation display
    - **Property 14: Conversation Message Display**
    - **Validates: Requirements 2.3, 2.7**

  - [ ] 9.5 Implement WebSocket server for real-time messaging
    - Set up Socket.io for real-time message delivery
    - Handle connection management and authentication
    - _Requirements: 2.2_

  - [ ] 9.6 Create message queue for offline users
    - Queue messages when recipient is offline
    - Deliver on reconnection
    - _Requirements: 7.3, 7.4_

- [ ] 10. Implement Product Catalog Service
  - [ ] 10.1 Create product CRUD endpoints
    - Implement POST, GET, PATCH, DELETE /api/products
    - Auto-translate product listings to all languages
    - _Requirements: 9.5, 9.6_

  - [ ] 10.2 Write property test for product translation
    - **Property 3: Automatic Product Translation**
    - **Validates: Requirements 9.5**

  - [ ] 10.3 Implement product search endpoint
    - Create GET /api/products/search with multilingual support
    - Support filtering by category, price, location
    - _Requirements: 9.1, 9.2, 9.4_

  - [ ] 10.4 Write property tests for product search
    - **Property 2: Cross-Language Search**
    - **Property 34: Search Filtering**
    - **Property 35: Search Result Ranking**
    - **Validates: Requirements 9.1, 9.2, 9.4, 9.7**

  - [ ] 10.5 Implement image upload functionality
    - Create POST /api/products/:id/images endpoint
    - Store images in local file storage (or S3-compatible)
    - _Requirements: 9.6_

  - [ ] 10.6 Write property test for search result completeness
    - **Property 33: Search Result Completeness**
    - **Validates: Requirements 9.3**

- [ ] 11. Implement Price Discovery Engine
  - [ ] 11.1 Create price recommendation algorithm
    - Implement ML-based price analysis using historical data
    - Calculate fair price, range, and confidence
    - _Requirements: 4.1, 4.2, 13.3_

  - [ ] 11.2 Write property tests for price recommendations
    - **Property 17: Price Recommendation Completeness**
    - **Property 45: Price Discovery Performance**
    - **Validates: Requirements 4.1, 4.2**

  - [ ] 11.3 Implement sparse data handling
    - Provide similar product suggestions when data is limited
    - _Requirements: 4.3_

  - [ ] 11.4 Write property test for sparse data handling
    - **Property 18: Sparse Data Handling**
    - **Validates: Requirements 4.3**

  - [ ] 11.5 Create price recommendation endpoint
    - Implement POST /api/pricing/recommend
    - Cache results in Redis with 6-hour TTL
    - _Requirements: 4.1, 4.6, 14.4_

  - [ ] 11.6 Write property tests for price updates
    - **Property 19: Price Update Reactivity**
    - **Property 20: Historical Data Integration**
    - **Validates: Requirements 4.6, 4.7**

  - [ ] 11.7 Implement transaction recording for price data
    - Create POST /api/transactions endpoint
    - Update price history database
    - _Requirements: 4.7_

- [ ] 12. Implement Market Intelligence Module
  - [ ] 12.1 Create price trend analysis endpoint
    - Implement GET /api/intelligence/trends
    - Return 30-day historical data with charts
    - _Requirements: 5.1, 5.2_

  - [ ] 12.2 Write property test for market intelligence period
    - **Property 21: Market Intelligence Period**
    - **Validates: Requirements 5.1**

  - [ ] 12.3 Implement demand forecasting
    - Create ML model for 7-day demand prediction
    - _Requirements: 5.3_

  - [ ] 12.4 Write property tests for demand forecasting
    - **Property 22: Demand Forecast Generation**
    - **Property 23: Market Intelligence Insights**
    - **Validates: Requirements 5.3, 5.4**

  - [ ] 12.5 Create vendor price comparison endpoint
    - Implement GET /api/intelligence/compare
    - Compare vendor prices to market averages
    - _Requirements: 5.6_

  - [ ] 12.6 Write property test for price comparison
    - **Property 24: Price Comparison Availability**
    - **Validates: Requirements 5.6**

  - [ ] 12.7 Implement market change notifications
    - Create notification system for significant price changes
    - _Requirements: 5.7_

- [ ] 13. Checkpoint - Backend services complete
  - Ensure all backend tests pass
  - Verify all API endpoints work correctly
  - Test end-to-end flows (registration → messaging → pricing)
  - Ask the user if questions arise

- [ ] 14. Implement Negotiation Assistant
  - [ ] 14.1 Create quote analysis service
    - Use GPT-4 to analyze quotes against fair prices
    - Provide feedback in both users' languages
    - _Requirements: 6.1, 6.4_

  - [ ] 14.2 Write property tests for negotiation
    - **Property 25: Quote Analysis**
    - **Property 26: Counteroffer Suggestions**
    - **Validates: Requirements 6.1, 6.3**

  - [ ] 14.3 Implement stalemate detection and resolution
    - Detect 3+ rounds without agreement
    - Suggest compromise prices
    - _Requirements: 6.5_

  - [ ] 14.4 Write property test for stalemate resolution
    - **Property 27: Stalemate Resolution**
    - **Validates: Requirements 6.5**

  - [ ] 14.5 Create negotiation endpoints
    - Implement POST /api/negotiations/quote
    - Implement POST /api/negotiations/agree
    - _Requirements: 6.1, 6.7_

  - [ ] 14.6 Write property test for agreement recording
    - **Property 28: Agreement Recording**
    - **Validates: Requirements 6.7**

- [ ] 15. Implement Transaction Service
  - [ ] 15.1 Create transaction history endpoints
    - Implement GET /api/transactions with filtering
    - Support search by product, date, counterparty
    - _Requirements: 10.2, 10.3_

  - [ ] 15.2 Write property tests for transaction history
    - **Property 36: Transaction History Ordering**
    - **Property 37: Transaction History Search**
    - **Validates: Requirements 10.2, 10.3**

  - [ ] 15.3 Implement transaction export endpoint
    - Create GET /api/transactions/export
    - Support JSON and CSV formats with translation
    - _Requirements: 10.6_

  - [ ] 15.4 Write property test for transaction export
    - **Property 39: Transaction Export Format**
    - **Validates: Requirements 10.6**

- [ ] 16. Implement error handling and logging
  - [ ] 16.1 Create global error handler middleware
    - Handle all error types with appropriate responses
    - Localize error messages based on user language
    - _Requirements: 8.5, 12.5, 12.7_

  - [ ] 16.2 Write property tests for error handling
    - **Property 40: Error Message Localization**
    - **Validates: Requirements 8.5, 12.5, 12.7**

  - [ ] 16.3 Implement logging system
    - Set up Winston for structured logging
    - Log all errors, API calls, and performance metrics
    - _Requirements: 13.6, 14.6_

  - [ ] 16.4 Implement rate limiting middleware
    - Use express-rate-limit for API protection
    - Set limit to 100 requests per minute per user
    - _Requirements: 14.7_

  - [ ] 16.5 Write property test for rate limiting
    - **Property 49: Rate Limiting Enforcement**
    - **Validates: Requirements 14.7**

- [ ] 17. Build frontend foundation
  - [ ] 17.1 Initialize React app with TypeScript
    - Set up Vite, React Router, TailwindCSS
    - Configure API client with axios
    - _Requirements: 8.1, 8.4_

  - [ ] 17.2 Create authentication UI components
    - Build registration and login forms
    - Support all 10 language selections
    - _Requirements: 1.1, 1.3_

  - [ ] 17.3 Implement authentication state management
    - Use React Context for auth state
    - Handle token storage and refresh
    - _Requirements: 11.3_

  - [ ] 17.4 Create protected route wrapper
    - Redirect unauthenticated users to login
    - _Requirements: 11.2_

- [ ] 18. Build messaging UI
  - [ ] 18.1 Create conversation list component
    - Display all user conversations
    - Show last message preview and timestamp
    - _Requirements: 2.3_

  - [ ] 18.2 Create message thread component
    - Display messages in chronological order
    - Show messages in user's preferred language
    - Support text and voice messages
    - _Requirements: 2.3, 2.7, 3.3_

  - [ ] 18.3 Implement message input component
    - Support text input and voice recording
    - Show translation indicator
    - _Requirements: 2.1, 3.1_

  - [ ] 18.4 Integrate WebSocket for real-time updates
    - Connect to Socket.io server
    - Update UI on new messages
    - _Requirements: 2.2_

  - [ ] 18.5 Write property test for UI feedback timing
    - **Property 50: Visual Feedback Timing**
    - **Property 51: Action Confirmation**
    - **Validates: Requirements 8.2, 8.3**

- [ ] 19. Build product catalog UI
  - [ ] 19.1 Create product listing component
    - Display products with images and prices
    - Support grid and list views
    - _Requirements: 9.3_

  - [ ] 19.2 Create product search component
    - Implement search bar with filters
    - Support category, price range, location filters
    - _Requirements: 9.1, 9.4_

  - [ ] 19.3 Create product detail component
    - Show full product information
    - Display vendor details and contact button
    - _Requirements: 9.3_

  - [ ] 19.4 Create product creation form (for vendors)
    - Support image upload and multilingual input
    - _Requirements: 9.6_

- [ ] 20. Build pricing and negotiation UI
  - [ ] 20.1 Create price recommendation component
    - Display fair price with confidence indicator
    - Show price range and market trends
    - _Requirements: 4.2, 4.5_

  - [ ] 20.2 Create negotiation interface
    - Show quote history and AI suggestions
    - Support sending counteroffers
    - _Requirements: 6.1, 6.3_

  - [ ] 20.3 Create market intelligence dashboard
    - Display price trends with charts (using Chart.js or Recharts)
    - Show demand forecasts and insights
    - _Requirements: 5.1, 5.2, 5.4_

- [ ] 21. Build transaction history UI
  - [ ] 21.1 Create transaction list component
    - Display transactions in chronological order
    - Support filtering and search
    - _Requirements: 10.2, 10.3_

  - [ ] 21.2 Create transaction detail component
    - Show complete transaction information
    - Provide export button
    - _Requirements: 10.4, 10.6_

- [ ] 22. Implement offline capability
  - [ ] 22.1 Set up Service Worker with Workbox
    - Configure PWA manifest
    - Cache static assets and API responses
    - _Requirements: 7.6_

  - [ ] 22.2 Implement IndexedDB for offline storage
    - Store conversations, messages, and price data
    - _Requirements: 7.2, 7.6_

  - [ ] 22.3 Write property test for offline data access
    - **Property 30: Offline Data Access**
    - **Validates: Requirements 7.2, 7.6**

  - [ ] 22.3 Create offline detection and notification
    - Detect network status changes
    - Show offline indicator in UI
    - _Requirements: 7.1_

  - [ ] 22.4 Write property test for offline mode transition
    - **Property 29: Offline Mode Transition**
    - **Validates: Requirements 7.1**

  - [ ] 22.5 Implement message queuing for offline mode
    - Queue messages in IndexedDB when offline
    - Sync on reconnection
    - _Requirements: 7.3, 7.4, 7.5_

  - [ ] 22.6 Write property test for offline sync
    - **Property 31: Offline Message Queuing**
    - **Property 32: Sync Round Trip**
    - **Validates: Requirements 7.3, 7.4, 7.5**

- [ ] 23. Checkpoint - Frontend complete
  - Ensure all UI components render correctly
  - Test user flows in browser
  - Verify offline mode works
  - Ask the user if questions arise

- [ ] 24. Implement performance optimizations
  - [ ] 24.1 Add database query optimization
    - Verify all indexes are in place
    - Optimize N+1 query problems
    - _Requirements: 14.3_

  - [ ] 24.2 Write property test for query performance
    - **Property 47: Database Query Performance**
    - **Validates: Requirements 14.3**

  - [ ] 24.3 Implement Redis caching strategy
    - Cache translations, price data, product listings
    - Set appropriate TTLs
    - _Requirements: 14.4_

  - [ ] 24.4 Write property test for caching effectiveness
    - **Property 48: Caching Effectiveness**
    - **Validates: Requirements 14.4**

  - [ ] 24.5 Add response time monitoring
    - Log slow requests (>3 seconds)
    - _Requirements: 14.1, 14.6_

  - [ ] 24.6 Write property tests for performance
    - **Property 46: General Response Time**
    - **Validates: Requirements 14.1**

- [ ] 25. Create deployment configuration
  - [ ] 25.1 Create production Dockerfiles
    - Dockerfile for backend service
    - Dockerfile for frontend (Nginx)
    - _Requirements: 12.3_

  - [ ] 25.2 Create Docker Compose for production
    - Configure all services (backend, frontend, PostgreSQL, Redis)
    - Set up networking and volumes
    - _Requirements: 12.3_

  - [ ] 25.3 Create deployment documentation
    - Write README.md with setup instructions
    - Document environment variables
    - Include troubleshooting guide
    - _Requirements: 12.1, 12.5_

  - [ ] 25.4 Create automated setup script
    - Write setup.sh for one-command deployment
    - Handle dependency checks
    - _Requirements: 12.6_

  - [ ] 25.5 Add health check endpoints
    - Implement GET /api/health
    - Check database and Redis connectivity
    - _Requirements: 12.3_

- [ ] 26. Create .kiro directory with hackathon materials
  - [ ] 26.1 Create project overview document
    - Explain the problem and solution
    - Highlight social impact (Viksit Bharat)
    - _Requirements: 12.4_

  - [ ] 26.2 Create architecture documentation
    - Include system diagrams
    - Explain technology choices
    - _Requirements: 12.4, 15.5_

  - [ ] 26.3 Create demo script
    - Step-by-step demo instructions
    - Include sample data and scenarios
    - _Requirements: 12.4_

  - [ ] 26.4 Create video demo (optional)
    - Record 3-5 minute demo video
    - Show key features and impact
    - _Requirements: 12.4_

- [ ] 27. Final integration testing and polish
  - [ ] 27.1 Run full property test suite
    - Execute all 55 property tests
    - Verify 100+ iterations per test
    - _All Properties_

  - [ ] 27.2 Run integration test suite
    - Test all API endpoints
    - Test cross-service interactions
    - _All Requirements_

  - [ ] 27.3 Perform manual testing checklist
    - Test all language pairs
    - Test on mobile devices
    - Test offline mode thoroughly
    - Verify accessibility
    - _Requirements: 8.1, 8.6, 8.7_

  - [ ] 27.4 Fix any bugs found during testing
    - Address test failures
    - Improve error messages
    - _All Requirements_

  - [ ] 27.5 Performance testing and optimization
    - Load test with simulated users
    - Optimize slow endpoints
    - _Requirements: 14.1, 14.2_

- [ ] 28. Final checkpoint - Production ready
  - Ensure all tests pass (unit, property, integration)
  - Verify deployment works from clean state
  - Confirm all documentation is complete
  - Demo the platform end-to-end
  - Ask the user if questions arise

## Notes

- All tasks are required for comprehensive implementation with full test coverage
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- The implementation follows a bottom-up approach: infrastructure → services → AI integration → frontend → deployment
- All code should include inline documentation and follow TypeScript best practices
- Environment variables should be documented in .env.example file
- The platform should be fully functional and demo-ready after task 28
