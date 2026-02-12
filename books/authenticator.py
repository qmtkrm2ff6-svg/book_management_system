from rest_framework_simplejwt.authentication import JWTAuthentication

class FlexibleJWTAuthentication(JWTAuthentication):
    """
    自定义认证类：如果用户没传 Bearer，自动帮他加上
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        # 如果发现传过来的 header 只有 Token 没前缀，手动修正它
        if b' ' not in header:
            # 假设当前 header 就是 Token，给它强行加上 Bearer 前缀
            header = b'Bearer ' + header
            
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token