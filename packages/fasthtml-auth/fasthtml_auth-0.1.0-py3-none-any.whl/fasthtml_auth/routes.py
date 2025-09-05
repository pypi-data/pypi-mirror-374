# auth/routes.py
from fasthtml.common import *
from .forms import create_login_form, create_register_form, create_forgot_password_form, create_profile_form


class AuthRoutes:
    """Handles route registration for auth system"""
    
    def __init__(self, auth_manager):
        self.auth = auth_manager
        self.routes = {}
    
    def register_all(self, app, prefix="/auth"):
        """Register all auth routes"""
        rt = app.route
        
        # Register each route group
        self._register_login_routes(rt, prefix)
        self._register_logout_route(rt, prefix)
        self._register_profile_route(rt, prefix)
        
        if self.auth.config.get('allow_registration'):
            self._register_registration_routes(rt, prefix)
        
        if self.auth.config.get('allow_password_reset'):
            self._register_password_reset_routes(rt, prefix)

        return self.routes
    
    def _register_login_routes(self, rt, prefix):
        """Register login routes"""

        # Login routes
        @rt(f"{prefix}/login", methods=["GET"])
        def login_page(req):
            error = req.query_params.get('error')
            # Get redirect destination from query params
            redirect_to = req.query_params.get('redirect_to', '/')
            return Title("Login"), Container(
                create_login_form(error=error, action=f"{prefix}/login", redirect_to=redirect_to)
            )
        self.routes['login_page'] = login_page
        
        @rt(f"{prefix}/login", methods=["POST"])
        async def login_submit(req, sess):
            form = await req.form()
            username = form.get('username', '').strip()
            password = form.get('password', '')
            
            # Authenticate
            user = self.auth.user_repo.authenticate(username, password)
            if user:
                # Set session
                sess['auth'] = user.username
                sess['user_id'] = user.id
                sess['role'] = user.role
                
                # Redirect to next URL or default
                redirect_url = form.get('redirect_to', '/')
                return RedirectResponse(redirect_url, status_code=303)
            # On failure, preserve the redirect_to parameter
            redirect_to = form.get('redirect_to', '/')
            error_url = f"{prefix}/login?error=invalid"
            if redirect_to != '/':
                error_url += f"&redirect_to={redirect_to}"
            return RedirectResponse(error_url, status_code=303)            
        
        self.routes['login_submit'] = login_submit
        
    def _register_logout_route(self, rt, prefix):
        @rt(f"{prefix}/logout")
        def logout(sess):
            sess.clear()
            return RedirectResponse(f"{prefix}/login", status_code=303)
        self.routes['logout'] = logout
        
    def _register_registration_routes(self, rt, prefix):

        # Optional: Register route
        if self.auth.config.get('allow_registration', False):
            @rt(f"{prefix}/register", methods=["GET"])
            def register_page(req):
                error = req.query_params.get("error")
                return Title("Register"), Container(
                    create_register_form(error=error, action=f"{prefix}/register")
                )
            
            @rt(f"{prefix}/register", methods=["POST"])
            async def register_submit(req, sess):
                form = await req.form()
                username = form.get('username', '').strip()
                email = form.get('email', '').strip()
                password = form.get('password', '')
                confirm = form.get('confirm_password', '')
                
                # Validation
                if password != confirm:
                    return RedirectResponse(f"{prefix}/register?error=password_mismatch", status_code=303)

                if password != confirm:
                    return RedirectResponse(f"{prefix}/register?error=password_mismatch", status_code=303)
                
                # Check if user exists
                if self.auth.user_repo.get_by_username(username):
                    return RedirectResponse(f"{prefix}/register?error=username_taken", status_code=303)
                
                # Create user
                try:
                    user = self.auth.user_repo.create(username, email, password)
                    if user:
                        # Auto-login after registration
                        sess['auth'] = user.username
                        sess['user_id'] = user.id
                        sess['role'] = user.role
                        return RedirectResponse('/', status_code=303)
                except Exception as e:
                    print(f"Registration error: {e}")
                    return RedirectResponse(f"{prefix}/register?error=creation_failed", status_code=303)
                       
                return RedirectResponse(f"{prefix}/register?error=creation_failed", status_code=303)
            
            self.routes['register_page'] = register_page
            self.routes['register_submit'] = register_submit
        
    def _register_password_reset_routes(self, rt, prefix):
        # Optional: Password reset route
        if self.auth.config.get('allow_password_reset', False):
            @rt(f"{prefix}/forgot", methods=["GET"])
            def forgot_page(req):
                error = req.query_params.get('error')
                success = req.query_params.get('success')
                return Title("Forgot Password"), create_forgot_password_form(
                    error=error, 
                    success=success,
                    action=f"{prefix}/forgot"
                )
            
            @rt(f"{prefix}/forgot", methods=["POST"])
            async def forgot_submit(req):
                form = await req.form()
                email = form.get('email', '').strip()
                
                # TODO: Implement actual password reset logic
                # For now, just show success message
                return RedirectResponse(f"{prefix}/forgot?success=sent", status_code=303)
            
            self.routes['forgot_password'] = forgot_page
            self.routes['forgot_submit'] = forgot_submit
        
    def _register_profile_route(self, rt, prefix):
        # Register route to a profile form
        @rt(f"{prefix}/profile", methods=["GET"])
        def profile_page(req):
            user = req.scope['user']  # Added by beforeware
            success = req.query_params.get('success')
            error = req.query_params.get('error')
            return Title("Profile"), create_profile_form(
                user=user,
                success=success,
                error=error,
                action=f"{prefix}/profile"
            )
        
        @rt(f"{prefix}/profile", methods=["POST"])
        async def profile_submit(req):
            user = req.scope['user']
            form = await req.form()
            
            try:
                # Update email if changed
                new_email = form.get('email', '').strip()
                if new_email and new_email != user.email:
                    self.auth.user_repo.update(user.id, email=new_email)
                
                # Handle password change
                current_password = form.get('current_password', '')
                new_password = form.get('new_password', '')
                confirm_password = form.get('confirm_password', '')
                
                if current_password or new_password:
                    if not current_password:
                        return RedirectResponse(f"{prefix}/profile?error=Current password required", status_code=303)
                    
                    if not self.auth.user_repo.verify_password(current_password, user.password):
                        return RedirectResponse(f"{prefix}/profile?error=Invalid current password", status_code=303)
                    
                    if new_password != confirm_password:
                        return RedirectResponse(f"{prefix}/profile?error=New passwords do not match", status_code=303)
                    
                    if len(new_password) < 8:
                        return RedirectResponse(f"{prefix}/profile?error=Password must be at least 8 characters", status_code=303)
                    
                    # Update password (repository will handle hashing)
                    self.auth.user_repo.update(user.id, password=new_password)
                
                return RedirectResponse(f"{prefix}/profile?success=1", status_code=303)
                
            except Exception as e:
                print(f"Profile update error: {e}")
                return RedirectResponse(f"{prefix}/profile?error=Update failed", status_code=303)
        
        self.routes['profile_page'] = profile_page
        self.routes['profile_submit'] = profile_submit