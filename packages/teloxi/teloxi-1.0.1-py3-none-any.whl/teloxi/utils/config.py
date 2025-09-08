
import re



def send_code_text(code_type: str) -> str:

    code_types={
        # Type of verification code that will be sent next if you call the resendCode method
        "CodeTypeSms":"SMS Message",
        "CodeTypeCall":"Phone Call",
        "CodeTypeFlashCall":"Flash Call",
        "CodeTypeMissedCall":"Missed Call",
        "CodeTypeFragmentSms":"Fragment SMS",

        # Type of the verification code that was sent
        "SentCodeTypeApp":"Telegram App",
        "SentCodeTypeSms":"SMS Message",
        "SentCodeTypeCall":"Phone Call",
        "SentCodeTypeFlashCall":"Flash Call",
        "SentCodeTypeMissedCall":"Missed Call",
        "SentCodeTypeEmailCode":"Email",
        "SentCodeTypeSetUpEmailRequired":"Set Up Email Required",
        "SentCodeTypeFragmentSms":"Fragment SMS",
        "SentCodeTypeFirebaseSms":"Firebase SMS",
        "SentCodeTypeSmsWord":"SMS Word",
        "SentCodeTypeSmsPhrase":"SMS Phrase",
        }

    if code_type in code_types:
        return code_types[code_type]



    cleaned = code_type.replace("SentCodeType", "").replace("CodeType", "")
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', cleaned)
    return spaced.strip().title()
