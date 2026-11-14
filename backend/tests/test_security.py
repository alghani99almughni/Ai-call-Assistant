from app.security import hash_password,verify_password

def test_password_hash_is_salted_and_verifiable():
    one=hash_password("correct horse battery staple")
    two=hash_password("correct horse battery staple")
    assert one != two
    assert verify_password("correct horse battery staple",one)
    assert not verify_password("wrong password",one)
    assert not verify_password("correct horse battery staple",two.replace("pbkdf2_sha256$","bad$"))
