from abc import ABC, abstractmethod


class BaseService:

    def __init__(self, api_key: str):
        self.api_key = api_key

    