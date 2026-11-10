"""Control: SearchProfileController - user story #13 (User Admin searches user profiles)."""
from entity.user_profile import UserProfile


class SearchProfileController:
    def handleSearchProfile(self, keyword: str) -> list[UserProfile]:
        if not (keyword or "").strip():
            return UserProfile.getAllProfiles()
        return UserProfile.searchProfiles(keyword)
