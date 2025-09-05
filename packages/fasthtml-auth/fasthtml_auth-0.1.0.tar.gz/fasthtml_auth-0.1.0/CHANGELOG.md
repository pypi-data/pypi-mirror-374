# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-09-03

### Added
- Initial release of FastHTML-Auth
- Complete authentication system with login/logout functionality  
- User registration and profile management
- Role-based access control (user, manager, admin)
- Beautiful MonsterUI-styled forms and components
- Session management with FastHTML
- Bcrypt password hashing for security
- SQLite database with fastlite ORM
- Modular, reusable architecture
- Comprehensive documentation and examples
- Default admin account creation (username: admin, password: admin123)
- Middleware-based route protection with decorators
- Public path configuration
- Mobile-responsive design
- Profile management with email and password updates
- Form validation and error handling

### Security
- Secure password hashing with bcrypt
- Session-based authentication
- Input validation and sanitization
- Protected routes with role-based access control

### Dependencies
- python-fasthtml >= 0.12.0
- monsterui >= 1.0.20
- fastlite >= 0.2.0
- bcrypt >= 4.0.0

### Documentation
- Complete README with examples
- Installation and usage instructions
- API reference
- Configuration guide