# -*- coding: utf-8 -*-
import logging
from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class LinkdocDomainBackend(object):
    #
    # The Django auth backend API
    #

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        """Django 认证后端接口

        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return: 如果验证成功，返回用户实例，否则返回 None
        """
        return self._authenticate(username, password)

    def get_user(self, user_id):
        user = None

        try:
            user = self.get_user_model().objects.get(pk=user_id)
        except ObjectDoesNotExist:
            pass

        return user

    def _authenticate(self, username, password):
        """实现通过 LDAP 认证代理服务进行认证的逻辑

        :param username: 用户名
        :param password: 密码
        :return: 如果验证成功，返回用户实例，否则返回 None
        """
        URL = settings.LDAP_AUTH_PROXY_ENDPOINT + '/ldap-auth'
        resp = requests.post(URL, json={
            'username': username,
            'password': password
        })

        try:
            data = resp.json()
        except JSONDecodeError:
            logger.warning('Unexpected error occur in LDAP auth proxy')
            return None

        if not data['ok']:
            if resp.status_code != 401:
                # 出现了账号密码错误以外的失败
                logger.warning('Error occur in LDAP auth proxy, message="%s"', data['message'])
            return None

        attrs = data['attrs']

        if not self.has_permission(username, attrs):
            return None

        return self.get_or_build_user(username, attrs)

    def has_permission(self, username, attrs):
        """判断该用户是否有使用该服务的特权

        :param username: 用户名
        :param attrs: 该用户的 LDAP 属性
        :return: 布尔值
        """
        if 'OU=技术研发部' in attrs['distinguishedName'][0].upper():
            return True
        return False

    def get_or_build_user(self, username, attrs):
        """如果用户名对应的用户不存在，则创建用户。否则从数据库获取该用户并返回

        :param username: 用户名
        :param attrs: 该用户的 LDAP 属性
        :return: 用户实例
        """
        model = self.get_user_model()

        query_field = model.USERNAME_FIELD
        query_value = username.lower()
        lookup = '{}__iexact'.format(query_field)

        try:
            user = model.objects.get(**{lookup: query_value})
        except model.DoesNotExist:
            user = model(**{query_field: query_value})
            built = True
        else:
            built = False

        if built:
            user.set_unusable_password()
            self.populate_user(user, attrs)
            user.save()

        return user

    def populate_user(self, user, attrs):
        """填充用户实例

        :param user: 用户实例
        :return: 用户实例
        """
        user.email = attrs['mail'][0]

    def get_user_model(self):
        """返回用户模型类"""
        return get_user_model()
