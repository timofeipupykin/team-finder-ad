from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileEditForm, RegisterForm
from .models import User

FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            return redirect("projects:list")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_details(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects", "owned_projects__participants"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:details", user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:details", user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def participants_list(request):
    participants = User.objects.all()
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        me = request.user
        if active_filter == FILTER_OWNERS_OF_FAVORITE_PROJECTS:
            participants = participants.filter(owned_projects__in=me.favorites.all())
        elif active_filter == FILTER_OWNERS_OF_PARTICIPATING_PROJECTS:
            participants = participants.filter(owned_projects__in=me.participated_projects.all())
        elif active_filter == FILTER_INTERESTED_IN_MY_PROJECTS:
            participants = participants.filter(favorites__owner=me)
        elif active_filter == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            participants = participants.filter(participated_projects__owner=me)

    participants = participants.distinct().order_by("-id")
    page_obj = paginate_queryset(request, participants, per_page=12)
    query_prefix = f"filter={active_filter}&" if active_filter else ""

    return render(
        request,
        "users/participants.html",
        {
            "participants": participants,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        },
    )
