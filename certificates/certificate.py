import argparse
from hashlib import sha1


def compute_hash(email):
    return sha1(email.encode('utf-8')).hexdigest()


def compute_certificate_id(email):
    email_clean = email.lower().strip()
    
    return compute_hash(email_clean + '_')


def generate_certificate_url(your_id, course, cohort):
    url = f"https://certificate.datatalks.club/{course}/{cohort}/{your_id}.pdf"

    return url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate certificate from the given email")
    parser.add_argument("--cohort", type=int, help="Cohort year on a certificate")
    parser.add_argument("--course", type=str, help="Course for getting a certificate")
    parser.add_argument("--email", type=str, help="Email for building a certificate")
    args = parser.parse_args()
    
    cohort = args.cohort
    course = args.course
    email = args.email

    your_id = compute_certificate_id(email)
    url = generate_certificate_url(your_id, course, cohort)
    print(url)
