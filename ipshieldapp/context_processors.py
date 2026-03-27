from .models import Slider

def global_sliders(request):
    return {
        'sliders': Slider.objects.filter(is_active=True)
    }
