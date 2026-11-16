import torch
import torch.nn.functional as F

from xlpersona.directions import (choose_layer, diff_in_means, jaccard, jaccard_chance, neuron_effect,
                                  random_units, split_half_sep, top_neurons, unit, window)


def test_diff_in_means_recovers_planted_direction():
    g = torch.Generator().manual_seed(0)
    r = unit(torch.randn(32, generator=g))
    plain = torch.randn(200, 6, 32, generator=g)
    persona = torch.randn(200, 6, 32, generator=g) + 3 * r
    assert F.cosine_similarity(diff_in_means(persona, plain)[2], r, dim=0) > 0.9


def test_split_half_sep_peaks_on_planted_layer():
    g = torch.Generator().manual_seed(0)
    r = unit(torch.randn(32, generator=g))
    plain = torch.randn(200, 6, 32, generator=g)
    persona = torch.randn(200, 6, 32, generator=g)
    persona[:, 4] += 2 * r
    sep = split_half_sep(persona, plain[:50])
    assert sep.shape == (6,) and int(sep.argmax()) == 4


def test_choose_layer_search_range():
    sep = torch.zeros(36)
    sep[0] = 99
    sep[10] = 5
    assert choose_layer(sep) == 10


def test_window_clipped():
    assert window(7, 36) == list(range(3, 12)) and window(2, 36) == list(range(0, 7))


def test_random_units_are_unit_and_seeded():
    a, b = random_units(4, 16, seed=0), random_units(4, 16, seed=0)
    assert torch.equal(a, b) and torch.allclose(a.norm(dim=-1), torch.ones(4))


def test_neuron_effect_and_top_neurons():
    g = torch.Generator().manual_seed(0)
    plain = torch.randn(100, 3, 20, generator=g)
    persona = torch.randn(100, 3, 20, generator=g)
    persona[:, 1, 7] += 5
    assert (1, 7) in top_neurons(neuron_effect(persona, plain), k=1)


def test_jaccard_and_chance():
    assert jaccard({(0, 1), (0, 2)}, {(0, 2), (0, 3)}) == 1 / 3
    assert abs(jaccard_chance(500, 396288) - 500 / (2 * 396288 - 500)) < 1e-12
