# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pycutest
import unittest

# All problems used here: ARWHEAD (unconstrained) / ARWHDNE (constrained)
# Test sparsity by comparing to dense versions

def array_compare(x, y, thresh=1e-8):
    return np.max(np.abs(x - y)) < thresh


class TestSparseUnconstrained(unittest.TestCase):
    def runTest(self):
        pycutest.clear_cache('ARWHEAD', sifParams={'N': 100})
        p = pycutest.import_problem('ARWHEAD', sifParams={'N':100})
        # Some test vectors
        xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2*np.arange(p.n), np.sin(np.arange(p.n))-np.cos(np.arange(p.n))]

        for x in xs:
            places = 8  # accuracy
            print("Trying x = [...]")
            ftrue, gdense = p.obj(x, gradient=True)
            Hdense = p.hess(x)
            # scons
            c = p.scons(x)
            self.assertIsNone(c, msg="scons c is not None")
            # slagjac
            g, J = p.slagjac(x)
            print(g.shape)
            self.assertTrue(array_compare(gdense, g.toarray(), thresh=10**(-places)), msg="slagjac g wrong")
            self.assertIsNone(J, msg="slagjac J is not None")
            # sphess
            H = p.sphess(x)
            self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="sphess H wrong")
            # isphess
            H = p.isphess(x)
            self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="isphess H wrong")
            # gradsphess
            g, H = p.gradsphess(x)
            self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="gradsphess g wrong")
            self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="gradsphess H wrong")


class TestSparseConstrained(unittest.TestCase):
    def runTest(self):
        pycutest.clear_cache('ARWHDNE', sifParams={'N':100})
        p = pycutest.import_problem('ARWHDNE', sifParams={'N':100})
        # Some test vectors
        xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2 * np.arange(p.n),
              np.sin(np.arange(p.n)) - np.cos(np.arange(p.n))]

        vs = [p.v0, np.ones((p.m,)), -np.ones((p.m)), 0.2 * np.arange(p.m),
              np.sin(np.arange(p.m)) - np.cos(np.arange(p.m))]

        for x in xs:
            places = 8  # accuracy
            print("Trying x = [...]")
            cdense, Jdense = p.cons(x, gradient=True)
            # scons
            c = p.scons(x)
            self.assertTrue(array_compare(cdense, c, thresh=10**(-places)), msg="scons c is wrong 1")
            for i in range(p.n):
                ci = p.scons(x, index=i)
                self.assertAlmostEqual(ci, cdense[i], places=places, msg="scons ci is wrong 2 [i = %g]" % i)
            c, J = p.scons(x, gradient=True)
            self.assertTrue(array_compare(cdense, c, thresh=10 ** (-places)), msg="scons c is wrong 3")
            self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="scons J is wrong 3")
            for i in range(p.n):
                ci, Ji = p.scons(x, index=i, gradient=True)
                self.assertAlmostEqual(ci, cdense[i], places=places, msg="scons ci is wrong 4 [i = %g]" % i)
                self.assertTrue(array_compare(Jdense[i,:], Ji.toarray(), thresh=10 ** (-places)), msg="scons J is wrong 4 [i = %g]" % i)

            # slagjac
            g, J = p.slagjac(x)
            gdense, Jdense = p.slagjac(x)
            self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="slagjac g wrong 1")
            self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="slagjac J is wrong 1")
            for v in vs:
                g, J = p.slagjac(x, v=v)
                gdense, Jdense = p.lagjac(x, v=v)
                self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="slagjac g wrong 2")
                self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="slagjac J is wrong 2")
            # sphess
            for v in vs:
                H = p.sphess(x, v=v)
                Hdense = p.hess(x, v=v)
                self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="sphess H wrong")
            # isphess
            H = p.isphess(x)
            Hdense = p.ihess(x)
            self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="isphess H wrong 0")
            for i in range(p.m):
                H = p.isphess(x, cons_index=i)
                Hdense = p.ihess(x, cons_index=i)
                self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="isphess H wrong [i = %g]" % i)
            # gradsphess
            for v in vs:
                g, J, H = p.gradsphess(x, v=v)
                gdense, Jdense, Hdense = p.gradhess(x, v=v)
                self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="gradsphess g wrong 1")
                self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="gradsphess J wrong 1")
                self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="gradsphess H wrong 1")
                g, J, H = p.gradsphess(x, v=v, gradient_of_lagrangian=False)
                gdense, Jdense, Hdense = p.gradhess(x, v=v, gradient_of_lagrangian=False)
                self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="gradsphess g wrong 2")
                self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="gradsphess J wrong 2")
                self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="gradsphess H wrong 2")
