import pytest

import chainofresponsibility


@pytest.fixture
def accepted_application():
    return chainofresponsibility.Application(
        id="1",
        name="Mariusz",
        yearly_income=10000,
        employment_score=1,
        history_score=2,
        is_employed=True,
    )


@pytest.fixture
def rejected_application():
    return chainofresponsibility.Application(
        id="1",
        name="Mariusz",
        yearly_income=1000,
        employment_score=1,
        history_score=2,
        is_employed=True,
    )


@pytest.fixture
def chain_config():
    return chainofresponsibility.ChainConfig(
        [
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.EmploymentHandler, None
            ),
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.IncomeHandler,
                chainofresponsibility.are_offers_available,
            ),
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.HistoryHandler,
                chainofresponsibility.are_offers_available,
            ),
        ]
    )


@pytest.fixture
def selective_chain_config():
    return chainofresponsibility.ChainConfig(
        [
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.EmploymentHandler,
                chainofresponsibility.are_offers_available,
            ),
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.IncomeHandler,
                chainofresponsibility.are_offers_available,
            ),
            chainofresponsibility.HandlerConfig(
                chainofresponsibility.HistoryHandler, None
            ),
        ]
    )


def test_naive_chain_handling(accepted_application, mocker, check):
    handler_1 = chainofresponsibility.EmploymentHandler()
    handler_2 = chainofresponsibility.IncomeHandler()
    handler_3 = chainofresponsibility.HistoryHandler()
    handler_1.next_handler = handler_2
    handler_2.next_handler = handler_3

    handler_1_spy = mocker.spy(handler_1, "_process_application")
    handler_2_spy = mocker.spy(handler_2, "_process_application")
    handler_3_spy = mocker.spy(handler_3, "_process_application")

    handler_1.handle_application(accepted_application)

    with check:
        handler_1_spy.assert_called_once()
    with check:
        handler_2_spy.assert_called_once()
    with check:
        handler_3_spy.assert_called_once()


def test_basic_chainconfig_handling(accepted_application, chain_config, mocker, check):
    chain = chainofresponsibility.create_chain_of_responsibility(chain_config)
    handler_1_spy = mocker.spy(
        chainofresponsibility.EmploymentHandler, "_process_application"
    )
    handler_2_spy = mocker.spy(
        chainofresponsibility.IncomeHandler, "_process_application"
    )
    handler_3_spy = mocker.spy(
        chainofresponsibility.HistoryHandler, "_process_application"
    )

    chain.handle_application(accepted_application)

    with check:
        handler_1_spy.assert_called_once()
    with check:
        handler_2_spy.assert_called_once()
    with check:
        handler_3_spy.assert_called_once()


def test_rejected_application_handling(
    rejected_application, chain_config, mocker, check
):
    chain = chainofresponsibility.create_chain_of_responsibility(chain_config)
    handler_1_spy = mocker.spy(
        chainofresponsibility.EmploymentHandler, "_process_application"
    )
    handler_2_spy = mocker.spy(
        chainofresponsibility.IncomeHandler, "_process_application"
    )
    handler_3_spy = mocker.spy(
        chainofresponsibility.HistoryHandler, "_process_application"
    )

    application = chain.handle_application(rejected_application)

    with check:
        handler_1_spy.assert_called_once()
    with check:
        handler_2_spy.assert_called_once()
    with check:
        handler_3_spy.assert_not_called()

    with check:
        assert not application.offers


def test_selective_chain_config_function_handling(
    accepted_application, selective_chain_config, mocker, check
):
    chain = chainofresponsibility.create_chain_of_responsibility(selective_chain_config)
    handler_1_spy = mocker.spy(
        chainofresponsibility.EmploymentHandler, "_process_application"
    )
    handler_2_spy = mocker.spy(
        chainofresponsibility.IncomeHandler, "_process_application"
    )
    handler_3_spy = mocker.spy(
        chainofresponsibility.HistoryHandler, "_process_application"
    )

    chain.handle_application(accepted_application)

    with check:
        handler_1_spy.assert_not_called()
    with check:
        handler_2_spy.assert_not_called()
    with check:
        handler_3_spy.assert_called_once()
