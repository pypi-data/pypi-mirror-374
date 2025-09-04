from js2py import EvalJs

def evaluateJSWithContext(x: str, context: dict):
    '''
    Evaluate a javascript expression with the provided context.
    '''
    ctx = EvalJs(context)
    return ctx.eval(x)