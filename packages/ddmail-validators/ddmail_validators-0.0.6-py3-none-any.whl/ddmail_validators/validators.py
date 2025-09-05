import re
import dns.resolver


def is_username_allowed(username,username_len=12):
    """Validate username string. Only allow the following chars: A-Z and 0-9.

    Keyword arguments:
    username -- string containing the username.
    username_len -- integer max length of username string, default 12.
    """
    # Check length.
    if len(username) != username_len:
        return False

    pattern = re.compile(r"[A-Z0-9]")

    for char in username:
        if not re.match(pattern, char):
            return False

    return True


def is_password_allowed(password, password_len=24):
    """Validate password. Only allow the following chars: A-Z, a-z and 0-9.

    Keyword arguments:
    password -- string containing the password.
    password_len -- integer max length of password string, default 24.
    """
    # Check length.
    if len(password) != password_len:
        return False

    pattern = re.compile(r"[a-zA-Z0-9]")

    for char in password:
        if not re.match(pattern, char):
            return False

    return True


def is_domain_allowed(domain):
    """Validate domain names.
    Only allow the following chars: a-z, A-Z, 0-9 and .-

    Keyword arguments:
    domain -- string containing the domain.
    """
    if not len(domain) > 3:
        return False

    if domain.startswith('.') or domain.startswith('-'):
        return False
    if domain.endswith('.') or domain.endswith('-'):
        return False
    if '--' in domain:
        return False
    if '..' in domain:
        return False

    if domain.find(".") == -1:
        return False

    pattern = re.compile(r"[a-zA-Z0-9.-]")
    for char in domain:
        if not re.match(pattern, char):
            return False

    return True


def is_email_allowed(email):
    """Validate email address. Only allow the following chars: a-z, 0-9 and @.-

    Keyword arguments:
    email -- string containing the email.
    """
    # Check email length.
    if not len(email) > 6:
        return False
    if len(email) > 256:
        return False

    if email.count('@') != 1:
        return False
    if email.startswith('.') or email.startswith('@') or email.startswith('-'):
        return False
    if email.endswith('.') or email.endswith('@') or email.endswith('-'):
        return False

    # Split email in local part and domain part.
    # Example: [local part]@[domain part].
    splitted_email = email.split('@')
    local_part = splitted_email[0]
    domain_part = splitted_email[1]

    # Validate local part of email.
    if len(local_part) > 64:
        return False
    if local_part.startswith('.') or local_part.startswith('-'):
        return False
    if local_part.endswith('.') or local_part.endswith('-'):
        return False
    if '--' in local_part:
        return False
    if '..' in local_part:
        return False

    pattern = re.compile(r"[a-zA-Z0-9.+=_-]")
    for char in local_part:
        if not re.match(pattern, char):
            return False

    # Validate domain part of email.
    if is_domain_allowed(domain_part) is not True:
        return False

    return True


def is_account_allowed(account,account_len=12):
    """Validate account id string. Only allow the following chars: A-Z and 0-9

    Keyword arguments:
    account -- string containing the account is.
    account_len -- integer max length of account string, default 12.
    """
    # Check length.
    if len(account) != account_len:
        return False

    pattern = re.compile(r"[A-Z0-9]")

    for char in account:
        if not re.match(pattern, char):
            return False

    return True


def is_mx_valid(domain, host, priority):
    """Validate dns domain mx record.

    Keyword arguments:
    domain -- string containing the domain.
    host -- string containing the host.
    priority -- string containing the priority.
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        if len(answers) == 1 and str(answers[0].exchange) == host and str(answers[0].preference == priority):
            return True
        else:
            return False
    except:
        return False


def is_spf_valid(domain, spf_record):
    """Validate dns spf (as txt) record.

    Keyword aguments:
    domain -- string containg the domain.
    spf_record -- string containg the spf record.
    """
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            if 'spf1' in str(rdata) and str(rdata) == spf_record:
                return True
            else:
                return False
    except:
        return False

def is_cname_valid(cname_src_record,cname_dst_record):
    """Validate if the dns record is a cname to a specific domain.

    Keyword arguments:
    cname_src_record -- string containg the domain that should be a cname to cname variable below.
    cname_dst_record -- string containg the cname record source domain.
    """
    try:
        answers = dns.resolver.resolve(cname_src_record, 'CNAME')
        for rdata in answers:
            if str(rdata) == cname_dst_record:
                return True
            else:
                return False
    except:
        return False


def is_dkim_valid(domain, selector ,dkim_record):
    """Validate dns dkim txt record.

    Keyword arguments:
    domain -- string containg domain.
    selector -- string containg DKIM selector.
    dkim_record -- string containg DKIM record.
    """
    try:
        answers = dns.resolver.resolve(selector + "._domainkey." + domain, 'TXT')
        for rdata in answers:
            if 'DKIM1' in str(rdata) and str(rdata) == dkim_record:
                return True
            else:
                return False
    except:
        return False


def is_dmarc_valid(domain, dmarc_record):
    """Validate dns dmarc (as txt) record.

    Keyword arguments:
    domain -- string containg domain.
    dmarc_record -- string containg DMARC record.
    """
    try:
        answers = dns.resolver.resolve("_dmarc." + domain, 'TXT')
        for rdata in answers:
            if 'DMARC1' in str(rdata) and str(rdata) == dmarc_record:
                return True
            else:
                return False
    except:
        return False


def is_openpgp_public_key_allowed(public_key):
    """Validate openpgp public key.
    Only allow the following chars: A-Z, a-z, 0-9 and +/=

    Keyword arguments:
    public_key -- string containg OpenPGP public key in armored format.
    """
    if public_key is None:
        return False

    # Check start and end of string.
    if public_key.startswith(
            "-----BEGIN PGP PUBLIC KEY BLOCK-----"
            ) is not True:

        return False
    if public_key.endswith(
            "-----END PGP PUBLIC KEY BLOCK-----"
            ) is not True:

        return False

    public_key = public_key.replace(
            "-----BEGIN PGP PUBLIC KEY BLOCK-----",
            "",
            1
            )

    public_key = public_key.replace(
            "-----END PGP PUBLIC KEY BLOCK-----",
            "",
            1
            )

    # Only allow A-Z ,a-z, 0-9 and +/=
    pattern = re.compile(r"[a-zA-Z0-9\+\/\=\s]")
    for char in public_key:
        if not re.match(pattern, char):
            return False

    return True


def is_openpgp_key_fingerprint_allowed(fingerprint):
    """Validate openpgp public key fingerprint string.
    Only allow the following chars: A-Z, 0-9

    Keyword arguments:
    fingerprint -- string containg OpenPGP key fingeprint.
    """
    if fingerprint is None:
        return False

    # Fingerprint string should be 40 char.
    allowed_len = 40
    if len(fingerprint) != allowed_len:
        return False

    # Only allow A-Z, 0-9
    pattern = re.compile(r"[A-Z0-9]")
    for char in fingerprint:
        if not re.match(pattern, char):
            return False

    return True


def is_openpgp_keyring_allowed(keyring):
    """Validate openpgp keyring filename.
    Only allow the following chars: A-Z and 0-9

    Keyword arguments:
    keyring -- string containg OpenPGP keyring filename.
    """
    pattern = re.compile(r"[A-Z0-9]")

    for char in keyring:
        if not re.match(pattern, char):
            return False

    return True


def is_sha256_allowed(checksum):
    """Validate sha256 checksum.
    Only allow the following chars: a-z, A-Z  and 0-9

    Keyword arguments:
    checksum -- string containg the sha256 checksum.
    """
    if not len(checksum) == 64:
        return False

    pattern = re.compile(r"[a-zA-Z0-9]")

    for char in checksum:
        if not re.match(pattern, char):
            return False

    return True


def is_db_id_allowed(id):
    """Validate database ID.
    Only allow positive integers.

    Keyword arguments:
    id -- integer containing the datbase id.
    """
    # Check that id is integer.
    try:
        i = 1
        i = i + id
    except ValueError:
        return False
    except TypeError:
        return False

    # Check that id is not negative.
    if not id >= 0:
        return False

    return True


def is_cookie_allowed(cookie,cookie_len=128):
    """Validate flask session secret cookie.
    Only allow the following chars: A-Z, a-z and 0-9.

    Keyword arguments:
    cookie -- string containing the session secret cookie.
    cookie_len -- the allowed length of the string, default 128.
    """
    # Check length.
    if len(cookie) != cookie_len:
        return False

    # Allowed chars.
    pattern = re.compile(r"[a-zA-Z0-9]")

    # Check chars in string.
    for char in cookie:
        if not re.match(pattern, char):
            return False

    return True

def is_password_key_allowed(key,key_len=4096):
    """Validate password key.
    Only allow the following chars: A-Z, a-z and 0-9.

    Keyword arguments:
    key -- string containing the secret key.
    key_len -- the allowed length of the key, default 4096.
    """
    # Check length.
    if len(key) != key_len:
        return False

    # Allowed chars.
    pattern = re.compile(r"[a-zA-Z0-9]")

    # Check chars in string.
    for char in key:
        if not re.match(pattern, char):
            return False

    return True


def is_filename_allowed(filename,filename_max_len=256,filename_min_len=3):
    """Validate filename.
    Only allow the following chars: A-Z, a-z, 0-9 and .-_

    Keyword arguments:
    filename -- string containing the filanme.
    filanme_max_len -- the allowed max length of the filename, default 256.
    filanme_min_len -- the allowed min length of the filename, default 3.
    """
    if len(filename) > filename_max_len:
        return False

    if len(filename) < filename_min_len:
        return False

    if filename.startswith('.') or filename.startswith('-') or filename.startswith('_'):
        return False
    if filename.endswith('.') or filename.endswith('-') or filename.endswith('_'):
        return False
    if '--' in filename:
        return False
    if '..' in filename:
        return False
    if '__' in filename:
        return False

    pattern = re.compile(r"[a-zA-Z0-9\-\_\.]")

    for char in filename:
        if not re.match(pattern, char):
            return False

    return True

def is_base64_allowed(base64,base64_max_len=256,base64_min_len=3):
    """Validate base64 string.
    Only allow the following chars: A-Z, a-z, 0-9 and +/=

    Keyword arguments:
    base64 -- base64 string.
    base64_max_len -- the allowed max length of the base64 string, default 256.
    base64_min_len -- the allowed min length of the base64 string, default 3.
    """
    if len(base64) > base64_max_len:
        return False

    if len(base64) < base64_min_len:
        return False

    pattern = re.compile(r"[a-zA-Z0-9+/=]")

    for char in base64:
        if not re.match(pattern, char):
            return False

    return True
