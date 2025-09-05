from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Organization, ISDAS, SCIONLinkAssignment


class OrganizationTestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            short_name="ACME",
            full_name="ACME Corporation",
            description="Test organization"
        )

    def test_organization_str(self):
        """Test Organization string representation"""
        self.assertEqual(str(self.organization), "ACME")

    def test_organization_unique_short_name(self):
        """Test that short_name must be unique"""
        with self.assertRaises(Exception):
            Organization.objects.create(
                short_name="ACME",  # Duplicate
                full_name="Another ACME",
            )


class ISDATestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            short_name="ACME",
            full_name="ACME Corporation"
        )
        self.isdas = ISDAS.objects.create(
            isd_as="1-ff00:0:110",
            organization=self.organization,
            cores=["core1.example.com", "core2.example.com"],
            description="Test ISD-AS"
        )

    def test_isdas_str(self):
        """Test ISDAS string representation"""
        self.assertEqual(str(self.isdas), "1-ff00:0:110")

    def test_isdas_cores_display(self):
        """Test cores display property"""
        expected = "core1.example.com, core2.example.com"
        self.assertEqual(self.isdas.cores_display, expected)

    def test_invalid_isd_as_format(self):
        """Test that invalid ISD-AS format raises validation error"""
        with self.assertRaises(ValidationError):
            isdas = ISDAS(
                isd_as="invalid-format",
                organization=self.organization
            )
            isdas.full_clean()


class SCIONLinkAssignmentTestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            short_name="ACME",
            full_name="ACME Corporation"
        )
        self.isdas = ISDAS.objects.create(
            isd_as="1-ff00:0:110",
            organization=self.organization
        )
        self.assignment = SCIONLinkAssignment.objects.create(
            isd_as=self.isdas,
            interface_id=1,
            customer_id="CUST001",
            customer_name="Customer Corp",
            zendesk_ticket="12345"
        )

    def test_assignment_str(self):
        """Test SCIONLinkAssignment string representation"""
        expected = "1-ff00:0:110 - Interface 1"
        self.assertEqual(str(self.assignment), expected)

    def test_zendesk_url(self):
        """Test Zendesk URL generation"""
        expected = "https://anapaya.zendesk.com/agent/tickets/12345"
        self.assertEqual(self.assignment.get_zendesk_url(), expected)

    def test_unique_interface_per_isdas(self):
        """Test that interface_id must be unique per ISD-AS"""
        with self.assertRaises(Exception):
            SCIONLinkAssignment.objects.create(
                isd_as=self.isdas,
                interface_id=1,  # Duplicate
                customer_id="CUST002",
                customer_name="Another Customer",
                zendesk_ticket="54321"
            )

    def test_invalid_zendesk_ticket(self):
        """Test that non-numeric Zendesk ticket raises validation error"""
        with self.assertRaises(ValidationError):
            assignment = SCIONLinkAssignment(
                isd_as=self.isdas,
                interface_id=2,
                customer_id="CUST002",
                customer_name="Customer Corp",
                zendesk_ticket="not-a-number"
            )
            assignment.full_clean()
