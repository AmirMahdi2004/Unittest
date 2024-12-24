import traceback
from unittest import TestCase
import funcs
from itertools import count, cycle


class TakeTests(TestCase):
    def test_simple_take(self):
        t = funcs.take(range(10), 5)
        self.assertEqual(t, [0, 1, 2, 3, 4])

    def test_null_take(self):
        t = funcs.take(range(10), 0)
        self.assertEqual(t, [])

    def test_negative_take(self):
        self.assertRaises(ValueError, lambda: funcs.take(-3, range(10)))

    def test_take_too_much(self):
        t = funcs.take(range(5), 10)
        self.assertEqual(t, [0, 1, 2, 3, 4])


class ChunkedTests(TestCase):
    def test_even(self):
        self.assertEqual(
            list(funcs.chunked('ABCDEF', 3)), [['A', 'B', 'C', ], ['D', 'E', 'F']]
        )

    def test_odd_even(self):
        self.assertEqual(
            list(funcs.chunked('ABCDE', 3)), [['A', 'B', 'C'], ['D', 'E']]
        )

    def test_none(self):
        self.assertEqual(
            list(funcs.chunked('ABCDE', None)), [['A', 'B', 'C', 'D', 'E']]
        )

    def test_strict_false(self):
        self.assertEqual(
            list(funcs.chunked('ABCDE', 3, False)),
            [['A', 'B', 'C'], ['D', 'E']]
        )

    def test_strict_true(self):
        def f():
            return list(funcs.chunked('ABCDE', 3, True))

        self.assertRaisesRegex(ValueError, 'iterator is not divisible by n', f)
        self.assertEqual(
            list(funcs.chunked('ABCDEF', 3, True)), [['A', 'B', 'C'], ['D', 'E', 'F']]
        )

    def test_strict_true_none(self):
        def f():
            return list(funcs.chunked('ABCDE', None, True))

        self.assertRaisesRegex(
            ValueError, 'n cant be None when strict is True', f
        )


class FirstTest(TestCase):
    def test_empty(self):
        self.assertEqual(funcs.first(x for x in range(4)), 0)

    def test_one(self):
        self.assertEqual(funcs.first([3]), 3)

    def test_default(self):
        self.assertEqual(funcs.first([], 'boo'), 'boo')

    def test_empty_stop_iteration(self):
        try:
            funcs.first([])
        except ValueError:
            formatted_exc = traceback.format_exc()
            self.assertIn('StopIteration', formatted_exc)
            self.assertIn('The above exception was the direct cause', formatted_exc)
        else:
            self.fail()


class LastTest(TestCase):
    def test_basic(self):
        cases = [
            (range(4), 3),
            (iter(range(4)), 3),
            (range(1), 0),
            (iter(range(1)), 0),
            ({n: str(n) for n in range(5)}, 4)
        ]

        for iterable, expected in cases:
            with self.subTest(iterable=iterable):
                self.assertEqual(funcs.last(iterable), expected)

    def test_default(self):
        for iterable, default, expected in [
            (range(1), None, 0),
            ([], None, None),
            ({}, None, None),
            (iter([]), None, None)
        ]:
            with self.subTest(args=(iterable, default)):
                self.assertEqual(funcs.last(iterable, default=default), expected)

    def test_empty(self):
        for iterable in ([], iter(range(0))):
            with self.subTest(iterable=iterable):
                with self.assertRaises(ValueError):
                    funcs.last(iterable)


class NthOrLastTest(TestCase):
    def test_basic(self):
        self.assertEqual(funcs.nth_or_last(range(3), 1), 1)
        self.assertEqual(funcs.nth_or_last(range(3), 3), 2)

    def test_default_value(self):
        default = 42
        self.assertEqual(funcs.nth_or_last(range(0), 3, default), default)

    def test_empty_iterable_no_default(self):
        self.assertRaises(ValueError, lambda: funcs.nth_or_last(range(0), 0))


class OneTests(TestCase):
    def test_basic(self):
        it = ['item']
        self.assertEqual(funcs.one(it), 'item')

    def test_too_short(self):
        it = []
        for too_short, exc_type in [
            (None, ValueError),
            (IndexError, IndexError)
        ]:
            with self.subTest(too_short=too_short):
                try:
                    funcs.one(it, too_short=too_short)
                except exc_type:
                    formatted_exc = traceback.format_exc()
                    self.assertIn('StopIteration', formatted_exc)
                    self.assertIn('The above exception was the direct cause', formatted_exc)
                else:
                    self.fail()

    def test_too_long(self):
        it = count()
        self.assertRaises(ValueError, lambda: funcs.one(it))
        self.assertEqual(next(it), 2)
        self.assertRaises(
            OverflowError, lambda: funcs.one(it, too_long=OverflowError)
        )

    def test_too_long_default_message(self):
        it = count()
        self.assertRaisesRegex(
            ValueError,
            'Expected exactly one itme in iterable , but goy 0,1,'
            'and perhaps more.',
            lambda: funcs.one(it)
        )


class InterLeaveTest(TestCase):
    def test_even(self):
        actual = list(funcs.interleave([1, 4, 7], [2, 5, 8], [3, 6, 9]))
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.assertEqual(actual, expected)

    def test_shrt(self):
        actual = list(funcs.interleave([1, 4], [2, 5, 7], [3, 6, 8]))
        expected = [1, 2, 3, 4, 5, 6]
        self.assertEqual(actual, expected)

    def test_mixed_types(self):
        it_list = ['a', 'b', 'c', 'd']
        it_str = '123456'
        it_inf = count()
        actual = list(funcs.interleave(it_list, it_str, it_inf))
        expected = ['a', '1', 0, 'b', '2', 1, 'c', '3', 2, 'd', '4', 3]
        self.assertEqual(actual, expected)


class RepeatEachTests(TestCase):
    def test_default(self):
        actual = list(funcs.repeat_each('ABC'))
        expected = ['A', 'A', 'B', 'B', 'C', 'C']
        self.assertEqual(actual, expected)

    def test_basic(self):
        actual = list(funcs.repeat_each('ABC', 3))
        expected = ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C']
        self.assertEqual(actual, expected)

    def test_empty(self):
        actual = list(funcs.repeat_each(''))
        expected = []
        self.assertEqual(actual, expected)

    def test_no_repeats(self):
        actual = list(funcs.repeat_each('ABC', 0))
        expected = []
        self.assertEqual(actual, expected)

    def test_negative_repeat(self):
        actual = list(funcs.repeat_each('ABC', -1))
        expected = []
        self.assertEqual(actual, expected)

    def test_infinite_input(self):
        repeater = funcs.repeat_each(cycle('AB'))
        actual = funcs.take(repeater, 6)
        expected = ['A', 'A', 'B', 'B', 'A', 'A']
        self.assertEqual(actual, expected)


class StrictlyNTests(TestCase):
    def test_basic(self):
        iterable = ['a', 'b', 'c', 'd']
        n = 4
        actual = list(funcs.strictly_n(iterable, n))
        expected = iterable
        self.assertEqual(actual, expected)

    def test_too_short_default(self):
        iterable = ['a', 'b', 'c', 'd']
        n = 5
        with self.assertRaises(ValueError) as exc:
            list(funcs.strictly_n(iterable, n))
        self.assertEqual(
            'Too few items in iterable (got 4)', exc.exception.args[0]
        )

    def test_too_long_default(self):
        iterable = ['a', 'b', 'c', 'd']
        n = 3
        with self.assertRaises(ValueError) as exc:
            list(funcs.strictly_n(iterable, n))
        self.assertEqual('Too few items in iterable (got at least 4', exc.exception.args[0])

    def test_too_short_custom(self):
        call_count = 0

        def too_short(item_count):
            nonlocal call_count
            call_count += 1

        iterable = ['a', 'b', 'c', 'd']
        n = 6
        actual = []

        for item in funcs.strictly_n(iterable, n, too_short=too_short):
            actual.append(item)
        expected = ['a', 'b', 'c', 'd']
        self.assertEqual(actual, expected)
        self.assertEqual(call_count, 1)

    def test_too_long_custom(self):
        import logging

        iterable = ['a', 'b', 'c', 'd']
        n = 2
        too_long = lambda item_count: logging.warning(f'Picked the first {n} items')
        with self.assertLogs(level='WARNING') as exc:
            actual = list(funcs.strictly_n(iterable, n, too_long=too_long))
        self.assertEqual(actual, ['a', 'b'])
        self.assertIn('Picked the first 2 items', exc.output[0])


class OnlyTests(TestCase):
    def test_defaults(self):
        self.assertEqual(funcs.only([]), None)
        self.assertEqual(funcs.only([1]), 1)
        self.assertRaises(ValueError, lambda: funcs.only([1, 2]))

    def test_custom_value(self):
        self.assertEqual(funcs.only([], default='!'), '!')
        self.assertEqual(funcs.only([1], default='!'), 1)
        self.assertRaises(ValueError, lambda: funcs.only([1, 2], default='!'))

    def test_custom_exception(self):
        self.assertEqual(funcs.only([], too_long=RuntimeError), None)
        self.assertEqual(funcs.only([1], too_long=RuntimeError), 1)
        self.assertRaises(RuntimeError, lambda: funcs.only([1, 2], too_long=RuntimeError))

    def test_default_exception_message(self):
        self.assertRaisesRegex(
            ValueError,
            'Expected exactly one item in iterable, but got foo, bar'
            'and perhaps more.',
            lambda: funcs.only(['foo', 'bar', 'baz'])

        )


class AlwaysReversibleTests(TestCase):
    def test_regular_reversed(self):
        self.assertEqual(
            list(reversed(range(10))), list(funcs.always_reversible(range(10)))
        )
        self.assertEqual(
            list(reversed([1, 2, 3])), list(funcs.always_reversible([1, 2, 3]))

        )
        self.assertEqual(
            reversed([1, 2, 3]).__class__, funcs.always_reversible([1, 2, 3]).__class__

        )

    def test_nonseq_reversed(self):
        self.assertEqual(
            list(reversed(range(10))), list(funcs.always_reversible(x for x in range(10)))
        )
        self.assertEqual(
            list(reversed([1, 2, 3])), list(funcs.always_reversible(x for x in [1, 2, 3]))
        )
        self.assertNotEqual(
            reversed((1, 2)).__class__, funcs.always_reversible(x for x in (1, 2)).__class__
        )


class AlwaysIterableTests(TestCase):
    def test_single(self):
        self.assertEqual(list(funcs.always_iterable(1)), [1])

    def test_string(self):
        for obj in ['foo', b'bar', 'baz']:
            actual = list(funcs.always_iterable(obj))
            expected = [obj]
            self.assertEqual(actual, expected)

    def test_base_type(self):
        dict_obj = {'a': 1, 'b': 2}
        str_obj = '123'
        default_actual = list(funcs.always_iterable(dict_obj))
        default_expected = list(dict_obj)
        self.assertEqual(default_actual, default_expected)

        custom_actual = list(funcs.always_iterable(dict_obj, base_type=dict))
        custom_expected = [dict_obj]
        self.assertEqual(custom_actual, custom_expected)
        str_actual = list(funcs.always_iterable(str_obj, base_type=None))
        str_expected = list(str_obj)
        self.assertEqual(str_actual, str_expected)

        base_type = ((dict,),)
        custom_actual = list(funcs.always_iterable(dict_obj, base_type=base_type))
        custom_expected = [dict_obj]
        self.assertEqual(custom_actual, custom_expected)

    def test_iterables(self):
        self.assertEqual(list(funcs.always_iterable([0, 1])), [0, 1])
        self.assertEqual(list(funcs.always_iterable([0, 1], base_type=list)), [[0, 1]])
        self.assertEqual(list(funcs.always_iterable(iter('foo'))), ['f', 'o', 'o'])
        self.assertEqual(list(funcs.always_iterable([])), [])

    def test_none(self):
        self.assertEqual(list(funcs.always_iterable(None)), [])

    def test_generator(self):
        def _gen():
            yield 0
            yield 1

        self.assertEqual(list(funcs.always_iterable(_gen())), [0, 1])


class SplitAfterTest(TestCase):
    def test_start_with_sep(self):
        actual = list(funcs.split_after('xooxoo', lambda c: c == 'x'))
        expected = [['x'], ['o', 'o', 'x'], ['o', 'o']]
        self.assertEqual(actual, expected)

    def test_ends_with_sep(self):
        actual = list(funcs.split_after('ooxoox', lambda c: c == 'x'))
        expected = [['o', 'o', 'x'], ['o', 'o', 'x']]
        self.assertEqual(actual, expected)

    def test_on_sep(self):
        actual = list(funcs.split_after('ooo', lambda c: c == 'x'))
        expected = [['o', 'o', 'o']]
        self.assertEqual(actual, expected)

    def test_max_split(self):
        for args, expected in [
            (
                    ('a,b,c,d', lambda c: c == ',', -1),
                    [['a', ','], ['b', ','], ['c', ','], ['d']]
            ),
            (
                    ('a,b,c,d', lambda c: c == ',', 0),
                    [['a', ',', 'b', ',', 'c', ',', 'd']]
            ),
            (
                    ('a,b,c,d', lambda c: c == ',', 1),
                    [['a', ','], ['b', ',', 'c', ',', 'd']]
            ),
            (
                    ('a,b,c,d', lambda c: c == ',', 2),
                    [['a', ','], ['b', ','], ['c', ',', 'd']]
            ),
            (
                    ('a,b,c,d', lambda c: c == ',', 10),
                    [['a', ','], ['b', ','], ['c', ','], ['d']]

            ),
            (
                    ('a,b,c,d', lambda c: c == '@', 2),
                    [['a', ',', 'b', ',', 'c', ',', 'd']]

            ),
            (
                    ('a,b,c,d', lambda c: c != ',', 2),
                    [['a'], [',', 'b'], [',', 'c', ',', 'd']]

            )
        ]:
            actual = list(funcs.split_after(*args))
            self.assertEqual(actual, expected)


class SplitIntoTests(TestCase):
    def test_iterable_just_right(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [2, 3, 4]
        expected = [[1, 2], [3, 4, 5], [6, 7, 8, 9]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_iterable_too_small(self):
        iterable = [1, 2, 3, 4, 5, 6, 7]
        sizes = [2, 3, 4]
        expected = [[1, 2], [3, 4, 5], [6, 7]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_iterable_too_small_extra(self):
        iterable = [1, 2, 3, 4, 5, 6, 7]
        sizes = [2, 3, 4, 5]
        expected = [[1, 2], [3, 4, 5], [6, 7], []]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_iterable_too_large(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [2, 3, 2]
        expected = [[1, 2], [3, 4, 5], [6, 7]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_using_none_with_leftover(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [2, 3, None]
        expected = [[1, 2], [3, 4, 5], [6, 7, 8, 9]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_using_none_without_leftover(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [2, 3, 4, None]
        expected = [[1, 2], [3, 4, 5], [6, 7, 8, 9], []]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_using_none_mid_sizes(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [2, 3, None, 4]
        expected = [[1, 2], [3, 4, 5], [6, 7, 8, 9]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_iterable_empty(self):
        iterable = []
        sizes = [1, 4, 2]
        expected = [[], [], []]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_iterable_empty_using_none(self):
        iterable = []
        sizes = [2, 4, None, 2]
        expected = [[], [], []]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_sizes_empty(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = []
        expected = []
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_both_empty(self):
        iterable = []
        sizes = []
        expected = []
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_bool_in_sizes(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [3, True, 2, False]
        expected = [[1, 2, 3], [4], [5, 6], []]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_invalid_in_sizes(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [1, [], 3]
        with self.assertRaises(ValueError):
            list(funcs.split_into(iterable, sizes))

    def test_invalid_in_sizes_after_none(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = [3, 4, None, []]
        expected = [[1, 2, 3], [4, 5, 6, 7], [8, 9]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

    def test_generator_iterable_integrity(self):
        iterable = (i for i in range(10))
        sizes = [2, 3]
        expected = [[0, 1], [2, 3, 4]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)
        iterable_expected = [5, 6, 7, 8, 9]
        iterable_actual = list(iterable)
        self.assertEqual(iterable_actual, iterable_expected)

    def test_generator_sizes_integrity(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        sizes = (i for i in [1, 2, None, 3, 4])
        expected = [[1], [2, 3], [4, 5, 6, 7, 8, 9]]
        actual = list(funcs.split_into(iterable, sizes))
        self.assertEqual(actual, expected)

        sizes_expected = [3, 4]
        sizes_actual = list(sizes)
        self.assertEqual(sizes_actual, sizes_expected)


class MapIFTests(TestCase):
    def test_without_func_else(self):
        iterable = list(range(-5, 5))
        actual = list(funcs.map_if(iterable, lambda x: x > 3, lambda x: 'toobig'))
        expected = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 'toobig']
        self.assertEqual(actual, expected)

    def test_with_func_else(self):
        iterable = list(range(-5, 5))
        actual = list(funcs.map_if(iterable, lambda x: x >= 0, lambda x: 'notneg', lambda x: 'neg'))
        expected = ['neg'] * 5 + ['notneg']*5
        self.assertEqual(actual, expected)

    def test_empty(self):
        actual = list(funcs.map_if([], lambda x: len(x) > 5, lambda x: None))
        expected = []
        self.assertEqual(actual,expected)
