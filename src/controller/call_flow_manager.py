from flask import request, Blueprint
from twilio.twiml.voice_response import VoiceResponse, Gather, Redirect

from util.logger import logger
from util.ai.nav_menu_navigator import find_next_nav_menu_key
import services.calls.active_call_methods as call_methods
import config.active_call_values as call_values
from util.ai.pregenerated_transcript_detector import detect_pregenerated_transcript

import os

call_flow_manager = Blueprint("call_flow_manager", __name__, url_prefix="/call")

public_url = os.environ.get("NGROK_URL")

# consider adding gpt to identify if human or robot:
# sometimes we may have a bot saying "the expected time to speak to someone is of 3 minutes"
# which would trigger /intro_message.
@call_flow_manager.route("/handle_on_hold/<int:clinic_id>", methods=["GET", "POST"])
def handle_on_hold(clinic_id: int):

    print("handle on hold form data: ", request.form.to_dict())

    logger.debug(f"\n--now in handle on hold--\n")

    speech_result = request.form.get("SpeechResult", "")

    if speech_result != "":

        logger.debug(f"\ntranscript: {speech_result}\n")

        if "hello" in speech_result:

            redirect = VoiceResponse()
            redirect.redirect(
                f"{public_url}/call/intro_message/{clinic_id}", method="POST"
            )
            return str(redirect)

        is_robot = detect_pregenerated_transcript(speech_result)
        logger.debug(f"\is robot? : {is_robot}\n")

        if is_robot == False:

        # Consider adding another gpt task that identifies if a digit should be returned
        #   if yes, then redirect to machine detection with the transcript attached,
        #   otherwise just ignore it and keep waiting
            
            redirect_response = VoiceResponse()
            redirect_response.redirect(f"{public_url}/call/intro_message/{clinic_id}")
            return str(redirect_response)

    repetition_count = int(request.args.get("repetition_count", 0))
    logger.loud(f"repetition_count: {repetition_count}")

    if repetition_count > 15:
        hangup = VoiceResponse().hangup()
        return str(hangup)

    print("on hold data: ", request.form.to_dict())

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        speech_model="phone_call",
        enhanced="true",
        action=f"{public_url}/call/handle_on_hold/{clinic_id}",
        speechTimeout=1,
        hints="$OPERAND, press $OPERAND"
    )
    response.append(gather)

    new_repetition_count = repetition_count + 1
    response.redirect(
        f"{public_url}/call/handle_on_hold/{clinic_id}?repetition_count={new_repetition_count}",
        method="POST",
    )
    return str(response)


@call_flow_manager.route("/machine_detection/<int:clinic_id>", methods=["GET", "POST"])
def handle_machine_detection(clinic_id: int):

    logger.debug(f"machine detection endpoint form:  {request.form.to_dict()}")
    answeredBy = request.form.get("AnsweredBy", "")
    logger.debug(f"answeredBy: {answeredBy}")

    response = VoiceResponse()

    # answeredBy can be: human, machine_start, fax or unknown.
    if "human" in answeredBy:
        response.redirect(f"{public_url}/call/intro_message/{clinic_id}", method="POST")
        return str(response)
    
    if "fax" in answeredBy:
        logger.error(f"answeredBy is either fax or unknown. answeredBy: {answeredBy} ")
        logger.info(f"finishing call...")
        hangup = VoiceResponse().hangup()
        return str(hangup)

    speech_result = request.form.get("SpeechResult", "")
    logger.debug(f"speech result: {speech_result}")

    if speech_result != "":

        try:
            next_nav_menu_data = find_next_nav_menu_key(speech_result)
            digit = next_nav_menu_data["digit"]
            human_reached = next_nav_menu_data["human_reached"]
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

            logger.info("human was reached and no digits need to be played. Redirecting to on hold...")

            response.redirect(
                f"{public_url}/call/handle_on_hold/{clinic_id}", method="POST"
            )
            return str(response)

        else:
            logger.debug(f"played digit: {digit}")
            response.play("", digits=str(digit))

    logger.debug("\ngather has been triggered\n")
    gather = Gather(
        input="speech",
        speech_model="phone_call",
        enhanced="true",
        action=f"{public_url}/call/machine_detection/{clinic_id}",
        speech_timeout=1,
        hints="$OPERAND, press $OPERAND"
    )
    response.append(gather)
    return str(response)


@call_flow_manager.route("/intro_message/<int:clinic_id>", methods=["GET", "POST"])
def intro_message(clinic_id: int):

    logger.info(f"\nintro message request form: {request.form.to_dict()}")
    logger.info(f"intro message request args: {request.args.to_dict()}\n")

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

    logger.loud(f"HERE IS THE TWIML: {response}")

    return str(response)


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

            logger.loud("User chose to answer both questions...continuing to the next question now")

            redirect_response = VoiceResponse()
            redirect_response.redirect(
                f"{public_url}/call/ask_male_doctors_number/{clinic_id}", method="GET"
            )
            return str(redirect_response)

        if choice == "2":
            logger.loud("User chose not to answer questions...ending call now")
            return call_methods.outro_message()

        if choice == "3":
            new_prompt_retry_count = prompt_retry_count + 1
            url = f"{public_url}/call/intro_message/{clinic_id}?prompt_retry_count={new_prompt_retry_count}&invalid_input_count={invalid_input_count}"
            response.redirect(url, method="POST")
            return str(response)

        else:
            new_invalid_input_count = invalid_input_count + 1

            if prompt_retry_count >= 3:
                message_url = "https://findadoc-7179.twil.io/intro_error_input_2_options.mp3"
            else:
                message_url = "https://findadoc-7179.twil.io/intro_error_input_3_options.mp3"

            return call_methods.handle_unrecognizable_response(
                f"call/handle_intro_message_response/{clinic_id}?prompt_retry_count={prompt_retry_count}&invalid_input_count={new_invalid_input_count}",
                message_url,
                num_digits=1,
            )

@call_flow_manager.get("/ask_male_doctors_number/<int:clinic_id>")
def ask_male_doctors_number(clinic_id: int):

    timeouts_count = int(request.args.get("timeouts_count", 0))

    logger.info(f"timeouts_count when asking male doctors number: {timeouts_count}")

    if timeouts_count > call_values.ENDPOINT_HIT_LIMIT:
        return call_methods.handle_endpoint_limits(clinic_id)
    
    response = VoiceResponse()

    gather = Gather(
        action=f"{public_url}/call/handle_number_male_doctors_response/{clinic_id}",
        timeout=call_values.timeout,
        num_digits=2,
    )

    if timeouts_count == 0:
        response.play("https://findadoc-7179.twil.io/male_doctors_question.mp3")
    else:
        response.play("https://findadoc-7179.twil.io/no_intro_male_doctors_question.mp3")


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
            message_url = "https://findadoc-7179.twil.io/wrong_input.mp3"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_number_male_doctors_response/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message_url,
                num_digits=2,
            )

    else:
        message_url = (
            "https://findadoc-7179.twil.io/ask_again_to_type_input.mp3"
        )
        logger.critical("Attribute 'Digits' doesn't exist in request values")

        new_invalid_input_count = invalid_input_count + 1
        return call_methods.handle_unrecognizable_response(
            f"/call/handle_intro_response/{clinic_id}?invalid_input_count={new_invalid_input_count}",
            message_url,
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

    response = VoiceResponse()

    gather = Gather(
        action=f"{public_url}/call/handle_female_doctors_number/{clinic_id}",
        timeout=call_values.timeout,
        num_digits=2,
    )

    if timeouts_count == 0:
        response.play("https://findadoc-7179.twil.io/female_doctors_question.mp3")
    else:
        response.play("https://findadoc-7179.twil.io/no_intro_female_doctors_question.mp3")

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
            message_url = "https://findadoc-7179.twil.io/wrong_input.mp3"
            return call_methods.handle_unrecognizable_response(
                f"/call/handle_female_doctors_number/{clinic_id}?invalid_input_count={new_invalid_input_count}",
                message_url,
                num_digits=2,
            )

    else:
        message_url = (
            "https://findadoc-7179.twil.io/wrong_input.mp3"
        )
        logger.critical("Attribute 'Digits' doesn't exist in request.values")
        return call_methods.handle_unrecognizable_response(
            f"/call/ask_female_doctors_number/{clinic_id}?invalid_input_count={invalid_input_count}",
            message_url,
            num_digits=2,
        )

    return call_methods.handle_successful_call(clinic_id)
