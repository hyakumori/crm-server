from django.contrib.auth.backends import ModelBackend as DjAuthBackend


class HyakumoriBackend(DjAuthBackend):
    def has_perm(self, user_obj, perm, obj=None):
        app_label = perm.split(".")[0]
        model_name = perm.split("_")[-1]  # let's assume that for now
        return user_obj.is_active and (
            super().has_perm(user_obj, perm, obj=obj)
            or super().has_perm(user_obj, f"{app_label}.manage_{model_name}", obj=obj)
        )
