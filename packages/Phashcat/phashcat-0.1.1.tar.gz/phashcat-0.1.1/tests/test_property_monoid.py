from hypothesis import given, strategies as st
from Phashcat import hashcat, HashcatBuilder, flags

# Small set of operations to compose randomly
def op_hash_type(n):    return lambda b: b.hash_type(n)
def op_attack_mode(n):  return lambda b: b.attack_mode(n)
def op_outfile(s):      return lambda b: b.outfile(s)
def op_status(v):       return lambda b: b.status(v)
def op_arg(s):          return lambda b: b.arg(s)

nums = st.integers(min_value=0, max_value=2000)
paths = st.text(min_size=1, max_size=12).map(lambda s: (s.replace(" ", "_") + ".txt"))
hashes = st.text(min_size=1, max_size=12).map(lambda s: (s.replace(" ", "_") + ".hash"))
bools = st.booleans()

def ops_strategy():
    return st.lists(
        st.one_of(
            nums.map(op_hash_type),
            st.sampled_from([0,1,3,6,7,9]).map(op_attack_mode),
            paths.map(op_outfile),
            bools.map(op_status),
            hashes.map(op_arg),
        ),
        min_size=0, max_size=8
    )

def apply_ops(b, ops):
    for f in ops:
        b = f(b)
    return b

@given(ops_a=ops_strategy(), ops_b=ops_strategy(), ops_c=ops_strategy())
def test_associativity_property(ops_a, ops_b, ops_c):
    e = HashcatBuilder.empty()
    a = apply_ops(e, ops_a)
    b = apply_ops(e, ops_b)
    c = apply_ops(e, ops_c)

    left  = a.mappend(b).mappend(c).cmdline()
    right = a.mappend(b.mappend(c)).cmdline()
    assert left == right

@given(ops_a=ops_strategy())
def test_identity_property(ops_a):
    e = HashcatBuilder.empty()
    a = apply_ops(e, ops_a)
    assert a.mappend(e).cmdline() == a.cmdline()
    assert e.mappend(a).cmdline() == a.cmdline()
