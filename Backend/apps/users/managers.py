import uuid
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_guest(self, email=None):
        """
        Creates a passwordless guest account so unauthenticated visitors can
        get a real JWT and use the normal cart/order/chat endpoints unchanged.
        If no email is given yet (e.g. opening chat before checkout), a
        placeholder is used until the guest supplies a real one at checkout.
        """
        email = self.normalize_email(email) if email else f"guest+{uuid.uuid4().hex}@guest.local"
        user  = self.model(email=email, is_guest=True)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)
