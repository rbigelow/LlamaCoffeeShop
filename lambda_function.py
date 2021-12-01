# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
#This example demoinstrates, reading a JSON file, chaining Alexa intents using Python, and autodelegation. 
# The OrderDrinkIntent and OrderFoodIntent Deligate to the Alexa interaction model to manage the slot filling. 
# These intents are then chained to the CheckoutIntent which then manages a couple of other slots. 

import requests # Needed to get data from external API.
import json #need to decode JSON
import logging
import ask_sdk_core.utils as ask_utils
import random

from random import randint
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_intent_name, get_dialog_state, get_slot_value
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, DialogState 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = 'Welcome to the Llama Coffee Shop. We have beverages and snacks. What would you like?'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

     
class OrderDrinkIntentHandler(AbstractRequestHandler):
    """Handler for OrderDrink Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("OrderDrinkIntent")(handler_input) 
        
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        drink = ask_utils.request_util.get_slot(handler_input, "drink")
        size = ask_utils.request_util.get_slot(handler_input, "size")
        modifierQty = ask_utils.request_util.get_slot(handler_input, "modifierQty")
        modifier = ask_utils.request_util.get_slot(handler_input, "modifier")

        #Save these slots into a single session attribute called order
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["order"] = str(size.value)+ " " + str(drink.value) +" with "+ str(modifierQty.value)  + " "+ str(modifier.value) 
        
        #To not say anything just directly call the Checkout Intent.
        return CheckoutIntentHandler.handle(self, handler_input)
  

class OrderFoodIntentHandler(AbstractRequestHandler):
    """Handler for Order Food Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("OrderFoodIntent")(handler_input) 
        
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        food = ask_utils.request_util.get_slot(handler_input, "food")
        
        #Save these slots into a session attribute called order
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["order"] = str(food.value)
         #To not say anything just directly call the Checkout Intent.
        return CheckoutIntentHandler.handle(self, handler_input)
        
class CheckoutIntentHandler(AbstractRequestHandler):
    """Handler for checkout Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CheckoutIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        #Get the slots and session attributes
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes
        
        #Check for existing order.
        if "order" in session_attr:
            order = session_attr["order"]
            #speak_output = order #Debugging.
            #This will prompt the user into triggering this intent. 
            speak_output = 'Is your order for here, to go or delivery?'
            if ask_utils.request_util.get_slot(handler_input, "stayGo") is not None:
                stayGo = ask_utils.request_util.get_slot(handler_input, "stayGo")
                paymentMethod = ask_utils.request_util.get_slot(handler_input, "paymentMethod")
                speak_output = 'OK, your ' + str(order) +' for ' + str(stayGo.value) + ' comes to $'  + str(round(random.uniform(1,5),2)) + '  paid by ' + str(paymentMethod.value)              
        else:
            # the user invoked this as the first intent and  don't have a order so we need to prompt them. 
            speak_output = 'Would you like to order a beverage or a snack?'
                    
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class RandomFactIntentHandler(AbstractRequestHandler):
    """Handler for Random Llama Facts Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RandomFactIntent")(handler_input)

    def handle(self, handler_input):
        with open('./llamaQuotes.json', 'r') as j:
            llamaQuotes = json.loads(j.read())
        # type: (HandlerInput) -> Response
        speak_output = "Here is a random llama quote: " + llamaQuotes[randint(0, len(llamaQuotes))]
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Here at the Llama Coffee Shop you can say Beverage or Snack to place an order. Or you can ask to to hear a random fact about Llamas by saying random fact."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure.  How can I help you?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(RandomFactIntentHandler())
sb.add_request_handler(OrderDrinkIntentHandler())
sb.add_request_handler(CheckoutIntentHandler())
sb.add_request_handler(OrderFoodIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) 
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()