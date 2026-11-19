from typing import Any, cast
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, View

from products.models import Application, Category, Material, Product, Standard
from utils.emails import send_app_email
from ..forms import ContactForm


class LLMsTxtView(View):
    """
    Serves /llms.txt following the LLM Web Discovery Specification.
    Provides machine-readable context for AI search agents (ChatGPT, Perplexity, Gemini, Claude).
    """

    def get(self, request, *args, **kwargs) -> HttpResponse:
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        categories = Category.objects.filter(is_active=True).order_by("name")
        standards = Standard.objects.all().order_by("name")
        materials = Material.objects.all().order_by("name")
        applications = Application.objects.all().order_by("name")
        products = Product.objects.filter(is_active=True).order_by("title")[:50]

        lines = [
            "# M.I. ENGINEERING WORKS",
            "",
            "> Leading Indian manufacturer, supplier, and exporter of precision industrial fasteners, high-tensile bolts, nuts, stud bolts, threaded rods, washers, screws, and custom drawing-based machined components.",
            "",
            "## Company Profile",
            "- **Legal Business Name:** M.I. Engineering Works",
            "- **Managing Director / Founder:** Mohd Iliyas",
            "- **Official Website:** " + base_url + "/",
            "- **Official Email:** miengineering17@gmail.com",
            "- **Phone / WhatsApp:** +91 9819972301 / +91 9137658733 / +91 8369593849",
            "- **Head Office:** 17, Floor-2nd, Plot-15/17, Ratan Building, Narayan Dhuru Street, Pydhonie, Mandvi, Mumbai - 400003, Maharashtra, India",
            "- **Manufacturing Works:** Ground Floor, Plot 222, Chhota Sonapur Compound, Maulana Shaukat Ali Road, Anjuman High School, Mumbai - 400008, Maharashtra, India",
            "- **Primary Capabilities:** Cold Forging, Hot Forging, CNC Precision Turning, Thread Rolling, Hexagon Machining, Custom Machining, EN 10204 3.1 Mill Test Certificates (MTC)",
            "- **Markets Served:** India (Domestic) and International / Global Export (Middle East, Europe, Americas, Southeast Asia, Africa)",
            "",
            "## Core Product Categories",
        ]

        if categories.exists():
            for cat in categories:
                cat_url = f"{base_url}{reverse('products:category_product_list', kwargs={'category_slug': cat.slug})}"
                lines.append(f"- [{cat.name}]({cat_url}): {cat.description or 'Precision fasteners and hardware components.'}")
        else:
            default_cats = [
                ("Bolts and Nuts", "/products/"),
                ("Stud Bolts", "/products/"),
                ("Screws and Washers", "/products/"),
                ("Threaded Rods", "/products/"),
                ("Anchor Fasteners", "/products/"),
                ("Rivets and Pins", "/products/"),
                ("Pipe Fittings and Flanges", "/products/"),
                ("Stainless Steel Fasteners (304, 316, 316L, 310, 321)", "/products/"),
                ("Alloy Steel Fasteners (ASTM A193 B7/B7M, B16, Grade 8.8, 10.9, 12.9)", "/products/"),
                ("Duplex and Super Duplex Fasteners (2205, 2507)", "/products/"),
                ("Inconel and Monel Fasteners (600, 625, 718, 400, K500)", "/products/"),
                ("Special and Custom Fasteners (Drawing-based)", "/products/"),
            ]
            for name, path in default_cats:
                lines.append(f"- [{name}]({base_url}{path})")

        lines.extend([
            "",
            "## Conforming Manufacturing Standards",
        ])
        if standards.exists():
            for std in standards:
                std_url = f"{base_url}{reverse('products:standard_product_list', kwargs={'standard_slug': std.slug})}"
                lines.append(f"- [{std.name}]({std_url})")
        else:
            for std_name in ["DIN 933 / DIN 931 (Hexagon Head Bolts)", "DIN 934 (Hexagon Nuts)", "ASTM A193 (Grade B7, B7M, B8, B8M Stud Bolts)", "ASTM A194 (Grade 2H, 7, 8, 8M Nuts)", "ISO 4014 / ISO 4017", "ASTM A325 / ASTM A490 (Structural Bolts)", "DIN 975 / DIN 976 (Threaded Rods)", "DIN 125 / DIN 127 (Washers)"]:
                lines.append(f"- {std_name}")

        lines.extend([
            "",
            "## Materials & Metallurgy",
        ])
        if materials.exists():
            for mat in materials:
                mat_url = f"{base_url}{reverse('products:material_product_list', kwargs={'material_slug': mat.slug})}"
                lines.append(f"- [{mat.name}]({mat_url})")
        else:
            for mat_name in ["Stainless Steel (SS 304, 304L, 316, 316L, 310, 321)", "High-Tensile Alloy Steel (Grade 8.8, 10.9, 12.9, B7, B7M)", "Carbon Steel & Mild Steel", "Duplex (2205 / UNS S31803) & Super Duplex (2507 / UNS S32750)", "High Nickel Alloys (Inconel 625/718, Monel 400/K500, Hastelloy)", "Brass, Bronze & Copper"]:
                lines.append(f"- {mat_name}")

        lines.extend([
            "",
            "## Target Industries & Applications",
        ])
        if applications.exists():
            for app in applications:
                app_url = f"{base_url}{reverse('products:application_product_list', kwargs={'application_slug': app.slug})}"
                lines.append(f"- [{app.name}]({app_url})")
        else:
            for app_name in ["Oil, Gas & Petrochemical Refineries", "Heavy Machinery & Industrial Equipment", "Marine, Offshore & Shipbuilding", "Power Plants & Renewable Energy", "Civil Construction & Structural Engineering", "Automotive & Railway Infrastructure"]:
                lines.append(f"- {app_name}")

        lines.extend([
            "",
            "## Key Web Navigation URLs",
            f"- [Home Page]({base_url}/)",
            f"- [About Us & Manufacturing Facilities]({base_url}{reverse('home:about-us')})",
            f"- [Complete Product Catalog]({base_url}{reverse('products:product_list')})",
            f"- [Contact & Request for Quotation (RFQ)]({base_url}{reverse('home:contact-us')})",
            f"- [XML Sitemap]({base_url}/sitemap.xml)",
            "",
            "## Quotations & Technical Procurement",
            "To request a bulk price quotation, technical drawing review, or Mill Test Certificate sample:",
            f"- Web RFQ Form: {base_url}{reverse('home:contact-us')}",
            "- Direct Email: miengineering17@gmail.com",
            "- Immediate Technical Assistance: +91 9819972301",
        ])

        content = "\n".join(lines) + "\n"
        return HttpResponse(content, content_type="text/markdown; charset=utf-8")


class HomePageView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TermsOfServiceView(TemplateView):
    template_name = "terms_of_service.html"


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home:contact-us")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        # Pre-fill details if the user is authenticated
        if self.request.user.is_authenticated:
            user = cast(Any, self.request.user)
            initial["email"] = user.email
            initial["full_name"] = user.get_full_name() or user.username

        # Capture URL parameter inputs from product detail page redirect
        product = self.request.GET.get("product")
        material = self.request.GET.get("material")
        grade = self.request.GET.get("grade")

        if product:
            specs = []
            if material:
                specs.append(f"Material: {material}")
            if grade:
                specs.append(f"Grade: {grade}")

            spec_details = f" ({', '.join(specs)})" if specs else ""

            initial["message"] = (
                f"I am interested in receiving a quote for: {product}{spec_details}.\n\n"
                f"Please provide pricing, delivery timeline, and minimum order quantity."
            )

        return initial

    def form_valid(self, form: ContactForm) -> HttpResponse:
        inquiry = form.save(commit=False)
        if self.request.user.is_authenticated:
            inquiry.user = self.request.user
        inquiry.save()

        import email.utils
        raw_from = getattr(settings, "DEFAULT_FROM_EMAIL", "")
        admin_email: str = email.utils.parseaddr(raw_from)[1] or getattr(settings, "EMAIL_HOST_USER", "webmaster@localhost")

        admin_attachments = []
        if inquiry.attachment:
            try:
                if hasattr(inquiry.attachment, "path"):
                    admin_attachments.append(inquiry.attachment.path)
            except Exception:
                pass

        send_app_email(
            subject=f"New Contact Inquiry: {inquiry.full_name}",
            recipient_list=[admin_email],
            template_name="emails/contact_inquiry",
            context={
                "full_name": inquiry.full_name,
                "email": inquiry.email,
                "message": inquiry.message,
                "attachment": inquiry.attachment,
            },
            attachments=admin_attachments if admin_attachments else None,
            fail_silently=True,
        )

        send_app_email(
            subject="We received your message - M.I. Engineering Works",
            recipient_list=[inquiry.email],
            template_name="emails/contact_receipt",
            context={
                "full_name": inquiry.full_name,
                "message": inquiry.message,
                "attachment": inquiry.attachment,
            },
            fail_silently=True,
        )

        messages.success(
            self.request,
            "Thank you for reaching out! Your inquiry has been received and our team will get back to you shortly.",
        )
        return super().form_valid(form)

    def form_invalid(self, form: ContactForm) -> HttpResponse:
        messages.error(
            self.request,
            "There was an error processing your submission. Please check the fields below.",
        )
        return super().form_invalid(form)
