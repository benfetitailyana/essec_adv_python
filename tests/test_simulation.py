from merton import JumpParameters, MertonJumpModel


def test_generator_length() -> None:
    model = MertonJumpModel(
        spot=100,
        rate=0.05,
        volatility=0.2,
        jump_params=JumpParameters(intensity=0.1, mean_jump=-0.2, jump_vol=0.1),
        maturity=1.0,
        steps=4,
    )
    paths = list(model.payoff_stream(paths=5, strike=100))
    assert len(paths) == 5
