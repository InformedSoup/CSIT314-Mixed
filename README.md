# Interior Design Matching Platform — CSIT314 Group Mixed

An online platform that matches renovation customers with interior designers.
Built with Flask + SQLite, following the Boundary–Control–Entity (BCE) design.

## Run it

```bash
pip install -r requirements.txt
python seed_data.py        # creates instance/idp_platform.db with test data
python app.py              # http://127.0.0.1:5000
```

Demo logins (password `password123`):

| Role | Username |
| --- | --- |
| User Admin | `admin` |
| Interior Designer | `designer` |
| Customer | `customer` |
| Platform Management | `platform` |

## Tests

```bash
python -m pytest -v
```

Each test is named after its report test case (e.g. `test_TC_CREATE_02_...`).

## CI/CD

`.github/workflows/ci.yml` has two jobs:

1. **test** — on every push and pull request to `main`: installs dependencies, runs all tests,
   checks the test data script, uploads the test report.
2. **deploy** — only on a push to `main`, and only if **test** passed: triggers a deploy on Render.

One-time Render setup:
1. On render.com: New → Blueprint → pick this repo (it reads `render.yaml`).
2. In the service's Settings, copy the **Deploy Hook** URL.
3. In GitHub: Settings → Secrets and variables → Actions → New secret `RENDER_DEPLOY_HOOK` = that URL.

Until the secret is set, the deploy job skips itself, so CI still goes green.

## Structure (BCE)

| Folder | Layer | Contents |
| --- | --- | --- |
| `boundary/` | Boundary | Flask routes — one module per group of pages |
| `templates/` | Boundary | HTML pages rendered by the routes |
| `control/` | Control | One controller class per user story |
| `entity/` | Entity | Classes that hold data and read/write SQLite |

Flow for every feature: **page (boundary) → controller (control) → entity → database**.
Boundaries never touch the database directly; entities never deal with HTTP.

## User story → code map

| Taiga | User story | Controller | Boundary |
| --- | --- | --- | --- |
| #2 #14 #31 #40 | Log in (all roles) | `LoginController.authenticate` | `login_page.submitLogin` |
| #3 #15 #32 #41 | Log out (all roles) | `LogoutController.logout` | `login_page.submitLogout` |
| #4 | Create user account | `CreateUserController.handleCreateUser` | `create_user_page.html` |
| #5 | View user account | `ViewUserController.getUserAccount(s)` | `view_user_page.html` |
| #6 | Update user account | `UpdateUserController.handleUpdateUser` | `update_user_page.html` |
| #7 | Suspend user account | `SuspendUserController.suspendUser` | `view_user_details.html` |
| #8 | Search user account | `SearchUserController.searchUsers` | `view_user_page.html` |
| #9 | Create user profile | `CreateProfileController.createProfile` | `profile_form_page.html` |
| #10 | View user profile | `ViewProfileController.viewProfile` | `profile_detail_page.html` |
| #11 | Update user profile | `UpdateProfileController.handleUpdateProfile` | `profile_form_page.html` |
| #12 | Suspend user profile | `SuspendProfileController.suspendProfile` | `profile_detail_page.html` |
| #13 | Search user profile | `SearchProfileController.handleSearchProfile` | `profile_list_page.html` |
| #16 | Create company information | `CreateCompanyController.createCompany` | `company_form_page.html` |
| #17 | View company information | `CompanyInfoController.getCompanyInfo` | `company_info_page.html` |
| #18 | Update company information | `UpdateCompanyController.handleUpdate` | `company_form_page.html` |
| #19 | Delete company information | `DeleteCompanyController.deleteCompany` | `company_delete_page.html` |
| #20 | Search company information | `SearchCompanyController.handleSearchCompany` | `company_list_page.html` |
| #21 | Create current IDP | `CreateCurrentIDPController.handleCreateIDP` | `idp_form_page.html` |
| #22 | View current IDP | `ViewCurrentIDPController.getIDPDetails` | `idp_detail_page.html` |
| #23 | Search current IDPs (title / client) | `SearchCurrentIDPsController.searchCurrentIDPs` | `idp_list_page.html` |
| #24 | Update current IDP (+ mark completed) | `UpdateCurrentIDPController.handleUpdateIDP` / `markCompleted` | `idp_form_page.html` |
| #25 | Delete current IDP | `DeleteCurrentIDPController.deleteIDP` | `idp_delete_page.html` |
| #26 | Create past IDP | `CreatePastIDPController.createPastIDP` | `idp_form_page.html` |
| #27 | View past IDP | `ViewPastIDPController.getIDPDetails` | `idp_detail_page.html` |
| #28 | Search past IDPs (category / year) | `SearchPastIDPsController.searchPastIDPs` | `idp_list_page.html` |
| #29 | Update past IDP | `UpdatePastIDPController.handleUpdateIDP` | `idp_form_page.html` |
| #30 | Delete past IDP | `DeletePastIDPController.deleteIDP` | `idp_delete_page.html` |
| #33 | Search IDPs | `SearchIDPController.handleSearch` | `search_idp_page.html` |
| #34 | View IDP | `ViewIDPController.getIDPDetails` | `view_idp_page.html` |
| #35 | Save IDP to favourites | `SaveFavouriteController.saveIDP` | `view_idp_page.html` |
| #36 | View favourite list | `ViewFavouriteListController.getFavouriteList` | `favourite_list_page.html` |
| #37 | View IDP from favourite list | `FavouriteListController.getIDPDetails` | `view_idp_page.html` |
| #38 | Track IDP views | `TrackIDPViewsController.getViewCounts` | `insights_page.html` |
| #39 | Track IDP shortlists | `TrackIDPShortlistsController.getShortlistCounts` | `insights_page.html` |
| #42 | Create IDP category | `CreateCategoryController.createCategory` | `category_form_page.html` |
| #43 | View IDP category | `ViewCategoryController.getCategoryDetails` | `category_detail_page.html` |
| #44 | Update IDP category | `UpdateCategoryController.updateCategory` | `category_form_page.html` |
| #45 | Delete IDP category (unused only) | `DeleteCategoryController.deleteCategory` | `category_detail_page.html` |
| #46 | Search IDP category | `SearchCategoryController.searchCategories` | `category_list_page.html` |
| #47 | Daily report | `DailyReportController.generateDailyReport` | `report_page.html` |
| #48 | Weekly report | `WeeklyReportController.generateWeeklyReport` | `report_page.html` |
| #49 | Monthly report | `MonthlyReportController.generateMonthlyReport` | `report_page.html` |

### Entities

| Entity | Table | Notes |
| --- | --- | --- |
| `UserAccount`, `UserProfile`, `UserSession` | `user_account`, `user_profile`, `user_session` | Sessions record each login/logout (used by reports) |
| `Company` | `company` | A designer can own several |
| `InteriorDesignProject` → `CurrentIDP`, `PastIDP` | `idp` | Shared base class; `status` tells them apart |
| `FavouriteList` | `favourite` | Saving an IDP = shortlisting it |
| `IDPCategory` | `idp_category` | |
| `PlatformActivity` | (reads all tables) | One day of activity, used by the reports |

### Profiles and roles

A **user profile** grants one of four base roles (User Admin, Interior Designer,
Customer, Platform Management). The four core profiles always exist and keep
their role; User Admin can add more, e.g. "Premium Customer" with the Customer
role. Access control checks the role, so new profiles work without code changes.
Suspending a profile stops every account under it from logging in.

## Test data

`seed_data.py` generates the records used for the live demo. Dates are relative to the
day it runs, so reports always have recent activity. Re-run it to reset the database.

| Data type | Records |
| --- | --- |
| User accounts | 124 (4 demo + 120 generated) |
| User profiles | 4 core |
| Companies | ~110 |
| IDP categories | 100 (10 styles × 10 rooms) |
| IDPs (current + past) | ~260 |
| IDP views | 3,000 (some projects far more popular than others) |
| Favourites / shortlists | ~400 |
| Login sessions | 1,500 |

Design choices worth knowing for the demo:
- Refreshing a project page within 30 minutes does not add another view, so view counts stay honest.
- Reports for a period still in progress compare against the same number of days of the previous period.
- A category can only be deleted when no projects use it.

Customers can save projects to a favourites list (user story #35).
