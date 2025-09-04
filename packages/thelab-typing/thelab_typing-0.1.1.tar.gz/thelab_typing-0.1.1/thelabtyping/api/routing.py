from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from functools import reduce
from operator import or_
from typing import Concatenate, NewType

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponseBase, HttpResponseNotAllowed
from django.urls import URLPattern, path, reverse
from django.urls.exceptions import NoReverseMatch
import pydantic

from ..abc import DictOf
from .responses import APIResponse


class HttpMethod(StrEnum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


URLPatternStr = NewType("URLPatternStr", str)
AllowedMethods = set[HttpMethod]

type ViewFn[**P, R: HttpResponseBase] = Callable[Concatenate[HttpRequest, P], R]

ALL_METHODS: AllowedMethods = {
    HttpMethod.GET,
    HttpMethod.POST,
    HttpMethod.PUT,
    HttpMethod.PATCH,
    HttpMethod.DELETE,
}


@dataclass
class RegisteredView[**P, R: HttpResponseBase]:
    """Container for a view function and its allowed HTTP methods."""

    methods: AllowedMethods
    fn: ViewFn[P, R]


@dataclass
class Route:
    """Represents a URL route with multiple HTTP method handlers."""

    name: str
    views: list[RegisteredView[[], HttpResponseBase]]

    def __init__(self, name: str) -> None:
        """Initialize a new route with the given name."""
        self.name = name
        self.views = []

    def get[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for GET requests."""
        return self.register({HttpMethod.GET})(fn)

    def post[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for POST requests."""
        return self.register({HttpMethod.POST})(fn)

    def put[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for PUT requests."""
        return self.register({HttpMethod.PUT})(fn)

    def patch[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for PATCH requests."""
        return self.register({HttpMethod.PATCH})(fn)

    def delete[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for DELETE requests."""
        return self.register({HttpMethod.DELETE})(fn)

    def register[**P, R: HttpResponseBase](
        self,
        methods: AllowedMethods = ALL_METHODS,
    ) -> Callable[
        [ViewFn[P, R]],
        ViewFn[P, R],
    ]:
        """Register a view function for the specified HTTP methods."""

        def decorator(view_fn: ViewFn[P, R]) -> ViewFn[P, R]:
            self.add_view(view_fn, methods)
            return view_fn

        return decorator

    def add_view[**P, R: HttpResponseBase](
        self,
        view_fn: ViewFn[P, R],
        methods: AllowedMethods,
    ) -> None:
        """Add a view function to this route for the given methods."""
        conflicts = self.allowed_methods & methods
        if conflicts:
            raise ImproperlyConfigured(
                f"Cannot {view_fn} for methods {conflicts}. Views already "
                "exist for these methods."
            )
        self.views.append(
            RegisteredView(
                methods=methods,
                fn=view_fn,
            )
        )

    def dispatch(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponseBase:
        """Dispatch an incoming request to the appropriate view function."""
        for view in self.views:
            if request.method in view.methods:
                return view.fn(request, *args, **kwargs)

        return HttpResponseNotAllowed(self.allowed_methods)

    @property
    def allowed_methods(self) -> AllowedMethods:
        """Get all HTTP methods supported by this route."""
        return reduce(or_, (view.methods for view in self.views), set())


type RouteMap = dict[URLPatternStr, Route]


RouterIndex = DictOf[str, pydantic.HttpUrl]


class Router:
    """URL router for organizing and dispatching API routes."""

    basename: str | None = None
    routes: RouteMap

    def __init__(
        self,
        basename: str | None = None,
        enable_index: bool = True,
    ) -> None:
        """Initialize a new router with optional basename and index view."""
        self.basename = basename
        self.routes: RouteMap = {}
        # Immediately register the root index view
        if enable_index:
            self.route("", name="index", get=self.index_view)

    def index_view(self, request: HttpRequest) -> APIResponse[RouterIndex]:
        """Auto-generated index view listing all available routes."""
        index = RouterIndex({})
        namespace = request.resolver_match.namespace if request.resolver_match else None
        for pattern, route in self.routes.items():
            name = f"{namespace}:{route.name}" if namespace else route.name
            try:
                url_path = reverse(name)
            except NoReverseMatch:
                # Catch and ignore this so that we skip URLs which require
                # params (e.g. detail views)
                continue
            url = request.build_absolute_uri(url_path)
            index[name] = pydantic.HttpUrl(url)
        return APIResponse(index)

    def route[**P, R: HttpResponseBase](
        self,
        url_pattern: str,
        name: str,
        get: ViewFn[P, R] | None = None,
        post: ViewFn[P, R] | None = None,
        put: ViewFn[P, R] | None = None,
        patch: ViewFn[P, R] | None = None,
        delete: ViewFn[P, R] | None = None,
    ) -> Route:
        """Register a new route with the given URL pattern and view functions."""
        _pattern = URLPatternStr(url_pattern)
        if _pattern in self.routes:
            raise ImproperlyConfigured(
                f"Cannot add route {_pattern} to router. Route already exists."
            )
        # Create route
        name = f"{self.basename}-{name}" if self.basename is not None else name
        route = Route(name)
        # Register any provided views
        views: dict[HttpMethod, ViewFn[P, R] | None] = {
            HttpMethod.GET: get,
            HttpMethod.POST: post,
            HttpMethod.PUT: put,
            HttpMethod.PATCH: patch,
            HttpMethod.DELETE: delete,
        }
        for method, view in views.items():
            if view is not None:
                route.register({method})(view)
        # Save and return the view
        self.routes[_pattern] = route
        return self.routes[_pattern]

    @property
    def urls(self) -> list[URLPattern]:
        """Get Django URLPattern objects for all registered routes."""
        return [
            path(pattern, route.dispatch, name=route.name)
            for pattern, route in self.routes.items()
        ]
