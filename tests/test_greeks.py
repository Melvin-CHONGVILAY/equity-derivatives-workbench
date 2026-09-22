import pytest
from greeks.greeks import delta_call_num,delta_call

def test_delta_call_num():
    S = 100
    K = 100
    T = 1
    r = 0.02
    sigma = 0.20
    q = 0
    h=0.01
    delta_ana = delta_call(S, K, T, r, sigma, q)
    delta_num = delta_call_num(S, K, T, r, sigma, q, h)
    assert delta_num == pytest.approx(delta_ana, abs=1e-3)