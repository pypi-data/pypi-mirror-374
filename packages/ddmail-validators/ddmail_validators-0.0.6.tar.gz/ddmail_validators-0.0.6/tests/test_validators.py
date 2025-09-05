import base64
from ddmail_validators.validators import is_username_allowed, is_email_allowed, is_domain_allowed, is_password_allowed, is_account_allowed, is_sha256_allowed, is_mx_valid, is_spf_valid, is_dkim_valid, is_cname_valid, is_dmarc_valid, is_openpgp_public_key_allowed, is_openpgp_key_fingerprint_allowed, is_openpgp_keyring_allowed, is_cookie_allowed, is_db_id_allowed, is_password_key_allowed, is_filename_allowed, is_base64_allowed


def test_is_username_allowed():
    assert is_username_allowed("FG1AOG6A2SX4") is True
    assert is_username_allowed("FG1AOG6A2SX4A") is False
    assert is_username_allowed("FG1AOG6A2SX") is False
    assert is_username_allowed("FGaAOG6A2SX4") is False
    assert is_username_allowed("!G1AOG6A2SX4") is False
    assert is_username_allowed("FG1A-G6A2SX4") is False
    assert is_username_allowed("F_1AOG6A2SX4") is False
    assert is_username_allowed("FG1:OG6A2SX4") is False
    assert is_username_allowed("FG1AOG6A2;X4") is False
    assert is_username_allowed("FG1AOG6A2SX$") is False


def test_is_password_allowed():
    assert is_password_allowed("aBfD3Fd2G6Jg5dE4G5jQrG5D") is True
    assert is_password_allowed("aBfD3Fd2G6Jg5dE4G5jQrG5DA") is False
    assert is_password_allowed("1a2A835") is False
    assert is_password_allowed("") is False
    assert is_password_allowed("a<fD3Fd2G6Jg5dE4G5jQrG5D") is False
    assert is_password_allowed("aBfD3Fd2G6Jg;dE4G5jQrG5D") is False
    assert is_password_allowed("aBfD3:d2G6Jg5dE4G5jQrG5D") is False
    assert is_password_allowed("-BfD3Fd2G6Jg5dE4G5jQrG5D") is False
    assert is_password_allowed("aBfD3Fd2G6Jg5dE4G5jQrG5_") is False
    assert is_password_allowed("aBfD3Fd2G\"Jg5dE4G5jQrG5D") is False
    assert is_password_allowed("aBfD3!d2G6Jg5dE4G5jQrG5D") is False


def test_is_domain_allowed():
    assert is_domain_allowed("test.se") is True
    assert is_domain_allowed("testtes-t.se") is True
    assert is_domain_allowed("t.s") is False
    assert is_domain_allowed("test.se.") is False
    assert is_domain_allowed("te_st.se") is False
    assert is_domain_allowed(".test@test.se") is False
    assert is_domain_allowed("t@est.se") is False
    assert is_domain_allowed("test.test.se@") is False
    assert is_domain_allowed("testte<>st.se") is False
    assert is_domain_allowed("te>sttest.se") is False
    assert is_domain_allowed("te<test.se") is False
    assert is_domain_allowed("te=sttest.se") is False
    assert is_domain_allowed("test=t.se") is False
    assert is_domain_allowed("testtest..se") is False
    assert is_domain_allowed("t\"est@test.se") is False


def test_is_email_allowed():
    assert is_email_allowed("test@test.se") is True
    assert is_email_allowed("test@tes-t.se") is True
    assert is_email_allowed("test@tes_t.se") is False
    assert is_email_allowed("t@t.s") is False
    assert is_email_allowed("test@test.se.") is False
    assert is_email_allowed(".test@test.se") is False
    assert is_email_allowed("@test.se") is False
    assert is_email_allowed("test.test.se@") is False
    assert is_email_allowed("test@te<>st.se") is False
    assert is_email_allowed("te>st@test.se") is False
    assert is_email_allowed("te<st@test.se") is False
    assert is_email_allowed("te=st@test.se") is True
    assert is_email_allowed("test@tes=t.se") is False
    assert is_email_allowed("test@test..se") is False
    assert is_email_allowed("t\"est@test.se") is False


def test_is_account_allowed():
    assert is_account_allowed("GQW3E4XN3BA2") is True
    assert is_account_allowed("A1B2C3") is False
    assert is_account_allowed("AbC1") is False
    assert is_account_allowed("GQ#3E4XN3BA2") is False
    assert is_account_allowed("G>Q3E4XN3BA2") is False
    assert is_account_allowed("G4Q3E4X;3BA2") is False
    assert is_account_allowed(".QW3E4XN3BA2") is False
    assert is_account_allowed("GQW3E4X,3BA2") is False
    assert is_account_allowed("GQW3E4X-3BA2") is False
    assert is_account_allowed("GQW3E4XN3BA_") is False


def test_is_mx_valid():
    assert is_mx_valid("crew.ddmail.se", "mail.ddmail.se.", "10") is True
    assert is_mx_valid("drz.se", "mail.ddmail.se.", "10") is False


def test_is_spf_valid():
    assert is_spf_valid("crew.ddmail.se", '"v=spf1 mx -all"') is True
    assert is_spf_valid("drz.se", '"v=spf1 mx -all"') is False


def test_is_dkim_valid():
    dkim_record = '"v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoxPfU8PtYnrc9gcSw7G15U9cYTeaa8FZ+Nnlz4Zarlv00vYBSejIgbbX6WUE1HoVUT37+uGMHzSPIt7UyEdtSJs/c5caxfqP++Db11d5JJ1LnDAhtWuwe+dLFrQMSInCxKR+aqUBFK51DPhEDKD9dMAGIBeoZsZmIqqIFrpH7DgHCQdgUm1CbqFtQxEmJQ8zm" "b+C2SPcs3pxaI+4/fNFT7pcjLtZhmKHrxKJ7+iaUPKt6pFELgsB9RY3HGx039gsO2PC+4ULsYumxzhobCvwwLRzPqAWux00p5LhSadl5Obx88exLXRU0JIn1UeffiGzxNX6+3vrE2LLksjl+Jgo3wIDAQAB"'
    assert is_dkim_valid("ddmail.se", "dkim1", dkim_record) is True
    assert is_dkim_valid("drz.se", "dkim1", dkim_record) is False

def test_is_cname_valid():
    cname_record = 'dkim1._domainkey.ddmail.se.'
    assert is_cname_valid("dkim1._domainkey.crew.ddmail.se", cname_record) is True

def test_is_dmarc_valid():
    dmarc_record = '"v=DMARC1; p=none"'

    assert is_dmarc_valid("crew.ddmail.se", dmarc_record) is False
    assert is_dmarc_valid("drz.se", dmarc_record) is True


def test_is_openpgp_public_key_allowed():
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK-----abcABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is True
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK-----abc;ABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is False
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK------abcABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is False
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK-----\"abcABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is False
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK-----a:bcABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is False
    assert is_openpgp_public_key_allowed("----BEGIN PGP PUBLIC KEY BLOCK-----abcABC012=/+-----END PGP PUBLIC KEY BLOCK-----") is False
    assert is_openpgp_public_key_allowed("-----BEGIN PGP PUBLIC KEY BLOCK-----abcABC012=/+-----END PGP PUBLIC KEY BLOCK------") is False


def test_is_openpgp_key_fingerprint_allowed():
    assert is_openpgp_key_fingerprint_allowed("EF6E286DDA85EA2A4BA7DE684E2C6E8793298290") is True
    assert is_openpgp_key_fingerprint_allowed("EF6E286DDA85EA2A4BA7DE684E2C6E8793298290A") is False
    assert is_openpgp_key_fingerprint_allowed("F6E286DDA85EA2A4BA7DE684E2C6E8793298290") is False
    assert is_openpgp_key_fingerprint_allowed("EF6E286DDA85EA2A4:A7DE684E2C6E8793298290") is False
    assert is_openpgp_key_fingerprint_allowed("E;6E286DDA85EA2A4BA7DE684E2C6E8793298290") is False


def test_is_openpgp_keyring_allowed():
    assert is_openpgp_keyring_allowed("ABC012") is True
    assert is_openpgp_keyring_allowed("aBC012") is False
    assert is_openpgp_keyring_allowed("A:BC012") is False
    assert is_openpgp_keyring_allowed("AB;C012") is False
    assert is_openpgp_keyring_allowed("ABC$012") is False
    assert is_openpgp_keyring_allowed("ABC0@12") is False
    assert is_openpgp_keyring_allowed("ABC0&12") is False


def test_is_sha256_allowed():
    assert is_sha256_allowed("7b7632005be0f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0") is True
    assert is_sha256_allowed("") is False
    assert is_sha256_allowed("a1d4") is False
    assert is_sha256_allowed("a1b2") is False
    assert is_sha256_allowed("7b7632005be0f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0a") is False
    assert is_sha256_allowed("7b7632005be0f36c5d1663a6c5ec4d13315589d651ef8687fB4b9866f9bc4b0") is False
    assert is_sha256_allowed("7b7632005b.0f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0") is False
    assert is_sha256_allowed("7b7632005be\"f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0") is False
    assert is_sha256_allowed("7b7632005be-f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0") is False
    assert is_sha256_allowed("7b7632005b.0f36c5d1663a6c5ec4d13315589d65e1ef8687fb4b9866f9bc4b0") is False

def test_is_db_id_allowed():
    assert is_db_id_allowed("453") is False
    assert is_db_id_allowed("1") is False
    assert is_db_id_allowed("-1") is False
    assert is_db_id_allowed("Ab2v") is False
    assert is_db_id_allowed(-1) is False
    assert is_db_id_allowed(-123) is False
    assert is_db_id_allowed(0) is True
    assert is_db_id_allowed(1) is True
    assert is_db_id_allowed(4365) is True


def test_is_cookie_allowed():
    assert is_cookie_allowed("a"*128) is True
    assert is_cookie_allowed(("a"*126)+"1"+"A") is True
    assert is_cookie_allowed("A"*128) is True
    assert is_cookie_allowed("1"*128) is True
    assert is_cookie_allowed(("a"*126)+"-"+"A") is False
    assert is_cookie_allowed(("a"*126)+"_"+"A") is False
    assert is_cookie_allowed(("a"*126)+"4"+"!") is False
    assert is_cookie_allowed("aB1") is False
    assert is_cookie_allowed("a"*129) is False
    assert is_cookie_allowed("a"*127) is False


def test_is_password_key_allowed():
    data = "A"*4096
    assert is_password_key_allowed(data) is True
    assert is_password_key_allowed("A"*4097) is False
    assert is_password_key_allowed("A"*4095) is False

def test_is_filename_allowed():
    assert is_filename_allowed("aA3") is True
    assert is_filename_allowed("a.A3") is True
    assert is_filename_allowed("a-A3") is True
    assert is_filename_allowed("a_A3") is True
    assert is_filename_allowed("A"*256) is True
    assert is_filename_allowed("aA") is False
    assert is_filename_allowed("A"*257) is False
    assert is_filename_allowed("aA3#") is False
    assert is_filename_allowed("aA!3") is False
    assert is_filename_allowed("\"aA3") is False
    assert is_filename_allowed(".aA3") is False
    assert is_filename_allowed("-aA3") is False
    assert is_filename_allowed("_aA3") is False
    assert is_filename_allowed("aA3.") is False
    assert is_filename_allowed("aA3-") is False
    assert is_filename_allowed("aA3_") is False
    assert is_filename_allowed("a..A3") is False
    assert is_filename_allowed("a--A3") is False
    assert is_filename_allowed("a__A3") is False
    assert is_filename_allowed("a!A3") is False

def test_is_base64_allowed():
    assert is_base64_allowed("aA3+/=") is True
    assert is_base64_allowed("aA3+/=") is True
    assert is_base64_allowed("R2Vla3NGb3JHZWVrcyBpcyB0aGUgYmVzdA==") is True
    assert is_base64_allowed("aA") is False
    assert is_base64_allowed("A"*257) is False
    assert is_base64_allowed("R2Vla#3NGb3JHZWVrcyBpcyB0aGUgYmVzdA==") is False
    assert is_base64_allowed("R2Vla-3NGb3JHZWVrcyBpcyB0aGUgYmVzdA==") is False
    assert is_base64_allowed("R2Vla.3NGb3JHZWVrcyBpcyB0aGUgYmVzdA==") is False
