def set_verified(backend, user, response, *args, **kwargs):
    if backend.name == "google-oauth2":
        user.is_verified = True
        user.save()