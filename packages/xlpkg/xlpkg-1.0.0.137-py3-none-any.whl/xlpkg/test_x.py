import unittest
from xlpkg import x


class TestFSubinstr(unittest.TestCase):

    def test_f_subinstr_Mode0_CaseInsensitive(self):
        self.assertTrue(x.f_subinstr("abc", "Abcdef", m=0, s=0))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=0, s=0))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=0, s=0))

    def test_f_subinstr_Mode0_CaseSensitive(self):
        self.assertFalse(x.f_subinstr("abc", "Abcdef", m=0, s=1))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=0, s=1))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=0, s=1))

    def test_f_subinstr_Mode1_CaseInsensitive(self):
        self.assertTrue(x.f_subinstr("abc", "Abcdef", m=1, s=0))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=1, s=0))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=1, s=0))

    def test_f_subinstr_Mode1_CaseSensitive(self):
        self.assertFalse(x.f_subinstr("abc", "Abcdef", m=1, s=1))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=1, s=1))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=1, s=1))

    def test_f_subinstr_Mode2_CaseInsensitive(self):
        self.assertTrue(x.f_subinstr("abc", "Abcdef", m=2, s=0))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=2, s=0))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=2, s=0))

    def test_f_subinstr_Mode2_CaseSensitive(self):
        self.assertFalse(x.f_subinstr("abc", "Abcdef", m=2, s=1))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=2, s=1))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=2, s=1))

    def test_f_subinstr_Mode3_CaseInsensitive(self):
        self.assertTrue(x.f_subinstr("abc", "Abcdef", m=3, s=0))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=3, s=0))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=3, s=0))

    def test_f_subinstr_Mode3_CaseSensitive(self):
        self.assertFalse(x.f_subinstr("abc", "Abcdef", m=3, s=1))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=3, s=1))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=3, s=1))

    def test_f_subinstr_Mode4_CaseInsensitive(self):
        self.assertTrue(x.f_subinstr("abc", "Abcdef", m=4, s=0))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=4, s=0))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=4, s=0))

    def test_f_subinstr_Mode4_CaseSensitive(self):
        self.assertFalse(x.f_subinstr("abc", "Abcdef", m=4, s=1))
        self.assertTrue(x.f_subinstr("abc", "abcdef", m=4, s=1))
        self.assertFalse(x.f_subinstr("xyz", "abcdef", m=4, s=1))

    def test_f_subinstr_InvalidMode(self):
        with self.assertRaises(ValueError):
            x.f_subinstr("abc", "abcdef", m=5, s=1)

if __name__ == '__main__':
    a= TestFSubinstr()
    # a.test_f_subinstr_InvalidMode()
    a.test_f_subinstr_Mode0_CaseInsensitive()
    a.test_f_subinstr_Mode0_CaseSensitive()
    a.test_f_subinstr_Mode1_CaseInsensitive()
    a.test_f_subinstr_Mode1_CaseSensitive()
    a.test_f_subinstr_Mode2_CaseInsensitive()
    #a.test_f_subinstr_Mode2_CaseSensitive()
    a.test_f_subinstr_Mode3_CaseInsensitive()
    a.test_f_subinstr_Mode3_CaseSensitive()
    a.test_f_subinstr_Mode4_CaseInsensitive()
    a.test_f_subinstr_Mode4_CaseSensitive()
    #print(x.f_get_methods(TestFSubinstr))

    print('Game Over！')