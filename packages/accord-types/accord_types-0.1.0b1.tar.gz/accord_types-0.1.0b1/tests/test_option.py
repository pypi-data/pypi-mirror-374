import unittest
from src.option import Option, Some
from typing import cast

class TestOption(unittest.TestCase):
    """Test suite for the Option type and its Some variant."""

    def test_some_creation(self):
        """Test creating a Some instance."""
        s = Some(10)
        self.assertIsInstance(s, Some)
        self.assertEqual(s._value, 10)

    def test_some_repr(self):
        """Test the string representation of Some."""
        self.assertEqual(repr(Some(10)), "Some(10)")
        self.assertEqual(repr(Some("hello")), "Some('hello')")
        self.assertEqual(repr(Some([1, 2])), "Some([1, 2])")
        self.assertEqual(repr(Some(None)), "None")

    def test_some_eq(self):
        """Test equality comparison for Some instances."""
        self.assertEqual(Some(10), Some(10))
        self.assertNotEqual(Some(10), Some(20))
        self.assertNotEqual(Some(10), None) 
        self.assertNotEqual(Some("a"), Some("b"))
        
        self.assertEqual(Some(None), Some(None))
        self.assertNotEqual(Some(None), Some(0))

    def test_some_hash(self):
        """Test hashing of Some instances."""
        s1 = Some(10)
        s2 = Some(10)
        s3 = Some(20)
        self.assertEqual(hash(s1), hash(s2))
        self.assertNotEqual(hash(s1), hash(s3))
        
        self.assertNotEqual(hash(s1), hash(None))
        
        self.assertEqual(hash(Some(None)), hash(("Some", None)))

    def test_is_some_and_is_none_for_some(self):
        """Test is_some and is_none for a valid Some instance."""
        s = Some(10)
        self.assertTrue(s.is_some())
        self.assertFalse(s.is_none())

    def test_is_some_and_is_none_for_some_holding_none(self):
        """Test is_some and is_none for Some(None) based on your implementation."""
        s: str = None
        s_with_none_value = Some(s)
        self.assertFalse(s_with_none_value.is_some()) 
        self.assertTrue(s_with_none_value.is_none())  

    def test_is_none_for_python_none(self):
        """Test that Python's None keyword acts like the 'None' variant of Option."""
        t: str = None
        s = cast(Option[str], Some(t))
        self.assertTrue(s.is_none())

    def test_unwrap_on_some_with_value(self):
        """Test unwrap on a Some instance with an actual value."""
        s = Some(10)
        self.assertEqual(s.unwrap(), 10)
        
        s_str = Some("hello")
        self.assertEqual(s_str.unwrap(), "hello")

    def test_unwrap_on_some_holding_none_raises_runtime_error(self):
        """Test unwrap on a Some(None) instance (based on your implementation)."""
        s: str = None
        s_with_none = Some(s)
        with self.assertRaisesRegex(RuntimeError, 'Called unwrap in a None Option value: None'):
            s_with_none.unwrap()

    def test_unwrap_implicitly_on_python_none_raises_runtime_error(self):
        """Test that using Python's None directly where unwrap might be implied fails."""
        def maybe_return_some_or_none(x):
            if x > 0:
                return cast(Option[int], Some(x))
            else:
                s: str = None
                return cast(Option[int], Some(s))

        option_val_positive = maybe_return_some_or_none(5)
        self.assertEqual(option_val_positive.unwrap(), 5)

        option_val_negative = maybe_return_some_or_none(-5)
        with self.assertRaisesRegex(RuntimeError, f'Called unwrap in a None Option value: None'):
            option_val_negative.unwrap()

    def test_expect_on_some_with_value(self):
        """Test expect on a Some instance with an actual value."""
        s = Some(10)
        self.assertEqual(s.expect("This should not happen"), 10)

    def test_expect_on_some_holding_none_raises_runtime_error(self):
        """Test expect on a Some(None) instance (based on your implementation)."""
        s: str = None
        s_with_none = Some(s)
        custom_msg = "Custom error message"
        with self.assertRaisesRegex(RuntimeError, f'{custom_msg}.\nNone'):
            s_with_none.expect(custom_msg)

    def test_unwrap_or_on_some_with_value(self):
        """Test unwrap_or on a Some instance with a value."""
        s = Some(10)
        self.assertEqual(s.unwrap_or(0), 10)
        
        s_str = Some("hello")
        self.assertEqual(s_str.unwrap_or("default"), "hello")

    def test_unwrap_or_on_some_holding_none(self):
        """Test unwrap_or on a Some(None) instance (based on your implementation)."""
        s: str = None
        s_with_none = Some(s)
        fallback_val = "default_fallback"
        self.assertEqual(s_with_none.unwrap_or(fallback_val), fallback_val)

    def test_unwrap_or_on_python_none(self):
        """Test unwrap_or on Python's None keyword."""
        s: str = None
        option_none = cast(Option[str], Some(s))
        fallback_val = "default_for_none"
        self.assertEqual(option_none.unwrap_or(fallback_val), fallback_val)

    def test_map_on_some_with_value(self):
        """Test map on a Some instance with a value."""
        s = Some(5)
        
        mapped_s = s.map(lambda x: x * 2)
        self.assertIsInstance(mapped_s, Some)
        self.assertEqual(mapped_s, Some(10))
        
        s_str = Some("abc")
        mapped_s_str = s_str.map(lambda x: x.upper())
        self.assertIsInstance(mapped_s_str, Some)
        self.assertEqual(mapped_s_str, Some("ABC"))

    def test_map_on_some_holding_none(self):
        """Test map on a Some(None) instance (based on your implementation)."""
        s: int = None
        s_with_none = Some(s)
        mapped_s_handled = s_with_none.map(lambda x: x * 2 if x is not None else 0)
        self.assertIsNone(mapped_s_handled)

        s_with_none.map(lambda x: x * 2)
        self.assertTrue(s_with_none.is_none())

        t = s_with_none.map(lambda x: x * 2)
        self.assertIsNone(t)
             
    def test_map_on_python_none(self):
        """Test map on Python's None keyword (as the None variant of Option)."""
        s: int = None
        mapped_option = cast(Option[int], Some(s)).map(lambda x: x * 2)
        self.assertIsNone(mapped_option) 

        none = Some(s)
        mapped_option_value = none.map(lambda x: "default_val")
        self.assertIsNone(mapped_option_value) 

        def func_returning_option(x):
            return Some(x) if x is not None else None

        mapped_option_func = none.map(func_returning_option)
        self.assertIsNone(mapped_option_func)


    def test_and_then_on_some_with_value(self):
        """Test and_then on a Some instance with a value."""
        s = Some(5)
        
        def process_value(val: int) -> Option[str]:
            if val > 0:
                return Some(f"Processed: {val}")
            else:
                return None 
        
        result = s.and_then(process_value)
        self.assertIsInstance(result, Some)
        self.assertEqual(result, Some("Processed: 5"))
        
        def return_none_option(val: int) -> Option[str]:
            return None 

        result_none = s.and_then(return_none_option)
        self.assertIsNone(result_none) 

    def test_and_then_on_some_holding_none(self):
        """Test and_then on a Some(None) instance (based on your implementation)."""
        s: str = None
        s_with_none = Some(s)
        
        def func_handling_none(val):
            if val is None:
                return Some("Got None from Some")
            return Some(f"Got value: {val}")

        result = s_with_none.and_then(func_handling_none)
        self.assertIsInstance(result, Some)
        self.assertEqual(result, Some("Got None from Some"))

        def func_not_handling_none(val):
            return Some(val + 1) 
            
        with self.assertRaises(TypeError): 
             s_with_none.and_then(func_not_handling_none)

    def test_and_then_on_python_none(self):
        """Test and_then on Python's None keyword (as the None variant of Option)."""
        
        def dummy_func(val):
            s: str = None
            return Some(s)
        
        result = cast(Option[str], Some(None)).and_then(dummy_func)
        self.assertTrue(result.is_none())

    def test_take_on_some_with_value(self):
        """Test the take method on a Some instance with a value."""
        s = Some(10)
        taken_value = s.take()
        
        self.assertEqual(taken_value, 10)
        self.assertIsNone(s._value) 
        self.assertTrue(s.is_none()) 
        self.assertFalse(s.is_some())
        
    def test_take_on_some_holding_none(self):
        """Test take on a Some instance that already holds None."""
        s: str = None
        s_with_none = Some(s)
        taken_value = s_with_none.take()
        
        self.assertIsNone(taken_value) 
        self.assertIsNone(s_with_none._value) 
        self.assertTrue(s_with_none.is_none())


if __name__ == '__main__':
    unittest.main()