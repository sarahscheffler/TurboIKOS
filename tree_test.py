import unittest
import tree

class TestTreeImplementation(unittest.TestCase):

    def test_even(self):
        """
        Test tree.py
        """
        n = 0
        for n_seeds in range(2, 20):
            for ommit in range(n_seeds-1):
                with self.subTest(i=n):
                    (seeds, root) = tree.make_tree(n_seeds)
                    path = tree.get_path(ommit, root)
                    recreated_seeds = tree.recreate_seeds(path)
                    count = 0
                    for s in range(len(seeds)):
                        if s!= ommit:
                            self.assertEqual(seeds[s], recreated_seeds[count], 'not equal %d%d' %(n_seeds, ommit))
                            count += 1
                n+=1 

if __name__ == '__main__':
    unittest.main()