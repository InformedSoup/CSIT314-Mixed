"""Control: ViewProfileController - user story #10 (User Admin views a user profile)."""
from entity.user_profile import UserProfile


class ViewProfileController:
    def viewProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.findById(profileId)

    def getAllProfiles(self) -> list[UserProfile]:
        return UserProfile.getAllProfiles()
