# Task: Utilize Staff Table for Admin Role Checks and Remove Unused User Table

## Information Gathered
- The `User` model in `models.py` was defined but not used in the application.
- The `admin_login` function was using `Staff.query.filter_by(role='admin')` for authentication.
- The `staff_login` function checks if `staff.role == 'admin'`, and if so, sets `session['role'] = 'admin'` and redirects to `admin_dashboard`; otherwise, sets `'staff'`.
- The `user_login` function was checking `Staff` for admin role, but now only handles patient login.
- The goal was to use the `Staff` table's `role` for admin checks in both `admin_login` and `staff_login`, and remove the unused `User` table.

## Plan
- [x] Remove the `User` class from `models.py`.
- [x] Update `app.py` to remove `User` from the imports (not needed as it wasn't imported).
- [x] Modify `admin_login` function to query `Staff` for `role='admin'` (already done).
- [x] Modify `staff_login` function to check if `staff.role == 'admin'`, and if so, set `session['role'] = 'admin'` and redirect to `admin_dashboard`; otherwise, set `'staff'` (already done).
- [x] Update `user_login` function to only handle patient login, removing admin check.

## Dependent Files to be Edited
- `models.py`: Remove `User` class.
- `app.py`: Update login functions.

## Followup Steps
- [x] Recreate database tables to reflect model changes (run `db.create_all()`).
- [x] Test admin login via `/admin_login` with a staff member having `role='admin'`.
- [x] Test staff login via `/staff_login` with a staff member having `role='admin'` to ensure redirection to admin dashboard.
- [x] Test staff login with non-admin role to ensure normal staff dashboard access.
- [x] Verify that admin functionalities still work correctly.
- [x] Confirm that patient login via `/user/login` works without admin access.
