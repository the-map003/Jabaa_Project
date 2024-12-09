from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
import re
from datetime import date
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger(__name__)


def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirmPassword", "")

        # Comprehensive validation
        errors = []

        # Full name validation
        if not full_name:
            errors.append("Full name is required.")
        elif len(full_name) < 2:
            errors.append("Full name must be at least 2 characters long.")

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            errors.append("Invalid email address.")

        # Password validation
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        elif not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        elif not re.search(r'\d', password):
            errors.append("Password must contain at least one number.")

        # Confirm password
        if password != confirm_password:
            errors.append("Passwords do not match.")

        # Check if email already exists
        if Account.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")

        # Handle errors
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "jabaa_admin_dashboard/signup.html")

        # Create and save the account
        try:
            account = Account(
                full_name=full_name,
                email=email,
                password=make_password(password),
            )
            account.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("signup_view")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "jabaa_admin_dashboard/signup.html")

    return render(request, "jabaa_admin_dashboard/signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # Validate form input
        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, "jabaa_admin_dashboard/login.html")

        # First, check Django User model by email
        try:
            # Find user by email (Django doesn't natively search by email)
            django_user = User.objects.get(email=email)
            
            # Authenticate using username
            user = authenticate(request, username=django_user.username, password=password)
            
            if user is not None:
                django_login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard")
        
        except User.DoesNotExist:
            # If no Django user, check custom Account model
            try:
                account = Account.objects.get(email=email)
                
                # Verify password for custom Account
                if check_password(password, account.password):
                    request.session['user_id'] = account.id
                    request.session['user_name'] = account.full_name
                    request.session['user_email'] = account.email
                    
                    messages.success(request, "Login successful!")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid email or password.")
            
            except Account.DoesNotExist:
                messages.error(request, "No account found with this email.")

    return render(request, "jabaa_admin_dashboard/login.html")

def dashboard(request):
    # Check if it's a session-based login or Django auth login
    if 'user_id' in request.session:
        # Custom Account model login
        user_id = request.session.get('user_id')
        user = Account.objects.get(id=user_id)
        context = {
            'user_name': user.full_name,
            'user_email': user.email
        }
    else:
        # Django auth login
        context = {
            'user_name': request.user.username,
            'user_email': request.user.email
        }
    
    return render(request, 'jabaa_admin_dashboard/dashboard.html', context)

@login_required
def logout_view(request):
    # Clear all session data
    request.session.flush()
    
    # Logout the user
    auth_logout(request)
    
    # Create response with security headers
    response = redirect('login_view')
    
    # Prevent caching and browser navigation
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    messages.success(request, "You have successfully logged out")
    return response

def forget_password(request):
    # Basic forget password view
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            account = Account.objects.get(email=email)
            # Generate and send password reset token
            # Implement password reset logic here
            messages.success(request, "Password reset instructions sent to your email.")
        except Account.DoesNotExist:
            messages.error(request, "No account found with this email.")
    
    return render(request, 'jabaa_admin_dashboard/forget_password.html')

def manage_accounts(request):
    # Fetch all accounts from the database
    accounts = Account.objects.all()
    return render(request, 'jabaa_admin_dashboard/manage_account.html', {'accounts': accounts})

def update_staff(request, staff_id):
    account = get_object_or_404(Account, id=staff_id)
    
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        old_password = request.POST.get('password')
        new_password = request.POST.get('confirmPassword')
        
        # Validate full name and email
        if not full_name or not email:
            messages.error(request, 'Full name and email are required.')
            return redirect('update_staff', staff_id=staff_id)
        
        # Check if email is already in use by another account
        if Account.objects.exclude(id=staff_id).filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('update_staff', staff_id=staff_id)
        
        # Update account details
        account.full_name = full_name
        account.email = email
        
        # Password update logic
        if old_password:
            # If old password is provided, validate and update
            if new_password:
                # Check existing password (assuming you're storing hashed passwords)
                if check_password(old_password, account.password):
                    account.password = make_password(new_password)
                else:
                    messages.error(request, 'Current password is incorrect.')
                    return redirect('update_staff', staff_id=staff_id)
        
        account.save()
        messages.success(request, 'Staff account updated successfully.')
        return redirect('manage_accounts')  # Redirect to staff management page
    
    # GET request - show update form
    return render(request, 'jabaa_admin_dashboard/update_account.html', {'account': account})

@csrf_protect
@require_POST
def delete_staff(request, staff_id):
    try:
        # Fetch the account
        account = get_object_or_404(Account, id=staff_id)
        
        # Perform deletion
        account.delete()
        
        # Return a successful JSON response
        return JsonResponse({
            'status': 'success', 
            'message': 'Staff account deleted successfully.'
        })
    except Exception as e:
        # Log the error (recommended)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Delete staff error: {str(e)}")
        
        # Return an error JSON response
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@login_required
def add_citizen(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        card_id = request.POST.get('card_id')
        contact_number = request.POST.get('contact')
        address = request.POST.get('address')

        # Validate inputs
        if not all([full_name, dob, gender, card_id, contact_number, address]):
            messages.error(request, "All fields are required!")
            return redirect('add_citizen')

        try:
            # Parse dob into a date object
            dob_date = date.fromisoformat(dob)

            # Save citizen data
            citizen = Citizen.objects.create(
                full_name=full_name,
                dob=dob_date,
                gender=gender,
                card_id=card_id,
                contact_number=contact_number,
                address=address,
            )
            messages.success(request, f"Citizen {citizen.full_name} (Age: {citizen.age}) registered successfully!")
            return redirect('add_citizen')
        except ValueError as e:
            messages.error(request, f"Invalid date format: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('add_citizen')

    return render(request, 'jabaa_admin_dashboard/add_citizen.html')

@login_required
def manage_citizen(request, citizen_id=None):
    if citizen_id:
        citizen = get_object_or_404(Citizen, id=citizen_id)
        context = {
            'citizen': citizen,
            'age': citizen.age
        }
    else:
        citizens = Citizen.objects.all()
        context = {
            'citizens': citizens
        }
    return render(request, 'jabaa_admin_dashboard/manage_citizen.html', context)


@login_required
def edit_citizen(request, citizen_id):
    citizen = get_object_or_404(Citizen, id=citizen_id)

    if request.method == 'POST':
        citizen.full_name = request.POST.get('fullName')
        citizen.dob = request.POST.get('dob')
        citizen.gender = request.POST.get('gender')
        citizen.card_id = request.POST.get('card_id')
        citizen.contact_number = request.POST.get('contact')
        citizen.address = request.POST.get('address')

        try:
            citizen.save()
            return redirect('manage_citizen')  
        except Exception as e:
            return render(request, 'jabaa_admin_dashboard/edit_citizen.html', {
                'citizen': citizen,
                'error': str(e)
            })

    return render(request, 'jabaa_admin_dashboard/edit_citizen.html', {'citizen': citizen})

@login_required
@csrf_exempt
def delete_citizen(request, citizen_id):
    if request.method == 'POST':
        logger.info(f"Request to delete citizen with ID {citizen_id}")
        citizen = get_object_or_404(Citizen, id=citizen_id)
        try:
            citizen.delete()
            return JsonResponse({'status': 'success', 'message': 'Citizen record deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting citizen: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        logger.warning("Invalid request method for delete_citizen")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})