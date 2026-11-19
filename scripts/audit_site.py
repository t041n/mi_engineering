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

def audit_views_and_rendering():
    print("\n=== 2. AUDITING VIEWS & TEMPLATE RENDERING ===")
    client = Client()
    
    # Ensure at least 1 test product exists with FAQs and specs
    cat = Category.objects.first()
    mat = Material.objects.first()
    std = Standard.objects.first()
    app = Application.objects.first()
    
    test_prod, created_prod = Product.objects.get_or_create(
        slug="audit-test-stud-bolt-b7",
        defaults={
            "title": "ASTM A193 B7 Heavy Hex Stud Bolt",
            "short_description": "High tensile alloy steel stud bolt for petrochemical flange joints.",
            "category": cat,
            "is_active": True,
        }
    )
    if mat:
        test_prod.materials.add(mat)
    if std:
        test_prod.standards.add(std)
    if app:
        test_prod.applications.add(app)
        
    ProductFAQ.objects.get_or_create(
        product=test_prod,
        question="What is the torque rating for this stud bolt?",
        defaults={"answer": "Torque values follow ASME PCC-1 guidelines based on bolt diameter."}
    )
    ProductSpecification.objects.get_or_create(
        product=test_prod,
        key="Thread Profile",
        defaults={"value": "UNC / Metric Coarse Pitch"}
    )

    # Ensure gallery item exists
    gcat = GalleryCategory.objects.first()
    gitem, created_gitem = GalleryItem.objects.get_or_create(
        title="Audit Workshop Photo",
        defaults={
            "category": gcat,
            "media_type": GalleryItem.MediaType.IMAGE,
            "description": "CNC Lathe turning B7 stud bolts.",
            "is_active": True,
        }
    )

    test_urls = [
        ("/", "homepage"),
        ("/about-us/", "about"),
        ("/contact-us/", "contact"),
        ("/contact-us/?product=Test%20Stud&material=SS316", "contact prefill"),
        ("/terms-of-service/", "terms"),
        ("/privacy-policy/", "privacy"),
        ("/llms.txt", "llms.txt"),
        ("/robots.txt", "robots.txt"),
        ("/sitemap.xml", "sitemap.xml"),
        ("/products/", "product_list"),
        ("/products/?q=bolt", "product search"),
        ("/products/applications/", "application_list"),
        ("/products/standards/", "standard_list"),
        ("/products/materials/", "material_list"),
        (f"/products/{test_prod.slug}/", f"product detail: {test_prod.slug}"),
        ("/gallery/", "gallery_list"),
        ("/gallery/?type=IMAGE", "gallery image filter"),
        (f"/gallery/{gitem.pk}/", f"gallery detail: {gitem.pk}"),
        ("/accounts/login/", "login"),
        ("/accounts/register/", "register"),
        ("/accounts/password-reset/", "password_reset"),
    ]

    if cat:
        test_urls.append((f"/products/category/{cat.slug}/", f"category: {cat.slug}"))
    if app:
        test_urls.append((f"/products/applications/{app.slug}/", f"app: {app.slug}"))
    if std:
        test_urls.append((f"/products/standards/{std.slug}/", f"std: {std.slug}"))
    if mat:
        test_urls.append((f"/products/materials/{mat.slug}/", f"mat: {mat.slug}"))

    failed = []
    for url, label in test_urls:
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

    # Test HTMX partial request for catalog
    try:
        htmx_resp = client.get("/products/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="catalog-content")
        if htmx_resp.status_code == 200 and "product" in htmx_resp.content.decode("utf-8").lower():
            print("  [OK] HTMX catalog-content partial rendering works")
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
            "message": "Automated audit test RFQ for fasteners.",
        })
        # Should redirect back to success_url (302)
        if contact_post.status_code == 302:
            print("  [OK] Contact form submission POST redirects 302")
        else:
            print(f"  [FAIL] Contact form POST returned HTTP {contact_post.status_code}")
            failed.append(("/contact-us/ POST", "contact post", contact_post.status_code))
    except Exception as e:
        print(f"  [EXCEPTION] Contact form POST -> {e}")
        failed.append(("/contact-us/ POST", "contact post", str(e)))

    # Clean up test product and inquiry
    if created_prod:
        test_prod.delete()
    if created_gitem:
        gitem.delete()
    ContactInquiry.objects.filter(email="audit.test@example.com").delete()

    print(f"Total view test cases: {len(test_urls) + 2}. Failures: {len(failed)}")
    return failed

def audit_authenticated_flows():
    print("\n=== 3. AUDITING AUTHENTICATED & PROTECTED FLOWS ===")
    client = Client()
    failed = []

    # Test Anonymous access to protected views (should redirect 302)
    for url, name in [("/accounts/profile/", "profile"), ("/accounts/password-change/", "password_change")]:
        resp = client.get(url)
        if resp.status_code == 302 and "/accounts/login" in resp.headers.get("Location", ""):
            print(f"  [OK] Anonymous redirected from {name}: {resp.headers.get('Location')}")
        else:
            print(f"  [FAIL] Anonymous access to {name} returned {resp.status_code} without redirect!")
            failed.append((url, resp.status_code))

    # Test Logged-in access
    test_user, created_user = User.objects.get_or_create(
        username="audit_test_client",
        defaults={"email": "client_audit@example.com", "role": User.Role.CLIENT}
    )
    test_user.set_password("AuditPassword123!")
    test_user.save()

    client.force_login(test_user)

    # Create dummy inquiry for profile view
    inq = ContactInquiry.objects.create(
        user=test_user,
        full_name="Audit Test Client",
        email="client_audit@example.com",
        message="I need 500 pcs ASTM A193 B7 stud bolts."
    )

    prof_resp = client.get("/accounts/profile/")
    if prof_resp.status_code == 200:
        print("  [OK] Authenticated client profile view returns HTTP 200")
        content = prof_resp.content.decode("utf-8")
        if "500 pcs ASTM A193 B7" in content:
            print("  [OK] Profile view correctly renders client inquiry history")
        else:
            print("  [WARN] Inquiry history text not found in profile response")
    else:
        print(f"  [FAIL] Profile view returned HTTP {prof_resp.status_code}")
        failed.append(("/accounts/profile/", prof_resp.status_code))

    pw_resp = client.get("/accounts/password-change/")
    if pw_resp.status_code == 200:
        print("  [OK] Password change view returns HTTP 200 for logged-in user")
    else:
        print(f"  [FAIL] Password change returned HTTP {pw_resp.status_code}")
        failed.append(("/accounts/password-change/", pw_resp.status_code))

    # Clean up test user & inquiry
    inq.delete()
    if created_user:
        test_user.delete()

    return failed

def audit_settings_and_security():
    print("\n=== 4. AUDITING SETTINGS & DEPLOYMENT SECURITY ===")
    os.environ["DJANGO_SECRET_KEY"] = "audit-temporary-secret-key-123456789012345678901234567890"
    from mi_engineering.settings import prod, base, dev
    
    issues = []
    
    # 1. Base settings
    if "accounts.User" != base.AUTH_USER_MODEL:
        issues.append(f"Unexpected AUTH_USER_MODEL: {base.AUTH_USER_MODEL}")
    if not base.SECRET_KEY and os.environ.get("ENV") == "prod":
        issues.append("SECRET_KEY is empty in production environment!")

    # 2. Prod settings
    if prod.DEBUG is not False:
        issues.append("prod.DEBUG is not False!")
    if not prod.SESSION_COOKIE_SECURE:
        issues.append("prod.SESSION_COOKIE_SECURE is not True!")
    if not prod.CSRF_COOKIE_SECURE:
        issues.append("prod.CSRF_COOKIE_SECURE is not True!")
    if not prod.SECURE_CONTENT_TYPE_NOSNIFF:
        issues.append("prod.SECURE_CONTENT_TYPE_NOSNIFF is not True!")

    print(f"  prod.DEBUG: {prod.DEBUG} [SECURE]")
    print(f"  prod.SESSION_COOKIE_SECURE: {prod.SESSION_COOKIE_SECURE} [SECURE]")
    print(f"  prod.CSRF_COOKIE_SECURE: {prod.CSRF_COOKIE_SECURE} [SECURE]")
    print(f"  prod.ALLOWED_HOSTS: {prod.ALLOWED_HOSTS}")
    print(f"  prod.CSRF_TRUSTED_ORIGINS: {prod.CSRF_TRUSTED_ORIGINS}")
    print(f"  prod.SECURE_HSTS_SECONDS: {prod.SECURE_HSTS_SECONDS}")

    if issues:
        for iss in issues:
            print(f"  [SECURITY ISSUE] {iss}")
    else:
        print("  [OK] All production security flags validated.")
    return issues

if __name__ == "__main__":
    t_err = audit_templates_compilation()
    v_err = audit_views_and_rendering()
    a_err = audit_authenticated_flows()
    s_err = audit_settings_and_security()

    total_issues = len(t_err) + len(v_err) + len(a_err) + len(s_err)
    if total_issues == 0:
        print("\n==========================================")
        print(">>> ALL AUDIT CHECKS PASSED (0 ERRORS) <<<")
        print("==========================================")
    else:
        print(f"\nAudit completed with {total_issues} issues.")
