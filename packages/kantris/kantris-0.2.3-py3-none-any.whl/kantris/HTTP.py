import requests
from typing import Optional, Dict, Any, Union


class HTTP:
    class Request:
        def __init__(self,
            url:        str = None,
            method:     str = 'GET',
            json_body:  Optional[Dict[str, Any]] = None,
            form_body:  Optional[Dict[str, Any]] = None,
            headers:    Optional[Dict[str, str]] = None,
            timeout:    Union[int, float] = 10,
            secure:     bool = True
            ):
            self.url = url
            self.json_body = json_body
            self.form_body = form_body
            self.headers = headers
            self.method = method
            self.timeout = timeout
            self.secure = secure
        
        def URL(self, url):
            self.url = url
            return self
        
        def Json(self, json):
            self.json_body = json
            return self
        def Form(self, form):
            self.form_body = form

        def Method(self, method: str):
            self.method = method.Upper()
            return self

        def Secure(self, secure: bool = True):
            self.secure = secure
            return self

        def Send(self):
            _headers = self.headers.copy() if self.headers else {}
        
            if self.json_body is not None and self.form_body is not None:
                raise ValueError("Provide either json_body or form_body, not both.")
            
            if self.secure:
                url = f'https://{self.url}'
            else:
                url = f'http://{self.url}'

            try:
                response = requests.request(
                    method=self.method.upper(),
                    url=url,
                    json=self.json_body,
                    data=self.form_body,
                    headers=_headers,
                    timeout=self.timeout
                )
            except requests.RequestException as e:
                # Return error info in a consistent format
                return {
                    "status_code": None,
                    "headers": {},
                    "body": {
                        "error": str(e)
                    }
                }

            # Attempt to parse JSON response
            try:
                body_content = response.json()
            except ValueError:
                body_content = response.text

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body_content
            }
