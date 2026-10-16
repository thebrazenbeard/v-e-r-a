from unvtrslr.bridge import BridgeLearner, Episode


def ep(signal, context, source=None):
    return Episode.build(signal, context, source=source)


def compositional_training():
    return [
        ep(["ka"], ["c:red", "s:circle"], "speaker-a"),
        ep(["ka"], ["c:red", "s:triangle"], "speaker-b"),
        ep(["ka"], ["c:red", "s:hexagon"], "speaker-c"),
        ep(["zu"], ["c:blue", "s:square"], "speaker-a"),
        ep(["zu"], ["c:green", "s:square"], "speaker-b"),
        ep(["zu"], ["c:yellow", "s:square"], "speaker-c"),
        ep(["ka", "zu"], ["c:red", "s:square"], "speaker-a"),
        ep(["mi"], ["c:blue", "s:circle"], "speaker-b"),
        ep(["mi"], ["c:green", "s:triangle"], "speaker-c"),
    ]


def test_cross_situational_learning_recovers_distinctions():
    learner = BridgeLearner().fit(compositional_training())
    assert learner.infer("ka").status == "OPERATIONAL_RELATION_SUPPORTED"
    assert learner.infer("ka").candidates[0].atom == "c:red"
    assert learner.infer("zu").status == "OPERATIONAL_RELATION_SUPPORTED"
    assert learner.infer("zu").candidates[0].atom == "s:square"


def test_composition_translates_multiple_learned_relations():
    learner = BridgeLearner().fit(compositional_training())
    result = learner.translate(["ka", "zu"])
    assert result.status == "OPERATIONAL_TRANSLATION_SUPPORTED"
    assert set(result.relations) == {"c:red", "s:square"}
    assert result.unresolved_tokens == ()


def test_renderer_is_separate_from_learned_operational_relation():
    learner = BridgeLearner().fit(compositional_training())
    result = learner.translate(
        ["ka", "zu"],
        renderer={"c:red": "red", "s:square": "square"},
    )
    assert set(result.relations) == {"red", "square"}


def test_confounded_relations_remain_ambiguous():
    data = [
        ep(["ka"], ["c:red", "s:square"]),
        ep(["ka"], ["c:red", "s:square"]),
        ep(["ka"], ["c:red", "s:square"]),
        ep(["zu"], ["c:blue", "s:circle"]),
        ep(["zu"], ["c:blue", "s:circle"]),
        ep(["zu"], ["c:blue", "s:circle"]),
    ]
    learner = BridgeLearner().fit(data)
    inference = learner.infer("ka")
    assert inference.status == "AMBIGUOUS"
    assert {inference.candidates[0].atom, inference.candidates[1].atom} == {"c:red", "s:square"}


def test_ambiguous_relation_requests_discriminating_probe():
    data = [
        ep(["ka"], ["c:red", "s:square"]),
        ep(["ka"], ["c:red", "s:square"]),
        ep(["zu"], ["c:blue", "s:circle"]),
        ep(["zu"], ["c:blue", "s:circle"]),
    ]
    learner = BridgeLearner().fit(data)
    probe = learner.suggest_probe("ka")
    assert probe.status == "CONTRAST_REQUESTED"
    assert probe.requested_contrast is not None
    left, right = probe.requested_contrast
    assert left != right


def test_unknown_token_fails_closed():
    learner = BridgeLearner().fit(compositional_training())
    result = learner.translate(["never-seen"])
    assert result.status == "UNRESOLVED"
    assert result.unresolved_tokens == ("never-seen",)
    assert result.token_inferences[0].status == "UNKNOWN_TOKEN"


def test_low_support_does_not_get_translation_credit():
    data = [
        ep(["rare"], ["x:1"]),
        ep(["other"], ["x:2"]),
        ep(["other"], ["x:3"]),
    ]
    learner = BridgeLearner(min_support=2).fit(data)
    assert learner.infer("rare").status == "INSUFFICIENT_EVIDENCE"


def test_negative_association_does_not_become_positive_meaning():
    data = [
        ep(["ka"], ["x:a"]),
        ep(["ka"], ["x:a"]),
        ep(["zu"], ["x:b"]),
        ep(["zu"], ["x:b"]),
    ]
    learner = BridgeLearner().fit(data)
    ranked = learner.hypotheses("ka")
    xa = next(h for h in ranked if h.atom == "x:a")
    xb = next(h for h in ranked if h.atom == "x:b")
    assert xa.effect > 0
    assert xb.effect < 0
