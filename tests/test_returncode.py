from enhancements.returncode import BaseReturnCode, MissingInnerResultClass, WrongResultSubclass, WrongResultValue
import pytest


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

    with pytest.raises(ValueError):
        CustomScanResult.convert('invalid')


def test_missing_inner_result_class():
    with pytest.raises(MissingInnerResultClass):
        class CustomScanResultMissingResultClass(BaseReturnCode):
            pass


def test_wrong_subclass():
    with pytest.raises(WrongResultSubclass):
        class CustomScanWrongResultClass(BaseReturnCode):
            class Result():
                pass


def test_wrong_result_subclass():
    with pytest.raises(WrongResultValue):
        class CustomScanWrongResultClass(BaseReturnCode):
            class Result(BaseReturnCode.Result):
                pass
            Success = BaseReturnCode.Result('success', 10)
