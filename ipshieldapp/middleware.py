from .models import Customer

class CustomerSessionMiddleware:
    """
    Gắn customer vào request nếu khách hàng đang đăng nhập qua session.
    Truy cập bằng: request.customer (None nếu chưa đăng nhập)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        customer_id = request.session.get('customer_id')
        if customer_id:
            try:
                request.customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                request.customer = None
                del request.session['customer_id']
        else:
            request.customer = None

        return self.get_response(request)