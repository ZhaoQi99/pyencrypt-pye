from util import random_list

from pyencrypt.ntt import ntt, intt
import pytest


class TestNtt:
    @pytest.mark.parametrize(
        "input,expected",
        [
            ([1, 2, 3, 4], [10, 173167434, 998244351, 825076915]),
            (
                [1, 2, 3, 4, 5, 0, 0, 0],
                [
                    15,
                    443713764,
                    173167439,
                    730825730,
                    3,
                    35028273,
                    825076920,
                    786920923,
                ],
            ),
        ],
    )
    def test_ntt(self, input, expected):
        assert ntt(input) == expected

    @pytest.mark.parametrize(
        "input,expected",
        [
            ([10, 173167434, 998244351, 825076915], [1, 2, 3, 4]),
            (
                [
                    15,
                    443713764,
                    173167439,
                    730825730,
                    3,
                    35028273,
                    825076920,
                    786920923,
                ],
                [1, 2, 3, 4, 5, 0, 0, 0],
            ),
        ],
    )
    def test_ntt_inverse(self, input, expected):
        assert intt(input) == expected

    @pytest.mark.parametrize(
        "input",
        [
            [1, 2, 3, 4, 5],
            random_list(6),
            random_list(7),
        ],
    )
    def test_ntt_exception(self, input):
        with pytest.raises(ValueError) as excinfo:
            ntt(input)
        assert str(excinfo.value) == "The length of input must be a power of 2."

    @pytest.mark.parametrize(
        "input",
        [
            [1, 2, 3, 4, 5],
            random_list(6),
            random_list(7),
        ],
    )
    def test_intt_exception(self, input):
        with pytest.raises(ValueError) as excinfo:
            intt(input)
        assert str(excinfo.value) == "The length of input must be a power of 2."

    @pytest.mark.parametrize(
        "input,expected",
        [
            (random_list(4), 4),
            (random_list(8), 8),
            (random_list(16), 16),
        ],
    )
    def test_ntt_result_length(self, input, expected):
        assert len(ntt(input)) == expected

    @pytest.mark.parametrize(
        "input,expected",
        [
            (random_list(4), 4),
            (random_list(8), 8),
            (random_list(16), 16),
        ],
    )
    def test_intt_result_length(self, input, expected):
        assert len(intt(input)) == expected
