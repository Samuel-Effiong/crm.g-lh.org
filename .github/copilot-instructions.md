# Copilot Instructions for crm.g-lh.org

## Project Overview
- This is a Django-based CRM for religious institutions, using PostgreSQL as the primary database.
- The project is modularized by domain: `api/`, `bot/`, `church_work/`, `diaconate/`, `evangelism/`, `home/`, `pastoring/`, `personal_development/`, `project_management/`, `prophetic_vision/`, `site_admin/`, etc.
- REST API endpoints are defined in `api/` using Django REST Framework (DRF). Custom pagination, throttling, and user-related logic are implemented here.
- Wagtail CMS is integrated for content management, with API endpoints under `/api/v2/` and CMS admin at `/cms/`.
- Authentication uses Django Allauth and Djoser for RESTful auth endpoints. Token auth is available at `/api/api-token-auth/`.

## Key Workflows
- **Run the server:** `python manage.py runserver` (uses `assessment/settings.py`)
- **Migrate DB:** `python manage.py migrate`
- **Create superuser:** `python manage.py createsuperuser`
- **Run tests:** `python manage.py test`
- **Static files:** Managed via Django's staticfiles, with custom assets in `staticfiles/`.
- **Logging:** Errors are logged to `ERROR_REPORT.log` as configured in `assessment/settings.py`.

## API & Routing
- Main API endpoints are registered in `api/urls.py` and included at `/api/` in `assessment/urls.py`.
- Wagtail API endpoints: `/api/v2/pages`, `/api/v2/images`, `/api/v2/document`.
- Auth endpoints: `/auth/` (Djoser), `/accounts/` (Allauth), `/api/api-token-auth/` (DRF token).
- Each app has its own `urls.py` for modular routing.

## Patterns & Conventions
- **ViewSets:** DRF `ModelViewSet` is used for most resources, with custom actions via `@action`.
- **Serializers:** Located in each app or in `api/serializers.py` (may be empty if not used).
- **Models:** Each domain app defines its own models in `models.py`.
- **Permissions/Throttling:** DRF permission and throttle classes are used per-ViewSet.
- **Pagination:** Custom paginator in `api/paginator.py`.
- **Settings:** All global config is in `assessment/settings.py`.

## Integration Points
- **Wagtail:** For CMS and API, see `assessment/urls.py` and `api/urls.py`.
- **Djoser/Allauth:** For REST and web-based authentication.
- **Debug Toolbar:** Enabled via `django-debug-toolbar` and available at `/__debug__/`.

## Examples
- To add a new API resource: create a model, serializer, and ViewSet in the relevant app, then register it in `api/urls.py`.
- To add a new page type to the CMS: define a Wagtail Page model in the relevant app and register with Wagtail.

## References
- Main entry: `manage.py`, settings: `assessment/settings.py`, main URLs: `assessment/urls.py`, API: `api/`.
- For static assets, see `staticfiles/`.
- For error logs, see `ERROR_REPORT.log`.

---

If you are unsure about a workflow or pattern, check the relevant app's `urls.py`, `views.py`, and `models.py` for examples.
