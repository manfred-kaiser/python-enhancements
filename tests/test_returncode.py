from enhancements.returncode import BaseReturnCode, WrongResultSubclass, WrongResultValue
import pytest  # type: ignore


def test_default_result():
    class DefaultResultClass(BaseReturnCode):
        Success = BaseReturnCode.Result('success', 10)
        Skip = BaseReturnCode.Result('skip', 11, skip=True)
        Error = BaseReturnCode.Result('error', 12)

    assert sorted(DefaultResultClass.get_results().keys()) == [10, 11, 12]
    assert sorted(DefaultResultClass.get_result_types()) == ['error', 'skip', 'success']

    assert DefaultResultClass.convert('success') == DefaultResultClass.Success
    assert DefaultResultClass.convert('success') == 10

    assert DefaultResultClass.Success == 'success'
    assert DefaultResultClass.Success == 10

    assert DefaultResultClass.min() == 10
    assert DefaultResultClass.max() == 12

    assert DefaultResultClass.Success < DefaultResultClass.Error
    assert DefaultResultClass.Success <= DefaultResultClass.Success
    assert DefaultResultClass.Success <= DefaultResultClass.Error
    assert DefaultResultClass.Error > DefaultResultClass.Success
    assert DefaultResultClass.Error >= DefaultResultClass.Success

    assert DefaultResultClass.get_score(DefaultResultClass.Error, DefaultResultClass.Success) == 'error'
    assert DefaultResultClass.get_score(DefaultResultClass.Skip, DefaultResultClass.Success) == 'success'

    result = DefaultResultClass('success')
    assert result.set_result(DefaultResultClass.Error) is True
    assert isinstance(result.result, DefaultResultClass.Result)

    assert result.result == 'error'
    assert result.set_result('success') is False
    assert result.set_result('success', force=True) is True
    assert result.set_result('skip') is False
    assert result.set_result('skip', force=True) is True

    result.result = 'success'
    assert result.result == 11
    assert result.set_result(10, force=True) is True
    assert result.result == 'success'
    assert result.result == DefaultResultClass.Success

    result.result = 'error'
    assert isinstance(result.result, DefaultResultClass.Result)
    assert result.result == 12
    assert result.result == 'error'
    assert result.result == DefaultResultClass.Error

    assert DefaultResultClass.Result.convert('success') == 10

    with pytest.raises(ValueError):  # type: ignore
        DefaultResultClass.convert('invalid')


def test_custom_class():

    class CustomScanResult(BaseReturnCode):
        class Result(BaseReturnCode.Result):
            pass
        Success = Result('success', 10)
        Skip = Result('skip', 11, skip=True)
        Error = Result('error', 12)

    assert sorted(CustomScanResult.get_results().keys()) == [10, 11, 12]
    assert sorted(CustomScanResult.get_result_types()) == ['error', 'skip', 'success']

    assert CustomScanResult.convert('success') == CustomScanResult.Success
    assert CustomScanResult.convert('success') == 10

    assert CustomScanResult.Success == 'success'
    assert CustomScanResult.Success == 10

    assert CustomScanResult.min() == 10
    assert CustomScanResult.max() == 12

    assert CustomScanResult.Success < CustomScanResult.Error
    assert CustomScanResult.Success <= CustomScanResult.Success
    assert CustomScanResult.Success <= CustomScanResult.Error
    assert CustomScanResult.Error > CustomScanResult.Success
    assert CustomScanResult.Error >= CustomScanResult.Success

    assert CustomScanResult.get_score(CustomScanResult.Error, CustomScanResult.Success) == 'error'
    assert CustomScanResult.get_score(CustomScanResult.Skip, CustomScanResult.Success) == 'success'

    result = CustomScanResult('success')
    assert result.set_result(CustomScanResult.Error) is True
    assert isinstance(result.result, CustomScanResult.Result)

    assert result.result == 'error'
    assert result.set_result('success') is False
    assert result.set_result('success', force=True) is True
    assert result.set_result('skip') is False
    assert result.set_result('skip', force=True) is True

    result.result = 'success'
    assert result.result == 11
    assert result.set_result(10, force=True) is True
    assert result.result == 'success'
    assert result.result == CustomScanResult.Success

    result.result = 'error'
    assert isinstance(result.result, CustomScanResult.Result)
    assert result.result == 12
    assert result.result == 'error'
    assert result.result == CustomScanResult.Error

    assert CustomScanResult.Result.convert('success') == 10

    with pytest.raises(ValueError):  # type: ignore
        CustomScanResult.convert('invalid')


def test_wrong_subclass():
    with pytest.raises(WrongResultSubclass):  # type: ignore
        class CustomScanWrongResultClass(BaseReturnCode):
            class Result():  # type: ignore
                pass


def test_wrong_result_subclass():
    with pytest.raises(WrongResultValue):  # type: ignore
        class CustomScanWrongResultClass(BaseReturnCode):  # pyright: reportUnusedClass=false
            class Result(BaseReturnCode.Result):
                pass
            Success = BaseReturnCode.Result('success', 10)


def test_lt_comperator():
    import operator

    class CustomScanResult(BaseReturnCode):
        class Result(BaseReturnCode.Result):
            pass
        COMPERATOR = operator.lt

        Success = Result('success', 12)
        Skip = Result('skip', 11, skip=True)
        Error = Result('error', 11)

    assert CustomScanResult.get_score(CustomScanResult.Success, CustomScanResult.Error) == CustomScanResult.Error
