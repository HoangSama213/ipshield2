from .models import Slider

def global_sliders(request):
    return {
        'sliders': Slider.objects.filter(is_active=True)
    }

def user_profile(request):
    if request.user.is_authenticated:
        from ipshieldapp.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return {'user_profile': profile}
    return {}