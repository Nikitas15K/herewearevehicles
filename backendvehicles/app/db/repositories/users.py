import requests
from typing import Optional
from app.models.users import UserPublic, UserInDB
from fastapi import Depends, HTTPException, status


class UsersRepository:
    def __init__(self):
        self.url = 'http://sohereweare_server_1:8000'

    @staticmethod
    def get_headers(token):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        return headers

    def get_current_user(self, token: str) -> Optional[UserPublic]:
        url = self.url + r'/api/users/me/'
        current_user = UserPublic(**requests.request('GET', url=url, headers=self.get_headers(token)).json())
        return current_user

