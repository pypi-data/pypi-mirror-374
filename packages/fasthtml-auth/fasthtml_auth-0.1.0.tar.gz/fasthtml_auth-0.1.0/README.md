# FastHTML-Auth

A comprehensive, drop-in authentication system for FastHTML applications with beautiful UI components, session management, and role-based access control.

This repro is intended to simplify the process of setting up a authentiation, user management and database setup for fastHTML apps.  Some of the code is based upon examples from Answer.ai code base, and for more information about fastHTML see [fastHTML](https://www.fastht.ml)

## Installation

```bash
pip install fasthtml-auth

## Features

- 🔐 **Secure Authentication** - Bcrypt password hashing, session management
- 👤 **User Management** - Registration, profile management, role-based access
- 🎨 **Beautiful UI** - Styled with MonsterUI components, fully responsive
- 🛡️ **Role-Based Access Control** - User, Manager, Admin roles with decorators
- 🔄 **Session Management** - Automatic session handling with FastHTML
- 📱 **Mobile Friendly** - Responsive design works on all devices
- ⚡ **Easy Integration** - Drop-in solution with minimal setup required

## Quick Start

### Installation

```bash
pip install fasthtml-auth
```

### Quick Start

```python
from fasthtml.common import *
from monsterui.all import *
from fasthtml_auth import AuthManager

# Initialize authentication system
auth = AuthManager(
    db_path="data/app.db",
    config={
        'allow_registration': True,
        'public_paths': ['/about', '/contact']
    }
)

# Set up database and middleware
db = auth.initialize()
beforeware = auth.create_beforeware()

# Create FastHTML app with authentication
app = FastHTML(
    before=beforeware,
    secret_key='your-secret-key-change-in-production',
    hdrs=Theme.blue.headers()  # MonsterUI styling
)

# Register authentication routes
auth.register_routes(app)

# Your protected routes
@app.route("/")
def dashboard(req):
    user = req.scope['user']  # Automatically available
    return Title("Dashboard"), H1(f"Welcome, {user.username}!")

@app.route("/admin")
@auth.require_admin()
def admin_panel(req):
    return Title("Admin"), H1("Admin Only Area")

if __name__ == "__main__":
    serve(port=5000)
```

That's it! Your app now has:
- Login/logout at `/auth/login` and `/auth/logout`
- User registration at `/auth/register` 
- Profile management at `/auth/profile`
- Role-based access control
- Beautiful, responsive forms

## Configuration

```python
config = {
    'login_path': '/auth/login',           # Custom login URL
    'public_paths': ['/about', '/api'],    # Routes that don't require auth
    'allow_registration': True,            # Enable user registration
    'allow_password_reset': False,         # Enable password reset (coming soon)
}

auth = AuthManager(db_path="data/app.db", config=config)
```

## User Roles and Access Control

### Available Roles
- **user** - Basic authenticated user
- **manager** - Manager privileges + user access  
- **admin** - Full system access

### Role-Based Route Protection

```python
# Require specific roles
@app.route("/manager-area")
@auth.require_role('manager', 'admin')
def manager_view(req, *args, **kwargs):
    return H1("Manager+ Only")

# Admin only shortcut
@app.route("/admin")
@auth.require_admin()
def admin_panel(req, *args, **kwargs):
    return H1("Admin Only")

# Check roles in templates
@app.route("/dashboard")
def dashboard(req):
    user = req.scope['user']
    
    admin_link = A("Admin Panel", href="/admin") if user.role == 'admin' else None
    manager_link = A("Manager Area", href="/manager") if user.role in ['manager', 'admin'] else None
    
    return Div(admin_link, manager_link)
```

## User Object

In protected routes, `req.scope['user']` contains:

```python
user.id          # Unique user ID  
user.username    # Username
user.email       # Email address
user.role        # 'user', 'manager', or 'admin'
user.active      # Boolean - account status
user.created_at  # Account creation timestamp
user.last_login  # Last login timestamp
```

## Database Schema

FastHTML-Auth automatically creates these tables:

```sql
-- Users table
CREATE TABLE user (
   id INTEGER PRIMARY KEY,
   username TEXT UNIQUE NOT NULL,
   email TEXT UNIQUE NOT NULL, 
   password TEXT NOT NULL,        -- Bcrypt hashed
   role TEXT DEFAULT 'user',
   created_at TEXT,
   last_login TEXT,
   active INTEGER DEFAULT 1
);

-- Sessions table (for future use)
CREATE TABLE session (
   id TEXT PRIMARY KEY,
   user_id INTEGER,
   data TEXT,
   expires_at TEXT,
   created_at TEXT
);
```

## Styling and Themes

FastHTML-Auth uses [MonsterUI](https://github.com/pixeltable/monster-ui) for beautiful, consistent styling.

```python
# Choose your theme
app = FastHTML(
    before=beforeware,
    hdrs=Theme.blue.headers()    # or Theme.red, Theme.green, etc.
)
```

All forms include:
- Responsive card-based layouts
- Professional input styling  
- Clear error/success messages
- Loading states and validation
- Mobile-optimized design

## API Reference

### AuthManager

```python
class AuthManager:
    def __init__(self, db_path="data/app.db", config=None)
    def initialize(self) -> Database
    def create_beforeware(self, additional_public_paths=None) -> Beforeware
    def register_routes(self, app, prefix="/auth") -> Dict
    def require_role(self, *roles) -> Decorator
    def require_admin(self) -> Decorator
    def get_user(self, username: str) -> Optional[User]
```

### Default Admin Account

A default admin account is created automatically:
- **Username**: `admin`  
- **Password**: `admin123`
- **Role**: `admin`

⚠️ **Change this password in production!**

## Available Routes

FastHTML-Auth automatically registers these routes:

- `GET /auth/login` - Login form
- `POST /auth/login` - Login submission  
- `GET /auth/logout` - Logout and redirect
- `GET /auth/register` - Registration form (if enabled)
- `POST /auth/register` - Registration submission (if enabled)
- `GET /auth/profile` - User profile management
- `POST /auth/profile` - Profile update submission

## Examples

### Complete Example App

```python
from fasthtml.common import *
from monsterui.all import *
from fasthtml_auth import AuthManager

# Initialize auth
auth = AuthManager(
    db_path="data/myapp.db",
    config={
        'allow_registration': True,
        'public_paths': ['/about', '/pricing', '/contact']
    }
)

db = auth.initialize()
beforeware = auth.create_beforeware()

app = FastHTML(
    before=beforeware,
    secret_key='super-secret-change-me',
    hdrs=Theme.blue.headers()
)

auth.register_routes(app)

# Public landing page
@app.route("/")
def home(req):
    user = req.scope.get('user')  # None if not logged in
    
    if user:
        return RedirectResponse('/dashboard')
    
    return Title("Welcome"), Container(
        H1("My Awesome App"),
        P("Please login to continue"),
        A("Login", href="/auth/login", cls=ButtonT.primary),
        A("Sign Up", href="/auth/register", cls=ButtonT.secondary)
    )

# Protected dashboard
@app.route("/dashboard")  
def dashboard(req, *args, **kwargs):
    user = req.scope['user']
    
    return Title("Dashboard"), Container(
        H1(f"Welcome back, {user.username}!"),
        
        # Role-specific content
        Card(
            CardHeader("Your Account"),
            CardBody(
                P(f"Role: {user.role.title()}"),
                P(f"Member since: {user.created_at[:10]}"),
                A("Edit Profile", href="/auth/profile", cls=ButtonT.primary)
            )
        ) if user.role == 'user' else None,
        
        # Manager content
        Card(
            CardHeader("Management Tools"),
            CardBody(
                A("View Reports", href="/reports", cls=ButtonT.primary),
                A("Manage Users", href="/users", cls=ButtonT.secondary)
            )
        ) if user.role in ['manager', 'admin'] else None
    )

if __name__ == "__main__":
    serve(port=5000)
```

## Dependencies

- `fasthtml` - Web framework
- `monsterui` - UI components
- `fastlite` - Database ORM
- `bcrypt` - Password hashing

## Development

```bash
# Clone the repository
git clone https://github.com/fromlittleacorns/fasthtml-auth.git
cd fasthtml-auth

# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest

# Run example
python examples/complete_app.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release
- Basic authentication system
- MonsterUI integration
- Role-based access control
- User registration and profiles

---

**FastHTML-Auth** - Authentication made simple for FastHTML applications.

For more examples and documentation, visit: [https://github.com/fromlittleacorns/fasthtml-auth](https://github.com/fromlittleacorns/fasthtml-auth)