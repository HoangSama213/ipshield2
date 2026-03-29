from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def customer_login_required(view_func):
    """Chỉ cho phép khách hàng đã đăng nhập qua session"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.customer:
            messages.error(request, '⛔ Vui lòng đăng nhập để tiếp tục.')
            return redirect('login')  # ← đổi thành 'login' cho khớp urls.py
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Chỉ cho phép staff / admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, '⛔ Bạn không có quyền truy cập.')
            return redirect('portal_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper