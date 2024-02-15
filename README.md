This package contains the example implementation of Chain Of Responsibility
design pattern that could be potentially used as an implementation of mechanism of selective
processing of given request. 

Check tests for usage examples.

# Basic information

Package `chainofresponsibility` implements the `InterfaceHandler` class which implements the
following public interface:
* `next_handler` attribute - is used to set and execute the next handler in the chain
* `handle_application` method - this it the chain's entry point - it is executed when user wants to 
  start the Chain of Responsibility execution

Note that decision 

The idea is simple - user creates the Handlers 


# Implementing custom handlers

Taking into account that `InterfaceHandler` is an abstract class - user needs to define its own
concrete implementations by inheriting from it and implementing the private method `_process_application`.

This method is responsible for processing the whole application before passing it by the next handler.

Example of implementation:

```python
class EmploymentHandler(InterfaceHandler):
    def _process_application(self, application: Application) -> Application:
        if application.is_employed and application.employment_score > 0:
            # in case of fulfilling the criteria we add the offers, if not we remove them all
            application.offers.append(f"{self.__class__.__name__} offer")
        else:
            application.offers.clear()
        print(f"{self.__class__.__name__} processed application")
        return application
```

# The purpose of handling_criteria_function

`handling_criteria_function` has been added as an optional attribute when instantiating 
handlers to provide ability to configure the execution flow of the handlers in the 
chain of responsibility. Function is used to determine if a given handler should process the
application or not. User can configure different behaviour using this function like in the example below.
Note that by default the behaviour is to always run the application processing. 

```python
def are_offers_available(application: Application) -> bool:
    return bool(application.offers)

def is_special_user(application: Application) -> bool:
    return application.name == "John"

handler_1 = EmploymentHandler()
handler_2 = EmploymentHandler(handling_criteria_function=is_special_user)
handler_3 = EmploymentHandler(handling_criteria_function=are_offers_available)
```

In the example above the `_process_application` function is executed always for `handler_1` (default behaviour).
For `handler_2` it will be executed if the passed application attribute `name` will be equal to "John".
For `handler_3` it will be executed if the passed application attribute `offers` will not be empty. 


# Instantiating the chain of responsibility

Client (the user) needs to setup the chain of the handlers in the desired order. 
There are two ways of doing it.

## The manual way

```python
import chainofresponsibility

handler_1 = chainofresponsibility.EmploymentHandler()
handler_2 = chainofresponsibility.IncomeHandler()
handler_3 = chainofresponsibility.HistoryHandler()
handler_1.next_handler = handler_2
handler_2.next_handler = handler_3

application = handler_1.handle_application(application)

# this will result in the following chain of execution:
# EmploymentHandler.handle_application -> IncomeHandler.handle_application -> HistoryHandler.handle_application
```


## Using ChainFactory class

```python
import chainofresponsibility

chain_config = chainofresponsibility.ChainConfig(
    [
        chainofresponsibility.HandlerConfig((chainofresponsibility.EmploymentHandler, None)),
        chainofresponsibility.HandlerConfig((chainofresponsibility.IncomeHandler, chainofresponsibility.are_offers_available)),
        chainofresponsibility.HandlerConfig((chainofresponsibility.HistoryHandler, chainofresponsibility.are_offers_available)),
    ]
)
chain = chainofresponsibility.create_chain_of_responsibility(chain_config)

chain.handle_application(application)
# this will result in the following chain of execution:
# EmploymentHandler.handle_application -> IncomeHandler.handle_application -> HistoryHandler.handle_application
```

Please note that due to the usage of `handling_criteria_function` 2nd and 3rd handler will only process
the application if any offers are available in the application during the time of processing. 

