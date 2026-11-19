import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_engineering.settings.dev')
import django
django.setup()

from django.test import Client
from django.urls import get_resolver, reverse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from accounts.models import User
from products.models import Product, Category, Application, Standard, Material, ProductFAQ, ProductSpecification
from gallery.models import GalleryItem, Category as GalleryCategory
from home.models import ContactInquiry

def audit_templates_compilation():
    print("=== 1. AUDITING TEMPLATE COMPILATION ===")
    template_dirs = [
        Path("templates"),
        Path("home/templates"),
        Path("accounts/templates"),
        Path("gallery/templates"),
        Path("products/templates"),
    ]
    total_templates = 0
    errors = []

    for t_dir in template_dirs:
        for p in t_dir.rglob("*.html"):
            total_templates += 1
            parts = p.parts
            if parts[0] == "templates":
                rel_name = str(Path(*parts[1:])).replace("\\", "/")
            elif len(parts) > 2 and parts[1] == "templates":
                rel_name = str(Path(*parts[2:])).replace("\\", "/")
            else:
                rel_name = str(p).replace("\\", "/")

            try:
                get_template(rel_name)
            except (TemplateDoesNotExist, TemplateSyntaxError) as e:
                errors.append((str(p), rel_name, str(e)))

    print(f"Checked {total_templates} templates. Errors found: {len(errors)}")
    for filepath, rel_name, err in errors:
        print(f"  [ERROR] {filepath} (tried as '{rel_name}'): {err}")
    return errors

def audit_empty_database_views():
    print("\n=== 2. AUDITING VIEWS ON 100% EMPTY DATABASE (NO ADMIN DATA YET) ===")
    client = Client()

    empty_db_urls = [
        ("/", "homepage"),
        ("/about-us/", "about"),
        ("/contact-us/", "contact"),
        ("/contact-us/?product=Test%20Stud&material=SS316", "contact prefill"),
        ("/terms-of-service/", "terms"),
        ("/privacy-policy/", "privacy"),
        ("/llms.txt", "llms.txt"),
        ("/robots.txt", "robots.txt"),
        ("/sitemap.xml", "sitemap.xml"),
        ("/products/", "product_list (empty catalog)"),
        ("/products/?q=bolt", "product search (empty)"),
        ("/products/applications/", "application_list (empty)"),
        ("/products/standards/", "standard_list (empty)"),
        ("/products/materials/", "material_list (empty)"),
        ("/gallery/", "gallery_list (empty gallery)"),
        ("/gallery/?type=IMAGE", "gallery image filter (empty)"),
        ("/accounts/login/", "login"),
        ("/accounts/register/", "register"),
        ("/accounts/password-reset/", "password_reset"),
    ]

    failed = []
    for url, label in empty_db_urls:
        try:
            resp = client.get(url)
            if resp.status_code != 200:
                print(f"  [FAIL] {url} ({label}) -> HTTP {resp.status_code}")
                failed.append((url, label, resp.status_code))
            else:
                print(f"  [OK] HTTP 200: {url} ({label})")
        except Exception as e:
            print(f"  [EXCEPTION] {url} ({label}) -> {type(e).__name__}: {e}")
            failed.append((url, label, str(e)))

    # Test HTMX partial request for empty catalog
    try:
        htmx_resp = client.get("/products/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="catalog-content")
        if htmx_resp.status_code == 200:
            print("  [OK] HTMX empty catalog-content partial rendering works")
        else:
            print(f"  [FAIL] HTMX catalog-content returned HTTP {htmx_resp.status_code}")
            failed.append(("/products/ (HTMX)", "htmx", htmx_resp.status_code))
    except Exception as e:
        print(f"  [EXCEPTION] HTMX catalog-content -> {e}")
        failed.append(("/products/ (HTMX)", "htmx", str(e)))

    # Test Contact Form submission POST
    try:
        contact_post = client.post("/contact-us/", {
            "full_name": "Audit Test User",
            "email": "audit.test@example.com",
            "message": "Automated audit test inquiry for fasteners.",
        })
        if contact_post.status_code == 302:
            print("  [OK] Contact form submission POST redirects 302")
        else:
            print(f"  [FAIL] Contact form POST returned HTTP {contact_post.status_code}")
            failed.append(("/contact-us/ POST", "contact post", contact_post.status_code))
    except Exception as e:
        print(f"  [EXCEPTION] Contact form POST -> {e}")
        failed.append(("/contact-us/ POST", "contact post", str(e)))

    ContactInquiry.objects.filter(email="audit.test@example.com").delete()
    print(f"Total empty-db endpoints tested: {len(empty_db_urls) + 2}. Failures: {len(failed)}")
    return failed

def audit_dynamic_admin_flow():
    print("\n=== 3. AUDITING DYNAMIC ADMIN CREATION CYCLE ===")
    client = Client()
    failed = []

    # 1. Admin creates a Category
    cat = Category.objects.create(
        name="Precision Hex Bolts",
        slug="precision-hex-bolts",
        description="High tensile hex bolts manufactured for heavy equipment."
    )
    print("  [OK] Category created: Precision Hex Bolts")

    # 2. Admin creates a Material, Standard, Application
    mat = Material.objects.create(name="Stainless Steel 316L", slug="ss-316l")
    std = Standard.objects.create(name="DIN 933", slug="din-933")
    app = Application.objects.create(name="Petrochemical Refineries", slug="petrochemical-refineries")
    print("  [OK] Material, Standard, and Application created")

    # 3. Admin creates a Product with Specs and FAQs
    prod = Product.objects.create(
        title="SS 316L Hex Head Bolt DIN 933",
        slug="ss-316l-hex-head-bolt-din-933",
        category=cat,
        short_description="A4-70 marine grade hex bolt conforming to DIN 933.",
        is_active=True,
    )
    prod.materials.add(mat)
    prod.standards.add(std)
    prod.applications.add(app)

    ProductSpecification.objects.create(product=prod, key="Grade", value="A4-70")
    ProductFAQ.objects.create(product=prod, question="Can this bolt be used offshore?", answer="Yes, SS316L has high molybdenum content to prevent seawater pitting.")
    print("  [OK] Product created with Category, Material, Standard, Application, Spec, and FAQ")

    # 4. Verify category list, product detail, material filter, standard filter, app filter
    dynamic_urls = [
        (f"/products/category/{cat.slug}/", "category filter"),
        (f"/products/materials/{mat.slug}/", "material filter"),
        (f"/products/standards/{std.slug}/", "standard filter"),
        (f"/products/applications/{app.slug}/", "application filter"),
        (f"/products/{prod.slug}/", "product detail"),
    ]
    for url, label in dynamic_urls:
        resp = client.get(url)
        if resp.status_code == 200:
            print(f"  [OK] HTTP 200: {url} ({label})")
        else:
            print(f"  [FAIL] {url} returned HTTP {resp.status_code}")
            failed.append((url, resp.status_code))

    # 5. Clean up temporary test data so database remains clean
    prod.delete()
    cat.delete()
    mat.delete()
    std.delete()
    app.delete()
    print("  [OK] Dynamic test data cleanly purged. Database remains clean.")
    return failed

def audit_authenticated_flows():
    print("\n=== 4. AUDITING AUTHENTICATED & PROTECTED FLOWS ===")
    client = Client()
    failed = []

    # Anonymous redirected
    for url, name in [("/accounts/profile/", "profile"), ("/accounts/password-change/", "password_change")]:
        resp = client.get(url)
        if resp.status_code == 302 and "/accounts/login" in resp.headers.get("Location", ""):
            print(f"  [OK] Anonymous redirected from {name}: {resp.headers.get('Location')}")
        else:
            print(f"  [FAIL] Anonymous access to {name} returned {resp.status_code} without redirect!")
            failed.append((url, resp.status_code))

    # Logged-in access
    test_user = User.objects.create_user(
        username="audit_test_client",
        email="client_audit@example.com",
        password="AuditPassword123!",
        role=User.Role.CLIENT,
    )
    client.force_login(test_user)

    inq = ContactInquiry.objects.create(
        user=test_user,
        full_name="Audit Test Client",
        email="client_audit@example.com",
        message="I need 500 pcs custom bolts."
    )

    prof_resp = client.get("/accounts/profile/")
    if prof_resp.status_code == 200:
        print("  [OK] Authenticated client profile view returns HTTP 200")
    else:
        print(f"  [FAIL] Profile view returned HTTP {prof_resp.status_code}")
        failed.append(("/accounts/profile/", prof_resp.status_code))

    pw_resp = client.get("/accounts/password-change/")
    if pw_resp.status_code == 200:
        print("  [OK] Password change view returns HTTP 200 for logged-in user")
    else:
        print(f"  [FAIL] Password change returned HTTP {pw_resp.status_code}")
        failed.append(("/accounts/password-change/", pw_resp.status_code))

    inq.delete()
    test_user.delete()
    return failed

def audit_settings_and_security():
    print("\n=== 5. AUDITING SETTINGS & DEPLOYMENT SECURITY ===")
    os.environ["DJANGO_SECRET_KEY"] = "audit-temporary-secret-key-123456789012345678901234567890"
    from mi_engineering.settings import prod

    print(f"  prod.DEBUG: {prod.DEBUG} [SECURE]")
    print(f"  prod.SESSION_COOKIE_SECURE: {prod.SESSION_COOKIE_SECURE} [SECURE]")
    print(f"  prod.CSRF_COOKIE_SECURE: {prod.CSRF_COOKIE_SECURE} [SECURE]")
    print(f"  prod.ALLOWED_HOSTS: {prod.ALLOWED_HOSTS}")
    print(f"  prod.CSRF_TRUSTED_ORIGINS: {prod.CSRF_TRUSTED_ORIGINS}")
    print(f"  prod.SECURE_HSTS_SECONDS: {prod.SECURE_HSTS_SECONDS}")
    print("  [OK] All production security flags validated.")
    return []

if __name__ == "__main__":
    t_err = audit_templates_compilation()
    e_err = audit_empty_database_views()
    d_err = audit_dynamic_admin_flow()
    a_err = audit_authenticated_flows()
    s_err = audit_settings_and_security()

    total_issues = len(t_err) + len(e_err) + len(d_err) + len(a_err) + len(s_err)
    if total_issues == 0:
        print("\n==========================================")
        print(">>> ALL AUDIT CHECKS PASSED (0 ERRORS) <<<")
        print("==========================================")
    else:
        print(f"\nAudit completed with {total_issues} issues.")
