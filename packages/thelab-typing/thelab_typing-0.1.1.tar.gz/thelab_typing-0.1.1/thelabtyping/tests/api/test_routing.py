from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase
from django.urls import reverse

from thelabtyping.api.routing import HttpMethod, Router
from thelabtyping.api.status import Status

from ..sampleapp.views import (
    route_users,
    router,
    router_users_list,
)


class RouterTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="joe", password="password")
        self.client = Client()

    def test_reverse_router_urls(self) -> None:
        self.assertEqual(
            reverse("sampleapp:router-users-list"),
            "/api/router/users/",
        )
        self.assertEqual(
            reverse("sampleapp:router-users-detail", args=(42,)),
            "/api/router/users/42/",
        )
        self.assertEqual(
            reverse("sampleapp:alt-router-users-list"),
            "/api/alt-router/users/",
        )
        self.assertEqual(
            reverse("sampleapp:alt-router-users-detail", args=(42,)),
            "/api/alt-router/users/42/",
        )

    def test_router_index_main(self) -> None:
        url = reverse("sampleapp:index")
        self.assertEqual(url, "/api/router/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "sampleapp:index": "http://testserver/api/router/",
                "sampleapp:router-users-list": "http://testserver/api/router/users/",
            },
        )

    def test_router_index_unnamespaced(self) -> None:
        url = reverse("unnamespaced-router-index")
        self.assertEqual(url, "/unnamespaced-router/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "unnamespaced-router-index": "http://testserver/unnamespaced-router/",
                "unnamespaced-router-users-list": "http://testserver/unnamespaced-router/users/",
            },
        )

    def test_router_dispatch_get(self) -> None:
        resp = self.client.get(reverse("sampleapp:router-users-list"))
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            [
                {
                    "username": "joe",
                    "first_name": "",
                    "last_name": "",
                }
            ],
        )

    def test_router_dispatch_post(self) -> None:
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            reverse("sampleapp:router-users-list"),
            content_type="application/json",
            data={
                "username": "jack",
                "first_name": "Jack",
                "last_name": "Jackson",
            },
        )
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "username": "jack",
                "first_name": "Jack",
                "last_name": "Jackson",
            },
        )

    def test_router_dispatch_method_not_allowed(self) -> None:
        self.client.login(username="joe", password="password")
        resp = self.client.put(reverse("sampleapp:router-users-list"))
        self.assertEqual(resp.status_code, Status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_duplicate_route(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            router.route("users/", name="router-users-list-duplicate")

    def test_register_duplicate_route_method(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            route_users.get(router_users_list)

    def test_register_get(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.get(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.GET})

    def test_register_post(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.post(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.POST})

    def test_register_put(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.put(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.PUT})

    def test_register_patch(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.patch(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.PATCH})

    def test_register_delete(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.delete(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.DELETE})

    def test_register_during_route_creation(self) -> None:
        router = Router()
        route = router.route(
            "test/",
            name="test",
            get=router_users_list,
            post=router_users_list,
        )
        self.assertEqual(
            route.allowed_methods,
            {
                HttpMethod.GET,
                HttpMethod.POST,
            },
        )
