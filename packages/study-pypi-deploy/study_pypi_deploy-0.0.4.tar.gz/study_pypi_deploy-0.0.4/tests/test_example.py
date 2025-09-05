def test_add_one():
    from study_pypi_deploy.example import add_one
    assert add_one(1) == 2

def test_divide():
    from study_pypi_deploy.example import divide
    assert divide(6, 3) == 2
    assert divide(8, 2) == 4
    assert divide(10, 5) == 2