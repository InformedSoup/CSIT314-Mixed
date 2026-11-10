"""Control: SuspendProfileController - user story #12 (User Admin suspends a user profile).

Accounts under a suspended profile cannot log in until it is reactivated.
"""
from entity.user_profile import UserProfile


class SuspendProfileController:
    def suspendProfile(self, profileId: int, actingProfileId: int | None = None) -> tuple[bool, str]:
        profile = UserProfile.findById(profileId)
        if profile is None:
            return False, "User profile not found."
        if actingProfileId is not None and profileId == actingProfileId:
            return False, "You cannot suspend the profile you are logged in with."
        if not profile.isActive():
            return False, f"'{profile.profileName}' is already suspended."
        profile.setStatus("SUSPENDED")
        return True, (f"'{profile.profileName}' suspended. "
                      f"{profile.accountCount} account(s) under it can no longer log in.")

    def reactivateProfile(self, profileId: int) -> tuple[bool, str]:
        profile = UserProfile.findById(profileId)
        if profile is None:
            return False, "User profile not found."
        if profile.isActive():
            return False, f"'{profile.profileName}' is already active."
        profile.setStatus("ACTIVE")
        return True, f"'{profile.profileName}' reactivated."
