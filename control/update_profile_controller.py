"""Control: UpdateProfileController - user story #11 (User Admin updates a user profile)."""
from control.create_profile_controller import CreateProfileController
from entity.user_profile import UserProfile


class UpdateProfileController:
    def handleUpdateProfile(self, profileId: int, profileName: str, description: str,
                            role: str) -> tuple[bool, str]:
        profile = UserProfile.findById(profileId)
        if profile is None:
            return False, "User profile not found."
        # The four core profiles keep their role, otherwise e.g. nobody could reach the admin pages.
        if profile.isCore() and role != profile.role:
            return False, "The role of a core profile cannot be changed."
        errors = CreateProfileController().validateDetail(profileName, description, role,
                                                          excludeProfileId=profileId)
        if errors:
            return False, " ".join(errors)
        profile.updateProfile(profileName, description, role)
        return True, f"User profile '{profileName.strip()}' updated."
