from marshmallow import Schema, fields, validates, ValidationError, validates_schema
import re


class CreateAccountSerializer(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)

    @validates("password")
    def validate_password(self, value):
        com = re.compile(
            """^(?=.*[a-zA-Z])(?=.*\d)(?=.*[~!@#$%^&*()_+`\-\[\]\\|·={}:";'<>?,.\/]).{8,30}$"""
        )
        if not com.match(value):
            raise ValidationError("密码必须包含数字、字母和特殊字符.")

    @validates_schema
    def validate_confirm_password(self, data, **kwargs):
        if data['confirm_password'] != data['password']:
            raise ValidationError("两次输入的密码不同.")


class Account(Schema):
    email = fields.Email()
    country_code = fields.Str()
    phone_number = fields.Str()
    last_login_at = fields.Integer()
