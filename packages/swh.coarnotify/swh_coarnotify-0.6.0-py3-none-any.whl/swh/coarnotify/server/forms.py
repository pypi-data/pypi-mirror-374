from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Actor


class ActorCreationForm(UserCreationForm):
    class Meta:
        model = Actor
        fields = ("email",)


class ActorChangeForm(UserChangeForm):
    class Meta:
        model = Actor
        fields = ("email",)
