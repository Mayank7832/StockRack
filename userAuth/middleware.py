from portfolio.models import User

class AttachMyUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #print("Session user_id:", request.session.get('user_id'))
        
        request.myuser = None
        user_id = request.session.get('user_id')
        if user_id:
            try:
                request.myuser = User.objects.get(userId=user_id)
            except User.DoesNotExist:
                pass
        #print("Attached user:", request.myuser)
        return self.get_response(request)