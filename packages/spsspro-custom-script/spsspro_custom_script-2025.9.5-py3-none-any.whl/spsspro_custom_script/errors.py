class AlgorithmError(RuntimeError):
    """
    算法异常抛出
    如果知道异常来源比如被除数为 0 的话: raise AlgorithmError("A 列数据不能存在 0 值") from ZeroDivisionError
    如果不知道异常来源的话直接: raise AlgorithmError("A 列数据错误")
    """
    pass
