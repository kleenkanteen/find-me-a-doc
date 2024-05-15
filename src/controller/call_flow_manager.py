from flask import request, Blueprint
<<<<<<< HEAD
from twilio.twiml.voice_response import VoiceResponse, Gather, Redirect
=======
from twilio.twiml.voice_response import VoiceResponse, Gather
>>>>>>> master

from util.logger import logger
from util.ai.nav_menu_navigator import find_next_nav_menu_key
import services.calls.active_call_methods as call_methods
import config.active_call_values as call_values
from util.ai.pregenerated_transcript_detector import detect_pregenerated_transcript

import os
from dotenv import load_dotenv

load_dotenv(override=True)

MODE = os.environ.get("MODE")

import os

call_flow_manager = Blueprint("call_flow_manager", __name__, url_prefix="/call")

public_url = os.environ.get("NGROK_URL")

<<<<<<< HEAD
@call_flow_manager.route("/machine_detection/<int:clinic_id>", methods=["GET", "POST"])
def handle_machine_detection(clinic_id: int):

        

    logger.info(f"\n--now in machine_detection enpoint--\n")

    logger.info(f"machine detection endpoint form:  {request.form.to_dict()}")
    answeredBy = request.form.get("AnsweredBy", "")
    logger.info(f"call was answered by: {answeredBy}")

    response = VoiceResponse()

    # answeredBy can be: human, machine_start, fax or unknown.
    if MODE == "PROD":
        if "human" in answeredBy:
            response.redirect(f"{public_url}/call/intro_message/{clinic_id}", method="POST")
            return str(response)

        elif "fax" in answeredBy:
            logger.info(f"call was answered by fax. finishing the call now...")
            hangup = VoiceResponse().hangup()
            return str(hangup)

    speech_result = request.form.get("SpeechResult", "")
    logger.info(f"speech result: {speech_result}")

    if speech_result != "":

        if "hello" in speech_result.lower():
            redirect = VoiceResponse()
            redirect.redirect(
                f"{public_url}/call/intro_message/{clinic_id}", method="POST"
            )
            return str(redirect)

        try:
            #find what digit needs to be pressed next (if any)
            next_nav_menu_data = find_next_nav_menu_key(speech_result)
            digit = next_nav_menu_data["digit"]
            human_reached = next_nav_menu_data["human_reached"]
            logger.info("navigation menu data: ", next_nav_menu_data, '\n')
        except TypeError as e:
            logger.error(f"chatgpt returned an invalid response. full error log: {e}")

        if human_reached == True and isinstance(digit, int):

            response.play("", digits=str(digit))
            logger.info(f"typing digit {digit} and then redirecting to on hold...")
            response.redirect(
                f"{public_url}/call/handle_on_hold/{clinic_id}", method="POST"
            )
            return str(response)

        if human_reached == True and digit is None:

            logger.info(
                "human was reached and no digits need to be played. Redirecting to on hold..."
            )

            response.redirect(
                f"{public_url}/call/handle_on_hold/{clinic_id}", method="POST"
            )
            return str(response)

        else:
            logger.info(f"played digit: {digit}")
            response.play("", digits=str(digit))

    logger.info("\nlistening for voice input in machine detection...\n")
    gather = Gather(
        input="speech",
        speech_model="phone_call",
        enhanced="true",
        action=f"{public_url}/call/machine_detection/{clinic_id}",
        speech_timeout=1,
        hints="$OPERAND, press $OPERAND",
    )
=======

@call_flow_manager.route("/intro_message/<int:clinic_id>", methods=["GET", "POST"])
def intro_message(clinic_id: int):

    prompt_retry_count = int(request.args.get("prompt_retry_count", 0))
    # Invalid_value_count is always 1 behind when attaching it to a Gather action, so it's set to 1 instead of 0
    invalid_input_count = int(request.args.get("invalid_value_count", 1))
    timeouts_count = int(request.args.get("timeouts_count", 0))

    logger.info(f"intro message retrys count: {prompt_retry_count}")
    logger.info(f"intro message invalid key count: {invalid_input_count}")
    logger.info(f"intro message timeouts count: {timeouts_count}")

    max_count = max(prompt_retry_count, timeouts_count, invalid_input_count)
    if max_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

    print("Intro Message")

    action_url = f"{public_url}/call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&invalid_input_count={invalid_input_count}"

    gather = Gather(action=action_url, timeout=call_values.timeout, num_digits=1)

    response = VoiceResponse()

    if prompt_retry_count >= call_values.ENDPOINT_HIT_LIMIT:
        gather.say(
            "Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Press 1 for yes or 2 for no"
        )

    else:
        gather.say(
            "Hello, I am a robocaller created to gather data on family doctor's accepting patients for public use. I only have 2 questions. The first is, are any family doctors accepting patients? Press 1 for yes, 2 for no, or 3 to repeat this message"
        )
>>>>>>> master
    response.append(gather)

    # Redirect user in a loop if no option is selected
    new_timeouts_count = timeouts_count + 1
    response.redirect(
        f"{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={prompt_retry_count}&timeouts_count={new_timeouts_count}&invalid_input_count={invalid_input_count}"
    )

    return str(response)


<<<<<<< HEAD
# consider adding gpt to identify if human or robot:
# sometimes we may have a bot saying "the expected time to speak to someone is of 3 minutes"
# which would trigger /intro_message.
@call_flow_manager.route("/handle_on_hold/<int:clinic_id>", methods=["GET", "POST"])
def handle_on_hold(clinic_id: int):

    logger.info(f"\n--now in handle_on_hold enpoint--\n")
    logger.info(f"handle on hold form data: {request.form.to_dict()}")

    speech_result = request.form.get("SpeechResult", "")

    if speech_result != "":

        logger.info(f"\speech result: {speech_result}\n")

        if "hello" in speech_result:

            redirect = VoiceResponse()
            redirect.redirect(
                f"{public_url}/call/intro_message/{clinic_id}", method="POST"
            )
            return str(redirect)

        is_robot = detect_pregenerated_transcript(speech_result)
        logger.info(f"is robot? : {is_robot}\n")

        if is_robot == False:

            # Consider adding another gpt task that identifies if a digit should be returned
            #   if yes, then redirect to machine detection with the transcript attached,
            #   otherwise just ignore it and keep waiting

            redirect_response = VoiceResponse()
            redirect_response.redirect(f"{public_url}/call/intro_message/{clinic_id}")
            return str(redirect_response)

    repetition_count = int(request.args.get("repetition_count", 0))
    logger.info(f"on hold repetition_count: {repetition_count}")

    if repetition_count > 15:
        hangup = VoiceResponse().hangup()
        return str(hangup)

    response = VoiceResponse()

    response.say("you are in handle on hold now. you may speak now")

    # If repetition count is not greater than 15, listen for voice input again
    #   and send it to this same endpoint, it will check if the voice input belongs
    #   to a human or a robot. Don't increase the repetition count if there's voice input.
    gather = Gather(
        input="speech",
        speech_model="phone_call",
        enhanced="true",
        action=f"{public_url}/call/handle_on_hold/{clinic_id}?repetition_count={repetition_count}",
        speechTimeout=1,
        hints="$OPERAND, press $OPERAND",
    )
    response.append(gather)

    new_repetition_count = repetition_count + 1
    response.redirect(
        f"{public_url}/call/handle_on_hold/{clinic_id}?repetition_count={new_repetition_count}",
        method="POST",
    )
    return str(response)

@call_flow_manager.route("/intro_message/<int:clinic_id>", methods=["GET", "POST"])
def intro_message(clinic_id: int):

    logger.info(f"\nintro message request form: {request.form.to_dict()}")
    logger.info(f"intro message request args: {request.args.to_dict()}")

    prompt_retry_count = int(request.args.get("prompt_retry_count", 0))
    # Invalid_value_count is always 1 behind when attaching it to a Gather action, so it's set to 1 instead of 0
    invalid_input_count = int(request.args.get("invalid_value_count", 1))
    timeouts_count = int(request.args.get("timeouts_count", 0))

    logger.info(f"\nintro message retrys count: {prompt_retry_count}")
    logger.info(f"intro message invalid key count: {invalid_input_count}")
    logger.info(f"intro message timeouts count: {timeouts_count}")

    max_count = max(prompt_retry_count, timeouts_count, invalid_input_count)
    if max_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

    response = VoiceResponse()

    if prompt_retry_count >= call_values.ENDPOINT_HIT_LIMIT:

        response.play("https://findadoc-7179.twil.io/intro_message_2_options.mp3")

    else:
        response.play("https://findadoc-7179.twil.io/intro_message_3_options.mp3")

    action_url = f"{public_url}/call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&invalid_input_count={invalid_input_count}"

    gather = Gather(action=action_url, timeout=call_values.timeout, num_digits=1)

    response.append(gather)

    # Redirect user in a loop if no option is selected
    new_timeouts_count = timeouts_count + 1
    response.redirect(
        f"{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={prompt_retry_count}&timeouts_count={new_timeouts_count}&invalid_input_count={invalid_input_count}",
        method="GET",
    )

    return str(response)


=======
>>>>>>> master
@call_flow_manager.route(
    "/handle_intro_message_response/<int:clinic_id>", methods=["POST", "GET"]
)
def handle_intro_message_response(clinic_id: int):

    invalid_input_count = int(request.args.get("invalid_value_count", 1))
    prompt_retry_count = int(request.args.get("prompt_retry_count", 0))

    response = VoiceResponse()

    logger.info(f"invalid key count on intro message: {invalid_input_count}")
    logger.info(f"prompt retrys count on intro message: {prompt_retry_count}")

    if "Digits" in request.values:
        choice = request.values["Digits"]
        if choice == "1":

<<<<<<< HEAD
            logger.info(
                "\nUser chose to answer both questions...continuing to the next question now"
            )

=======
>>>>>>> master
            redirect_response = VoiceResponse()
            redirect_response.redirect(
                f"{public_url}/call/ask_male_doctors_number/{clinic_id}", method="GET"
            )
            return str(redirect_response)

        if choice == "2":
<<<<<<< HEAD
            logger.info("\nUser chose not to answer questions...ending call now")
=======
>>>>>>> master
            return call_methods.outro_message()

        if choice == "3":
            new_prompt_retry_count = prompt_retry_count + 1
            url = f"{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={new_prompt_retry_count}&invalid_input_count={invalid_input_count}"
            response.redirect(url, method="POST")
            return str(response)

        else:
            new_invalid_input_count = invalid_input_count + 1

            if prompt_retry_count >= 3:
<<<<<<< HEAD
                message_url = (
                    "https://findadoc-7179.twil.io/intro_error_input_2_options.mp3"
                )
            else:
                message_url = (
                    "https://findadoc-7179.twil.io/intro_error_input_3_options.mp3"
                )

            return call_methods.handle_unrecognizable_response(
                f"call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&invalid_input_count={new_invalid_input_count}",
                message_url,
=======
                message = "You can only enter 1 for yes, or 2 for no"
            else:
                message = "You can only enter 1 for yes, 2 for no, or 3 to listen to the introduction again"

            return call_methods.handle_unrecognizable_response(
                f"call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&invalid_input_count={new_invalid_input_count}",
                message,
>>>>>>> master
                num_digits=1,
            )


@call_flow_manager.get("/ask_male_doctors_number/<int:clinic_id>")
def ask_male_doctors_number(clinic_id: int):

    timeouts_count = int(request.args.get("timeouts_count", 0))

    logger.info(f"timeouts_count when asking male doctors number: {timeouts_count}")

    if timeouts_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

<<<<<<< HEAD
    response = VoiceResponse()

=======
>>>>>>> master
    gather = Gather(
        action=f"{public_url}/call/handle_number_male_doctors_response/{clinic_id}",
        timeout=call_values.timeout,
        num_digits=2,
    )
<<<<<<< HEAD

    if timeouts_count == 0:
        response.play("https://findadoc-7179.twil.io/male_doctors_question.mp3")
    else:
        response.play(
            "https://findadoc-7179.twil.io/no_intro_male_doctors_question.mp3"
        )

=======
    if timeouts_count == 0:
        gather.say(
            f"I see. How many of the available doctors are male? Please type the number on your keypad."
        )
    else:
        gather.say(
            f"How many of the available doctors are male? Please type the number on your keypad."
        )

    response = VoiceResponse()
>>>>>>> master
    response.append(gather)

    new_timeouts_count = timeouts_count + 1
    response.redirect(
        f"{public_url}/call/ask_male_doctors_number/{clinic_id}?timeouts_count={new_timeouts_count}",
        method="GET",
    )
    return str(response)


@call_flow_manager.route(
    "/handle_number_male_doctors_response/<int:clinic_id>", methods=["POST", "GET"]
)
def handle_number_male_doctors_response(clinic_id: int):

    invalid_input_count = int(request.args.get("invalid_input_count", 1))

    logger.info(
        f"invalid_input_count when asking male doctors number: {invalid_input_count}"
    )

    if invalid_input_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

    if "Digits" in request.values:

        response = VoiceResponse()

        try:
            call_values.male_docs_number = int(request.values["Digits"])
            logger.info(f"male doctors: {call_values.male_docs_number}")

            response.redirect(
                f"{public_url}/call/ask_female_doctors_number/{clinic_id}", method="GET"
            )
            return str(response)

        except (ValueError, TypeError) as e:
            new_invalid_input_count = invalid_input_count + 1
            logger.error(f"type error exception thrown. error message: {e}")
<<<<<<< HEAD
            message_url = "https://findadoc-7179.twil.io/wrong_input.mp3"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_number_male_doctors_response/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message_url,
=======
            message = "Please try again, enter numeric values only"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_number_male_doctors_response/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message,
>>>>>>> master
                num_digits=2,
            )

    else:
<<<<<<< HEAD
        message_url = "https://findadoc-7179.twil.io/ask_again_to_type_input.mp3"
=======
        message = (
            "I'm sorry, I didn't get that. Could you type the number on your keypad?"
        )
>>>>>>> master
        logger.critical("Attribute 'Digits' doesn't exist in request values")

        new_invalid_input_count = invalid_input_count + 1
        return call_methods.handle_unrecognizable_response(
            f"/call/handle_intro_response/{clinic_id}?invalid_input_count={new_invalid_input_count}",
<<<<<<< HEAD
            message_url,
=======
            message,
>>>>>>> master
            num_digits=2,
        )


@call_flow_manager.get("ask_female_doctors_number/<int:clinic_id>")
def ask_female_doctors_number(clinic_id: int):

    timeouts_count = int(request.args.get("timeouts_count", 0))

    logger.info(
        f"timeouts_count when asking for female doctors number: {timeouts_count}"
    )

    if timeouts_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

<<<<<<< HEAD
    response = VoiceResponse()

=======
>>>>>>> master
    gather = Gather(
        action=f"{public_url}/call/handle_female_doctors_number/{clinic_id}",
        timeout=call_values.timeout,
        num_digits=2,
    )

    if timeouts_count == 0:
<<<<<<< HEAD
        response.play("https://findadoc-7179.twil.io/female_doctors_question.mp3")
    else:
        response.play(
            "https://findadoc-7179.twil.io/no_intro_female_doctors_question.mp3"
        )

=======
        gather.say(
            f"I see. How many of the available doctors are female? Please type the number on your keypad."
        )
    else:
        gather.say(
            f"How many of the available doctors are female? Please type the number on your keypad."
        )

    response = VoiceResponse()
>>>>>>> master
    response.append(gather)

    new_timeouts_count = timeouts_count + 1
    response.redirect(
        f"{public_url}/call/ask_female_doctors_number/{clinic_id}?timeouts_count={new_timeouts_count}",
        method="GET",
    )
    return str(response)


@call_flow_manager.route(
    "/handle_female_doctors_number/<int:clinic_id>", methods=["GET", "POST"]
)
def handle_number_female_doctors_response(clinic_id: int):

    invalid_input_count = int(request.args.get("invalid_input_count", 1))

    logger.info(
        f"invalid_input_count when asking female doctors number: {invalid_input_count}"
    )

    if invalid_input_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)

    if "Digits" in request.values:

        try:
            call_values.female_docs_number = int(request.values["Digits"])
            logger.info(f"female doctors: {call_values.female_docs_number}")

        except (ValueError, TypeError) as e:
            new_invalid_input_count = invalid_input_count + 1
            logger.error(f"type error exception thrown. error message: {e}")
<<<<<<< HEAD
            message_url = "https://findadoc-7179.twil.io/wrong_input.mp3"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_female_doctors_number/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message_url,
=======
            message = "Please try again, enter numeric values only"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_female_doctors_number/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message,
>>>>>>> master
                num_digits=2,
            )

    else:
<<<<<<< HEAD
        message_url = "https://findadoc-7179.twil.io/wrong_input.mp3"
        logger.error("Attribute 'Digits' doesn't exist in request.values")
        return call_methods.handle_unrecognizable_response(
            f"/call/ask_female_doctors_number/{clinic_id}?invalid_input_count={invalid_input_count}",
            message_url,
=======
        message = (
            "I'm sorry, I didn't get that. Could you type the number on your keypad?"
        )
        logger.critical("Attribute 'Digits' doesn't exist in request.values")
        return call_methods.handle_unrecognizable_response(
            f"/call/ask_female_doctors_number/{clinic_id}?invalid_input_count={invalid_input_count}",
            message,
>>>>>>> master
            num_digits=2,
        )

    return call_methods.handle_successful_call(clinic_id)
