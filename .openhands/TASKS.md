# Task List

1. ✅ Initialize Django project with DRF, CORS, QR code support, and database config (SQLite dev, Postgres prod)

2. ✅ Inspect ref.html and extract UI assets/structure

3. 🔄 Design and implement models (Category, MenuItem, Bill, BillItem) and DRF serializers/viewsets

4. 🔄 Define permissions and roles (Admin Vijay full, Manager Sadam limited: can edit/save bills, cannot export)

5. ✅ Create management command to seed menu from ref.html and create users/permissions

6. 🔄 Build Django templates and static files using ref.html for responsive billing UI

7. ⏳ Wire frontend to DRF: menu fetch, cart, create/edit bills; CSRF, CORS, 0.0.0.0

8. 🔄 Implement export endpoint (CSV) restricted by can_export_bills permission

9. ✅ Implement QR endpoint returning base64 PNG

10. ✅ Register models in Django admin with useful list displays and search

11. 🔄 Run migrations, seed data, and start server on port 12000 accessible from any host

12. ⏳ Provide run instructions, local share QR usage, and security/performance notes


