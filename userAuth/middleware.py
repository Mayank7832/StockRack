from portfolio.models import User

class AttachMyUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.myuser = None
        user_id = request.session.get('user_id')

        if user_id:
            try: 
                request.myuser = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                pass

        
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response