'''
Forward counter class test module
'''

import unittest
from yaam.utils.counter import ForwardCounter


class TestForwardCounter(unittest.TestCase):
    '''
    ForwardCounter test class
    '''

    def test_increment(self):
        '''
        Test 1
        '''
        counter = ForwardCounter()
        self.assertEqual(counter.count(), 0)
        self.assertEqual(counter.next(), 2)

    def test_start_step(self):
        '''
        Test 2
        '''
        counter = ForwardCounter(3, 3)
        self.assertEqual(counter.count(), 3)
        self.assertEqual(counter.next(), 9)

    def test_start_step_negative(self):
        '''
        Test 3
        '''
        counter = ForwardCounter(3, -3)
        self.assertEqual(counter.count(), 3)
        self.assertEqual(counter.next(), -3)

    def test_sum_int(self):
        '''
        Test 3
        '''
        counter = ForwardCounter()
        counter.next()
        self.assertEqual(counter + 1, 2)

    def test_sum_counter(self):
        '''
        Test 3
        '''
        counter1 = ForwardCounter()
        counter2 = ForwardCounter(3, 3)
        counter1.next()
        counter2.next()
        self.assertEqual(counter1 + counter2, 7)
