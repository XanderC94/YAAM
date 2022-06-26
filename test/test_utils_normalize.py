'''
Path normalize unit test module
'''
import unittest
from yaam.utils.path import Path
from yaam.utils import normalize


class TestNormalizeModule(unittest.TestCase):
    '''
    Path normalize unit test
    '''
    def test_if_path_starts_with_double_dots_they_should_be_stripped_1(self):
        '''
        Test 1
        '''
        path = Path("../../a/b/c/d.txt")
        root = Path("T:/foo/bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a/b/c/d.txt")

    def test_if_path_starts_with_double_dots_they_should_be_stripped_2(self):
        '''
        Test 2
        '''
        path = Path("..\\..\\a\\b\\c\\d.txt")
        root = Path("T:\\foo\\bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a\\b\\c\\d.txt")

    def test_if_path_starts_with_single_dot_it_should_be_stripped_1(self):
        '''
        Test 3
        '''
        path = Path("./a/b/c/d.txt")
        root = Path("T:/foo/bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a/b/c/d.txt")

    def test_if_path_starts_with_single_dot_it_should_be_stripped_2(self):
        '''
        Test 2
        '''
        path = Path(".\\a\\b\\c\\d.txt")
        root = Path("T:\\foo\\bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a\\b\\c\\d.txt")

    def test_if_path_starts_with_slash_it_should_be_stripped_1(self):
        '''
        Test 3
        '''
        path = Path("/a/b/c/d.txt")
        root = Path("T:/foo/bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a/b/c/d.txt")

    def test_if_path_starts_with_slash_it_should_be_stripped_2(self):
        '''
        Test 2
        '''
        path = Path("\\a\\b\\c\\d.txt")
        root = Path("T:\\foo\\bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a\\b\\c\\d.txt")

    def test_if_relative_path_should_just_be_joined_2(self):
        '''
        Test 3
        '''
        path = Path("a/b/c/d.txt")
        root = Path("T:/foo/bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a/b/c/d.txt")

    def test_if_relative_path_should_just_be_joined_1(self):
        '''
        Test 2
        '''
        path = Path("a\\b\\c\\d.txt")
        root = Path("T:\\foo\\bar")

        test = normalize.normalize_abs_path(path, root)

        self.assertEqual(test, root / "a\\b\\c\\d.txt")


if __name__ == '__main__':
    unittest.main()
