import pytest

from sam._planet import Planet

reprs_to_test = [
	({'K':1.,'P':10,'e':0.12}, 'Planet(P=10.00days, K=1.00m/s, e=0.12)'),
	({'K':2.,'P':10,'e':0.17}, 'Planet(P=10.00days, K=2.00m/s, e=0.17)'),
	({'K':100.,'P':100.,'e':0.}, 'Planet(P=100.00days, K=100.00m/s, e=0.00)'),
	({'K':[1.,2.],'P':10,'e':0.12}, 'Planet(P=10.00days, K=[ 1.  2.]m/s, e=0.12)'),
	({'K':[1.,2.,3.,4.,5.],'P':10,'e':0.12}, 'Planet(P=10.00days, K=[ 1.0.. 5.0]m/s, e=0.12)'),
	({'K':range(5),'P':range(10),'e':0.12}, 'Planet(P=[ 0.0.. 9.0]days, K=[ 0.0.. 4.0]m/s, e=0.12)')
]

@pytest.mark.parametrize("kwargs,representation", reprs_to_test)
def test_repr(kwargs, representation):
	assert Planet(**kwargs).__repr__() == representation


def test_set_grid():
	assert Planet(P=[1.,2.]).grid == True
	assert Planet(K=[1.,2.]).grid == True
	assert Planet(e=[0.1,0.9]).grid == True