# -*- coding: utf-8 -*-
"""
Test the Input and associated Marginal classes in bayesvalidrox.
Tests are available for the following functions
Class Marginal contains no functions - no tests to write.
Class Input: 
    add_marginals

@author: Rebecca Kohlhaas
"""
import sys

from bayesvalidrox.surrogate_models.inputs import Input

sys.path.append("src/")


def test_addmarginals() -> None:
    """
    Tests function 'Input.add_marginals()'
    Ensure that marginals get appended
    """
    inp = Input()
    inp.add_marginals()
    assert len(inp.marginals) == 1


def test_addmarginals_param() -> None:
    """
    Add marginals in two ways
    """
    inp = Input()
    inp.add_marginals(
        name="name", dist_type="normal", parameters=[0, 1], input_data=[0, 0]
    )
    inp.add_marginals(
        name="name2", dist_type="normal", parameters=[0, 1], input_data=[0, 0]
    )
    assert len(inp.marginals) == 2
    assert inp.marginals[0].name == "name"
    assert inp.marginals[0].dist_type == "normal"
    assert inp.marginals[0].parameters == [0, 1]
    assert inp.marginals[0].input_data == [0, 0]

    assert inp.marginals[1].name == "name2"
    assert inp.marginals[1].dist_type == "normal"
    assert inp.marginals[1].parameters == [0, 1]
    assert inp.marginals[1].input_data == [0, 0]
