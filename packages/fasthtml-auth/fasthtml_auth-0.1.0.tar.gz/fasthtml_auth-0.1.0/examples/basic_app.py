from fasthtml.common import *
from monsterui.all import *
from fasthtml_auth import AuthManager

css_links = [
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@unocss/reset/tailwind.min.css"),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css")
]

# Initialize auth system
auth = AuthManager(
    db_path="data/app.db",
    config={
        'login_path': '/auth/login',
        'public_paths': ['/about', '/contact'],  # Additional public pages
        'allow_registration': True,  # Enable registration
        'allow_password_reset': False,  # Disable password reset for now
    }
)

# Initialize database
try:
    db = auth.initialize()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    raise

# Create beforeware
try:
    beforeware = auth.create_beforeware(
        additional_public_paths=['/api/webhook', '/status']
    )
    print("✓ Beforeware created successfully")
except Exception as e:
    print(f"✗ Beforeware creation failed: {e}")
    raise

# Create app with auth beforeware
app = FastHTML(
    before=beforeware,
    secret_key='change-me-in-production',
    hdrs=Theme.blue.headers()
)

# Register auth routes
try:
    routes = auth.register_routes(app)
    print(f"✓ Auth routes registered: {list(routes.keys())}")
except Exception as e:
    print(f"✗ Route registration failed: {e}")
    raise

# Test basic route
@app.route("/")
def home(req):
    user = req.scope.get('user')
    if user:
        return Title("Dashboard"), Container(
            DivFullySpaced(
                H1(f"Welcome, {user.username}!"),
                Div(
                    A("Profile", href="/auth/profile", cls=ButtonT.secondary),
                    " ",
                    A("Logout", href="/auth/logout", cls=ButtonT.primary)
                )
            ),
            Card(
                CardHeader(H3("Account Information")),
                CardBody(
                    Div(
                        P(Strong("Username: "), user.username),
                        P(Strong("Role: "), user.role.title()),
                        P(Strong("Email: "), user.email),
                        P(Strong("Status: "), "Active" if user.active else "Inactive"),
                        cls="space-y-2"
                    )
                )
            ),
            Card(
                CardHeader(H3("Quick Links")),
                CardBody(
                    Div(
                        A("Manager View", href="/manager", cls=ButtonT.secondary) if user.role in ['manager', 'admin'] else None,
                        " ",
                        A("Admin Panel", href="/admin", cls=ButtonT.secondary) if user.role == 'admin' else None,
                        " ",
                        A("About Page", href="/about", cls=ButtonT.secondary),
                        cls="space-x-2"
                    )
                )
            ),
            cls=ContainerT.xl
        )
    else:
        # This should not happen due to beforeware, but just in case
        return RedirectResponse("/auth/login", status_code=303)

# Test admin route
@app.route("/admin")
@auth.require_admin()
def admin_panel(req):
    user = req.scope['user']
    return Title("Admin Panel"), Container(
        DivFullySpaced(
            H1("Admin Panel"),
            A("← Back to Dashboard", href="/", cls=ButtonT.secondary)
        ),
        Alert("This is admin-only content!", cls=AlertT.info),
        Card(
            CardHeader(H3("Admin Controls")),
            CardBody(
                P("Welcome to the admin panel, ", Strong(user.username), "!"),
                P("Here you can manage users, settings, and system configuration."),
                Div(
                    Button("Manage Users", cls=ButtonT.primary, disabled=True),
                    " ",
                    Button("System Settings", cls=ButtonT.secondary, disabled=True),
                    " ",
                    Button("View Logs", cls=ButtonT.outline, disabled=True),
                    cls="mt-4"
                ),
                P("(These buttons are disabled in demo)", cls="text-sm text-muted-foreground mt-2")
            )
        ),
        cls=ContainerT.md
    )

# Test manager route
@app.route("/manager") 
@auth.require_role('manager', 'admin')
def manager_view(req, *args, **kwargs):
    user = req.scope['user']
    return Title("Manager View"), Container(
        DivFullySpaced(
            H1("Manager Dashboard"),
            A("← Back to Dashboard", href="/", cls=ButtonT.secondary)
        ),
        Alert("Manager and Admin access only!", cls=AlertT.success),
        Card(
            CardHeader(H3("Manager Tools")),
            CardBody(
                P(f"Welcome, {user.username}! Your role: ", Strong(user.role.title())),
                P("This area is accessible to managers and administrators."),
                Div(
                    Button("View Reports", cls=ButtonT.primary, disabled=True),
                    " ",
                    Button("Manage Team", cls=ButtonT.secondary, disabled=True),
                    cls="mt-4"
                ),
                P("(These buttons are disabled in demo)", cls="text-sm text-muted-foreground mt-2")
            )
        ),
        cls=ContainerT.md
    )

# Public route for testing
@app.route("/about")
def about():
    return Title("About"), Container(
        DivFullySpaced(
            H1("About Our System"),
            A("← Home", href="/", cls=ButtonT.secondary)
        ),
        Card(
            CardHeader(H3("Authentication Demo")),
            CardBody(
                P("This is a public page that doesn't require login."),
                P("It demonstrates the public path configuration in the auth system."),
                Hr(),
                H4("Features Demonstrated:", cls="font-semibold mt-4 mb-2"),
                Ul(
                    Li("User authentication with session management"),
                    Li("Role-based access control (admin, manager, user)"),
                    Li("Public and protected routes"),
                    Li("Styled forms using MonsterUI"),
                    Li("Profile management"),
                    Li("Registration system"),
                    cls="list-disc pl-6 space-y-1"
                )
            )
        ),
        cls=ContainerT.md
    )

# Contact page - another public route
@app.route("/contact")
def contact():
    return Title("Contact"), Container(
        DivFullySpaced(
            H1("Contact Us"),
            A("← Home", href="/", cls=ButtonT.secondary)
        ),
        Card(
            CardHeader(H3("Get in Touch")),
            CardBody(
                P("This is another public page for demonstration."),
                P("Email: demo@example.com"),
                P("Phone: (555) 123-4567")
            )
        ),
        cls=ContainerT.md
    )

if __name__ == "__main__":
    print("\n🚀 Starting FastHTML app with authentication...")
    print("🔐 Default admin user: username='admin', password='admin123'")
    print("🌐 Visit: http://localhost:5001")
    print("📋 Available routes:")
    print("   • / (protected - redirects to login)")
    print("   • /auth/login (login form)")
    print("   • /auth/register (registration form)")
    print("   • /auth/profile (user profile - protected)")
    print("   • /manager (manager+ only)")
    print("   • /admin (admin only)")
    print("   • /about (public)")
    print("   • /contact (public)")
    serve(port=5001)