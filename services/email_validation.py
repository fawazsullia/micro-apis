import re
import dns.resolver

disposable_email_domains = {
    "mailinator.com", "10minutemail.com", "guerrillamail.com",
    "tempmail.net", "throwawaymail.com", "yopmail.com", "maildrop.cc",
    "getnada.com", "dispostable.com", "fakeinbox.com", "tempmail.org",
    "spamgourmet.com", "trashmail.com"
}

role_based_keywords = [
    "admin", "support", "contact", "info", "sales", "help", "no-reply", "webmaster", "service", "manager"
]

free_email_providers = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com", "mail.com", "zoho.com", "protonmail.com", "yandex.com"
]

class EmailValidation:
    def __init__(self, email):
        self.email = email
        self.is_syntax_valid = self.is_valid_email_syntax()
        self.domain = self.extract_domain()
        self.is_domain_valid = self.is_valid_domain()
        self.mx_records_found = self.verify_mx_records()
        self.is_disposable = self.is_disposable_email()
        self.is_role_based = self.is_role_based_email()
        self.is_free_email = self.is_free_email()

    def is_valid_email_syntax(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, self.email))

    def extract_domain(self):
        parts = self.email.split("@")
        return parts[1] if len(parts) == 2 else ""

    def is_valid_domain(self):
        try:
            dns.resolver.resolve(self.domain, 'A')
            return True
        except dns.resolver.NoAnswer:
            return False
        except dns.resolver.NXDOMAIN:
            return False
        except dns.resolver.LifetimeTimeout:
            return False

    def is_role_based_email(self):
        local_part = self.email.split('@')[0].lower()
        for keyword in role_based_keywords:
            if keyword in local_part:
                return True
        return False

    def is_free_email(self):
        if self.domain in free_email_providers:
            return True
        return False

    def verify_mx_records(self):
        try:
            records = dns.resolver.resolve(self.domain, 'MX')
            return bool(records)
        except dns.resolver.NoAnswer:
            return False
        except dns.resolver.NXDOMAIN:
            return False
        except dns.resolver.LifetimeTimeout:
            return False

    def is_disposable_email(self):
        return self.domain.lower() in disposable_email_domains

    def to_dict(self):
        return {
            "email": self.email,
            "isSyntaxValid": self.is_syntax_valid,
            "isDomainValid": self.is_domain_valid,
            "mxRecordsFound": self.mx_records_found,
            "isDisposable": self.is_disposable,
            "isRoleBased": self.is_role_based,
            "domain": self.domain,
            "isFreeEmail": self.is_free_email
        }

# Example usage:
if __name__ == "__main__":
    email = "test@mailinator.com"
    validation_result = EmailValidation(email)
    print(validation_result.to_dict())
