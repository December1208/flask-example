from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    email: Optional[str]
    password: Optional[str]
    salt: Optional[str]
    country_code: Optional[str]
    phone_number: Optional[str]
    last_login_at: Optional[int]
