from app.native_problems import native_problems


def test_original_problem_bank_has_all_difficulty_levels_and_private_tests():
    rows = native_problems()
    assert len(rows) >= 15
    assert {row['difficulty'] for row in rows} == {'Easy', 'Medium', 'Hard'}
    assert len({row['slug'] for row in rows}) == len(rows)
    for row in rows:
        assert row['description']
        assert row['examples']
        assert row['time_complexity']
        assert row['space_complexity']
        assert len(row['tests']) >= 2
        assert sum(1 for _, _, sample in row['tests'] if sample) >= 1


def test_all_native_tests_have_expected_input_and_output_strings():
    for row in native_problems():
        for input_data, expected_output, _ in row['tests']:
            assert isinstance(input_data, str)
            assert isinstance(expected_output, str)
            assert expected_output.strip() != ''
