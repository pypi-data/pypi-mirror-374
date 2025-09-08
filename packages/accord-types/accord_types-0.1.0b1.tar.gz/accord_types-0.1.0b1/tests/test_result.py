import unittest

from src.result import Result, Ok, Err

class TestResult(unittest.TestCase):
    """Test suite for the Result type and its variants Ok and Err."""

    def test_result_cannot_be_instantiated_directly(self):
        """Test that the abstract Result class cannot be instantiated."""
        with self.assertRaisesRegex(TypeError, "Can't instantiate abstract class Result"):
            Result() 

    def test_result_cannot_be_inherited_manually(self):
        """Test that Result cannot be subclassed arbitrarily."""
        with self.assertRaisesRegex(TypeError, "You cannot inherit from a sealed class"):
            class MyCustomResult(Result[int, str]): 
                def is_ok(self) -> bool: return False
                pass

    def test_ok_creation_and_properties(self):
        """Test Ok instance creation and its state properties."""
        ok_value = 42
        ok_result: Result[int, str] = Ok(ok_value) 

        self.assertTrue(ok_result.is_ok())
        self.assertFalse(ok_result.is_err())
        self.assertEqual(ok_result.unwrap(), ok_value)
        self.assertEqual(ok_result.unwrap_or(0), ok_value)

    def test_err_creation_and_properties(self):
        """Test Err instance creation and its state properties."""
        err_value = "An error occurred"
        err_result: Result[int, str] = Err(err_value)

        self.assertFalse(err_result.is_ok())
        self.assertTrue(err_result.is_err())
        self.assertEqual(err_result.unwrap_err(), err_value)
        self.assertEqual(err_result.unwrap_or(0), 0)

    def test_ok_unwrap(self):
        """Test unwrap on Ok returns the contained value."""
        self.assertEqual(Ok(10).unwrap(), 10)
        self.assertEqual(Ok("hello").unwrap(), "hello")

    def test_err_unwrap_raises_error(self):
        """Test unwrap on Err raises the contained error."""
        err_val = ValueError("test error")
        with self.assertRaises(ValueError) as cm:
            Err(err_val).unwrap()
        self.assertIs(cm.exception, err_val)

    def test_ok_expect(self):
        """Test expect on Ok returns the contained value."""
        self.assertEqual(Ok(10).expect("Should not panic"), 10)

    def test_err_expect_raises_runtime_error(self):
        """Test expect on Err raises a RuntimeError with the custom message."""
        err_val = "original error"
        custom_msg = "This operation failed"
        with self.assertRaisesRegex(RuntimeError, f"{custom_msg}.\n{err_val!r}"):
            Err(err_val).expect(custom_msg)

    def test_ok_unwrap_err_raises_runtime_error(self):
        """Test unwrap_err on Ok raises a RuntimeError."""
        ok_val = 10
        with self.assertRaisesRegex(RuntimeError, f"Called unwrap_err on an Ok value: {ok_val!r}"):
            Ok(ok_val).unwrap_err()

    def test_err_unwrap_err(self):
        """Test unwrap_err on Err returns the contained error."""
        err_val = "An error"
        self.assertEqual(Err(err_val).unwrap_err(), err_val)

    def test_ok_unwrap_or(self):
        """Test unwrap_or on Ok returns the contained value, ignoring the fallback."""
        self.assertEqual(Ok(10).unwrap_or(0), 10)

    def test_err_unwrap_or(self):
        """Test unwrap_or on Err returns the fallback value."""
        self.assertEqual(Err("error").unwrap_or(0), 0)

    def test_ok_map(self):
        """Test map on Ok applies the function to the contained value."""
        ok_result: Result[int, str] = Ok(5)
        mapped_result: Result[str, str] = ok_result.map(lambda x: f"Value is {x}")
        self.assertEqual(mapped_result, Ok("Value is 5"))

    def test_err_map(self):
        """Test map on Err does nothing and returns the original Err."""
        err_result: Result[int, str] = Err("error")
        mapped_result: Result[str, str] = err_result.map(lambda x: f"Value is {x}")
        self.assertEqual(mapped_result, Err("error"))

    def test_ok_map_err(self):
        """Test map_err on Ok does nothing and returns the original Ok."""
        ok_result: Result[int, str] = Ok(5)
        mapped_result: Result[int, ValueError] = ok_result.map_err(lambda e: ValueError(e))
        self.assertEqual(mapped_result, Ok(5))

    def test_err_map_err(self):
        """Test map_err on Err applies the function to the contained error."""
        err_result: Result[int, str] = Err("error")
        mapped_result: Result[int, ValueError] = err_result.map_err(lambda e: ValueError(f"Error: {e}"))
        self.assertEqual(mapped_result, Err(ValueError("Error: error")))

    def test_ok_and_then(self):
        """Test and_then on Ok applies the function and returns the new Result."""
        ok_result: Result[int, str] = Ok(5)
        chained_result: Result[str, str] = ok_result.and_then(lambda x: Ok(f"Success: {x}"))
        self.assertEqual(chained_result, Ok("Success: 5"))

    def test_ok_and_then_with_err(self):
        """Test and_then on Ok that returns an Err."""
        ok_result: Result[int, str] = Ok(5)
        chained_result: Result[str, str] = ok_result.and_then(lambda x: Err("Failed in chain"))
        self.assertEqual(chained_result, Err("Failed in chain"))

    def test_err_and_then(self):
        """Test and_then on Err does nothing and returns the original Err."""
        err_result: Result[int, str] = Err("initial error")
        chained_result: Result[str, str] = err_result.and_then(lambda x: Ok(f"Success: {x}"))
        self.assertEqual(chained_result, Err("initial error"))

    def test_ok_or_else(self):
        """Test or_else on Ok does nothing and returns the original Ok."""
        ok_result: Result[int, str] = Ok(5)
        fallback_result: Result[int, ValueError] = ok_result.or_else(lambda e: Err(ValueError(e)))
        self.assertEqual(fallback_result, Ok(5))

    def test_err_or_else(self):
        """Test or_else on Err applies the function and returns the new Result."""
        err_result: Result[int, str] = Err("initial error")
        fallback_result: Result[int, ValueError] = err_result.or_else(lambda e: Err(ValueError(f"Recovered from: {e}")))
        self.assertEqual(fallback_result, Err(ValueError("Recovered from: initial error")))

    def test_err_or_else_with_ok(self):
        """Test or_else on Err that returns an Ok."""
        err_result: Result[int, str] = Err("initial error")
        fallback_result: Result[int, ValueError] = err_result.or_else(lambda e: Ok(100))
        self.assertEqual(fallback_result, Ok(100))

    def test_repr(self):
        """Test the __repr__ method for Ok and Err."""
        self.assertEqual(repr(Ok(10)), "Ok(10)")
        self.assertEqual(repr(Ok("hello")), "Ok('hello')")
        self.assertEqual(repr(Err("error")), "Err('error')")
        self.assertEqual(repr(Err(ValueError("oops"))), "Err(ValueError('oops'))")

    def test_equality(self):
        """Test the __eq__ method for Ok and Err."""
        self.assertEqual(Ok(10), Ok(10))
        self.assertNotEqual(Ok(10), Ok(20))
        self.assertNotEqual(Ok(10), Err("error"))
        self.assertEqual(Err("error"), Err("error"))
        self.assertNotEqual(Err("error"), Err("another error"))
        self.assertNotEqual(Err("error"), Ok(10))

    def test_hash(self):
        """Test the __hash__ method for Ok and Err."""
        ok_set = {Ok(10), Ok(20), Ok(10)}
        self.assertEqual(len(ok_set), 2)
        self.assertIn(Ok(10), ok_set)
        self.assertIn(Ok(20), ok_set)

        err_set = {Err("error"), Err("another"), Err("error")}
        self.assertEqual(len(err_set), 2)
        self.assertIn(Err("error"), err_set)
        self.assertIn(Err("another"), err_set)

        mixed_set = {Ok(10), Err("error"), Ok(10), Err("error")}
        self.assertEqual(len(mixed_set), 2)


if __name__ == '__main__':
    unittest.main()